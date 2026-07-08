"""Python entrypoint for the trangium BatchSolver worker.

Spawns Node.js on ``cubevis/solver/run_worker.js`` (a thin bridge that shims
``self``/``postMessage`` and delegates to ``cubevis/solver/worker.js``), feeds
the input as JSON via stdin, and parses the stream of newline-delimited JSON
messages the worker emits.

The :class:`BatchInput` dataclass exposes exactly the same 11 options as
``worker.js``'s ``main(input)`` function; field names match the JS-side keys
so :meth:`BatchInput.to_worker_dict` is a straight conversion.
"""

from __future__ import annotations
from pathlib import Path

import dataclasses
import json
import subprocess
import sys
from contextlib import nullcontext
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import typer
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.text import Text

_BRIDGE_JS = Path(__file__).with_name("run_worker.js")


class _CasesPerSecondColumn(ProgressColumn):
    """Renders the current processing rate in cases per second."""

    def render(self, task: "Any") -> Text:  # type: ignore[override]
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("? case/s", style="progress.data.speed")
        return Text(f"{speed:,.2f} case/s", style="progress.data.speed")


class BatchSolverError(RuntimeError):
    """Raised on any error reported by the worker or bridge, or on a mismatch
    between the worker's reported ``num-states`` and the number of ``next-state``
    messages actually received.
    """


@dataclass
class SubgroupSpec:
    subgroup: str = ""
    prune: str = ""
    search: str = ""


@dataclass
class SortingSpec:
    # One of: priority | ori-of | ori-at | perm-of | perm-at
    type: str = "priority"
    pieces: str = ""


@dataclass
class BatchInput:
    """Mirrors the ``input`` object accepted by ``worker.js``'s ``main()``.

    Field names match the JS-side keys exactly (camelCase preserved).
    """

    puzzle: str = ""
    ignore: str = ""
    solve: str = ""
    preAdjust: str = ""
    postAdjust: str = ""
    subgroups: list[SubgroupSpec] = field(default_factory=list)
    sorting: list[SortingSpec] = field(default_factory=list)
    esq: str = ""
    rankesq: str = ""
    showPost: bool = False
    optimise: bool = False

    def to_worker_dict(self) -> dict[str, Any]:
        return {
            "puzzle": self.puzzle,
            "ignore": self.ignore,
            "solve": self.solve,
            "preAdjust": self.preAdjust,
            "postAdjust": self.postAdjust,
            "subgroups": [dataclasses.asdict(s) for s in self.subgroups],
            "sorting": [dataclasses.asdict(s) for s in self.sorting],
            "esq": self.esq,
            "rankesq": self.rankesq,
            "showPost": self.showPost,
            "optimise": self.optimise,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BatchInput":
        subs = [SubgroupSpec(**s) for s in d.get("subgroups", [])]
        sortings = [SortingSpec(**s) for s in d.get("sorting", [])]
        return cls(
            puzzle=d.get("puzzle", ""),
            ignore=d.get("ignore", ""),
            solve=d.get("solve", ""),
            preAdjust=d.get("preAdjust", ""),
            postAdjust=d.get("postAdjust", ""),
            subgroups=subs,
            sorting=sortings,
            esq=d.get("esq", ""),
            rankesq=d.get("rankesq", ""),
            showPost=bool(d.get("showPost", False)),
            optimise=bool(d.get("optimise", False)),
        )


@dataclass
class CaseResult:
    index: int
    case_num: int
    setup: str
    solutions: list[str] = field(default_factory=list)


@dataclass
class BatchResult:
    num_states: Optional[int] = None
    cases: list[CaseResult] = field(default_factory=list)
    move_weights: dict[str, float] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    # Intermediate "N (not reduced)" strings emitted during BFS.
    bfs_progress: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "num_states": self.num_states,
            "cases": [dataclasses.asdict(c) for c in self.cases],
            "move_weights": self.move_weights,
            "errors": self.errors,
            "bfs_progress": self.bfs_progress,
        }


MessageCallback = Callable[[dict[str, Any]], None]


def run_batch(
    inp: BatchInput,
    *,
    node_path: Path = Path("node"),
    on_message: Optional[MessageCallback] = None,
    show_progress: bool = True,
    max_old_space_size_mb: int = 1024 * 1024,
) -> BatchResult:
    """Run the BatchSolver worker on ``inp`` and return the collected results.

    Parameters
    ----------
    inp:
        Worker input. See :class:`BatchInput`.
    node_path:
        Path to (or name of, on PATH) the Node.js executable. Default ``"node"``.
    on_message:
        Optional callback invoked with every raw ``{"type": ..., "value": ...}``
        message dict as it arrives — useful for streaming progress display.
    show_progress:
        If ``True`` (the default), display a rich progress bar on stderr that
        shows cases solved / total and the current processing speed. Set to
        ``False`` to suppress it (e.g. when piping output or running in a
        non-interactive context).
    max_old_space_size_mb:
        Value passed to Node's ``--max-old-space-size`` flag (in MB). Defaults
        to 1 TiB so the V8 heap effectively never caps the run; the OS remains
        the real limit.

    Raises
    ------
    BatchSolverError
        If the worker reported any error ``stop`` messages, if the Node bridge
        exited with a non-zero code, or if the reported ``num-states`` does not
        match the number of ``next-state`` messages received.
    """
    if not _BRIDGE_JS.exists():
        raise FileNotFoundError(f"Node bridge not found at {_BRIDGE_JS}")

    proc = subprocess.Popen(
        [
            node_path.as_posix(),
            f"--max-old-space-size={max_old_space_size_mb}",
            str(_BRIDGE_JS),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(_BRIDGE_JS.parent),
        text=True,
        encoding="utf-8",
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None

    try:
        proc.stdin.write(json.dumps(inp.to_worker_dict()))
        proc.stdin.close()
    except BrokenPipeError:
        # Worker may have exited before consuming stdin; downstream error
        # handling (return code / errors list) will surface the real cause.
        pass

    result = BatchResult()

    if show_progress:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[progress.percentage]{task.percentage:>5.1f}%"),
            _CasesPerSecondColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            transient=False,
        )
        progress_ctx: Any = progress
    else:
        progress = None
        progress_ctx = nullcontext()

    with progress_ctx:
        task_id = None
        if progress is not None:
            task_id = progress.add_task("Preparing solver…", total=None, start=False)

        for raw in proc.stdout:
            line = raw.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                result.errors.append(f"Malformed JSON from worker: {line!r}")
                continue

            if on_message is not None:
                on_message(msg)

            mtype = msg.get("type")
            mval = msg.get("value")

            if mtype == "moveWeights":
                # Bridge converts JS Map -> list of [k, v] pairs.
                if isinstance(mval, list):
                    result.move_weights = {k: v for k, v in mval}
            elif mtype == "num-states":
                if isinstance(mval, int):
                    result.num_states = mval
                    if progress is not None and task_id is not None:
                        progress.update(
                            task_id,
                            total=mval,
                            description=f"Solving {mval} cases",
                        )
                        progress.start_task(task_id)
                else:
                    result.bfs_progress.append(str(mval))
                    if progress is not None and task_id is not None:
                        progress.update(
                            task_id,
                            description=f"BFS: {mval}",
                        )
            elif mtype == "next-state":
                result.cases.append(CaseResult(
                    index=int(mval["index"]),
                    case_num=int(mval["num"]),
                    setup=str(mval["setup"]),
                ))
                if progress is not None and task_id is not None:
                    progress.update(task_id, advance=1)
            elif mtype == "solution":
                if result.cases:
                    result.cases[-1].solutions.append(str(mval))
                else:
                    result.errors.append(f"Stray solution before next-state: {mval!r}")
            elif mtype == "stop":
                if mval is None:
                    # Terminal stop — consume any remaining output then break.
                    break
                result.errors.append(str(mval))
            # depthUpdate / set-depth / debug are ignored here but still delivered
            # to on_message for callers that want them.

    stderr_data = proc.stderr.read() or ""
    return_code = proc.wait()

    if return_code != 0:
        detail = stderr_data.strip() or "(no stderr)"
        msg = f"Node bridge exited with code {return_code}: {detail}"
        if result.errors:
            msg = "Worker errors: " + " | ".join(result.errors) + "\n" + msg
        raise BatchSolverError(msg)

    if result.errors:
        raise BatchSolverError("Worker reported errors: " + " | ".join(result.errors))

    if result.num_states is not None and result.num_states != len(result.cases):
        raise BatchSolverError(
            f"Case count mismatch: worker reported num_states={result.num_states} "
            f"but received {len(result.cases)} next-state messages."
        )

    return result


app = typer.Typer(
    add_completion=False,
    help="Run the trangium BatchSolver worker.js from Python.",
)


@app.command()
def solve(
    input: Optional[Path] = typer.Option(
        None, "--input", "-i",
        exists=True, dir_okay=False, readable=True,
        help="Path to a JSON file with the 11 worker input fields.",
    ),
    stdin: bool = typer.Option(
        False, "--stdin",
        help="Read the input JSON object from stdin instead of a file.",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o",
        dir_okay=False, writable=True,
        help="Path to write BatchResult JSON. Defaults to stdout.",
    ),
    node_path: str = typer.Option(
        "node", "--node-path",
        help="Node.js executable path (default: 'node' on PATH).",
    ),
    progress: bool = typer.Option(
        True, "--progress/--no-progress",
        help="Show a rich progress bar on stderr (default on).",
    ),
    verbose: bool = typer.Option(
        False, "--verbose",
        help="Also print per-message worker output to stderr.",
    ),
) -> None:
    """Solve a batch using worker.js and write the result as JSON."""
    if stdin == (input is not None):
        typer.echo("Exactly one of --input or --stdin must be provided.", err=True)
        raise typer.Exit(code=2)

    if stdin:
        data = json.loads(sys.stdin.read())
    else:
        assert input is not None
        data = json.loads(input.read_text(encoding="utf-8"))
    inp = BatchInput.from_dict(data)

    def _log(msg: dict[str, Any]) -> None:
        t = msg.get("type")
        if t in ("next-state", "num-states", "stop"):
            typer.echo(f"[{t}] {msg.get('value')}", err=True)

    try:
        result = run_batch(
            inp,
            node_path=node_path,
            on_message=_log if verbose else None,
            show_progress=progress,
        )
    except BatchSolverError as e:
        typer.echo(f"BatchSolverError: {e}", err=True)
        raise typer.Exit(code=1)

    total_solutions = sum(len(c.solutions) for c in result.cases)
    typer.echo(
        f"cases={len(result.cases)} num_states={result.num_states} "
        f"solutions={total_solutions} errors={len(result.errors)}",
        err=True,
    )

    out_json = json.dumps(result.to_dict(), indent=2)
    if output is not None:
        output.write_text(out_json, encoding="utf-8")
    else:
        typer.echo(out_json)


if __name__ == "__main__":
    app()

import typer 
import json
import shutil
import logging
import re
from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, InvalidResponse
from cubevis.scripts.jsons import gen_jsons
from cubevis.scripts.images import gen_images, make_batch_solver_string
from cubevis.colorizer import get_colorizer
from cubevis.solver.solver import run_batch, BatchInput, SubgroupSpec, SortingSpec
from pathlib import Path


# Matches typical cube move tokens: optional layer number, face/axis letter(s),
# optional 'w' for wide, optional "2" and/or "'" (prime). Examples: R, U', R2, Rw, 3Rw', x, M2
_MOVE_RE = re.compile(r"^\d*[A-Za-z]+w?['2]{0,2}$")


class MovesPrompt(Prompt):
    """Rich prompt for a whitespace-separated sequence of cube moves.

    Accepts empty input. Rejects tokens that don't look like moves.
    """

    def process_response(self, value: str) -> str:
        value = value.strip()
        if not value:
            return ""
        bad = [tok for tok in value.split() if not _MOVE_RE.match(tok)]
        if bad:
            raise InvalidResponse(
                f"[prompt.invalid]Not valid move tokens: {', '.join(bad)}"
            )
        return str(value.split())


def full_pipeline(
        algset: str, 
        colorizer_name: str, 
        data: Path = Path('./data'), 
        node_path: Path = Path("node"), 
        alg_trainers: Path = Path("../Alg-Trainers"), 
        override_prune: int | None =None, 
        override_search: int | None = None, 
        override_subgroup: str | None = None,
        override_adjust: str | None = None,
        override_preadjust: str | None = None,
        override_postadjust: str | None = None,
    ):
    console = Console()
    puzzle = "-".join(colorizer_name.split("-")[:-1])
    colorizer = get_colorizer(colorizer_name)
    data_root = data / puzzle / algset
    pictures_root = data_root / "pic"
    csv_file = data_root / f"{puzzle.lower()}{algset.lower()}.csv"
    json_file = csv_file.with_suffix(".json")
    subgroups = []
    for row in colorizer.get_prune_search_subgroup().splitlines():
        subgroup = " ".join(row.split()[2:])
        prune, search = row.split()[:2]
        if override_subgroup is not None:
            subgroup = override_subgroup
        if override_prune is not None:
            prune = str(override_prune)
        if override_search is not None:
            search = str(override_search)
        spec = SubgroupSpec(subgroup, prune, search)
        subgroups.append(spec)
    
    # optional adjust move override
    preadjust = colorizer.get_pre_adjust()
    postadjust = colorizer.get_post_adjust()
    if override_adjust == "none":
        override_adjust = ""
    if override_postadjust == "none":
        override_postadjust = ""
    if override_preadjust == "none":
        override_postadjust = ""
    if override_adjust is not None:
        preadjust = override_adjust
        postadjust = override_adjust
    if override_preadjust is not None:
        preadjust = override_preadjust
    if override_postadjust is not None:
        postadjust = override_postadjust
    output = gen_images(colorizer_name, csv_file, pictures_root)
    batch_solver_scrambles = output['setups']
    num_cases = len(output['df'])
    def on_message(msg):
        mtype = msg.get("type")
        mval = msg.get("value")
        if mtype == "num-states":
            assert type(mval) == int
            if num_cases != mval:
                logging.root.warning("Number of states reported by batch solver doesn't match number of cases in algs csv file.")
                # TODO: implement finding the duplicates
    
    result = None
    if json_file.is_file():
        console.print("[red]Solutions file already exists, do you want to \n(s) skip generation \n(f) re-generate fully \n(m) generate missing \n(a) abort/exit")
        answer = ""
        while answer.lower() not in "fmas" or answer == "":
            answer = input(">")

        if answer == "a":
            exit(0)

        if answer == "s":
            result = json.loads(json_file.read_text())

        if answer == "m":
            scrambles = json.loads(json_file.read_text())
            missing_scrambles_indexes = []
            missing_scrambles = []
            for i, case in enumerate(scrambles['cases']):
                if len(case['solutions']) == 0:
                    missing_scrambles_indexes.append(i)
                    missing_scrambles.append(batch_solver_scrambles[i])
            inp = BatchInput(
                puzzle=colorizer.get_definitions(),
                ignore=colorizer.get_equivalences(),
                solve=make_batch_solver_string(missing_scrambles),
                preAdjust=preadjust,
                postAdjust=postadjust,
                subgroups=subgroups,
            )
            def on_message_missing(msg):
                mtype = msg.get("type")
                mval = msg.get("value")
                if mtype == "num-states":
                    assert type(mval) == int
                    if len(missing_scrambles) != mval:
                        logging.root.warning("Number of states reported by batch solver doesn't match number of cases in algs csv file.")
                        # TODO: implement finding the duplicates
            result = run_batch(inp, node_path=node_path, on_message=on_message_missing).to_dict()
            assert len(missing_scrambles_indexes) == len(result['cases']), "something went wrong and the number of solutions is not equal to the number of missing scrambles"
            for index, case in zip(missing_scrambles_indexes, result['cases']):
                scrambles['cases'][index]['solutions'] = case['solutions']
            result = scrambles

    if result is None:
        inp = BatchInput(
            puzzle=colorizer.get_definitions(),
            ignore=colorizer.get_equivalences(),
            solve=make_batch_solver_string(batch_solver_scrambles),
            preAdjust=preadjust,
            postAdjust=postadjust,
            subgroups=subgroups,
        )
        console.print(Panel(f"""[red]{inp.puzzle}
[blue]{inp.ignore}
[green]{inp.solve[:500]}...
[purple]{inp.subgroups}
{inp.preAdjust}
{inp.postAdjust}""", title="Starting scramble generation with settings"))
        result = run_batch(inp, node_path=node_path, on_message=on_message).to_dict()


    for case in result['cases']:
        solutions = sorted(list(set(case['solutions'])), key=lambda x: len(x.split()))
        case['solutions'] = solutions
    with open(json_file, "w") as file:
        json.dump(result, file)
    console.print("[green]Finished solving cases")

    gen_jsons(colorizer_name, json_file, csv_file, data_root)
    console.print("[green]Finished generating jsons")
    relevant_files = [
        "algs_info.json",
        "algsets_info.json",
        "combined.json",
        "groups_info.json",
        "scrambles.json",
        "selected_algsets.json"
    ]
    alg_trainer_name = f"{puzzle}-{algset}-Trainer"
    alg_trainer_path = alg_trainers / alg_trainer_name
    if alg_trainer_path.is_dir(): 
        console.print(f"[green]Alg trainer {alg_trainer_path.as_posix()} directory, copying relevant files.")
        for file in relevant_files:
            print(f"Copying {file}")
            shutil.copy(data_root / file, alg_trainer_path / file)
    if not alg_trainer_path.is_dir():
        console.print(f"[red]Alg trainer {alg_trainer_path.as_posix()} not a directory, creating new alg trainer directory, copying relevant files.")
        create_new_trainer(trainer_path=alg_trainer_path, data_root=data_root, relevant_files=relevant_files, puzzle=puzzle, algset=algset)
    
def create_new_trainer(trainer_path: Path, data_root: Path, relevant_files: list[str], puzzle: str, algset: str):
    env = Environment(
        loader=PackageLoader("cubevis.scripts"),
        autoescape=select_autoescape()
    )
    template_keys = {}
    template_keys['max_algs_per_row'] = IntPrompt.ask(
        "max_algs_per_row", default=8
    )
    template_keys['pre_rotations'] = MovesPrompt.ask(
        "pre_rotations", default=""
    )
    template_keys['post_rotations'] = MovesPrompt.ask(
        "post_rotations", default=""
    )
    template_keys['pre_moves'] = MovesPrompt.ask(
        "pre_moves", default="U U' U2"
    )
    template_keys['post_moves'] = MovesPrompt.ask(
        "post_moves", default="U U' U2"
    )
    template_keys['puzzle'] = puzzle
    template_keys['algset'] = algset
    index_json_entry = {
        "name": algset,
        "location": trainer_path.name
    }
    index_json_group = Prompt.ask(
        "Algset group name:", default=puzzle
    )
    
    algsinfo = env.get_template("algsinfo.js.jinja").render(**template_keys)
    index = env.get_template("index.html.jinja").render(**template_keys)
    trainer_path.mkdir()
    (trainer_path / "algsinfo.js").write_text(algsinfo)
    (trainer_path / "index.html").write_text(index)
    for file in relevant_files:
        shutil.copy(data_root / file, trainer_path / file)
    
    index_json = json.loads((trainer_path.parent / "index.json").read_text())
    if index_json_group not in index_json:
        index_json[index_json_group] = []
    
    for trainer_entry in index_json[index_json_group]:
        if trainer_entry['name'] == trainer_path.name:
            raise ValueError("Trainer path already exists in index.json")
    
    index_json[index_json_group].append(index_json_entry)
    (trainer_path.parent / "index.json").write_text(json.dumps(index_json))
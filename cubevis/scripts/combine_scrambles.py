import polars as pl
from pathlib import Path
import typer
app = typer.Typer()

@app.command()
def write_missing_scrambles(batch_solver_input: Path, scrambles: Path, batch_solver_output: Path):
    input_lines = batch_solver_input.read_text().splitlines()[1:-1]
    df = pl.read_excel(scrambles)
    missing = ["["]
    for i, line in enumerate(input_lines):
        col = pl.col(df.columns[i * 2 + 1])
        if len(df.select(col).filter(col.is_not_null(), (col.str.strip_chars() != ""))) == 0:
            missing.append(line)
    missing.append("]")
    batch_solver_output.write_text("\n".join(missing))

@app.command()
def combine_scrambles(large: Path, small: Path, out: Path):
    ldf = pl.read_excel(large)
    sdf = pl.read_excel(small)
    small_column = 0
    for i, col in enumerate(ldf.columns):
        if i % 2 == 0:
            continue
        numeric_col = ldf.columns[i - 1]
        if len(ldf.select(col).filter(pl.col(col).is_not_null(), (pl.col(col) != ""))) == 0:
            move_counts = sdf.get_column(sdf.columns[small_column]).head(20)
            algs = sdf.get_column(sdf.columns[small_column + 1]).head(20)
            ldf = ldf.with_columns(pl.lit(move_counts).alias(numeric_col), pl.lit(algs).alias(col))
            small_column += 2
    ldf.write_excel(out)

if __name__ == "__main__":
    app()
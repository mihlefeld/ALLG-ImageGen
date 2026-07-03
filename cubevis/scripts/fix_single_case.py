import typer
from pathlib import Path
from cubevis.scripts.images import gen_images
app = typer.Typer()

@app.command()
def fix_specific_cases(puzzle: str, algs_csv: Path, gen_out: Path, scrambles: Path, cases: list[str]):
    import polars as pl
    gen_images(puzzle, algs_csv, gen_out)
    algs = pl.read_csv(algs_csv)
    algs = algs.with_columns(bsid=pl.row_index() + 1).filter(pl.col("Name").is_in(cases))
    bs_lines = (gen_out / "_batch_solver_input.txt").read_text().splitlines()
    new_batch_solver_input = ["["]
    for bsid in algs['bsid']:
        new_batch_solver_input.append(bs_lines[bsid])
    new_batch_solver_input.append("]")
    print("\n".join(new_batch_solver_input))
    new_scrambles = None
    while True:
        path_to_partial_scrambles = input("Path to batch solver outpt excel (q to quit): ")
        if path_to_partial_scrambles.lower() == 'q':
            exit(0)
        try:
            new_scrambles = pl.read_excel(path_to_partial_scrambles)
            break
        except Exception as e:
            print("Failed to read excel {e}")
    assert new_scrambles is not None
    scrambles_df = pl.read_excel(scrambles)
    for bsid, new_scramble_col in zip(algs['bsid'], new_scrambles.columns[1::2]):
        old_scramble_col = scrambles_df.columns[(bsid - 1) * 2 + 1]
        print(scrambles_df[old_scramble_col][0], bsid - 1)
        old_scrambles_len = len(scrambles_df[old_scramble_col])
        new_scramble = pl.Series(old_scramble_col, ([scramble for scramble in new_scrambles[new_scramble_col]] + [""] * old_scrambles_len)[:old_scrambles_len])
        print(new_scramble[0])
        scrambles_df = scrambles_df.with_columns(pl.lit(new_scramble).alias(old_scramble_col))
    scrambles_df.write_excel(scrambles.with_suffix('.new.xlsx'))

app() 
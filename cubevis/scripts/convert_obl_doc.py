import polars as pl
import typer
import re
from cubevis.scripts.karnotation import karnaukh_to_standard
from pathlib import Path
app = typer.Typer()

@app.command()
def main(input_path: Path, output_path: Path):
    df = pl.read_csv(input_path)
    new_data = []
    for row in df.iter_rows(named=True):
        if row["Algs"] is None:
            continue
        lines = row['Algs'].splitlines()
        new_lines = []
        for line in lines:
            match_obj = re.match(r"(\[['a-zA-Z2 ]*\] )?([^\[\]]*)", line)
            if not match_obj:
                continue
            abf = match_obj.group(1)
            abf = "" if abf is None else abf
            alg = match_obj.group(2)
            standard = karnaukh_to_standard(alg)
            new_lines.append(abf + standard)
            new_lines.append(abf + alg)
        line = "\n".join(new_lines)
        row.update({"Algs": line})
        new_data.append(row)
    pl.DataFrame(new_data).write_csv(output_path)

app()
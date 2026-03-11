import typer
import polars as pl
from collections import defaultdict
from pathlib import Path

app = typer.Typer()

def join_algs(algs: str):
    return "\n".join(algs).replace("’", "'")

def tl4eb(pyarminx_sheet: Path):
    alg_set = "TL4E-B"
    df = pl.read_excel(pyarminx_sheet, sheet_name=alg_set, has_header=False)
    data = defaultdict(list)
    current_alg = None
    current_algs_plus = []
    current_algs_minus = []
    for cols in df.filter(pl.row_index() != 1).iter_rows():
        if cols[0] != None:
            if any(cols[1:]):
                if current_alg is None:
                    current_alg = cols[0]
                if len(current_algs_plus) != 0:
                    data['Algset'].append(f"{alg_set} +")
                    data['Group'].append(f"{current_group}")
                    data['Name'].append(f"{current_alg}")
                    data['Algs'].append(join_algs(current_algs_plus))
                    current_algs_plus = []
                if len(current_algs_minus) != 0:
                    data['Algset'].append(f"{alg_set} -")
                    data['Group'].append(f"{current_group}")
                    data['Name'].append(f"{current_alg}")
                    data['Algs'].append(join_algs(current_algs_minus))
                    current_algs_minus = []
                current_alg = cols[0]
            else:
                current_group = cols[0]
        if cols[2]:
            current_algs_plus.append(cols[2])
        if cols[4]:
            current_algs_minus.append(cols[4])

    if len(current_algs_plus) != 0:
        data['Algset'].append(f"{alg_set} +")
        data['Group'].append(f"{current_group}")
        data['Name'].append(f"{current_alg}")
        data['Algs'].append(join_algs(current_algs_plus))
    if len(current_algs_minus) != 0:
        data['Algset'].append(f"{alg_set} -")
        data['Group'].append(f"{current_group}")
        data['Name'].append(f"{current_alg}")
        data['Algs'].append(join_algs(current_algs_minus))
    result = pl.DataFrame(data)
    return result

def tl4er(pyarminx_sheet: Path):
    alg_set = "TL4E-R"
    df = pl.read_excel(pyarminx_sheet, sheet_name=alg_set, has_header=False)
    data = defaultdict(list)
    current_algs_left_plus = []
    current_algs_right_plus = []
    current_algs_left_minus = []
    current_algs_right_minus = []
    current_alg = None
    current_group = None
    for cols in df.filter(pl.row_index() != 1).iter_rows():
        if cols[0] != None:
            if any(cols[1:]) and (cols[2] != "Bar on Left"):
                if current_group is None:
                    current_group = new_group
                if  current_alg is None:
                    current_alg = cols[0]
                if len(current_algs_left_plus) != 0:
                    data['Algset'].append(f"{alg_set} L+")
                    data['Group'].append(f"{current_group}")
                    data['Name'].append(f"{current_alg}")
                    data['Algs'].append(join_algs(current_algs_left_plus))
                    current_algs_left_plus = []
                if len(current_algs_right_plus) != 0:
                    data['Algset'].append(f"{alg_set} R+")
                    data['Group'].append(f"{current_group}")
                    data['Name'].append(f"{current_alg}")
                    data['Algs'].append(join_algs(current_algs_right_plus))
                    current_algs_right_plus = []
                if len(current_algs_left_minus) != 0:
                    data['Algset'].append(f"{alg_set} L-")
                    data['Group'].append(f"{current_group}")
                    data['Name'].append(f"{current_alg}")
                    data['Algs'].append(join_algs(current_algs_left_minus))
                    current_algs_left_minus = []
                if len(current_algs_right_minus) != 0:
                    data['Algset'].append(f"{alg_set} R-")
                    data['Group'].append(f"{current_group}")
                    data['Name'].append(f"{current_alg}")
                    data['Algs'].append(join_algs(current_algs_right_minus))
                    current_algs_right_minus = []
                current_alg = cols[0]
                current_group = new_group
            else:
                new_group = cols[0]
        if cols[2] and cols[2] != "Bar on Left":
            current_algs_left_plus.append(cols[2])
        if cols[3] and cols[3] != "Bar on Right":
            current_algs_right_plus.append(cols[3])
        if cols[5] and cols[5] != "Bar on Left":
            current_algs_left_minus.append(cols[5])
        if cols[6] and cols[6] != "Bar on Right":
            current_algs_right_minus.append(cols[6])

    if len(current_algs_left_plus) != 0:
        data['Algset'].append(f"{alg_set} L+")
        data['Group'].append(f"{current_group}")
        data['Name'].append(f"{current_alg}")
        data['Algs'].append(join_algs(current_algs_left_plus))
        current_algs_left_plus = []
    if len(current_algs_right_plus) != 0:
        data['Algset'].append(f"{alg_set} R+")
        data['Group'].append(f"{current_group}")
        data['Name'].append(f"{current_alg}")
        data['Algs'].append(join_algs(current_algs_right_plus))
        current_algs_right_plus = []
    if len(current_algs_left_minus) != 0:
        data['Algset'].append(f"{alg_set} L-")
        data['Group'].append(f"{current_group}")
        data['Name'].append(f"{current_alg}")
        data['Algs'].append(join_algs(current_algs_left_minus))
        current_algs_left_minus = []
    if len(current_algs_right_minus) != 0:
        data['Algset'].append(f"{alg_set} R-")
        data['Group'].append(f"{current_group}")
        data['Name'].append(f"{current_alg}")
        data['Algs'].append(join_algs(current_algs_right_minus))
        current_algs_right_minus = []

    result = pl.DataFrame(data)
    return result

def ml4e(pyarminx_sheet: Path):
    alg_set = "ML4E "
    df = pl.read_excel(pyarminx_sheet, sheet_name=alg_set, has_header=False)
    data = defaultdict(list)
    current_algs_right = []
    current_algs_left = []
    current_alg = None
    for cols in df.iter_rows():
        if cols[0] != None and any(cols[2:4]) and cols[2] != "Right Slot" and cols[3] != "Left Slot":
            current_alg = cols[0]
            if len(current_algs_right) != 0:
                data['Algset'].append(f"{alg_set}R")
                data['Group'].append(current_group)
                data['Name'].append(current_alg)
                data['Algs'].append(join_algs(current_algs_right))
                current_algs_right = []
            if len(current_algs_left) != 0:
                data['Algset'].append(f"{alg_set}L")
                data['Group'].append(current_group)
                data['Name'].append(current_alg)
                data['Algs'].append(join_algs(current_algs_left))
                current_algs_left = []
        elif cols[0] is not None:
            current_group = cols[0]
        if cols[2] and cols[2] != "Right Slot":
            current_algs_right.append(cols[2])
        if cols[3] and cols[3] != "Left Slot":
            current_algs_left.append(cols[3])

    if len(current_algs_right) != 0:
        data['Algset'].append(f"{alg_set}R")
        data['Group'].append(current_group)
        data['Name'].append(current_alg)
        data['Algs'].append(join_algs(current_algs_right))
        current_algs_right = []
    if len(current_algs_left) != 0:
        data['Algset'].append(f"{alg_set}L")
        data['Group'].append(current_group)
        data['Name'].append(current_alg)
        data['Algs'].append(join_algs(current_algs_left))
    result = pl.DataFrame(data)
    return result

@app.command()
def extract_algs(pyraminx_sheet: Path, pyra_dir: Path, name: list[str], out_name: str | None = None):
    combined_name = name[0] if len(name) == 1 else out_name
    assert combined_name is not None
    out_path = pyra_dir / combined_name.upper() / f"pyra{combined_name.lower()}.csv"
    out_path.parent.mkdir(exist_ok=True, parents=True)
    dfs = []
    for name_ in name:
        fun = {
            "tl4eb": tl4eb,
            "tl4er": tl4er,
            "ml4e": ml4e
        }[name_.lower()]
        dfs.append(fun(pyraminx_sheet))
    df: pl.DataFrame = pl.concat(dfs)
    df = df.with_columns(
        pl.col('Algs')
        .str.replace("Y", "y")
    )
    df.write_csv(out_path)

app()
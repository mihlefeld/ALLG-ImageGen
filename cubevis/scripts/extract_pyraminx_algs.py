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
    for cols in df.filter(pl.row_index() != 1).iter_rows():
        if cols[0] != None:
            if any(cols[1:]) and (cols[2] != "Bar on Left"):
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
            else:
                current_group = cols[0]
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

if __name__ == "__main__":
    as1 = tl4eb("The Pyraminx Sheet.xlsx")
    as1.write_csv("sheet.csv")
    # as2 = ml4e("The Pyraminx Sheet.xlsx")
    # as2.write_csv("sheet.csv")
    # as3 = tl4er("The Pyraminx Sheet.xlsx")
    # as3.write_csv("sheet.csv")
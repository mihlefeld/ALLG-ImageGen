from cubevis.colorizer import SquareOneColorizer
import re
from collections import OrderedDict

def multiple_replace(string, rep_dict, escaped_dict=None):
    pattern = re.compile("|".join([re.escape(k) if escaped_dict is None else k for k in sorted(rep_dict,key=len,reverse=True)]), flags=re.DOTALL)
    if escaped_dict:
        return pattern.sub(lambda x: escaped_dict[x.group(0)], string)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)

move_map = OrderedDict({
    "\\": "/",
    "U": "3,0/",
    "U2": "6,0/",
    "U'": "-3,0/",
    "U2'": "-6,0/",
    "D": "0,3/",
    "D2": "0,6/",
    "D'": "0,-3/",
    "D2'": "0,-6/",
    "u ": "2,-1/",
    "u'": "-2,1/",
    "d ": "-1,2/",
    "d'": "1,-2/",
    "E": "3,-3/",
    "E'": "-3,3/",
    "e": "3,3/",
    "e'": "-3,-3/",
    "F": "4,1/",
    "F'": "-4,-1/",
    "f": "1,4/",
    "f'": "-1,-4/",
    "M": "1,1/",
    "M'": "-1,-1/",
    "m": "2,2/",
    "m'": "-2,-2/",
    "u2": "5,-1/",
    "u2'": "-5,1/",
    "d2": "-1,5/",
    "d2'": "1,-5/",
    "W": "3,0/-3,0/",
    "W'": "-3,0/3,0/",
    "B": "0,3/0,-3/",
    "B'": "0,-3/0,3/",
    "w": "2,-1/-2,1/",
    "w'": "-2,1/2,-1/",
    "b": "-1,2/1,-2/",
    "b'": "1,-2/-1,2/",
    "Ɇ": "3,0/0,-3/",
    "Ɇ'": "-3,0/0,3/",
    "ɇ": "3,0/0,3/",
    "ɇ'": "-3,0/0,-3/",
    "F2": "4,1/-4,-1/",
    "F2'": "-4,-1/4,1/",
    "f2": "1,4/-1,-4/",
    "f2'": "-1,-4/1,4/",
    "T": "2,-4/",
    "T'": "-2,4/",
    "t": "4,-2/",
    "t'": "-4,2/",
    "U3": "3,0/-3,0/3,0/",
    "U3'": "-3,0/3,0/-3,0/",
    "U4": "3,0/-3,0/3,0/-3,0/",
    "U4'": "-3,0/3,0/-3,0/3,0/",
    "D3": "0,3/0,-3/0,3/",
    "D3'": "0,-3/0,3/0,-3/",
    "D3": "0,3/0,-3/0,3/0,-3/",
    "D3'": "0,-3/0,3/0,-3/0,3/",
    "u3": "2,-1/-2,1/2,-1/",
    "u3'": "-2,1/2,-1/-2,1/",
    "d3": "-1,2/1,-2/-1,2/",
    "d3'": "1,-2/-1,2/1,-2/",
    "u4": "2,-1/-2,1/2,-1/-2,1",
    "u4'": "-2,1/2,-1/-2,1/2,-1/",
    "d4": "-1,2/1,-2/-1,2/1,-2/",
    "d4'": "1,-2/-1,2/1,-2/-1,2/",
    "UU": "3,0/3,0/",
    "UU'": "-3,0/-3,0/",
    "DD'": "0,-3/0,-3/",
    "F3": "4,1/-4,-1/4,1/",
    "F3'": "-4,-1/4,1/-4,-1/",
    "f3": "1,4/-1,-4/1,4/",
    "f3'": "-1,-4/1,4/-1,-4/",
    "K": "5,2/",
    "K'": "-5,-2/",
    "k": "2,5/",
    "k'": "-2,-5/",
    "JJ": "/0,-3/3,3/-3,0/",
    "jJ": "/0,-3/3,3/-3,0/",
    "Jj": "/0,-3/3,3/-3,0/",
    "jj": "/0,-3/3,3/-3,0/",
    "bJJ": "/-3,0/3,3/0,-3/",
    "bjJ": "/-3,0/3,3/0,-3/",
    "bJj": "/-3,0/3,3/0,-3/",
    "bjj": "/-3,0/3,3/0,-3/",
    "JN": "/0,-3/0,3/0,-3/0,3/",
    "jN": "/0,-3/0,3/0,-3/0,3/",
    "Jn": "/0,-3/0,3/0,-3/0,3/",
    "jn": "/0,-3/0,3/0,-3/0,3/",
    "NJ": "/3,0/-3,0/3,0/-3,0/",
    "nJ": "/3,0/-3,0/3,0/-3,0/",
    "Nj": "/3,0/-3,0/3,0/-3,0/",
    "nj": "/3,0/-3,0/3,0/-3,0/",
    "NN": "/3,-3/-3,3/",
    "nN": "/3,-3/-3,3/",
    "Nn": "/3,-3/-3,3/",
    "nn": "/3,-3/-3,3/",
    "-NN": "/-3,3/3,-3/",
    "-Nn": "/-3,3/3,-3/",
    "-nN": "/-3,3/3,-3/",
    "-nn": "/-3,3/3,-3/",
    "3Adj": "/3,0/-1,-1/-2,1/",
    "03Adj": "/0,3/-1,-1/1,-2/",
    "-3Adj": "/-3,0/1,1/2,-1/",
    "0-3Adj": "/0,-3/1,1/-1,2/",
    "JR": "/-3,-3/2,-1/-2,1/3,3/",
    "jR": "/-3,-3/2,-1/-2,1/3,3/",
    "Jr": "/-3,-3/1,-2/-1,2/3,3/",
    "jr": "/-3,-3/1,-2/-1,2/3,3/",
    "RJ": "/3,3/1,-2/-1,2/-3,-3/",
    "rJ": "/3,3/2,-1/-2,1/-3,-3/",
    "Rj": "/3,3/1,-2/-1,2/-3,-3/",
    "rj": "/3,3/2,-1/-2,1/-3,-3/",
    "bRJ": "/-3,-3/-2,1/2,-1/3,3/",
    "brJ": "/-3,-3/-1,2/1,-2/3,3/",
    "bRj": "/-3,-3/-2,1/2,-1/3,3/",
    "brj": "/-3,-3/-1,2/1,-2/3,3/",
    "RR": "/2,-1/-2,4/5,-1/-2,1/",
    "rr": "/-2,1/5,-1/-2,4/2,-1/",
    "pJ": "/-2,1/2,2/0,-3/",
    "fpJ": "/2,-1/-2,-2/0,3/",
    "AA": "/0,-3/2,2/0,-3/-2,4/",
    "aa": "/1,-2/2,2/1,-2/-4,2/",
    "TT": "/5,-1/-3,0/-2,-2/0,3/",
    "30Adj": "/3,0/-1,-1/-2,1/",
    "-30Adj": "/0,-1/0,-3/1,1/-1,2/",
    "bJJ+E2": "/-3,0/3,3/0,3/0,6/0,6",
    "bjJ+E2": "/-3,0/3,3/0,3/0,6/0,6",
    "bJj+E2": "/-3,0/3,3/0,3/0,6/0,6",
    "bjj+E2": "/-3,0/3,3/0,3/0,6/0,6",
    "ObOpp": "1,0/-1,-1/3,0/1,1/3,0/-1,-1/0,1",
    "OaOpp": "1,0/-1,-1/-3,0/1,1/-3,0/-1,-1/0,1",
    "bjj OaOpp": "/-3,0/3,3/0,-3/0,1/-1,-1/-3,0/1,1/-3,0/-1,-1/0,1",
    "(e' U)3": "/-3,-3/3,0/-3,-3/3,0/-3,-3/3,0"
    }
)

ud_combinations = {}
for i, u_move in zip([3, -3, 6, 6], ["U", "U'", "U2", "U2'"]):
    for j, d_move in zip([3, -3, 6, 6], ["D", "D'", "D2", "D2'"]):
        ud_combinations[u_move + d_move] = f"{i},{j}/"

for i in range(-5, 7, 1):
    for j in range(-5, 7, 1):
        move_map[f"{i}{j}"] = f"{i},{j}/"

end_of_string_map = {}
escaped_dict = {}
for i in range(-5, 7, 1):
    for j in range(-5, 7, 1):
        end_of_string_map[f"{i}{j}$"] = f"{i},{j}"
        escaped_dict[f"{i}{j}"] = f"{i},{j}"


def karnaukh_to_standard(alg):
    alg = alg.strip()
    alg = multiple_replace(alg, end_of_string_map, escaped_dict)
    alg = multiple_replace(alg, ud_combinations)
    alg = multiple_replace(alg, move_map)
    replaced_parts = alg.split("/")
    replaced_parts = [replaced_parts[0]] + [x for x in replaced_parts[1:-1] if x.strip() != ""] + [replaced_parts[-1]]
    standard_parts = []
    for part in replaced_parts:
        top_total = 0
        down_total = 0
        for double_move in part.split():
            top, down = [int(x.strip(" ")) % 12 for x in double_move.split(",")]
            top_total = (top_total + top) % 12
            down_total = (down_total + down) % 12
        tt = f"{top_total}" if top_total <= 6 else f"-{12 - top_total}"
        dt = f"{down_total}" if down_total <= 6 else f"-{12 - down_total}"
        standard_parts.append(f"{tt},{dt}")

    return " / ".join(standard_parts).strip()


import polars as pl
from pathlib import Path
from cubevis.cube import SquareOne
sq = SquareOneColorizer()
algs_data = {
    "Algset": [],
    "Group": [],
    "Name": [],
    "Algs": []
}
p = Path("data/Square-1 PBL Fixes.xlsx")
tables = range(13, 41)
for sheet_id in tables:
    df = pl.read_excel(p, sheet_id=sheet_id, drop_empty_cols=True, drop_empty_rows=True)
    if df.columns[1].strip().lower() != "image":
        df = df.drop(df.columns[1])
    alg_cols = [df.columns[3]]
    angle_cols = [df.columns[2]]
    name_col = df.columns[0]
    if "Angle_1" in df.columns:
        alg_cols.append(df.columns[4])
        angle_cols.append(df.columns[5])
    for alg_col, angle_col in zip(alg_cols, angle_cols):
        for alg_name, alg_options, angles in df.select(name_col, alg_col, angle_col).filter(pl.col(alg_col).is_not_null()).iter_rows():
            alg_options: str
            angles: str
            algs = [x for x in alg_options.splitlines() if x.strip() != ""]
            if angles is None:
                angles = "\n".join([""] * len(algs))
            angles = ([x for x in angles.splitlines() if x.strip() != ""] + [""] * len(algs))[:len(algs)]
            st_algs = []
            for alg in algs:
                try:
                    st_alg = karnaukh_to_standard(alg)
                    st_alg = sq.fix_last_move_to_cubeshape(st_alg)
                except Exception as e:
                    print(f"<<<<Failed for case {alg_col} {alg_name}:::\n{alg}\n::::with exception {e}>>>>")
                    st_alg = e
                st_algs.append(st_alg)
            csv_algs = []
            for alg, st_alg, angle in zip(algs, st_algs, angles):
                csv_algs.append(f"[{angle}] {st_alg}")
                csv_algs.append(f"[{angle}] {alg}")
            algs_data["Algset"].append("PBL")
            algs_data["Group"].append(alg_col)
            algs_data["Name"].append(alg_name)
            algs_data["Algs"].append("\n".join(csv_algs))

total_df = pl.DataFrame(algs_data)
total_df.write_csv("data/Sq1/PBL/sq1pbl.csv")

from collections import defaultdict
from pathlib import Path
from cubevis.cube import FTO
from cubevis.colorizer import FTOLLColorizer
from cubevis.scripts.images import clean_alg_fto
import polars as pl
import re

def auf(canonical):
    new_canonical = []
    for side in canonical[2:] + canonical[:2]:
        a, b, c = side
        new_canonical.append(((a+1)%3, (b+1)%3, (c+1)%3))
    return tuple(new_canonical)


def get_l6x_case_rep(svg: str):
    color_regex = re.compile(r"'#[A-Fa-f0-9]+'")
    color_1_line = 8
    color_2_line = 15
    color_3_line = 22
    image = svg.splitlines()
    color_to_canonical = {}
    for i, line in enumerate([color_1_line, color_2_line, color_3_line]):
        color_to_canonical[color_regex.search(image[line]).group(0)] = i

    canonical = []
    for i, line in enumerate([color_1_line, color_2_line, color_3_line]):
        color_a = color_to_canonical[color_regex.search(image[line-1]).group(0)]
        color_b = color_to_canonical[color_regex.search(image[line+1]).group(0)]
        canonical.append((color_a, i, color_b))

    return tuple(canonical)

rep_to_case_name = {
    ((1, 0, 0), (0, 1, 2), (1, 2, 2)): "D11", #0
    ((1, 0, 0), (1, 1, 2), (0, 2, 2)): "D8",  #1
    ((1, 0, 0), (2, 1, 0), (2, 2, 1)): "D10", #2
    ((0, 0, 2), (1, 1, 2), (1, 2, 0)): "D13", #3
    ((2, 0, 1), (2, 1, 0), (1, 2, 0)): "C4",  #4
    ((2, 0, 0), (1, 1, 0), (2, 2, 1)): "D5",  #5
    ((1, 0, 2), (0, 1, 2), (0, 2, 1)): "C2",  #6
    ((0, 0, 1), (2, 1, 1), (2, 2, 0)): "D6",  #7
    ((2, 0, 0), (1, 1, 0), (1, 2, 2)): "D7",  #8
    ((0, 0, 2), (0, 1, 2), (1, 2, 1)): "H10", #9
    ((2, 0, 1), (2, 1, 1), (0, 2, 0)): "H8",  #10
    ((1, 0, 0), (1, 1, 0), (2, 2, 2)): "T1",  #11
    ((2, 0, 0), (2, 1, 0), (1, 2, 1)): "H6",  #12
    ((0, 0, 1), (0, 1, 1), (2, 2, 2)): "T2",  #13
    ((1, 0, 2), (1, 1, 2), (0, 2, 0)): "H4",  #14
    ((0, 0, 2), (1, 1, 2), (0, 2, 1)): "D14", #15
    ((1, 0, 0), (2, 1, 0), (1, 2, 2)): "D12", #16
    ((2, 0, 1), (0, 1, 1), (2, 2, 0)): "D15", #17
    ((1, 0, 1), (2, 1, 2), (0, 2, 0)): "H2",  #18
    ((0, 0, 0), (1, 1, 1), (2, 2, 2)): "T0",  #19
    ((2, 0, 2), (0, 1, 0), (1, 2, 1)): "H1",  #20
    ((0, 0, 1), (2, 1, 2), (1, 2, 0)): "H3",  #21
    ((2, 0, 0), (1, 1, 1), (0, 2, 2)): "T4",  #22
    ((1, 0, 2), (0, 1, 0), (2, 2, 1)): "H9",  #23
    ((1, 0, 0), (2, 1, 2), (0, 2, 1)): "H7", # 24
    ((0, 0, 2), (1, 1, 1), (2, 2, 0)): "T3", # 25
    ((2, 0, 1), (0, 1, 0), (1, 2, 2)): "H5", # 26
    ((0, 0, 0), (2, 1, 2), (1, 2, 1)): "T5", # 27
    ((0, 0, 1), (1, 1, 2), (2, 2, 0)): "D3", # 28
    ((2, 0, 0), (0, 1, 1), (1, 2, 2)): "D1", # 29
    ((1, 0, 2), (2, 1, 0), (0, 2, 1)): "C1", # 30
    ((2, 0, 1), (1, 1, 0), (0, 2, 2)): "D9", # 31
    ((2, 0, 1), (0, 1, 2), (1, 2, 0)): "C3", # 32
    ((1, 0, 0), (2, 1, 1), (0, 2, 2)): "D2", # 33
    ((0, 0, 2), (1, 1, 0), (2, 2, 1)): "D4", # 34
    ((2, 0, 0), (1, 1, 2), (0, 2, 1)): "D16", # 35
}
case_rep_to_id = defaultdict(list)
case_id_to_l6x_name = {}
df = pl.read_csv("data/FTO/LL/ftoll_semi_old.csv")

def fix_auf_and_maybe_make_eif(alg: str, auf_fix: int):
    subs = {
        "br": "r",
        "BR": "R",
        "R": "F",
    }
    current_auf_numeric = 0
    if alg.startswith("("):
        split_alg = alg.split()
        current_auf = split_alg[0][1:-1]
        if "'" in current_auf:
            current_auf_numeric = 2
        else:
            current_auf_numeric = 1
        alg = " ".join(split_alg[1:])
    new_auf_numeric = ( current_auf_numeric - auf_fix) % 3
    new_prefix = ["", "(U) ", "(U') "][new_auf_numeric]
    alg = new_prefix + alg
    if len(re.findall("BR", alg)) > 2 and " r" not in alg:
        alg = "{U,R} " + re.sub("|".join(re.escape(k) for k in subs.keys()), lambda x: subs[x.group(0)], alg)
    return alg

transformed_algs = []
color = FTOLLColorizer()
for case_id, algs in enumerate(df['Algs']):
    first_alg = algs.splitlines()[0]
    svg = color.scramble(color.inverse(clean_alg_fto(first_alg.replace("(", "").replace(")", ""))))
    rep = get_l6x_case_rep(svg)
    auf_fix = 0
    for i in range(3):
        if rep in case_rep_to_id:
            case_rep_to_id[rep].append(case_id)
            break
        else:
            rep = auf(rep)
            auf_fix += 1
        if i == 2:
            case_rep_to_id[rep].append(case_id)
    new_algs = []
    for alg in algs.splitlines():
        new_algs.append(fix_auf_and_maybe_make_eif(alg, auf_fix))
    transformed_algs.append("\n".join(new_algs))
change_auf_per_case = {
    "T1": 1,
    "T2": 1,
    "T5": 1,
    "H4": 1,
    "H6": 1,
    "H8": 1,
    "H10": 1,
    "D5": 1,
    "D7": 1,
    "D8": 2,
    "D9": 1,
    "D10": 2,
    "D12": 2,
    "D13": 1,
    "D14": 1,
    "D16": 2,
    "C2": 2,
}

fixed_auf_algs = []
for i, algs in enumerate(transformed_algs):
    case_id += 1
    group = df[i, "Group"]
    if group not in change_auf_per_case:
        fixed_auf_algs.append(algs)
        continue

    transformed = []
    for alg in algs.splitlines():
        matches = re.search(r"\(U'?\)", alg)
        if matches is None:
            current_auf = 0
        elif matches.group(0) == "(U)":
            current_auf = 1
        elif matches.group(0) == "(U')":
            current_auf = 2
        new_auf = (current_auf - change_auf_per_case[group]) % 3
        if alg.startswith("{U,R}"):
            prefix = "{U,R} "
            alg = " ".join(alg.split()[1:])
        else:
            prefix = ""
        move = ["", "U ", "U' "][new_auf]
        if matches is None:
            alg = prefix + move + alg
        if matches is not None:
            alg = prefix + re.sub(r"\(U'?\) ", move, alg)
        transformed.append(alg)
    fixed_auf_algs.append("\n".join(transformed))
        

group_order = "T0 T1 T2 T3 T4 T5 H1 H2 H3 H4 H5 H6 H7 H8 H9 H10 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 C1 C2 C3 C4".split()
group_order = {v: k for k, v in enumerate(group_order)}

def get_case_name(algs):
    alg = algs.splitlines()[0]
    svg = color.scramble(color.inverse(clean_alg_fto(alg.replace("(", "").replace(")", ""))))
    group_name = df[i, "Group"]
    pieces = color.cube.pieces
    twist_state = pieces['WPOB'][1], pieces['WBZR'][1], pieces['WRGP'][1]
    twist_letter = "o"
    match twist_state:
        case (2, 2, 0):
            twist_letter = "r"
        case (0, 2, 2):
            twist_letter = "l"
        case (2, 0, 2):
            twist_letter = "b"
    if group_name in ["T0", "H1", "H2", "D1", "D2", "D3", "D4", "C1", "C3"] and twist_letter != "o":
        twist_letter = "b"
    fc, rc, lc, edge = pieces["WRGP"][0], pieces["WBZR"][0], pieces["WPOB"][0], pieces["WR"][0][1]
    perm_state = edge in fc, edge in lc, edge in rc
    perm_letter = "0"
    match perm_state:
        case (True, True, False):
            perm_letter = "-"
        case (True, False, True):
            perm_letter = ""
        case (False, True, True):
            perm_letter = "+"
    return group_name + "<>" + twist_letter + perm_letter

new_names = []
for i, algs in enumerate(transformed_algs):
    group = df[i, "Group"]
    new_names.append(get_case_name(algs))


df = (
    df.with_columns(
        Algs=pl.Series(fixed_auf_algs)
    )
    .sort(
        by=(pl.col("Group").replace_strict(group_order, return_dtype=pl.Int64), "Name"
    ))
    .select(
        "Algset", 
        "Group", 
        "Algs",
        Name=pl.arange(1, 1+len(df)), 
        NameProposed=pl.Series(new_names),
        Movecount="Movecount", 
        Setup="Setup"
    )
)
df.write_csv("data/FTO/LL/ftoll.csv")
print()
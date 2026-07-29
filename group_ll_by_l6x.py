from collections import defaultdict
from pathlib import Path
import polars as pl
import re

def auf(canonical):
    new_canonical = []
    for side in canonical[2:] + canonical[:2]:
        a, b, c = side
        new_canonical.append(((a+1)%3, (b+1)%3, (c+1)%3))
    return tuple(new_canonical)


def get_l6x_case_rep(path):
    color_regex = re.compile(r"'#[A-Fa-f0-9]+'")
    color_1_line = 8
    color_2_line = 15
    color_3_line = 22
    image = Path(path).read_text().splitlines()
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
for svg in Path("data/FTO/LL/pic").glob("*.svg"):
    case_id = int(svg.with_suffix("").name)
    rep = get_l6x_case_rep(svg)
    for i in range(3):
        if rep in case_rep_to_id:
            case_rep_to_id[rep].append(case_id)
            break
        else:
            rep = auf(rep)
        if i == 2:
            case_rep_to_id[rep].append(case_id)

    l6x_name = rep_to_case_name[rep]
    case_id_to_l6x_name[case_id] = l6x_name

case_l6x_names = sorted(case_id_to_l6x_name.items())
df = pl.read_csv("data/FTO/LL/ftoll.csv")
df = df.with_columns(Group=pl.Series([x for _, x in case_l6x_names]))
group_order = "T0 T1 T2 T3 T4 T5 H1 H2 H3 H4 H5 H6 H7 H8 H9 H10 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 C1 C2 C3 C4".split()
group_order = {v: k for k, v in enumerate(group_order)}
df = df.sort(by=(pl.col("Group").replace(group_order), "Name")).select("Algset", "Group", Oldname="Name", Algs="Algs", Name=pl.arange(1, 1+len(df)), Movecount="Movecount", Setup="Setup")
df.write_csv("data/FTO/LL/ftoll_improved.csv")
print()
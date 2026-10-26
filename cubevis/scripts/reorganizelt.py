from cubevis.cube import FTO
from cubevis.scripts.images import clean_alg_fto
import polars as pl
df = pl.read_csv("data/FTO/LT/ftolt.csv")
def change_auf(alg: str, auf_change):
    if auf_change == "":
        return alg

    if auf_change == "U":
        if alg.startswith("{"):
            return "(U) " + alg
        if alg.startswith("(U)"):
            return alg.replace("(U)", "(U')")
        if alg.startswith("(U')"):
            return alg.replace("(U') ", "")

    if auf_change == "U'":
        if alg.startswith("{"):
            return "(U') " + alg
        if alg.startswith("(U)"):
            return alg.replace("(U) ", "")
        if alg.startswith("(U')"):
            return alg.replace("(U')", "(U)")


def find_case_identifier(state: dict, original_group: str) -> tuple[tuple[str, str], str]:
    slot_fix_auf = {
        "B1": "U'",
        "B2": "U'",
        "P1": "U",
        "P2": "U",
        "R1": "",
        "R2": "",
        "R3": "",
        "Y2": "",
    }
    change_position = {
        "U'": {
            "B1": "R1",
            "B2": "R2",
            "P1": "B1",
            "P2": "B2",
            "R1": "P1",
            "R2": "P2",
        },
        "U": {
            "B1": "P1",
            "B2": "P2",
            "P1": "R1",
            "P2": "R2",
            "R1": "B1",
            "R2": "B2",
        },
    }
    positions = ["Y2", "R3"]
    check_pieces = ["B1", "B2", "P1", "P2", "R1", "R2", "R3", "Y2"]
    for p in check_pieces:
        piece = state[p][0]
        if piece == "Y2":
            positions[0] = p
        if piece == "R3":
            positions[1] = p
    auf_fix = ""
    if original_group.startswith("T") or original_group.startswith("S"):
        auf_fix = slot_fix_auf[positions[0]]
        if auf_fix != "":
            if positions[0] in change_position[auf_fix]:
                positions[0] = change_position[auf_fix][positions[0]]
            if positions[1] in change_position[auf_fix]:
                positions[1] = change_position[auf_fix][positions[1]]

    return (tuple(positions), auf_fix)

new_group_names = {
    "T": {
        "R1": "T-Left",
        "R2": "T-Right",
        "R3": "T-Pair",
        "Y2": "T-Flip"
    },
    "S": {
        "R1": "S-Left",
        "R2": "S-Right",
        "R3": "S-Flip",
        "Y2": "S-Pair"
    },
    "R": {
        "R1": "R-Headlights",
        "R2": "R-Pair",
        "B1": "R-Flip",
        "B2": "R-Arrow",
        "P1": "R-Bow",
        "P2": "R-Axe",
        "R3": "R-Front",
        "Y2": "R-Bottom",
    },
    "L": {
        "R1": "L-Pair",
        "R2": "L-Headlights",
        "B1": "L-Axe",
        "B2": "L-Bow",
        "P1": "L-Arrow",
        "P2": "L-Flip",
        "R3": "L-Front",
        "Y2": "L-Bottom",
    }
}

new_case_name_suffixes = {
    "R1": "L",
    "R2": "R",
    "R3": "F",
    "B2": "RF",
    "P2": "LF",
    "B1": "RB",
    "P1": "LB",
    "Y2": "D",
}

case_order = {c: i for i, c in enumerate(new_case_name_suffixes.values())}

new_group_order = {name: i for i, name in enumerate([
    "S-Pair", 
    "S-Flip",
    "S-Right", 
    "S-Left", 
    "T-Pair", 
    "T-Flip",
    "T-Right", 
    "T-Left", 
    "R-Pair", 
    "R-Headlights", 
    "R-Axe", 
    "R-Bow", 
    "R-Arrow", 
    "R-Flip",
    "R-Front",
    "R-Bottom",
    "L-Pair", 
    "L-Headlights",
    "L-Axe",
    "L-Bow",
    "L-Arrow",
    "L-Flip",
    "L-Front",
    "L-Bottom"
])}

cube = FTO()
new_data = []
for row in df.iter_rows(named=True):
    alg = clean_alg_fto(row['Algs'].split("\n")[0].replace("(", "").replace(")", ""))
    if "y" in alg:
        alg += " y'"
    group = row['Group']
    cube.inverse(alg)
    state_id, auf = find_case_identifier(cube.pieces, group)
    new_algs = "\n".join([change_auf(alg, auf) for alg in row['Algs'].split("\n")])
    new_group = new_group_names[group[0]][state_id[0]]
    new_name = f"{new_group} {new_case_name_suffixes[state_id[1]]}"
    new_data.append({
        "Algset": "LT",
        "Group": new_group,
        "Name": new_name,
        "Algs": new_algs,
        "Setup": change_auf(row["Inverse"], auf),
        "Group-Order": new_group_order[new_group],
        "Case-Order": case_order[new_case_name_suffixes[state_id[1]]]
    })
new_df = pl.DataFrame(new_data).sort("Group-Order", "Case-Order").select("Algset", "Group", "Name", "Algs", "Setup")
new_df.write_csv("test.csv")
print()
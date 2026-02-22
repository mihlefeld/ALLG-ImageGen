import argparse
import polars as pl
import json
import pathlib
import re
from cubevis.colorizer import get_colorizer
from pathlib import Path
from collections import defaultdict

def save_json(obj, filename):
    with open(filename, 'w', encoding="UTF-8") as file:
        json.dump(obj, file, ensure_ascii=False)

def naive_invert(scramble: str, replace_2prime):
    inverted = []
    scramble = scramble.strip()
    for move in scramble.split(" ")[::-1]:
        inverted.append(move + "'" if move[-1] != "'" else move[:-1])
    if replace_2prime:
        return " ".join(inverted).replace("2'", "2")
    return " ".join(inverted)

def remove_aufs(scramble: str):
    moves = scramble.split()
    if "U" in moves[0]:
        moves = moves[1:]
    if "U" in moves[-1]:
        moves = moves[:-1]
    return " ".join(moves)

def square_one_self_to_standard(alg):
    moves = re.findall(r"T|[UD][2']?|t", alg)
    standard_moves = []
    current_u = 0
    current_d = 0
    def normalize_move(move):
        if move > 6:
            return move - 12
        return move
    for move in moves:
        move_type = move[0]
        mult = 1
        if move[-1] == "'":
            mult = -1
        if move[-1] == "2":
            mult = 2
        if move_type == "U":
            current_u += mult * 3
        if move_type == "D":
            current_d += mult * 3
        if move == "T":
            current_u += 1
            standard_moves += [f"{normalize_move(current_u)},{normalize_move(current_d)}", "/"]
            current_u = -1
            current_d = 0
        if move == "t":
            current_d -= 1
            standard_moves += [f"{normalize_move(current_u)},{normalize_move(current_d)}", "/"]
            current_u = 0
            current_d = 1
    standard_moves += [f"{normalize_move(current_u)},{normalize_move(current_d)}"]
    return " ".join(standard_moves)


def translate_scamble(scramble: str):
    """
    r -> R
    l -> L
    B -> U
    b -> b
    """
    return (
        scramble
        .replace("r", "R")
        .replace("l", "L")
        .replace("B", "U")
        .replace("b", "B")
        )

def get_jsons(puzzle: str, scrambles_path: Path, csv_path: Path, output_dir: Path, filter: list[str] = []):
    colorizer = get_colorizer(puzzle)
    cut_auf_override = "5x5" in csv_path.as_posix().lower()
    needs_invert = colorizer.needs_invert()
    replace_2prime = "zbls" in csv_path.as_posix().lower()
    needs_translate = "skewb" in csv_path.as_posix().lower()
    needs_squan_translate = "sq1" in csv_path.as_posix().lower()
    output_dir.mkdir(parents=True, exist_ok=True)
    algs_info = defaultdict(dict)
    groups_info = defaultdict(list)
    algsets_info = defaultdict(list)
    scrambles = {}
    filter_set = set()
    selected_algsets = {}
    algs_df = (pl.read_csv(csv_path, encoding="UTF-8").filter(pl.col('Algs').is_not_null(), pl.col('Algs') != ""))
    
    if needs_squan_translate:
        def every_other_row(col, start):
            return pl.col(col).str.split("\n").list.gather_every(2, start).list.join("\n")
        orig = algs_df
        algs_df = algs_df.with_columns(every_other_row("Algs", 1).add("\n").add(every_other_row("Algs", 0)).alias("Algs"))

    case_id = 1
    for i, (algset, group, name, algs) in enumerate(algs_df.select("Algset", "Group", "Name", "Algs").iter_rows()):
        algs = [alg.strip() for alg in algs.split("\n")]
        if len(filter) > 0 and algset not in filter:
            continue
        filter_set.add(i)
        selected_algsets[algset] = True
        group_unique = f"{algset} {group}"
        groups_info[group_unique].append(case_id)
        if group_unique not in algsets_info[algset]:
            algsets_info[algset].append(group_unique)
        algs_info[case_id]['a'] = algs
        algs_info[case_id]['name'] = name
        algs_info[case_id]['group'] = group
        algs_info[case_id]['algset'] = algset
        case_id += 1
    
    scramble_df = pl.read_excel(scrambles_path)
    case_id = 1
    for i, c in enumerate(scramble_df.columns):
        if i % 2 != 1:
            continue
        if i // 2 not in filter_set:
            continue
        case_scrambles = [scr for scr in scramble_df[c] if type(scr) == str]
        if len(case_scrambles) < 1:
            print(f"No solution for case {case_id}.")
        case_scrambles = [re.sub(r'\([^\)]*\) ', '', scr) for scr in case_scrambles if scr != ""]
        if needs_invert:
            case_scrambles = list(map(lambda x: naive_invert(x, replace_2prime), case_scrambles))
        if needs_translate:
            case_scrambles = list(map(translate_scamble, case_scrambles))
        if cut_auf_override:
            case_scrambles = list(map(remove_aufs, case_scrambles))
        if needs_squan_translate:
            case_scrambles = list(map(square_one_self_to_standard, case_scrambles))
        if len(case_scrambles) == 0:
            case_scrambles = ["ERROR"]
        scrambles[case_id] = list(set(case_scrambles))
        algs_info[case_id]['s'] = case_scrambles[0]
        case_id += 1 

    save_json(algs_info, output_dir / 'algs_info.json')
    save_json(scrambles, output_dir / 'scrambles.json')
    save_json(algsets_info, output_dir / 'algsets_info.json')
    save_json(groups_info, output_dir / 'groups_info.json')
    save_json(selected_algsets, output_dir / 'selected_algsets.json')


if __name__ == "__main__":
    get_jsons()
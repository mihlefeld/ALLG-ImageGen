import argparse
import pandas as pd
import json
import pathlib
import re
from pathlib import Path
from collections import defaultdict

def save_json(obj, filename):
    with open(filename, 'w', encoding="UTF-8") as file:
        json.dump(obj, file, ensure_ascii=False)

def naive_invert(scramble: str):
    inverted = []
    scramble = scramble.strip()
    for move in scramble.split(" ")[::-1]:
        inverted.append(move + "'" if move[-1] != "'" else move[:-1])
    return " ".join(inverted)

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

def get_jsons(scrambles_path: Path, csv_path: Path, output_dir: Path, filter: list[str] = []):
    needs_invert = "octaminx" in csv_path.as_posix().lower() or "zbls" in csv_path.as_posix().lower()
    needs_translate = "skewb" in csv_path.as_posix().lower()
    output_dir.mkdir(parents=True, exist_ok=True)
    algs_info = defaultdict(dict)
    groups_info = defaultdict(list)
    algsets_info = defaultdict(list)
    scrambles = {}
    filter_set = set()
    selected_algsets = {}
    algs_df = pd.read_csv(csv_path, encoding="UTF-8")
    with open("test.txt", encoding="UTF-8", mode="w") as file:
        file.write('\n'.join([group for group in algs_df["Group"].unique()]))
    case_id = 1
    for i, row in algs_df.iterrows():
        algset = row["Algset"]
        group = row["Group"]
        name = row["Name"]
        algs = [alg.strip() for alg in row["Algs"].split("\n")]
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
    
    scramble_df = pd.read_excel(scrambles_path, engine="openpyxl")
    case_id = 1
    for c in scramble_df.columns:
        number = int(c.split()[-1])
        if number % 2 != 1:
            continue
        if number // 2 not in filter_set:
            continue
        case_scrambles = [scr for scr in scramble_df[c][1:] if type(scr) == str]
        if len(case_scrambles) < 1:
            print(f"Wrong {case_id}!")
        case_scrambles = [re.sub(r'\([^\)]*\) ', '', scr) for scr in case_scrambles if type(scr) == str]
        if needs_invert:
            case_scrambles = list(map(naive_invert, case_scrambles))
        if needs_translate:
            case_scrambles = list(map(translate_scamble, case_scrambles))
        scrambles[case_id] = case_scrambles
        algs_info[case_id]['s'] = case_scrambles[0]
        case_id += 1 

    save_json(algs_info, output_dir / 'algs_info.json')
    save_json(scrambles, output_dir / 'scrambles.json')
    save_json(algsets_info, output_dir / 'algsets_info.json')
    save_json(groups_info, output_dir / 'groups_info.json')
    save_json(selected_algsets, output_dir / 'selected_algsets.json')


if __name__ == "__main__":
    get_jsons()
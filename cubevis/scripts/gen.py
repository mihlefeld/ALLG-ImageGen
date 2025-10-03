import argparse
from cubevis import get_colorizer
from cubevis.colorizer import OctaminxColorizer, BaseColorizer
from cubevis.cube import OctaminxRotations
from typing import List
import json
import os
import pandas as pd
from pathlib import Path
import re
import numpy as np

def clean_alg(alg: str, puzzle):
    cleaned_alg = re.sub(r"/\w+'?| \(Cancel\)| \(cancel\)|[\(\)]|[\]\[]", '', alg).strip()
    moves = []
    for move in cleaned_alg.split(' '):
        move_trunk = re.match(r"[A-z]+", move)
        if not move_trunk:
            moves.append(move)
            continue
        move_trunk = move_trunk.group(0)
        
        move_quantity = re.match(r".*(\d)", move)
        if move_quantity:
            move_quantity = int(move_quantity.group(1))
        else:
            move_quantity = 1
        move_inverse = "'" in move
        cycles = puzzle.max_cycles[move_trunk]
        if move_quantity > cycles // 2:
            move_quantity = cycles - (move_quantity % cycles)
            move_inverse = not move_inverse
        inverse_str = "'" if move_inverse else ""
        move_quantity_str = "" if move_quantity == 1 else move_quantity
        move = f"{move_trunk}{move_quantity_str}{inverse_str}"
        moves.append(move)
    return " ".join(moves)
        
def clean_alg_octaminx(alg):
    alg = re.sub(r",\s*", ",", alg)
    cif_orbit = {"R", "L", "B", "D"}
    eif_orbit = {"R", "L", "B", "U"}
    cif = {
        "R": "R", "L": "P",
        "U": "W", "D": "Y",
        "F": "G", "B": "B",
        "BR": "Z", "BL": "O"
    }
    eif = {
        "R": "G", "L": "O",
        "U": "W", "D": "Y",
        "F": "P", "B": "Z",
        "BR": "R", "BL": "B"
    }
    front_checking_stickers = ["P", "G"]
    cif_eif = [eif, cif]
    def switches(top, front, in_cif):
        if in_cif:
            return (top in cif_orbit) != (front in cif_orbit)
        return (top in eif_orbit) == (front in eif_orbit)
    def rotation_to_top_front(rot: str):
        return rot.strip("{}").upper().split(',')
    to_top_rotations = {
        "W": "", "Y": "t xl",
        "R": "t'", "P": "t",
        "G": "xr", "B": "xr' t",
        "O": "xl", "Z": "xr'"
    }
    moves = alg.split()
    in_cif = True
    converted = []
    for move in moves:
        if "{" not in move:
            converted.append(move if in_cif else "e" + move)
        else:
            top, front = rotation_to_top_front(move)
            top_side = cif_eif[in_cif][top]
            front_side = cif_eif[in_cif][front]
            sw = switches(top, front, in_cif)
            if sw:
                in_cif = not in_cif
            front_check = front_checking_stickers[in_cif]
            rot = OctaminxRotations()
            rotations = [to_top_rotations[top_side]]
            if rotations[0] != "":
                rot.move(rotations[0])
            else:
                rotations = []
            if rot.pieces[front_check][0] == front_side:
                converted += rotations
                continue

            for i in range(2):
                rot.move("y")
                if rot.pieces[front_check][0] == front_side:
                    rotations.append(f"y'" if i > 0 else "y")
                    break
            if rot.pieces[front_check][0] != front_side:
                print(f"error, rotation {move} impossible")
                break
            converted.append(" ".join(rotations))
    final_moves = " ".join(converted)
    return final_moves


def gen_images(puzzle_name: str, input_path: Path, output_path: Path, filter: List[str] = []):
    puzzle: BaseColorizer = get_colorizer(puzzle_name)
    os.makedirs(output_path, exist_ok=True)
    batch_solver_inputs = []
    df = pd.read_csv(input_path)
    case_id = 1
    svg_strings = dict()
    for i, row in df.iterrows():
        if len(filter) > 0 and row["Algset"] not in filter:
            continue
        filename =  output_path / f"{case_id}.svg"
        alg = clean_alg(row["Algs"].split("\n")[0], puzzle.cube)
        if "Skewb" in puzzle_name:
            alg = clean_alg([alg for alg in row["Algs"].split("\n") if "H" not in alg and "S" not in alg][0])
        if "Octaminx" in puzzle_name:
            alg = clean_alg_octaminx(alg)
        
        puzzle.inverse(alg, filename)
        svg_strings[case_id] = puzzle.create_svg()
        if isinstance(puzzle, OctaminxColorizer):
            alg = puzzle.inverse(alg)
        else:
            puzzle.cube.scramble(alg)
        ref_rot = puzzle.cube.to_reference_rotation()
        if ref_rot != "":
            alg += " " + ref_rot
        batch_solver_inputs.append(alg)
        case_id += 1
    with open(output_path / "_batch_solver_def.txt", "w") as file:
        file.write(puzzle.cube.mdefs)
    with open(output_path / "_batch_solver_input.txt", "w") as file:
        unique, inverses, counts = np.unique(batch_solver_inputs, return_inverse=True, return_counts=True)
        for i, s in enumerate(batch_solver_inputs):
            if s in batch_solver_inputs[:i]:
                b = batch_solver_inputs.index(s)
                print("Duplicate:", *df.iloc[i][["Algset", "Group", "Name"]])
                print("First occurance:", *df.iloc[b][["Algset", "Group", "Name"]])
        
        bs_str = ',\n'.join(batch_solver_inputs)
        file.write(f"[\n{bs_str}\n]")
    
    with open(output_path.parent / "combined.json", "w") as file:
        json.dump(svg_strings, file)
        



if __name__ == "__main__":
    gen_images()
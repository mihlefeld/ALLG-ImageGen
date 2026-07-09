import json
from pathlib import Path
from typing import Dict

import numpy as np

from cubevis.colorizer.colorizer import BaseColorizer, colors
from cubevis.cube import FiveByFive


class FiveByFiveColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(FiveByFive(), pre_moves)
        self.vertices = []
        for i in range(8):
            for j in range(8):
                self.vertices.append([j, i])
        self.vertices = np.array(self.vertices)
        self.normalize_vertices()

    def get_polygons(self):
        return {
            "UFL": [1, 2, 10, 9],
            "UF2": [2, 3, 11, 10],
            "UF": [3, 4, 12, 11],
            "UF1": [4, 5, 13, 12],
            "UFR": [5, 6, 14, 13],
            "LFU": [8, 9, 17, 16],
            "FLU": [9, 10, 18, 17],
            "FU2": [10, 11, 19, 18],
            "FU": [11, 12, 20, 19],
            "FU1": [12, 13, 21, 20],
            "FRU": [13, 14, 22, 21],
            "RFU": [14, 15, 23, 22],
            "LF2": [16, 17, 25, 24],
            "FL2": [17, 18, 26, 25],
            "F1": [18, 19, 27, 26],
            "F2": [19, 20, 28, 27],
            "F3": [20, 21, 29, 28],
            "FR1": [21, 22, 30, 29],
            "RF1": [22, 23, 31, 30],
            "LF": [24, 25, 33, 32],
            "FL": [25, 26, 34, 33],
            "F8": [26, 27, 35, 34],
            "F": [27, 28, 36, 35],
            "F4": [28, 29, 37, 36],
            "FR": [29, 30, 38, 37],
            "RF": [30, 31, 39, 38],
            "LF1": [32, 33, 41, 40],
            "FL1": [33, 34, 42, 41],
            "F7": [34, 35, 43, 42],
            "F6": [35, 36, 44, 43],
            "F5": [36, 37, 45, 44],
            "FR2": [37, 38, 46, 45],
            "RF2": [38, 39, 47, 46],
            "LDF": [40, 41, 49, 48],
            "FDL": [41, 42, 50, 49],
            "FD1": [42, 43, 51, 50],
            "FD": [43, 44, 52, 51],
            "FD2": [44, 45, 53, 52],
            "FDR": [45, 46, 54, 53],
            "RDF": [46, 47, 55, 54],
            "DFL": [49, 50, 58, 57],
            "DF1": [50, 51, 59, 58],
            "DF": [51, 52, 60, 59],
            "DF2": [52, 53, 61, 60],
            "DFR": [53, 54, 62, 61],
        }

    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "U": colors["white"],
            "F": colors["green"],
            "R": colors["red"],
            "B": colors["blue"],
            "L": colors["orange"],
            "D": colors["yellow"],
        }

    def needs_invert(self):
        return True


class FiveByFiveL2EColorizer(FiveByFiveColorizer):
    def __init__(self):
        super().__init__("x2")

    def get_override_colors(self):
        return {
            "UF1": colors["ignore"],
            "UF2": colors["ignore"],
            "UF": colors["ignore"],
            "FU1": colors["ignore"],
            "FU2": colors["ignore"],
            "FU": colors["ignore"],
            "UFR": colors["ignore"],
            "RFU": colors["ignore"],
            "FRU": colors["ignore"],
            "UFL": colors["ignore"],
            "LFU": colors["ignore"],
            "FLU": colors["ignore"],
            "DFR": colors["ignore"],
            "FDR": colors["ignore"],
            "RDF": colors["ignore"],
            "DFL": colors["ignore"],
            "FDL": colors["ignore"],
            "LDF": colors["ignore"],
            "F1": colors["ignore"],
            "F2": colors["ignore"],
            "F3": colors["ignore"],
            "F4": colors["ignore"],
            "F5": colors["ignore"],
            "F6": colors["ignore"],
            "F7": colors["ignore"],
            "F8": colors["ignore"],
            "F": colors["ignore"],
            "FD": colors["ignore"],
            "FD1": colors["ignore"],
            "FD2": colors["ignore"],
        }


class FiveByFiveSpecialColorizer(FiveByFiveColorizer):
    def __init__(self, pre_moves=""):
        super().__init__(pre_moves)
        coords = json.loads((Path(__file__).parent / "5x5coords.json").read_text())
        self.vertices = np.array(coords["coordinates"])
        self.polygons = coords["index_map"]
        self.normalize_vertices()

    def get_polygons(self):
        return self.polygons


class FiveByFiveHoyaColorizer(FiveByFiveSpecialColorizer):
    def get_face_to_color(self):
        return {
            "U": colors["yellow"],
            "D": colors["white"],
            "R": colors["orange"],
            "L": colors["red"],
            "F": colors["green"],
            "B": colors["blue"],
        }

    def __init__(self, pre_moves=""):
        super().__init__(pre_moves)
        no_ignore = [
            "FD",
            "DF",
            "RD",
            "DR",
            "DL",
            "LD",
            "BD",
            "DB" "FD1",
            "DF1",
            "RD1",
            "DR1",
            "DL1",
            "LD1",
            "BD1",
            "DB1" "FD2",
            "DF2",
            "RD2",
            "DR2",
            "DL2",
            "LD2",
            "BD2",
            "DB2",
        ]
        no_ignore += [f"R{i}".strip("0") for i in range(9)]
        no_ignore += [f"L{i}".strip("0") for i in range(9)]
        no_ignore += [f"B{i}".strip("0") for i in range(9)]
        self.override = {
            k: colors["ignore"] for k in self.polygons.keys() if k not in no_ignore
        }
        self.override.update(
            {
                "DFR": colors["ignore"],
                "DBR": colors["ignore"],
                "DFL": colors["ignore"],
                "DBL": colors["ignore"],
            }
        )

    def get_override_pieces(self):
        return self.override


"""
{DFR DRB DBL DLF URF UFL ULB UBR}
{UF2 UL2 UB2 UR2 BR2 FR2 FL2 BL2}
{UF1 UL1 UB1 UR1 BR1 FR1 FL1 BL1}
{UF UL UB UR BR FR FL BL}
{U1 U3 U5 U7 F1 F3 F5 F7}
{F2 F4 F6 F8 U2 U4 U6 U8}
1: URF UFL ULB UBR UF1 UL1 UB1 UR1 UF2 UL2 UB2 UR2 UF UL UB UR DFR DRB DBL DLF
"""

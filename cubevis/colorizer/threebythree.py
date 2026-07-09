from typing import Dict, List

import numpy as np

from cubevis.colorizer.colorizer import BaseColorizer, colors
from cubevis.cube import ThreeByThree


class ThreeByThreeColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(ThreeByThree(), pre_moves)
        xy_to_key = {
            (0, 0): None,
            (1, 0): "BLU",
            (2, 0): "BU",
            (3, 0): "BRU",
            (4, 0): None,
            (0, 1): "LBU",
            (1, 1): "UBL",
            (2, 1): "UB",
            (3, 1): "UBR",
            (4, 1): "RBU",
            (0, 2): "LU",
            (1, 2): "UL",
            (2, 2): "U",
            (3, 2): "UR",
            (4, 2): "RU",
            (0, 3): "LFU",
            (1, 3): "UFL",
            (2, 3): "UF",
            (3, 3): "UFR",
            (4, 3): "RFU",
            (0, 4): None,
            (1, 4): "FLU",
            (2, 4): "FU",
            (3, 4): "FRU",
            (4, 4): None,
        }
        self.polygons = {}
        counter = 0
        coords = []
        for i in range(5 * 5):
            x = i % 5
            y = i // 5
            if xy_to_key[x, y] is None:
                continue
            tl = [x - 0.5, y - 0.5]
            tr = [x + 0.5, y - 0.5]
            br = [x + 0.5, y + 0.5]
            bl = [x - 0.5, y + 0.5]
            if x == 0:
                tl = [x + 0.1, y - 0.4]
                bl = [x + 0.1, y + 0.4]
            if x == 4:
                tr = [x - 0.1, y - 0.4]
                br = [x - 0.1, y + 0.4]
            if y == 0:
                tl = [x - 0.4, y + 0.1]
                tr = [x + 0.4, y + 0.1]
            if y == 4:
                bl = [x - 0.4, y - 0.1]
                br = [x + 0.4, y - 0.1]
            coords += [tl, tr, br, bl]
            key = xy_to_key[(x, y)]
            self.polygons[key] = [counter * 4 + j for j in range(4)]
            # print(key, (x, y), self.polygons[key], [tl, tr, br, bl])
            counter += 1
        self.vertices = np.array(coords)
        self.normalize_vertices()

    def get_polygons(self) -> Dict[str, List[int]]:
        return self.polygons

    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "U": colors["white"],
            "F": colors["green"],
            "R": colors["red"],
            "B": colors["blue"],
            "L": colors["orange"],
            "D": colors["yellow"],
        }

    def get_prune_search_subgroup(self):
        return "8 7 R U F"


class ThreeByThreeLLColorizer(ThreeByThreeColorizer):
    def __init__(self) -> None:
        super().__init__("z2")


class ThreeByThreeOLLColorizer(ThreeByThreeColorizer):
    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "U": colors["yellow"],
            "F": colors["ignore"],
            "R": colors["ignore"],
            "B": colors["ignore"],
            "L": colors["ignore"],
            "D": colors["ignore"],
        }

    def get_equivalences(self):
        return """\
{UR UL UF UB}
{URF UFL ULB UBR}
\
"""


class ThreeByThreeCMLLColorizer(ThreeByThreeLLColorizer):
    def get_override_colors(self) -> Dict[str, str]:
        return {
            "UL": colors["ignore"],
            "LU": colors["ignore"],
            "UR": colors["ignore"],
            "RU": colors["ignore"],
            "UF": colors["ignore"],
            "FU": colors["ignore"],
            "UB": colors["ignore"],
            "BU": colors["ignore"],
            "U": colors["ignore"],
        }

    def get_equivalences(self):
        return """\
{UR UL UF UB DF DB}
1: UR UL UF UB DF DB\
"""


class ThreeByThreeZBLSColorizer(ThreeByThreeColorizer):
    def __init__(self):
        super().__init__("x2")
        points = [
            [0.00, 0.00],
            [0.00, -100.00],
            [-86.60, -50.00],
            [-86.60, 50.00],
            [-0.00, 100.00],
            [86.60, 50.00],
            [86.60, -50.00],
            [-57.74, -66.67],
            [-28.87, -83.33],
            [28.87, -83.33],
            [57.74, -66.67],
            [0.00, -33.33],
            [-28.87, -50.00],
            [28.87, -50.00],
            [0.00, -66.67],
            [86.60, -16.67],
            [86.60, 16.67],
            [57.74, 66.67],
            [28.87, 83.33],
            [28.87, 16.67],
            [57.74, 0.00],
            [28.87, 50.00],
            [57.74, 33.33],
            [28.87, -16.67],
            [57.74, -33.33],
            [-86.60, -16.67],
            [-86.60, 16.67],
            [-0.00, 33.33],
            [-0.00, 66.67],
            [-28.87, 83.33],
            [-57.74, 66.67],
            [-57.74, -0.00],
            [-28.87, 16.67],
            [-57.74, 33.33],
            [-28.87, 50.00],
            [-57.74, -33.33],
            [-28.87, -16.67],
        ]
        self.vertices = np.array(points)
        self.vertices[:, 0] *= -1
        self.normalize_vertices()

    def needs_invert(self):
        return True

    def get_polygons(self):
        return {
            "UBL": [9, 1, 8, 14],
            "UL": [9, 14, 13, 10],
            "UFL": [10, 13, 24, 6],
            "UF": [24, 13, 11, 23],
            "U": [13, 14, 12, 11],
            "UB": [14, 8, 7, 12],
            "UBR": [12, 7, 2, 35],
            "UR": [11, 12, 35, 36],
            "UFR": [23, 11, 36, 0],
            "FRU": [23, 0, 27, 19],
            "FU": [24, 23, 19, 20],
            "FLU": [6, 24, 20, 15],
            "FL": [15, 20, 22, 16],
            "F": [20, 19, 21, 22],
            "FR": [19, 27, 28, 21],
            "FDR": [21, 28, 4, 18],
            "FD": [22, 21, 18, 17],
            "FDL": [16, 22, 17, 5],
            "RFU": [0, 36, 32, 27],
            "RU": [36, 35, 31, 32],
            "RBU": [35, 2, 25, 31],
            "RB": [31, 25, 26, 33],
            "R": [32, 31, 33, 34],
            "RF": [27, 32, 34, 28],
            "RDF": [28, 34, 29, 4],
            "RD": [34, 33, 30, 29],
            "RBD": [33, 26, 3, 30],
        }

    def get_override_pieces(self):
        return {
            "FD": colors["ignore"],
            "RD": colors["ignore"],
            "BD": colors["ignore"],
            "LD": colors["ignore"],
            "RDF": colors["ignore"],
            "FDR": colors["ignore"],
            "DFR": colors["ignore"],
            "LDF": colors["ignore"],
            "FDL": colors["ignore"],
            "DFL": colors["ignore"],
            "LBD": colors["ignore"],
            "BDL": colors["ignore"],
            "DBL": colors["ignore"],
            "RBD": colors["ignore"],
            "BDR": colors["ignore"],
            "DBR": colors["ignore"],
        }

    def get_equivalences(self):
        return """\
{UF UR UB UL}
1: URF UBR ULB UFL\
"""

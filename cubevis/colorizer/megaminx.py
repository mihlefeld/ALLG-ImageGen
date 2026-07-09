from collections import defaultdict
from typing import Dict, List

import numpy as np

from cubevis.colorizer.colorizer import BaseColorizer, colors
from cubevis.cube import Megaminx


class MegaminxColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(Megaminx(), pre_moves)
        coords = [
            [392, 473],
            [292, 473],
            [192, 473],
            [92, 473],
            [61, 378],
            [30, 283],
            [0, 188],
            [80, 129],
            [161, 70],
            [242, 11],
            [323, 70],
            [404, 129],
            [485, 188],
            [454, 283],
            [423, 378],
            [362, 432],
            [262, 432],
            [223, 432],
            [122, 432],
            [91, 336],
            [79, 299],
            [48, 203],
            [129, 144],
            [161, 121],
            [242, 62],
            [324, 121],
            [355, 144],
            [436, 203],
            [405, 299],
            [393, 336],
            [292, 335],
            [192, 335],
            [161, 240],
            [242, 182],
            [323, 240],
        ]
        self.vertices = np.array(coords, dtype=float)
        self.normalize_vertices()

    def get_polygons(self) -> Dict[str, List[int]]:
        return {
            "FRU": [0, 1, 16, 15],
            "FU": [1, 2, 17, 16],
            "FLU": [2, 3, 18, 17],
            "LFU": [3, 4, 19, 18],
            "LU": [4, 5, 20, 19],
            "LAU": [5, 6, 21, 20],
            "ALU": [6, 7, 22, 21],
            "AU": [7, 8, 23, 22],
            "ABU": [8, 9, 24, 23],
            "BAU": [9, 10, 25, 24],
            "BU": [10, 11, 26, 25],
            "BRU": [11, 12, 27, 26],
            "RBU": [12, 13, 28, 27],
            "RU": [13, 14, 29, 28],
            "RFU": [14, 0, 15, 29],
            "UFR": [15, 16, 30, 29],
            "UF": [16, 17, 31, 30],
            "UFL": [18, 19, 31, 17],
            "UL": [19, 20, 32, 31],
            "UAL": [21, 22, 32, 20],
            "UA": [22, 23, 33, 32],
            "UAB": [24, 25, 33, 23],
            "UB": [25, 26, 34, 33],
            "UBR": [27, 28, 34, 26],
            "UR": [28, 29, 30, 34],
            "U": [30, 31, 32, 33, 34],
        }

    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "I": colors["black"],
            "G": colors["lightgreen"],
            "H": colors["pink"],
            "C": colors["beige"],
            "E": colors["orange"],
            "A": colors["yellow"],
            "D": colors["lightblue"],
            "B": colors["blue"],
            "L": colors["purple"],
            "F": colors["green"],
            "R": colors["red"],
            "U": colors["white"],
        }


class MegaminxLLColorizer(MegaminxColorizer):
    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "C": colors["blue"],
            "D": colors["yellow"],
            "E": colors["purple"],
            "G": colors["green"],
            "H": colors["red"],
            "I": colors["white"],
            "B": colors["beige"],
            "A": colors["lightblue"],
            "L": colors["orange"],
            "F": colors["lightgreen"],
            "R": colors["pink"],
            "U": colors["black"],
        }

    def get_prune_search_subgroup(self):
        return "11 10 R U\n" "8 7 R U F"


class MegaminxOLLColorizer(MegaminxColorizer):
    def get_face_to_color(self) -> Dict[str, str]:
        ret = defaultdict(lambda: colors["ignore"])
        ret["U"] = colors["black"]
        return ret

    def get_equivalences(self):
        return """\
{UR UF UL UA UB}
{URF UFL ULA UAB UBR}
1: URF UFL ULA UAB UBR\
"""

    def get_prune_search_subgroup(self):
        return "7 6 R U F"


class MegaminxZBLSColorizer(MegaminxLLColorizer):
    def __init__(self):
        super().__init__()
        verts = self.vertices
        new_pts = np.zeros((6, 2))
        new_pts[0] = verts[1] + (verts[1] - verts[16])
        new_pts[1] = verts[1] + 2 * (verts[1] - verts[16])
        new_pts[2] = verts[0] + (verts[0] - verts[15])
        new_pts[3] = verts[0] + 2 * (verts[0] - verts[15])
        new_pts[4] = verts[14] + (verts[14] - verts[29])
        new_pts[5] = verts[14] + 2 * (verts[14] - verts[29])
        self.vertices = np.concatenate([verts, new_pts])
        self.normalize_vertices()
        self.polygons = super().get_polygons()
        self.polygons["FR"] = [0, 1, 35, 37]
        self.polygons["FCR"] = [35, 37, 38, 36]
        self.polygons["RF"] = [0, 14, 39, 37]
        self.polygons["RCF"] = [37, 39, 40, 38]

    def get_polygons(self):
        return self.polygons

    def get_override_pieces(self):
        return {
            # edges
            "FU": colors["ignore"],
            "RU": colors["ignore"],
            "AU": colors["ignore"],
            "BU": colors["ignore"],
            "LU": colors["ignore"],
            # corners
            "UFR": colors["ignore"],
            "RFU": colors["ignore"],
            "FRU": colors["ignore"],
            "UFL": colors["ignore"],
            "LFU": colors["ignore"],
            "FLU": colors["ignore"],
            "UAL": colors["ignore"],
            "LAU": colors["ignore"],
            "ALU": colors["ignore"],
            "UAB": colors["ignore"],
            "ABU": colors["ignore"],
            "BAU": colors["ignore"],
            "UBR": colors["ignore"],
            "BRU": colors["ignore"],
            "RBU": colors["ignore"],
        }

    def get_equivalences(self):
        return """\
{UR UF UL UA UB}
{URF UFL ULA UAB UBR}
1: URF UFL ULA UAB UBR\
"""

    def get_prune_search_subgroup(self):
        return "7 6 R U F"


class MegaminxWVColorizer(MegaminxLLColorizer):
    def get_override_pieces(self):
        return {
            # edges
            "FU": colors["ignore"],
            "LU": colors["ignore"],
            "AU": colors["ignore"],
            "BU": colors["ignore"],
            "RU": colors["ignore"],
            # corners
            "RFU": colors["ignore"],
            "FRU": colors["ignore"],
            "LFU": colors["ignore"],
            "FLU": colors["ignore"],
            "LAU": colors["ignore"],
            "ALU": colors["ignore"],
            "ABU": colors["ignore"],
            "BAU": colors["ignore"],
            "BRU": colors["ignore"],
            "RBU": colors["ignore"],
        }

    def get_equivalences(self):
        return """\
{UR UF UL UA UB}
{URF UFL ULA UAB UBR}\
"""

    def get_prune_search_subgroup(self):
        return "7 6 R U F"

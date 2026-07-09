from typing import Dict, List

import numpy as np

from cubevis.colorizer.colorizer import BaseColorizer, colors
from cubevis.cube import TwoByTwo


class TwoByTwoColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(TwoByTwo(), pre_moves)
        coords = [
            [0, 0],  # 0
            [1, 0],  # 1
            [2, 0],  # 2
            [2, 1],  # 3
            [2, 2],  # 4
            [1, 2],  # 5
            [0, 2],  # 6
            [0, 1],  # 7
            [1, 1],  # 8
            [0.1, -0.35],  # 9
            [0.9, -0.35],  # 10
            [1.1, -0.35],  # 11
            [1.9, -0.35],  # 12
            [2.35, 0.1],  # 13
            [2.35, 0.9],  # 14
            [2.35, 1.1],  # 15
            [2.35, 1.9],  # 16
            [1.9, 2.35],  # 17
            [1.1, 2.35],  # 18
            [0.9, 2.35],  # 19
            [0.1, 2.35],  # 20
            [-0.35, 1.9],  # 21
            [-0.35, 1.1],  # 22
            [-0.35, 0.9],  # 23
            [-0.35, 0.1],  # 24
            # [0.2, -0.25], # 25
            # [0.8, -0.25], # 26
            # [1.2, -0.25], # 27
            # [1.8, -0.25], # 28
            # [2.25, 0.2], # 29
            # [2.25, 0.8], # 30
            # [2.25, 1.2], # 31
            # [2.25, 1.8], # 32
            # [1.8, 2.25], # 33
            # [1.2, 2.25], # 34
            # [0.8, 2.25], # 35
            # [0.2, 2.25], # 36
            # [-0.25, 1.8], # 37
            # [-0.25, 1.2], # 38
            # [-0.25, 0.8], # 39
            # [-0.25, 0.2], # 40
        ]
        self.vertices = np.array(coords)
        self.normalize_vertices()

    def get_polygons(self) -> Dict[str, List[int]]:
        return {
            "UBL": [7, 0, 1, 8],
            "UBR": [1, 2, 3, 8],
            "UFR": [3, 4, 5, 8],
            "UFL": [5, 6, 7, 8],
            "BLU": [0, 9, 10, 1],
            "BRU": [1, 11, 12, 2],
            "RBU": [2, 13, 14, 3],
            "RFU": [3, 15, 16, 4],
            "FRU": [4, 17, 18, 5],
            "FLU": [5, 19, 20, 6],
            "LFU": [6, 21, 22, 7],
            "LBU": [7, 23, 24, 0],
            # "BDL": [25, 9, 10, 26],
            # "BDR": [27, 11, 12, 28],
            # "RBD": [29, 13, 14, 30],
            # "RDF": [31, 15, 16, 32],
            # "FDR": [33, 17, 18, 34],
            # "FDL": [35, 19, 20, 36],
            # "LDF": [37, 21, 22, 38],
            # "LBD": [39, 23, 24, 40],
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

    def get_prune_search_subgroup(self):
        return "6 5 R U F"


class TwoByTwoLLColorizer(TwoByTwoColorizer):
    def __init__(self) -> None:
        super().__init__("z2")

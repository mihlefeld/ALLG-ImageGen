from typing import Dict, List

from scipy.spatial.transform import Rotation

from cubevis.colorizer.colorizer import BaseColorizer, colors
from cubevis.cube import Skewb


class SkewbColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(Skewb(), pre_moves)
        coords = [
            [0, 0, 0],  # 0
            [1, 0, 0],  # 1
            [2, 0, 0],  # 2
            [2, 1, 0],  # 3
            [2, 2, 0],  # 4
            [1, 2, 0],  # 5
            [-2, 0, 0],  # 6l [-2, 0, 0]
            [-1, 0, 0],  # 7l [-1, 0, 0]
            [0, 0, 1],  # 8
            [2, 0, 1],  # 9
            [2, 2, 1],  # 10
            [-2, 0, 1],  # 11l [-2, 0, 1]
            [0, 0, 2],  # 12
            [1, 0, 2],  # 13
            [2, 0, 2],  # 14
            [2, 1, 2],  # 15
            [2, 2, 2],  # 16
            [1, 2, 2],  # 17
            [-2, 0, 2],  # 18l [-2, 0, 2]
            [-1, 0, 2],  # 19l [-1, 0, 2]
            [2, 3, 0],  # 20 5r [2, 3, 0]
            [2, 4, 0],  # 21 6r [2, 4, 0]
            [2, 4, 1],  # 22 11r [2, 4, 0]
            [2, 3, 2],  # 23 17r [2, 3, 2]
            [0, 2, 0],  # 24 6u
            [0, 1, 0],  # 25 7u
            [2, 4, 2],  # 26 18r [2, 4, 2]
        ]
        first_rotation = Rotation.from_rotvec([0, 0, 45], degrees=True).as_matrix()
        second_rotation = Rotation.from_rotvec([30, 0, 0], degrees=True).as_matrix()
        coords = coords @ first_rotation @ second_rotation
        coords = coords[:, [0, 2]]
        self.vertices = coords
        self.normalize_vertices()

    def get_polygons(self) -> Dict[str, List[int]]:
        return {
            "U": [1, 3, 5, 25],
            "F": [1, 9, 13, 8],
            "R": [3, 10, 15, 9],
            "B": [20, 22, 23, 10],
            "L": [7, 8, 19, 11],
            "RFU": [2, 3, 9],
            "RBU": [3, 4, 10],
            "RBD": [10, 15, 16],
            "RDF": [9, 14, 15],
            "UFL": [25, 0, 1],
            "UFR": [1, 2, 3],
            "UBR": [3, 4, 5],
            "UBL": [5, 24, 25],
            "FLU": [0, 1, 8],
            "FRU": [1, 2, 9],
            "FDR": [9, 13, 14],
            "FDL": [8, 12, 13],
            "BRU": [4, 20, 10],
            "BLU": [20, 21, 22],
            "BDL": [22, 23, 26],
            "BDR": [10, 23, 16],
            "LBU": [6, 7, 11],
            "LFU": [7, 0, 8],
            "LDF": [8, 19, 12],
            "LBD": [11, 18, 19],
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
        return "7 6 r l B b"

    def get_pre_adjust(self):
        return ""

    def get_post_adjust(self):
        return ""


class SkewbL2LColorizer(SkewbColorizer):
    def __init__(self) -> None:
        super().__init__()

    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "D": colors["white"],
            "F": colors["green"],
            "L": colors["red"],
            "B": colors["blue"],
            "R": colors["orange"],
            "U": colors["yellow"],
        }

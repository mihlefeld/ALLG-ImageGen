from typing import Dict, List

import numpy as np

from cubevis.colorizer.colorizer import BaseColorizer, colors
from cubevis.cube import Pyraminx


class PyraminxColorizer(BaseColorizer):
    def __init__(self) -> None:
        super().__init__(Pyraminx())
        coords = [
            [5.00, 7.40],
            [0.00, 10.00],
            [3.33, 10.00],
            [6.67, 10.00],
            [10.00, 10.00],
            [10.00, 10.00],
            [8.33, 7.11],
            [6.67, 4.23],
            [5.00, 1.34],
            [0.00, 10.00],
            [1.67, 7.11],
            [3.33, 4.23],
            [5.00, 1.34],
            [1.67, 9.13],
            [3.33, 8.27],
            [8.33, 9.13],
            [6.67, 8.27],
            [5.00, 3.36],
            [5.00, 5.38],
            [3.33, 6.25],
            [5.00, 9.13],
            [6.67, 6.25],
        ]
        self.vertices = np.array(coords)
        self.normalize_vertices()

    def get_polygons(self) -> Dict[str, List[int]]:
        return {
            "fbd": [3, 15, 4],
            "FBD": [20, 3, 15],
            "FD": [2, 20, 3],
            "FDR": [13, 2, 20],
            "fdr": [1, 13, 2],
            "rbd": [11, 17, 12],
            "RBD": [19, 11, 17],
            "RD": [10, 19, 11],
            "RDF": [13, 10, 19],
            "rdf": [9, 13, 10],
            "bdr": [7, 17, 8],
            "BDR": [21, 7, 17],
            "BD": [6, 21, 7],
            "BDF": [15, 6, 21],
            "bdf": [15, 4, 6],
            "FB": [15, 16, 20],
            "FBR": [20, 14, 16],
            "FR": [13, 14, 20],
            "RF": [19, 13, 14],
            "RBF": [19, 18, 14],
            "RB": [19, 17, 18],
            "BR": [17, 21, 18],
            "BFR": [21, 18, 16],
            "BF": [21, 15, 16],
            "fbr": [16, 0, 14],
            "rbf": [14, 18, 0],
            "bfr": [16, 18, 0],
        }

    def get_face_to_color(self) -> Dict[str, str]:
        initial_dict = {
            "R": colors["red"],
            "B": colors["blue"],
            "F": colors["green"],
            "D": colors["yellow"],
        }
        for k in "RBFD":
            initial_dict[k.lower()] = initial_dict[k]
        return initial_dict

    def get_prune_search_subgroup(self):
        return "6 5 R U L B"

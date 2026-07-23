from typing import Dict, List

import numpy as np

from cubevis.colorizer.colorizer import BaseColorizer, colors
from cubevis.cube import FTO


# R = right, G = front, P = Left, W = Up, O = Back left, B = Back, Z = Back right, Y = bottom
class FTOColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(FTO(), pre_moves)
        self.vertices = np.array(
            [
                [379, 438],
                [379, 219],
                [463, 294],
                [546, 438],
                [569, 548],
                [463, 583],
                [296, 583],
                [189, 548],
                [213, 438],
                [296, 294],
                [296, 144],
                [189, 329],
                [83, 513],
                [166, 658],
                [379, 658],
                [593, 658],
                [676, 513],
                [569, 329],
                [463, 144],
                [379, 69],
                [60, 623],
                [699, 623],
                [379, 0],
                [0, 658],
                [759, 658],
            ]
        )
        self.vertices[:, 1] *= -1
        self.normalize_vertices()

    def needs_invert(self):
        return True

    def get_polygons(self) -> Dict[str, List[int]]:
        return {
            "WGPR": [1, 2, 9],
            "RGPW": [1, 2, 18],
            "GPRW": [1, 10, 18],
            "PGRW": [1, 9, 10],
            "P2": [10, 9, 11],
            "PW": [9, 11, 8],
            "P1": [11, 8, 12],
            "WBOP": [6, 7, 8],
            "PBOW": [8, 12, 7],
            "OBPW": [7, 12, 13],
            "BOPW": [7, 13, 6],
            "B2": [13, 6, 14],
            "BW": [5, 6, 14],
            "B1": [5, 14, 15],
            "WBRZ": [3, 5, 4],
            "BRWZ": [4, 5, 15],
            "ZBRW": [4, 15, 16],
            "RBWZ": [3, 4, 16],
            "R2": [3, 16, 17],
            "RW": [2, 3, 17],
            "R1": [2, 17, 18],
            "G1": [10, 18, 19],
            "O1": [12, 13, 20],
            "Z1": [15, 16, 21],
            "W3": [0, 2, 9],
            "WP": [0, 8, 9],
            "W1": [0, 6, 8],
            "WB": [0, 5, 6],
            "W2": [0, 5, 3],
            "WR": [2, 0, 3],
            "G3": [18, 19, 10, 22],
            "O3": [12, 20, 13, 23],
            "Z3": [16, 21, 15, 24],
        }

    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "R": colors["red"],
            "B": colors["blue"],
            "G": colors["green"],
            "Y": colors["yellow"],
            "P": colors["purple"],
            "Z": colors["ignore"],
            "O": colors["orange"],
            "W": colors["white"],
        }

    def get_prune_search_subgroup(self):
        return "8 7 R U L B BR"


class FTOL3TColorizer(FTOColorizer):
    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "R": colors["orange"],
            "B": colors["ignore"],
            "G": colors["purple"],
            "Y": colors["white"],
            "P": colors["green"],
            "Z": colors["blue"],
            "O": colors["red"],
            "W": colors["yellow"],
        }

    def get_equivalences(self):
        return """\
{Y1 Y2 Y3}
{W1 W2 W3}
{G2 G3}
{P1 P2}
{R1 R2}
{B1 B2}
{O2 O2}
{Z2 Z3}
{W R G P O B Z Y}\
"""


class FTOL6XColorizer(FTOL3TColorizer):
    def get_override_colors(self):
        return {
            "G3": colors["black"],
            "Z3": colors["black"],
            "O3": colors["black"],
            "G1": colors["black"],
            "Z1": colors["black"],
            "O1": colors["black"],
            "WGPR": colors["black"],
            "RGPW": colors["black"],
            "GPRW": colors["black"],
            "PGRW": colors["black"],
            "WBOP": colors["black"],
            "PBOW": colors["black"],
            "OBPW": colors["black"],
            "BOPW": colors["black"],
            "WBRZ": colors["black"],
            "BRWZ": colors["black"],
            "ZBRW": colors["black"],
            "RBWZ": colors["black"],
        }

    def get_equivalences(self):
        return """\
{Y1 Y2 Y3}
{W1 W2 W3}
{G1 G2 G3}
{P1 P2}
{R1 R2}
{B1 B2}
{O1 O2 O3}
{Z1 Z2 Z3}
{W R G P O B Z Y}
{WRGP WPOB WBZR}
1: WRGP WPOB WBZR\
"""


class FTOL3CColorizer(FTOL3TColorizer):
    def get_override_colors(self):
        return {
            "G3": colors["black"],
            "Z3": colors["black"],
            "O3": colors["black"],
            "G1": colors["black"],
            "Z1": colors["black"],
            "O1": colors["black"],
        }

    def get_equivalences(self):
        return """\
{Y1 Y2 Y3}
{W1 W2 W3}
{G1 G2 G3}
{P1 P2}
{R1 R2}
{B1 B2}
{O1 O2 O3}
{Z1 Z2 Z3}
{W R G P O B Z Y}\
"""


class FTOOLPColorizer(FTOL3TColorizer):
    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "R": colors["ignore"],
            "B": colors["ignore"],
            "G": colors["ignore"],
            "Y": colors["yellow"],
            "P": colors["ignore"],
            "Z": colors["ignore"],
            "O": colors["ignore"],
            "W": colors["white"],
        }


class FTOFullColorizer(FTOColorizer):
    def __init__(self, pre_moves=""):
        super().__init__(pre_moves)
        self.vertices = np.array(
            [
                [26.59, 236.79],
                [64.38, 258.64],
                [102.14, 236.79],
                [140.03, 258.62],
                [177.76, 236.79],
                [215.58, 258.62],
                [253.35, 236.79],
                [102.22, 280.44],
                [177.76, 280.44],
                [139.97, 302.26],
                [38.85, 39.66],
                [1.0, 61.58],
                [1.0, 105.21],
                [38.84, 83.36],
                [76.58, 17.94],
                [76.63, 61.58],
                [114.39, -3.88],
                [1.0, 148.85],
                [38.84, 127.03],
                [1.0, 192.5],
                [203.33, 61.66],
                [203.33, 17.92],
                [165.56, -3.88],
                [241.11, 83.35],
                [241.13, 39.73],
                [278.87, 105.12],
                [278.92, 61.57],
                [241.13, 127.03],
                [278.95, 148.91],
                [278.92, 192.5],
                [26.06, 75.75],
                [26.06, 207.85],
                [140.44, 273.88],
                [254.83, 207.85],
                [254.83, 75.75],
                [140.44, 9.71],
                [27.09, 76.34],
                [64.91, 141.8],
                [102.73, 76.34],
                [140.49, 141.8],
                [178.28, 76.34],
                [216.08, 141.8],
                [253.88, 76.34],
                [102.63, 207.26],
                [178.24, 207.26],
                [140.47, 272.72],
                [178.25, 32.69],
                [140.44, 10.88],
                [102.64, 32.69],
                [140.44, 54.52],
                [64.84, 54.52],
                [216.01, 54.52],
                [253.83, 119.98],
                [216.04, 185.47],
                [253.83, 163.63],
                [178.29, 250.91],
                [216.04, 229.08],
                [253.83, 207.26],
                [27.06, 119.98],
                [27.06, 163.62],
                [64.86, 185.43],
                [27.06, 207.26],
                [64.86, 229.09],
                [102.63, 250.88],
            ]
        )
        self.normalize_vertices()

    def get_polygons(self):
        return {
            # D face
            "YBOZ": [0, 1, 2],
            "Y3": [3, 2, 1],
            "YZ": [2, 3, 4],
            "Y2": [5, 4, 3],
            "YGRZ": [4, 5, 6],
            "YO": [1, 7, 3],
            "Y1": [8, 3, 7],
            "YG": [3, 8, 5],
            "YGOP": [7, 9, 8],

            # BL Face
            "BOPW": [10, 11, 12],
            "B2": [12, 13, 10],
            "BW": [14, 10, 13],
            "B1": [13, 15, 14],
            "BRWZ": [16, 14, 15],
            "BO": [13, 12, 17],
            "B3": [17, 18, 13],
            "BZ": [15, 13, 18],
            "BOYZ": [18, 17, 19],

            # BR Face
            "RBWZ": [20, 21, 22],
            "R2": [21, 20, 23],
            "RW": [23, 24, 21],
            "R1": [24, 23, 25],
            "RGPW": [25, 26, 24],
            "RZ": [27, 23, 20],
            "R3": [23, 27, 28],
            "RG": [28, 25, 23],
            "RGYZ": [29, 28, 27],

            # F face
            "PBOW": [36, 37, 38],
            "P1": [39, 38, 37],
            "PW": [38, 39, 40],
            "P2": [41, 40, 39],
            "PGRW": [40, 41, 42],
            "PO": [37, 43, 39],
            "P3": [44, 39, 43],
            "PG": [39, 44, 41],
            "PGOY": [43, 45, 44],

            # U face
            "WBRZ": [46, 47, 48],
            "WB": [49, 48, 50],
            "W2": [48, 49, 46],
            "WR": [51, 46, 49],
            "WBOP": [38, 50, 36],
            "W1": [50, 38, 49],
            "WP": [40, 49, 38],
            "W3": [49, 40, 51],
            "WGPR": [42, 51, 40],

            # R face
            "GPRW": [41, 52, 42],
            "GP": [44, 53, 41],
            "G1": [52, 41, 53],
            "GR": [53, 54, 52],
            "GOPY": [45, 55, 44],
            "G3": [53, 44, 55],
            "GY": [55, 56, 53],
            "G2": [54, 53, 56],
            "GRYZ": [56, 57, 54],

            # L face
            "OBPW": [36, 58, 37],
            "OB": [58, 59, 60],
            "O1": [60, 37, 58],
            "OP": [37, 60, 43],
            "OBYZ": [59, 61, 62],
            "O3": [62, 60, 59],
            "OY": [60, 62, 63],
            "O2": [63, 43, 60],
            "OGPY": [43, 63, 45],
        }

class FTOLTBaseColorizer(FTOFullColorizer):
    def get_face_to_color(self):
        return {
            "W": colors['yellow'],
            "B": colors['orange'],
            "R": colors['green'],
            "P": colors['ignore'],
            "O": colors['blue'],
            "Y": colors['white'],
            "Z": colors['purple'],
            "G": colors['red']
        }
    
class FTOLBTColorizer(FTOLTBaseColorizer):
    def scramble(self, moves, path=None):
        #moves = " ".join(["y'", moves, "y"])
        return super().scramble(moves, path)
    
    def get_equivalences(self):
        return """\
{WBZR WPOB WRGP}
1: WBZR WPOB WRGP
{G1 O1 Z1 W1 W2 W3}
"""
    
    def get_prune_search_subgroup(self):
        return "6 6 R B U L"

    def get_override_colors(self):
        return {
            "B3": colors['orange'],
            "R3": colors['green'],
            "P3": colors['ignore']
        }

    def get_override_pieces(self):
        return {
            "R1": colors['black'],
            "R2": colors['black'],
            "B1": colors['black'],
            "B2": colors['black'],
            "Z1": colors['black'],
            "Z2": colors['black'],
            "W": colors['black'],
            "P": colors['black'],
            "G1": colors['black'],
            "O1": colors['black'],

            "WP": colors['black'],
            "WB": colors['black'],
            "WR": colors['black'],
            "PW": colors['black'],
            "BW": colors['black'],
            "RW": colors['black'],

            "WBRZ": colors['black'],
            "BRWZ": colors['black'],
            "RBWZ": colors['black'],
            "ZBRW": colors['black'],

            "WBOP": colors['black'],
            "BOPW": colors['black'],
            "OBPW": colors['black'],
            "PBOW": colors['black'],

            "WGPR": colors['black'],
            "GPRW": colors['black'],
            "PGRW": colors['black'],
            "RGPW": colors['black'],
        }
    

class FTOBTLTColorizer(FTOLTBaseColorizer):
    def scramble(self, moves, path=None):
        moves = " ".join(["y'", moves, "y"])
        return super().scramble(moves, path)

    def get_override_colors(self):
        return {
            "B3": colors['orange'],
            "R3": colors['green']
        }

    def get_override_pieces(self):
        return {
            "WBRZ": colors['black'],
            "BRWZ": colors['black'],
            "RBWZ": colors['black'],
            "ZBRW": colors['black'],

            "WBOP": colors['black'],
            "BOPW": colors['black'],
            "OBPW": colors['black'],
            "PBOW": colors['black'],

            "WGPR": colors['black'],
            "GPRW": colors['black'],
            "PGRW": colors['black'],
            "RGPW": colors['black'],

            "WP": colors['black'],
            "WB": colors['black'],
            "WR": colors['black'],
            "PW": colors['black'],
            "BW": colors['black'],
            "RW": colors['black'],

            "R": colors['black'],
            "B": colors['black'],
            "W": colors['black'],
            "P": colors['black'],
        }
    
    def get_prune_search_subgroup(self):
        return "6 6 R BR BL U"
    
    def get_equivalences(self):
        return """\
{R1 R2 R3 P1 P2 B1 B2}
{WBZR WPOB WRGP}
1: WBZR WPOB WRGP
"""

class FTOLTColorizer(FTOBTLTColorizer):
    def get_override_pieces(self):
        override = dict(**super().get_override_pieces())
        override.pop("P")
        override['P1'] = colors['black']
        override['P2'] = colors['black']
        return override

    def get_prune_search_subgroup(self):
        return "6 7 R BR F U"

    def get_equivalences(self):
        return """\
{R1 R2 P1 P2 B1 B2}
{WBZR WPOB WRGP}
1: WBZR WPOB WRGP
"""

class FTOFTLTColorizer(FTOLTColorizer): 
    def get_override_pieces(self):
        override = dict(**super().get_override_pieces())
        override['Y1'] = colors['black']
        return override

    def get_prune_search_subgroup(self):
        return "6 6 R BR F U"

    def get_equivalences(self):
        return """\
{R1 R2 P1 P2 B1 B2 Y2}
{WBZR WPOB WRGP}
1: WBZR WPOB WRGP
"""
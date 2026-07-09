import re

import numpy as np

from cubevis.colorizer.colorizer import BaseColorizer, colors
from cubevis.cube import SquareOne


class SquareOneColorizer(BaseColorizer):
    def __init__(self):
        super().__init__(SquareOne())
        points = [
            (0.00, 191.42),
            (0.00, 120.71),
            (0.00, 70.71),
            (0.00, 0.00),
            (70.71, 0.00),
            (120.71, 0.00),
            (191.42, 0.00),
            (191.42, 70.71),
            (191.42, 120.71),
            (191.42, 191.42),
            (120.71, 191.42),
            (70.71, 191.42),
            (91.46, 111.98),
            (87.26, 104.16),
            (79.44, 99.96),
            (64.13, 103.96),
            (67.00, 95.71),
            (64.13, 87.46),
            (79.44, 91.46),
            (87.26, 87.26),
            (91.46, 79.44),
            (87.46, 64.13),
            (95.71, 67.00),
            (103.96, 64.13),
            (99.96, 79.44),
            (104.16, 87.26),
            (111.98, 91.46),
            (127.30, 87.46),
            (124.42, 95.71),
            (127.30, 103.96),
            (111.98, 99.96),
            (104.16, 104.16),
            (99.96, 111.98),
            (103.96, 127.30),
            (95.71, 124.42),
            (87.46, 127.30),
            (-38.28, 229.71),
            (-38.28, 130.71),
            (-38.28, 60.71),
            (-38.28, -38.28),
            (60.71, -38.28),
            (130.71, -38.28),
            (229.71, -38.28),
            (229.71, 60.71),
            (229.71, 130.71),
            (229.71, 229.71),
            (130.71, 229.71),
            (60.71, 229.71),
        ]
        self.vertices = np.array(points)
        down_vert = np.array(points)
        down_vert[:, 1] += 1.1 * (
            np.max(self.vertices[:, 1]) - np.min(self.vertices[:, 1])
        )
        self.vertices = np.concatenate([self.vertices, down_vert])
        self.normalize_vertices()

    def needs_invert(self):
        return True

    def inverse(self, moves, path=None):
        moves = self.cube.to_self_notation(moves)
        moves = re.findall(r"\d?[A-z]+'?\d?'?", moves)
        inverted_moves = []
        for move in moves[::-1]:
            inverted = move[:-1] if move[-1] == "'" else move + "'"
            inverted_moves.append(inverted)
        scramble = " ".join(inverted_moves)
        self.cube.reset()
        self.cube.move(scramble)
        svg = self.create_svg()
        if path is not None:
            with open(path, "w") as file:
                file.write(svg)
        return scramble

    def fix_last_move_to_cubeshape(self, alg: str) -> str:
        cube: SquareOne = self.cube
        cube.scramble(alg)
        cube_state = dict(cube.pieces)
        move_parts = alg.split("/")
        u_test_piece = cube_state["X4"][0]
        d_test_piece = cube_state["X5"][0]

        u, d = map(int, move_parts[-1].strip(" ()").split(","))
        if "X" not in u_test_piece and len(u_test_piece) == 2:
            u = (u - 1) % 3
        if "X" not in u_test_piece and len(u_test_piece) == 3:
            u = (u + 1) % 3
        if "X" not in d_test_piece and len(d_test_piece) == 2:
            d = (d - 1) % 3
        if "X" not in d_test_piece and len(d_test_piece) == 3:
            d = (d + 1) % 3
        if u == 2:
            u = -1
        if d == 2:
            d = -1
        move_parts[-1] = f" {u},{d}"
        cube.reset()
        return "/".join(move_parts)

    def get_polygons(self):
        return {
            "UFL": [0, 1, 14, 13, 12, 11],
            "UL": [1, 2, 17, 16, 15],
            "UBL": [2, 3, 4, 20, 19, 18],
            "UB": [4, 5, 23, 22, 21],
            "UBR": [5, 6, 7, 26, 25, 24],
            "UR": [7, 8, 29, 28, 27],
            "UFR": [8, 9, 10, 32, 31, 30],
            "UF": [10, 11, 35, 34, 33],
            "LFU": [36, 37, 1, 0],
            "LU": [37, 38, 2, 1],
            "LBU": [38, 39, 3, 2],
            "BLU": [39, 40, 4, 3],
            "BU": [40, 41, 5, 4],
            "BRU": [41, 42, 6, 5],
            "RBU": [42, 43, 7, 6],
            "RU": [43, 44, 8, 7],
            "RFU": [44, 45, 9, 8],
            "FRU": [45, 46, 10, 9],
            "FU": [46, 47, 11, 10],
            "FLU": [47, 36, 0, 11],
            "DBL": [0 + 48, 1 + 48, 14 + 48, 13 + 48, 12 + 48, 11 + 48],  # DBL
            "DL": [1 + 48, 2 + 48, 17 + 48, 16 + 48, 15 + 48],
            "DFL": [2 + 48, 3 + 48, 4 + 48, 20 + 48, 19 + 48, 18 + 48],  # DFL
            "DF": [4 + 48, 5 + 48, 23 + 48, 22 + 48, 21 + 48],  # DF
            "DFR": [5 + 48, 6 + 48, 7 + 48, 26 + 48, 25 + 48, 24 + 48],  # DFR
            "DR": [7 + 48, 8 + 48, 29 + 48, 28 + 48, 27 + 48],
            "DBR": [8 + 48, 9 + 48, 10 + 48, 32 + 48, 31 + 48, 30 + 48],  # DBR
            "DB": [10 + 48, 11 + 48, 35 + 48, 34 + 48, 33 + 48],  # DB
            "LBD": [36 + 48, 37 + 48, 1 + 48, 0 + 48],  # LDB
            "LD": [37 + 48, 38 + 48, 2 + 48, 1 + 48],
            "LDF": [38 + 48, 39 + 48, 3 + 48, 2 + 48],  # LDF
            "FDL": [39 + 48, 40 + 48, 4 + 48, 3 + 48],
            "FD": [40 + 48, 41 + 48, 5 + 48, 4 + 48],
            "FDR": [41 + 48, 42 + 48, 6 + 48, 5 + 48],
            "RDF": [42 + 48, 43 + 48, 7 + 48, 6 + 48],  # RDF
            "RD": [43 + 48, 44 + 48, 8 + 48, 7 + 48],
            "RBD": [44 + 48, 45 + 48, 9 + 48, 8 + 48],  # RBD
            "BDR": [45 + 48, 46 + 48, 10 + 48, 9 + 48],
            "BD": [46 + 48, 47 + 48, 11 + 48, 10 + 48],
            "BDL": [47 + 48, 36 + 48, 0 + 48, 11 + 48],
        }

    def get_face_to_color(self):
        return {
            "U": colors["black"],
            "F": colors["red"],
            "R": colors["green"],
            "L": colors["blue"],
            "B": colors["orange"],
            "D": colors["white"],
            "X": colors["ignore"],
        }

    def get_prune_search_subgroup(self):
        return "7 6 U D T t"

    def get_pre_adjust(self):
        return "U D"

    def get_post_adjust(self):
        return "U D"


class SquareOneOBLColorizer(SquareOneColorizer):
    def get_face_to_color(self):
        return {
            "U": colors["black"],
            "F": colors["ignore"],
            "R": colors["ignore"],
            "L": colors["ignore"],
            "B": colors["ignore"],
            "D": colors["white"],
            "X": colors["ignore"],
        }

    def get_equivalences(self):
        return """\
{UR UL UF UB}
{DR DL DF DB}
{X1 X2 X3 X4}
{X5 X6 X7 X8}
{UFL ULB UBR URF}
{DLF DFR DRB DBL}\
"""

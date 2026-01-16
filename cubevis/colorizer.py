import numpy as np
import re
import pathlib
from typing import Dict, List
from scipy.spatial.transform import Rotation
from collections import defaultdict
from cubevis.cube import Cube, Megaminx, Skewb, TwoByTwo, ThreeByThree, Pyraminx, Octaminx, FiveByFive, SquareOne

colors = {
    "white": "#fafafa",
    "ignore": "#777",
    "black": "#222",
    "lightblue": "#A0CBE8",
    "blue": "#4E79A7",
    "red": "#E15759",
    "pink": "#FF9D9A",
    "beige": "#f4f3aa",
    "yellow": "#F1CE63",
    "green": "#59A14F",
    "lightgreen": "#8CD17D",
    "purple": "#B07AA1",
    "orange": "#F28E2B"
}



class BaseColorizer:
    def __init__(self, cube: Cube, pre_moves="") -> None:
        self.vertices = np.zeros((0, ))
        self.polygons = {}
        self.cube = cube
        self.width = 100
        self.height = 100
        self.pre_moves = pre_moves
        pass
    
    def normalize_vertices(self):
        self.vertices -= self.vertices.min(axis=0)
        max_coord = self.vertices.max()
        self.vertices = self.vertices / max_coord * 90
        self.vertices += 5
        self.width = self.vertices[:, 0].max() + 5
        self.height = self.vertices[:, 1].max() + 5

    def get_polygons(self) -> Dict[str, List[int]]:
        """Get a dictionary mapping from sticker name to polygon. Sticker name is side of sticker and then the other faces alphabetically sorted """
        pass
    
    def get_face_to_color(self) -> Dict[str, str]:
        """A dictionary that has a face like F, U, R as input, and outputs the color"""
        pass

    def make_stickers_from_piece(self, piece) -> List[str]:
        non_num_piece = "".join([c for c in piece if not c.isnumeric()])
        last_number = "".join([c for c in piece if c.isnumeric()])
        stickers = []
        for firstFace in non_num_piece:
            stickers.append(firstFace + "".join(sorted([f for f in non_num_piece if f != firstFace])) + last_number)
        return stickers
    
    def get_override_colors(self) -> Dict[str, str]:
        """Return a dictionary that maps from stickers to colors which defines the stickers that should always be a certain color. Use this to indicate parts of the visualization that can be ignored."""
        return dict()
    
    def get_override_pieces(self) -> Dict[str, str]:
        """Return a dictionary that maps from pieces in a given orientation to colors which defines an override for stickers of a piece that sholud be ignored. Use this if the location of ignored stickers isn't always the same."""
        return dict()

    def get_sticker_colors_from_cube(self) -> Dict[str, str]:
        sticker_positions_to_color = {}
        face_to_color = self.get_face_to_color()
        override_pieces = self.get_override_pieces()
        for position, (piece, ori) in self.cube.pieces.items():
            non_numeric_piece = "".join([c for c in piece if not c.isnumeric()])
            piece_stickers = self.make_stickers_from_piece(non_numeric_piece)
            sticker_positions = self.make_stickers_from_piece(position)
            for i in range(len(non_numeric_piece)):
                ival = (i + ori) % len(non_numeric_piece)
                try:
                    if piece_stickers[i] in override_pieces:
                        sticker_positions_to_color[sticker_positions[ival]] = override_pieces[piece_stickers[i]]
                    else:
                        sticker_positions_to_color[sticker_positions[ival]] = face_to_color[non_numeric_piece[i]]
                except:
                    pass
        for k, v in self.get_override_colors().items():
            sticker_positions_to_color[k] = v
        return sticker_positions_to_color


    def create_svg(self):
        style = "polygon { stroke: black; stroke-width: 0.5px; stroke-linejoin: round;}"
        svg = \
f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">
<style>
{style}
</style>"""
        sticker_colors = self.get_sticker_colors_from_cube()
        polygons = self.get_polygons()
        for sticker_name, polygon_picking in polygons.items():
            poygon_str = " ".join([f"{a:.2f} {b:.2f}" for (a, b) in self.vertices[polygon_picking]])
            try:
                svg += f"<polygon fill='{sticker_colors[sticker_name]}' points='{poygon_str}'/>\n"
            except:
                #TODO: log warning
                pass
        svg += "</svg>"
        return svg
    
    def inverse(self, moves, path=None):
        moves = re.findall(r"\d?[A-z]+'?\d?'?", moves)
        rotations = []
        inverted_moves = []
        for move in moves[::-1]:
            inverted = move[:-1] if move[-1] == "'" else move + "'"
            if move[0] in "xyz":
                rotations = [move] + rotations
            inverted_moves.append(inverted)
        scramble = " ".join(inverted_moves)
        self.cube.scramble(" ".join(moves))
        rotation = self.cube.to_reference_rotation(scramble=False)
        if rotation != "":
            rotation = " ".join([(m[:-1] if m[-1] == "'" else m + "'") for m in rotation.split(' ')][::-1]) + " "

        self.scramble(rotation + scramble, path)
        return rotation + scramble

    def scramble(self, moves, path=None):
        self.cube.scramble(" ".join([self.pre_moves, moves]).strip())
        svg = self.create_svg()
        if path is None:
            return svg
        with open(path, 'w') as file:
            file.write(svg)



class SkewbColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(Skewb(), pre_moves)
        coords = [
            [0, 0, 0], # 0
            [1, 0, 0], # 1
            [2, 0, 0], # 2
            [2, 1, 0], # 3
            [2, 2, 0], # 4
            [1, 2, 0], # 5
            [-2, 0, 0], # 6l [-2, 0, 0]
            [-1, 0, 0], # 7l [-1, 0, 0]
            [0, 0, 1], # 8
            [2, 0, 1], # 9
            [2, 2, 1], # 10
            [-2, 0, 1], # 11l [-2, 0, 1]
            [0, 0, 2], # 12
            [1, 0, 2], # 13
            [2, 0, 2], # 14
            [2, 1, 2], # 15
            [2, 2, 2], # 16
            [1, 2, 2], # 17
            [-2, 0, 2], # 18l [-2, 0, 2]
            [-1, 0, 2], # 19l [-1, 0, 2]
            [2, 3, 0], # 20 5r [2, 3, 0]
            [2, 4, 0], # 21 6r [2, 4, 0]
            [2, 4, 1], # 22 11r [2, 4, 0]
            [2, 3, 2], # 23 17r [2, 3, 2]
            [0, 2, 0], # 24 6u
            [0, 1, 0], # 25 7u
            [2, 4, 2], # 26 18r [2, 4, 2]
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
            "LBD": [11, 18, 19]
        }
    
    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "U": colors["white"],
            "F": colors["green"],
            "R": colors["red"],
            "B": colors["blue"],
            "L": colors["orange"],
            "D": colors["yellow"]
        }

class SkewbL2LColorizer(SkewbColorizer):
    def __init__(self) -> None:
        super().__init__("z2")

    
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
            [323, 240]
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
            "U": colors["white"]
            }

class MegaminxLLColorizer(MegaminxColorizer):
    def __init__(self) -> None:
        super().__init__("x2 z y'")


class MegaminxOLLColorizer(MegaminxColorizer):
    def get_face_to_color(self) -> Dict[str, str]:
        ret = defaultdict(lambda: colors["ignore"])
        ret["U"] = colors["black"]
        return ret

class TwoByTwoColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(TwoByTwo(), pre_moves)
        coords = [
            [0, 0], # 0
            [1, 0], # 1
            [2, 0], # 2
            [2, 1], # 3
            [2, 2], # 4
            [1, 2], # 5
            [0, 2], # 6
            [0, 1], # 7
            [1, 1], # 8
            [0.1, -0.35], # 9
            [0.9, -0.35], # 10
            [1.1, -0.35], # 11
            [1.9, -0.35], # 12
            [2.35, 0.1], # 13
            [2.35, 0.9], # 14
            [2.35, 1.1], # 15
            [2.35, 1.9], # 16
            [1.9, 2.35], # 17
            [1.1, 2.35], # 18
            [0.9, 2.35], # 19
            [0.1, 2.35], # 20
            [-0.35, 1.9], # 21
            [-0.35, 1.1], # 22
            [-0.35, 0.9], # 23
            [-0.35, 0.1], # 24
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
            "D": colors["yellow"]
        }
    
class TwoByTwoLLColorizer(TwoByTwoColorizer):
    def __init__(self) -> None:
        super().__init__("z2")

class ThreeByThreeColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(ThreeByThree(), pre_moves)
        xy_to_key = {
            (0, 0): None, (1, 0): "BLU", (2, 0): "BU", (3, 0): "BRU", (4, 0): None,
            (0, 1): "LBU", (1, 1): "UBL", (2, 1): "UB", (3, 1): "UBR", (4, 1): "RBU",
            (0, 2): "LU", (1, 2): "UL", (2, 2): "U", (3, 2): "UR", (4, 2): "RU",
            (0, 3): "LFU", (1, 3): "UFL", (2, 3): "UF", (3, 3): "UFR", (4, 3): "RFU",
            (0, 4): None, (1, 4): "FLU", (2, 4): "FU", (3, 4): "FRU", (4, 4): None,
        }
        self.polygons = {}
        counter = 0
        coords = []
        for i in range(5*5):
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
                bl = [x + 0.1, y + 0.4 ]
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
            "D": colors["yellow"]
        }

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
            "U": colors["ignore"]
        }
    
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
"""
Batch Solver equivalences:
{UF UR UB UL}
1: URF UBR ULB UFL 
"""    
    
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
            "FD" : [2, 20, 3],
            "FDR": [13, 2, 20],
            "fdr": [1, 13, 2],
            "rbd": [11, 17, 12],
            "RBD": [19, 11, 17],
            "RD" : [10, 19, 11],
            "RDF": [13, 10, 19],
            "rdf": [9, 13, 10],
            "bdr": [7, 17, 8],
            "BDR": [21, 7, 17],
            "BD" : [6, 21, 7],
            "BDF": [15, 6, 21],
            "bdf": [15, 4, 6],
            "FB" : [15, 16, 20],
            "FBR": [20, 14, 16],
            "FR" : [13, 14, 20],
            "RF" : [19, 13, 14],
            "RBF": [19, 18, 14],
            "RB" : [19, 17, 18],
            "BR" : [17, 21, 18],
            "BFR": [21, 18, 16],
            "BF" : [21, 15, 16],
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

class OctaminxColorizer(BaseColorizer):
    def __init__(self, pre_moves="") -> None:
        super().__init__(Octaminx(), pre_moves)
        p = pathlib.Path(__file__).parent / "octaminx.npy"
        self.vertices = np.array([
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
            [759, 658]
        ])
        self.vertices[:, 1] *= -1
        self.normalize_vertices()

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
            "Z3": [16, 21, 15, 24]
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
            "W": colors["white"]
        }

# R = right, G = front, P = Left, W = Up, O = Back left, B = Back, Z = Back right, Y = bottom

class OctaminxL3TColorizer(OctaminxColorizer):
    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "R": colors["orange"],
            "B": colors["ignore"],
            "G": colors["purple"],
            "Y": colors["white"],
            "P": colors["green"],
            "Z": colors["blue"],
            "O": colors["red"],
            "W": colors["yellow"]
        }

class OctaminxOLPColorizer(OctaminxL3TColorizer):
    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "R": colors["ignore"],
            "B": colors["ignore"],
            "G": colors["ignore"],
            "Y": colors["yellow"],
            "P": colors["ignore"],
            "Z": colors["ignore"],
            "O": colors["ignore"],
            "W": colors["white"]
        }

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
            "F":  [27, 28, 36, 35],
            "F4": [28, 29, 37, 36],
            "FR": [29, 30, 38, 37],
            "RF": [30, 31, 39, 38],

            "LF1": [32, 33, 41, 40],
            "FL1": [33, 34, 42, 41],
            "F7":  [34, 35, 43, 42],
            "F6":  [35, 36, 44, 43],
            "F5":  [36, 37, 45, 44],
            "FR2": [37, 38, 46, 45],
            "RF2": [38, 39, 47, 46],

            "LDF": [40, 41, 49, 48],
            "FDL": [41, 42, 50, 49],
            "FD1": [42, 43, 51, 50],
            "FD":  [43, 44, 52, 51],
            "FD2": [44, 45, 53, 52],
            "FDR": [45, 46, 54, 53],
            "RDF": [46, 47, 55, 54],

            "DFL": [49, 50, 58, 57],
            "DF1": [50, 51, 59, 58],
            "DF":  [51, 52, 60, 59],
            "DF2": [52, 53, 61, 60],
            "DFR": [53, 54, 62, 61]
    }
    
    def get_face_to_color(self) -> Dict[str, str]:
        return {
            "U": colors["white"],
            "F": colors["green"],
            "R": colors["red"],
            "B": colors["blue"],
            "L": colors["orange"],
            "D": colors["yellow"]
        }
    
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
            (93.71, 103.37),
            (92.09, 99.33),
            (88.05, 97.71),
            (72.74, 101.71),
            (74.65, 95.71),
            (72.74, 89.71),
            (88.05, 93.71),
            (92.09, 92.09),
            (93.71, 88.05),
            (89.71, 72.74),
            (95.71, 74.65),
            (101.71, 72.74),
            (97.71, 88.05),
            (99.33, 92.09),
            (103.37, 93.71),
            (118.68, 89.71),
            (116.77, 95.71),
            (118.68, 101.71),
            (103.37, 97.71),
            (99.33, 99.33),
            (97.71, 103.37),
            (101.71, 118.68),
            (95.71, 116.77),
            (89.71, 118.68),
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
        down_vert[:, 1] += 1.1 * (np.max(self.vertices[:, 1]) - np.min(self.vertices[:, 1]))
        self.vertices = np.concatenate([self.vertices, down_vert])
        self.normalize_vertices()

    def inverse(self, moves, path=None):
        moves = self.cube.to_self_notation(moves)
        moves = re.findall(r"\d?[A-z]+'?\d?'?", moves)
        inverted_moves = []
        for move in moves[::-1]:
            inverted = move[:-1] if move[-1] == "'" else move + "'"
            inverted_moves.append(inverted)
        scramble = " ".join(inverted_moves)
        self.cube.move(scramble)
        svg = self.create_svg()
        if path is not None:
            with open(path, 'w') as file:
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

            "DFL": [0+48, 1+48, 14+48, 13+48, 12+48, 11+48],
            "DL": [1+48, 2+48, 17+48, 16+48, 15+48],
            "DBL": [2+48, 3+48, 4+48, 20+48, 19+48, 18+48],
            "DB": [4+48, 5+48, 23+48, 22+48, 21+48],
            "DBR": [5+48, 6+48, 7+48, 26+48, 25+48, 24+48],
            "DR": [7+48, 8+48, 29+48, 28+48, 27+48],
            "DFR": [8+48, 9+48, 10+48, 32+48, 31+48, 30+48],
            "DF": [10+48, 11+48, 35+48, 34+48, 33+48],
            "LDF": [36+48, 37+48, 1+48, 0+48],
            "LD": [37+48, 38+48, 2+48, 1+48],
            "LBD": [38+48, 39+48, 3+48, 2+48],
            "FDL": [39+48, 40+48, 4+48, 3+48],
            "FD": [40+48, 41+48, 5+48, 4+48],
            "FDR": [41+48, 42+48, 6+48, 5+48],
            "RBD": [42+48, 43+48, 7+48, 6+48],
            "RD": [43+48, 44+48, 8+48, 7+48],
            "RDF": [44+48, 45+48, 9+48, 8+48],
            "BDR": [45+48, 46+48, 10+48, 9+48],
            "BD": [46+48, 47+48, 11+48, 10+48],
            "BDL": [47+48, 36+48, 0+48, 11+48],
        }

    def get_face_to_color(self):
        return {
            "U": colors["black"],
            "F": colors["red"],
            "R": colors["green"],
            "L": colors["blue"],
            "B": colors["orange"],
            "D": colors["white"],
            "X": colors["ignore"]
        }


def get_colorizer(name) -> BaseColorizer:
    """Returns the colorizer given as string implemented colorizers are:
    Megaminx, Megaminx-OLL, Pyraminx, Skewb, 3x3, 3x3-OLL, 2x2"""
    return {
        "Megaminx": MegaminxColorizer,
        "Megaminx-LL": MegaminxLLColorizer,
        "Megaminx-OLL": MegaminxOLLColorizer,
        "Pyraminx": PyraminxColorizer,
        "Skewb": SkewbColorizer,
        "Skewb-L2L": SkewbL2LColorizer,
        "5x5": FiveByFiveColorizer,
        "5x5-L2E": FiveByFiveL2EColorizer,
        "3x3": ThreeByThreeColorizer,
        "3x3-LL": ThreeByThreeLLColorizer,
        "3x3-OLL": ThreeByThreeOLLColorizer,
        "3x3-CMLL": ThreeByThreeCMLLColorizer,
        "3x3-ZBLS": ThreeByThreeZBLSColorizer,
        "2x2": TwoByTwoColorizer,
        "2x2-LL": TwoByTwoLLColorizer,
        "Octaminx": OctaminxColorizer,
        "Octaminx-L3T": OctaminxL3TColorizer,
        "Square-1": SquareOneColorizer
    }[name]()

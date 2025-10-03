import numpy as np
import re
import pathlib
from typing import Dict, List
from scipy.spatial.transform import Rotation
from collections import defaultdict
from .cube import Cube, Megaminx, Skewb, TwoByTwo, ThreeByThree, Pyraminx, Octaminx, OctaminxRotations

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
        stickers = []
        for firstFace in piece:
            stickers.append(firstFace + "".join(sorted([f for f in piece if f != firstFace])))
        return stickers
    
    def get_override_colors(self) -> Dict[str, str]:
        """Return a dictionary that maps from stickers to colors which defines the stickers that should always be a certain color. Use this to indicate parts of the visualization that can be ignored."""
        return dict()

    def get_sticker_colors_from_cube(self) -> Dict[str, str]:
        sticker_positions_to_color = {}
        face_to_color = self.get_face_to_color()
        for position, (piece, ori) in self.cube.pieces.items():
            sticker_positions = self.make_stickers_from_piece(position)
            for i in range(len(piece)):
                ival = (i + ori) % len(piece)
                if piece[i].isnumeric(): # special case for octaminx center pieces
                    continue
                sticker_positions_to_color[sticker_positions[ival]] = face_to_color[piece[i]]
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
            svg += f"<polygon fill='{sticker_colors[sticker_name]}' points='{poygon_str}'/>\n"
        svg += "</svg>"
        return svg
    
    def inverse(self, moves, path=None):
        moves = re.findall(r"[A-z]+'?\d?'?", moves)
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
        self.cube.scramble(" ".join([self.pre_moves, moves]))
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
        "3x3": ThreeByThree,
        "3x3-LL": ThreeByThreeLLColorizer,
        "3x3-OLL": ThreeByThreeOLLColorizer,
        "3x3-CMLL": ThreeByThreeCMLLColorizer,
        "2x2": TwoByTwoColorizer,
        "2x2-LL": TwoByTwoLLColorizer,
        "Octaminx": OctaminxColorizer,
        "Octaminx-L3T": OctaminxL3TColorizer,
    }[name]()

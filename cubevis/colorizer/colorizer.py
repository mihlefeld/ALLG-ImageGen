import re
from typing import Dict, List

import numpy as np

from cubevis.cube import Cube

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
    "orange": "#F28E2B",
}


class BaseColorizer:
    def __init__(self, cube: Cube, pre_moves="") -> None:
        self.vertices = np.zeros((0,))
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
        """Get a dictionary mapping from sticker name to polygon. Sticker name is side of sticker and then the other faces alphabetically sorted"""
        pass

    def get_face_to_color(self) -> Dict[str, str]:
        """A dictionary that has a face like F, U, R as input, and outputs the color"""
        pass

    def make_stickers_from_piece(self, piece) -> List[str]:
        non_num_piece = "".join([c for c in piece if not c.isnumeric()])
        last_number = "".join([c for c in piece if c.isnumeric()])
        stickers = []
        for firstFace in non_num_piece:
            stickers.append(
                firstFace
                + "".join(sorted([f for f in non_num_piece if f != firstFace]))
                + last_number
            )
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
            last_digit = piece[-1] if piece[-1].isnumeric() else ""
            piece_stickers = self.make_stickers_from_piece(non_numeric_piece)
            sticker_positions = self.make_stickers_from_piece(position)
            for i in range(len(non_numeric_piece)):
                ival = (i + ori) % len(non_numeric_piece)
                try:
                    if last_digit != "" and piece_stickers[i] + last_digit in override_pieces:
                        sticker_positions_to_color[sticker_positions[ival]] = (
                            override_pieces[piece_stickers[i] + last_digit]
                        )
                    elif piece_stickers[i] in override_pieces:
                        sticker_positions_to_color[sticker_positions[ival]] = (
                            override_pieces[piece_stickers[i]]
                        )
                    else:
                        sticker_positions_to_color[sticker_positions[ival]] = (
                            face_to_color[non_numeric_piece[i]]
                        )
                except:
                    pass
        for k, v in self.get_override_colors().items():
            sticker_positions_to_color[k] = v
        return sticker_positions_to_color

    def create_svg(self):
        style = "polygon { stroke: black; stroke-width: 0.5px; stroke-linejoin: round;}"
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">
<style>
{style}
</style>"""
        sticker_colors = self.get_sticker_colors_from_cube()
        polygons = self.get_polygons()
        for sticker_name, polygon_picking in polygons.items():
            poygon_str = " ".join(
                [f"{a:.2f} {b:.2f}" for (a, b) in self.vertices[polygon_picking]]
            )
            try:
                svg += f"<polygon fill='{sticker_colors[sticker_name]}' points='{poygon_str}'/>\n"
            except:
                # TODO: log warning
                pass
        svg += "</svg>"
        return svg

    def inverse(self, moves, path=None, ref_rot_override=None):
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
        rotation = self.cube.to_reference_rotation(
            scramble=False, override_piece=ref_rot_override
        )
        if rotation != "":
            rotation = (
                " ".join(
                    [
                        (m[:-1] if m[-1] == "'" else m + "'")
                        for m in rotation.split(" ")
                    ][::-1]
                )
                + " "
            )

        self.scramble(rotation + scramble, path)
        return rotation + scramble

    def scramble(self, moves, path=None):
        self.cube.scramble(" ".join([self.pre_moves, moves]).strip())
        svg = self.create_svg()
        if path is None:
            return svg
        with open(path, "w") as file:
            file.write(svg)

    def needs_invert(self):
        return True

    def get_equivalences(self):
        return ""

    def get_prune_search_subgroup(self):
        return ""

    def get_definitions(self):
        return self.cube.mdefs

    def get_pre_adjust(self):
        return "U"

    def get_post_adjust(self):
        return "U"



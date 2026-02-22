import os
from cubevis.colorizer import *
from pathlib import Path

def testing():
    colorizers = [FiveByFiveSpecialColorizer()]
    # for colorizer in colorizers:
    #     moves = list(colorizer.cube.moves.keys())
    #     colorizer_name = type(colorizer).__name__
    #     for move in moves:
    #         move_name = f"{move}_upper"
    #         if move.lower() == move:
    #             move_name = f"{move}_lower"
    #         moves_dir = Path(f"tests/move_images/{colorizer_name}/{move_name}")
    #         os.makedirs(moves_dir, exist_ok=True)
    #         for n in range(1, colorizer.cube.max_cycles[move]):
    #             colorizer.scramble(move + str(n), moves_dir / f"{n}.svg")
    # ff = colorizers[0]
    # ff.scramble("x U r U2 x r U2 r U2' r' U2 l U2 3r' U2' r U2 r' U2' r' U x'", "test.svg")
    # ff.inverse("x U r U2 x r U2 r U2' r' U2 l U2 3r' U2' r U2 r' U2' r' U x'", "test-i.svg")
    col = FiveByFiveHoyaColorizer()
    col.cube.scramble("3r' r")
    print(col.cube.pieces_to_cycles("m"))
    col.scramble("m' U2 m", "test.svg")

if __name__ == "__main__":
    testing()
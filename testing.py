import os
from cubevis.colorizer.fto import FTOFullColorizer, FTOBTLTColorizer, FTOLBTColorizer, FTOLTColorizer, FTOFTLTColorizer
from pathlib import Path

def testing():
    colorizers = [FTOFTLTColorizer()]
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
    col = colorizers[0]
    col.scramble("BR U BR' U' R' F BR' F' BR R U'", "test.svg") 
    #col.scramble("F' Rw R' U' Rw' F R F BR U' BR' U'", "test1.svg") 
    #col.scramble("B' U' B L U F' U' F L' B' U B", "test2.svg") 
    #col.scramble("BR U BR'", "test2.svg") 


if __name__ == "__main__":
    testing()
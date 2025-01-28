import os
from cubevis.colorizer import *
from pathlib import Path

def testing():
    colorizers = [OctaminxColorizer()]
    for colorizer in colorizers:
        moves = list(colorizer.cube.moves.keys())
        colorizer_name = type(colorizer).__name__
        for move in moves:
            move_name = f"{move}_upper"
            if move.lower() == move:
                move_name = f"{move}_lower"
            moves_dir = Path(f"tests/move_images/{colorizer_name}/{move_name}")
            os.makedirs(moves_dir, exist_ok=True)
            for n in range(1, colorizer.cube.max_cycles[move]):
                colorizer.scramble(move + str(n), moves_dir / f"{n}.svg")
    
    oc = OctaminxColorizer()
    # t' xr' y"
    oc.scramble("xr' t eU' eR eU' eR' eRw eU eR' eU' eR eRw' eU' t y'", "test1.svg")
    print(oc.cube.pieces_to_cycles("S"))
    print()

if __name__ == "__main__":
    testing()
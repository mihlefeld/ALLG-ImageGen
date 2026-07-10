from cubevis.colorizer.colorizer import BaseColorizer
from cubevis.colorizer.fivebyfive import FiveByFiveColorizer, FiveByFiveHoyaColorizer, FiveByFiveL2EColorizer
from cubevis.colorizer.fto import FTOColorizer, FTOL3CColorizer, FTOL3TColorizer, FTOL6XColorizer, FTOBTLTColorizer, FTOLBTColorizer
from cubevis.colorizer.megaminx import MegaminxColorizer, MegaminxLLColorizer, MegaminxOLLColorizer, MegaminxWVColorizer, MegaminxZBLSColorizer
from cubevis.colorizer.pyraminx import PyraminxColorizer
from cubevis.colorizer.skewb import SkewbColorizer, SkewbL2LColorizer
from cubevis.colorizer.sq1 import SquareOneColorizer, SquareOneOBLColorizer
from cubevis.colorizer.threebythree import ThreeByThreeCMLLColorizer, ThreeByThreeColorizer, ThreeByThreeLLColorizer, ThreeByThreeOLLColorizer, ThreeByThreeZBLSColorizer
from cubevis.colorizer.twobytwo import TwoByTwoColorizer, TwoByTwoLLColorizer


def get_colorizer(name) -> BaseColorizer:
    """Returns the colorizer given as string implemented colorizers are:
    Megaminx, Megaminx-OLL, Pyraminx, Skewb, 3x3, 3x3-OLL, 2x2"""
    options = {
        "Megaminx": MegaminxColorizer,
        "Megaminx-LL": MegaminxLLColorizer,
        "Megaminx-OLL": MegaminxOLLColorizer,
        "Megaminx-ZBLS": MegaminxZBLSColorizer,
        "Megaminx-WV": MegaminxWVColorizer,
        "Pyraminx": PyraminxColorizer,
        "Skewb": SkewbColorizer,
        "Skewb-L2L": SkewbL2LColorizer,
        "5x5": FiveByFiveColorizer,
        "5x5-L2E": FiveByFiveL2EColorizer,
        "5x5-Hoya": FiveByFiveHoyaColorizer,
        "3x3": ThreeByThreeColorizer,
        "3x3-LL": ThreeByThreeLLColorizer,
        "3x3-OLL": ThreeByThreeOLLColorizer,
        "3x3-CMLL": ThreeByThreeCMLLColorizer,
        "3x3-ZBLS": ThreeByThreeZBLSColorizer,
        "2x2": TwoByTwoColorizer,
        "2x2-LL": TwoByTwoLLColorizer,
        "FTO": FTOColorizer,
        "FTO-L3T": FTOL3TColorizer,
        "FTO-L3C": FTOL3CColorizer,
        "FTO-L6X": FTOL6XColorizer,
        "FTO-BTLT": FTOBTLTColorizer,
        "FTO-LBT": FTOLBTColorizer,
        "Square-1": SquareOneColorizer,
        "Square-1-OBL": SquareOneOBLColorizer,
    }
    if name not in options:
        raise KeyError(f"Puzzle must be one of {', '.join(options.keys())}")
    return options[name]()
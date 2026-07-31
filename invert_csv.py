import polars as pl
from cubevis.cube import FTO
from cubevis.colorizer import FTOLTColorizer
from cubevis.scripts.images import clean_alg_fto
df = pl.read_csv("data/FTO/LL/solutions_crude.txt", separator=";")
fto = FTOLTColorizer()
inverses = []
replacements = [
    ("K'", "R' F' r U r' R U' r' F r"),
    ("W'", "r' U' F' U F r"),
    ("C'", "br U BR' U' BR br' U BR U' BR'"),
    ("K", "r' F' r U R' r U' r' F R"),
    ("W", "r' F' U' F U r"),
    ("C", "BR U BR' U' br BR' U BR U' br'"),
]
for alg, in df.iter_rows():
    inv = alg
    #inv = fto.inverse(alg.replace("(", "").replace(")", ""))
    for key, repl in replacements:
        inv = inv.replace(key, repl)
    inverses.append(inv)
df = df.select(Algset=pl.lit("LL"), Group=pl.lit("All"), Name=pl.arange(1, len(inverses) + 1), Algs=pl.Series(inverses))
df.write_csv("data/FTO/LL/ftoll.csv")
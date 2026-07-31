import polars as pl
import re

def convert_to_eif(alg: str):
    br_count = len(re.findall("(BR)|(br)", alg))
    f_count = len(re.findall("F", alg))
    if alg.startswith("{"):
        return alg
    if br_count >= f_count:
        replacements = {
            "BR": "R",
            "br": "r",
            "F": "L",
            "U": "U",
            "R": "F",
            "L": "BL",
            "B": "BR",
            "BL": "B",
        }
        prefix = "{U,R} "
    else:
        replacements = {
            "F": "R",
            "R": "BR",
            "BR": "B",
            "U": "U",
            "L": "F",
            "B": "BL",
            "BL": "L",
        }
        prefix = "{U,L} "

    pattern = re.compile("|".join(sorted(replacements, key=len, reverse=True)))
    converted = pattern.sub(lambda match: replacements[match.group(0)], alg)

    replacements = {
        "Rw": "r"
    }
    pattern = re.compile("|".join(sorted(replacements, key=len, reverse=True)))
    converted = pattern.sub(lambda match: replacements[match.group(0)], converted)
    return prefix + converted

df = pl.read_csv("Alg Trainer Algs - FTO LT(2).csv")
new_algs_col = []
for algs in df['Algs']:
    eif_algs = []    
    for alg in algs.split("\n"):
        eif_algs.append(convert_to_eif(alg))
    new_algs_col.append("\n".join(eif_algs))

df.with_columns(Algs=pl.Series(new_algs_col)).write_csv("ftolt.csv")

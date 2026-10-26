import polars as pl
df_a = pl.read_csv("data/FTO/L3T/Alg Trainer Algs - FTO L3T.csv")
df_b = pl.read_csv("data/FTO/L3T/ftol3t.csv")
import json
with open("data/FTO/L3T/ftol3t.backup.json") as file:
    scram = json.load(file)
for i, (algs_a, algs_b) in enumerate(zip(df_a['Algs'], df_b['Algs'])):
    if algs_a != algs_b:
        print(i)
        scram['cases'][i]['solutions'] = []

with open("data/FTO/L3T/ftol3t.json", "w") as file:
    json.dump(scram, file)

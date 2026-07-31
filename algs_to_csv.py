from pathlib import Path
import polars as pl
import json
gen = json.loads(Path("data/FTO/LL/ftoll.json").read_text())

def solutions_with_movecount(sols):
    mc_sols = []
    sol_counts = []
    for sol in sols:
        sol = sol.strip()
        sol_count = len(sol.split())
        sol_counts.append(sol_count)
        sol = sol + f" [{sol_count}]"
        mc_sols.append(sol)
    return "\n".join(mc_sols), min(sol_counts)

cases = gen['cases']
table = []
for case in cases:
    sols, sol_count = solutions_with_movecount(case['solutions'])
    table.append(
        {
            "Algset": "LL",
            "Group": "All",
            "Name": case['index'],
            "Algs": sols,
            "Movecount": sol_count,
            "Setup": case['setup']
        }
    )

pl.DataFrame(table).write_csv("data/FTO/LL/ftoll.csv")
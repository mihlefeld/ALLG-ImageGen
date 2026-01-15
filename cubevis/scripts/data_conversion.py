import polars as pl
from pathlib import Path

def read_zbls_sheet(zbls_sheet: Path, out_path: Path):
    df = pl.read_csv(zbls_sheet, has_header=False)
    df = df.filter(pl.row_index() != 0)
    stacked_dfs = []
    for i in range(4):
        columns = [f"column_{5*i + j}" for j in [2, 4]]
        stacked_dfs.append(df.select(**{f"column_{i+1}": pl.col(c) for i, c in enumerate(columns)}, col=pl.lit(i), row=pl.row_index()))
    df = pl.concat(stacked_dfs)
    group_id = 1
    new_algs = []
    group_case_counter = 0
    for case1, case2, col, row in df.iter_rows():
        if row == 0:
            group_id = col + 1
            group_case_counter = 0
        elif case1 is None and case2 is None:
            group_case_counter = 0
            group_id += 4
        for case in [case1, case2]:
            if case is None:
                continue
            group_case_counter += 1
            new_algs.append(
                {
                    "Algset": "ZBLS",
                    "Group": f"F2L{group_id}",
                    "Name": f"F2L{group_id}-{group_case_counter}",
                    "Algs": case.strip(),
                    "group_id": group_id
                }
            )
        pass
    new_algs_df = pl.DataFrame(new_algs).sort("group_id", "Name").drop("group_id")
    new_algs_df.write_csv(out_path)

    print()


read_zbls_sheet(Path("data/3x3/ZBLS/ZBLS - FR.csv"), Path("data/3x3/ZBLS/3x3zbls.csv"))
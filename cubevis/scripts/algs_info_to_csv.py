import argparse
import json
import pandas as pd
from pathlib import Path
import re

def main(input_path: Path, groups_path: Path, algsets_path: Path, output_path: Path):
    with open(input_path) as file:
        algs_info = json.load(file)
    with open(groups_path) as file:
        groups_info = json.load(file)
    with open(algsets_path) as file:
        algsets_info = json.load(file)
    group_to_algset = {}
    for algset, groups in algsets_info.items():
        for group in groups:
            group_to_algset[group.replace("Group ", "")] = algset
        
    case_to_group = {}
    for group, cases in groups_info.items():
        group = group.replace("Group ", "")
        for case_id in cases:
            case_to_group[case_id] = group
    
    new_df = {
        "Algset": [],
        "Group": [],
        "Name": [],
        "Algs": []
    }
    for case_id, info in algs_info.items():
        algs = re.sub(r"[\(\)]", "", "\n".join(info['a']))
        new_df["Algs"].append(algs)
        new_df['Name'].append(info['name'])
        new_df['Group'].append(case_to_group[int(case_id)])
        new_df['Algset'].append(group_to_algset[case_to_group[int(case_id)]])

    df = pd.DataFrame(new_df)
    df.to_csv(output_path.as_posix(), index=False)



if __name__ == "__main__":
    main()
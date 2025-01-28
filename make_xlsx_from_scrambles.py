import argparse
import json
import pathlib
import pandas as pd
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    input_file = pathlib.Path(args.input)
    output_file = pathlib.Path(args.output)
    with open(input_file) as file:
        scrambles_js = json.load(file)
    
    new_df = {}
    for k, v in scrambles_js.items():
        column_name = f"Unnamed: {(int(k) - 1) * 2 + 1}"
        if len(v) < 10:
            v = v + [pd.NA] * (10 - len(v))
        new_df[column_name] = [pd.NA] + v

    df = pd.DataFrame(new_df)
    df.to_excel(output_file)

main()
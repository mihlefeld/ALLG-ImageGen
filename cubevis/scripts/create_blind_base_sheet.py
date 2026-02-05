import polars as pl
from collections import defaultdict
import json
from pathlib import Path

def main():
    case_id = 1
    algs_info = defaultdict(dict)
    groups_info = defaultdict(list)
    algsets_info = defaultdict(list)
    combined_svgs = {}
    scrambles = {}
    selected_algsets = {}
    output_dir = Path(f"data/3x3/BLD/UF")

    def save_json(obj, filename):
        with open(filename, 'w', encoding="UTF-8") as file:
            json.dump(obj, file, ensure_ascii=False)

    def make_algs(alg_sheet, buffer, case_id):

        edges = len(buffer) == 2
        col_0 = pl.col(alg_sheet.columns[0])

        if not edges:
            letter_to_sticker = {
                "A": "UBL",
                "B": "UBR",
                "D": "UFL",
                "C": "UFR",
                "I": "FUL",
                "J": "FUR",
                "K": "FDR",
                "L": "FDL",
                "M": "RUF",
                "N": "RUB",
                "O": "RDB",
                "P": "RDF",
                "Q": "BUR",
                "R": "BUL",
                "S": "BDL",
                "T": "BDR",
                "E": "LUB",
                "F": "LUF",
                "G": "LDF",
                "H": "LDB",
                "U": "DFL",
                "V": "DFR",
                "W": "DBR",
                "X": "DBL",
            }
            pieces = [
                "AER",
                "BNQ",
                "CJM",
                "DFI",
                "ULG",
                "VKP",
                "WOT",
                "XSH"
            ]
        else: 
            letter_to_sticker = {
                "A": "UB",
                "B": "UR",
                "C": "UF",
                "D": "UL",
                "I": "FU",
                "J": "FR",
                "K": "FD",
                "L": "FL",
                "M": "RU",
                "N": "RB",
                "O": "RD",
                "P": "RF",
                "Q": "BU",
                "R": "BL",
                "S": "BD",
                "T": "BR",
                "E": "LU",
                "F": "LF",
                "G": "LD",
                "H": "LB",
                "U": "DF",
                "V": "DR",
                "W": "DB",
                "X": "DL",
            }
            pieces = [
                "AQ",
                "BM",
                "CI",
                "DE",
                "UK",
                "VO",
                "WS",
                "XG",
                "LF",
                "JP",
                "RH",
                "TN"
            ]
        (output_dir / "pic").mkdir(exist_ok=True, parents=True)
        stickers = []
        for i, piece in enumerate(pieces):
            for letter in piece:
                stickers.append((letter, i))
        stickers = sorted(stickers)
        bld_data = {
            "Algset": [],
            "Group": [],
            "Name": [],
            "Algs": []
        }
        for a_letter, a_piece in stickers:
            for b_letter, b_piece in stickers:
                if a_piece == b_piece:
                    continue
                group = a_letter
                group = f"{buffer} {a_letter}"
                a_sticker = letter_to_sticker[a_letter]
                b_sticker = letter_to_sticker[b_letter]
                try:
                    algs = alg_sheet.filter(col_0.str.strip_chars() == b_sticker)[a_sticker][0]
                except:
                    continue
                algs: str = alg_sheet.filter(col_0.str.strip_chars() == b_sticker)[a_sticker][0]
                bld_data["Algset"].append(buffer)
                bld_data["Group"].append(group)
                bld_data["Name"].append(a_letter + b_letter)
                bld_data["Algs"].append(algs)
                svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40.0 30.0">
        <text x="5" y="12.5" textLength="30" line-height="15" font-family="'Titilium Web', sans-serif">{a_sticker}</text>
        <text x="5" y="27.5" textLength="30" line-height="15" font-family="'Titilium Web', sans-serif">{b_sticker}</text>
        </svg>"""
                (output_dir / "pic" / f"{case_id}.svg").write_text(svg)
                algs_info[str(case_id)]["a"] = algs.splitlines()
                algs_info[str(case_id)]["name"] = a_letter + b_letter
                algs_info[str(case_id)]["group"] = group
                algs_info[str(case_id)]["algset"] = buffer
                algs_info[str(case_id)]["s"] = a_letter + b_letter
                groups_info[group].append(case_id)
                if group not in algsets_info[buffer]:
                    algsets_info[buffer].append(group)
                selected_algsets[buffer] = True
                combined_svgs[str(case_id)]  = svg
                scrambles[str(case_id)] = [a_letter + b_letter]
                case_id += 1
        
        (output_dir / f"_len_{len(algs_info.items())}").write_text("")
        return case_id

    edge_buffers = ["UF", "UB", "UR", "UL", "DF", "DB", "FR", "FL", "DR", "DL"]
    corner_buffers = ["UFR", "UFL", "UBL", "UBR", "DFR", "DFL"]

    for buffer in edge_buffers:
        sheet = pl.read_excel("data/3x3/BLD/elliot.xlsx", sheet_name=buffer)
        case_id = make_algs(sheet, buffer, case_id)
    save_json(algs_info, output_dir / 'algs_info.json')
    save_json(scrambles, output_dir / 'scrambles.json')
    save_json(algsets_info, output_dir / 'algsets_info.json')
    save_json(groups_info, output_dir / 'groups_info.json')
    save_json(selected_algsets, output_dir / 'selected_algsets.json')
    save_json(combined_svgs, output_dir / "combined.json")

    case_id = 1
    algs_info = defaultdict(dict)
    groups_info = defaultdict(list)
    algsets_info = defaultdict(list)
    combined_svgs = {}
    scrambles = {}
    selected_algsets = {}
    output_dir = Path(f"data/3x3/BLD/UFR")
    for buffer in corner_buffers:
        sheet = pl.read_excel("data/3x3/BLD/elliot.xlsx", sheet_name=buffer)
        case_id = make_algs(sheet, buffer, case_id)
    save_json(algs_info, output_dir / 'algs_info.json')
    save_json(scrambles, output_dir / 'scrambles.json')
    save_json(algsets_info, output_dir / 'algsets_info.json')
    save_json(groups_info, output_dir / 'groups_info.json')
    save_json(selected_algsets, output_dir / 'selected_algsets.json')
    save_json(combined_svgs, output_dir / "combined.json")

if __name__ == "__main__":
    main()
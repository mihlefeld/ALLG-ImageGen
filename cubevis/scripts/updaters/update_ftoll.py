"""
Update ftoll.csv from the "FTO Nautilus LL" Google Sheet.

Only the tabs T0-T5, H1-H10, D1-D16 and C1-C4 are read.
Per tab ("group") the sheet has blocks of  Name | Image | Algs | STM | Cost | Comment
(several blocks may sit side by side).  A case starts on the row where the Name
column holds e.g. "T1o+"; every non-empty cell in that block's Algs column from
there until the next case name is one alg of that case.

CSV columns:  Algset, Group, Name, Algs     (Algs = one alg per line, "\n"-joined)

Usage
-----
    pip install openpyxl
    python update_ftoll.py ftoll.csv                  # download sheet, write ftoll_updated.csv
    python update_ftoll.py ftoll.csv --in-place       # overwrite ftoll.csv (keeps ftoll.csv.bak)
    python update_ftoll.py ftoll.csv --dry-run        # only print the differences
    python update_ftoll.py ftoll.csv --xlsx sheet.xlsx   # use a local File > Download > .xlsx

The sheet must be viewable by "anyone with the link" for the automatic download;
otherwise download it as .xlsx yourself and use --xlsx.

Row order: existing rows keep their position in the CSV; cases that are new in the
sheet are inserted after the last case of their group; cases that no longer exist
in the sheet are removed. The Algs content always comes from the sheet.
"""
import argparse
import csv
import io
import re
import shutil
import sys
import urllib.error
import urllib.request

try:
    import openpyxl
except ImportError:
    sys.exit("This script needs openpyxl:  pip install openpyxl")

SHEET_ID = "15v0A0PipO8RcEeS7TFAaAv3dI1zBykaopkXQK_WnLo0"
EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

# initial letter of the group -> Algset name (also learned from the CSV, see below)
DEFAULT_ALGSETS = {
    "T": "LL Trapezoids",
    "H": "LL Headlights",
    "D": "LL Diamonds",
    "C": "LL Cat Chameleons",
}
TABS = (
    [f"T{i}" for i in range(0, 6)]
    + [f"H{i}" for i in range(1, 11)]
    + [f"D{i}" for i in range(1, 17)]
    + [f"C{i}" for i in range(1, 5)]
)
FIELDS = ["Algset", "Group", "Name", "Algs"]


# --------------------------------------------------------------------------- helpers
def clean(text):
    """Normalise a cell to a plain string (typographic characters -> ASCII)."""
    if text is None:
        return ""
    s = str(text)
    s = s.replace("\u00a0", " ").replace("\u2019", "'").replace("\u2032", "'")
    s = s.replace("\u2212", "-").replace("\u2013", "-")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s.strip()


def download_xlsx():
    print("Downloading sheet ...", file=sys.stderr)
    try:
        with urllib.request.urlopen(EXPORT_URL, timeout=120) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(
            f"Download failed (HTTP {e.code}). Make the sheet viewable by anyone with "
            "the link, or download it via File > Download > .xlsx and pass --xlsx FILE."
        )
    if not data.startswith(b"PK"):  # an HTML login page instead of an xlsx
        sys.exit(
            "Google returned a web page instead of the spreadsheet (sheet not public?). "
            "Download it as .xlsx manually and pass --xlsx FILE."
        )
    return io.BytesIO(data)


def find_blocks(rows):
    """Locate header row + blocks. Returns [(name_col, algs_col), ...] and header row index."""
    for r, row in enumerate(rows[:15]):
        cells = [clean(c).lower() for c in row]
        if "name" in cells and "algs" in cells:
            name_cols = [i for i, c in enumerate(cells) if c == "name"]
            blocks = []
            for k, nc in enumerate(name_cols):
                limit = name_cols[k + 1] if k + 1 < len(name_cols) else len(cells)
                algs = [i for i in range(nc + 1, limit) if cells[i] == "algs"]
                if algs:
                    blocks.append((nc, algs[0]))
            if blocks:
                return blocks, r
    return None, None


def parse_tab(ws, group):
    """Return [(case_name, [algs...]), ...] in sheet order (blocks left to right, rows top down)."""
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    blocks, header_row = find_blocks(rows)
    if not blocks:
        raise ValueError(f"tab {group}: could not find a 'Name' / 'Algs' header row")

    name_re = re.compile(rf"^{re.escape(group)}([a-z][+-]?)$", re.IGNORECASE)
    cases = []
    for name_col, algs_col in blocks:
        current = None
        for row in rows[header_row + 1:]:
            name = clean(row[name_col]) if name_col < len(row) else ""
            alg_cell = clean(row[algs_col]) if algs_col < len(row) else ""
            if name:
                m = name_re.match(name)
                if m:
                    current = (group + m.group(1).lower(), [])
                    cases.append(current)
                else:  # stray text in the name column ends the current case
                    current = None
            if current is not None and alg_cell:
                current[1].extend(a.strip() for a in alg_cell.split("\n") if a.strip())
    return cases


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="the (outdated) ftoll.csv")
    ap.add_argument("--xlsx", help="local .xlsx export of the sheet instead of downloading")
    ap.add_argument("-o", "--output", help="output path (default: <csv>_updated.csv)")
    ap.add_argument("--in-place", action="store_true", help="overwrite the input CSV (a .bak copy is kept)")
    ap.add_argument("--dry-run", action="store_true", help="only report differences, write nothing")
    args = ap.parse_args()

    # ---- read old csv
    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            sys.exit(f"Unexpected CSV header {reader.fieldnames}, expected {FIELDS}")
        old_rows = list(reader)
    old = {r["Name"]: r for r in old_rows}
    algsets = dict(DEFAULT_ALGSETS)
    for r in old_rows:  # keep whatever naming the CSV already uses
        algsets[r["Group"][0]] = r["Algset"]

    # ---- read sheet
    wb = openpyxl.load_workbook(args.xlsx or download_xlsx(), read_only=True, data_only=True)
    missing = [t for t in TABS if t not in wb.sheetnames]
    if missing:
        sys.exit(f"Tabs not found in the workbook: {', '.join(missing)}\nFound: {', '.join(wb.sheetnames)}")

    new = {}          # name -> (group, [algs])
    new_order = {}    # group -> [names in sheet order]
    problems = []
    for group in TABS:
        try:
            cases = parse_tab(wb[group], group)
        except ValueError as e:
            sys.exit(str(e))
        if not cases:
            sys.exit(f"Tab {group}: no cases found - aborting so the CSV is not damaged.")
        new_order[group] = []
        for name, algs in cases:
            if name in new:
                problems.append(f"{name}: appears more than once in tab {group} (first occurrence kept)")
                continue
            if not algs:
                problems.append(f"{name}: no algs found in the sheet")
            new[name] = (group, algs)
            new_order[group].append(name)

    # ---- merge, keeping the CSV's row order
    out_names = []
    seen = set()
    last_pos_in_group = {}
    for r in old_rows:
        if r["Name"] in new and r["Name"] not in seen:
            out_names.append(r["Name"])
            seen.add(r["Name"])
            last_pos_in_group[r["Group"]] = len(out_names) - 1
    added = []
    for group in TABS:  # insert new cases after the last case of their group
        for name in new_order[group]:
            if name in seen:
                continue
            added.append(name)
            seen.add(name)
            if group in last_pos_in_group:
                pos = last_pos_in_group[group] + 1
                out_names.insert(pos, name)
                for g, p in last_pos_in_group.items():
                    if p >= pos:
                        last_pos_in_group[g] = p + 1
                last_pos_in_group[group] = pos
            else:  # brand-new group: after the previous tab's rows
                idx = TABS.index(group)
                pos = 0
                for g in TABS[:idx]:
                    if g in last_pos_in_group:
                        pos = max(pos, last_pos_in_group[g] + 1)
                out_names.insert(pos, name)
                for g, p in last_pos_in_group.items():
                    if p >= pos:
                        last_pos_in_group[g] = p + 1
                last_pos_in_group[group] = pos

    out_rows = []
    changed, unchanged = [], 0
    for name in out_names:
        group, algs = new[name]
        row = {"Algset": algsets.get(group[0], old.get(name, {}).get("Algset", "")),
               "Group": group, "Name": name, "Algs": "\n".join(algs)}
        out_rows.append(row)
        if name in old:
            if old[name]["Algs"].replace("\r\n", "\n") != row["Algs"]:
                changed.append((name, old[name]["Algs"], row["Algs"]))
            else:
                unchanged += 1
    removed = [r["Name"] for r in old_rows if r["Name"] not in new]

    # ---- report
    print(f"Sheet cases: {len(new)}   old CSV rows: {len(old_rows)}   new CSV rows: {len(out_rows)}")
    print(f"unchanged: {unchanged}   changed: {len(changed)}   added: {len(added)}   removed: {len(removed)}")
    for name, o, n in changed:
        print(f"\n~ {name}\n    old: {o!r}\n    new: {n!r}")
    for name in added:
        print(f"\n+ {name}: {new[name][1]!r}")
    for name in removed:
        print(f"\n- {name} (no longer in the sheet)")
    for p in problems:
        print(f"WARNING: {p}")

    if args.dry_run:
        return
    target = args.csv if args.in_place else (args.output or re.sub(r"(\.csv)?$", "_updated.csv", args.csv, count=1))
    if args.in_place:
        shutil.copyfile(args.csv, args.csv + ".bak")
    with open(target, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print(f"\nWrote {target}")


if __name__ == "__main__":
    main()

from pathlib import Path

start = Path("data\Sq1\OBL\pic\_batch_solver_input.txt")

def read_input(path: Path):
    return path.read_text().splitlines()[1:-1]

interm = Path("test.txt")

def write_lines(path: Path, lines):
    path.write_text("\n".join(["["] + lines + ["]"]))


def bin_search(lines, left, right, right_with_dupe):
    write_lines(interm, lines[:right])
    print(f"{right} lines written {left} {right}")
    bs_count = int(input("Batch solver count:"))
    middle = (left + right) // 2
    if left == right:
        print(f"Dupe found with line {lines[left]}")
        exit()
    if bs_count < right:
        bin_search(lines, left, middle, right)
    if bs_count == right:
        bin_search(lines, right, (right + right_with_dupe) // 2, right_with_dupe)
    
lines =read_input(start)
bin_search(lines, 0, len(lines), len(lines))
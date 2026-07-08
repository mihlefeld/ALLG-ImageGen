import typer 
import json
import shutil
import logging
from jinja2 import Environment, PackageLoader, select_autoescape
from cubevis.scripts.jsons import gen_jsons
from cubevis.scripts.images import gen_images
from cubevis.colorizer import get_colorizer
from cubevis.solver.solver import run_batch, BatchInput, SubgroupSpec, SortingSpec
from pathlib import Path


def full_pipeline(algset: str, colorizer_name: str, data: Path = Path('./data'), node_path: Path = Path("node"), alg_trainers: Path = Path("../Alg-Trainers")):
    puzzle = "-".join(colorizer_name.split("-")[:-1])
    colorizer = get_colorizer(colorizer_name)
    data_root = data / puzzle / algset
    pictures_root = data_root / "pic"
    csv_file = data_root / f"{puzzle.lower()}{algset.lower()}.csv"
    json_file = csv_file.with_suffix(".json")
    batch_solver_input = data_root / "pic" / "_batch_solver_input.txt"
    subgroups = []
    for row in colorizer.get_prune_search_subgroup().splitlines():
        subgroup = " ".join(row.split()[2:])
        prune, search = row.split()[:2]
        spec = SubgroupSpec(subgroup, prune, search)
        subgroups.append(spec)
    
    output = gen_images(colorizer_name, csv_file, pictures_root)
    num_cases = len(output['df'])
    inp = BatchInput(
        puzzle=colorizer.get_definitions(),
        ignore=colorizer.get_equivalences(),
        solve=batch_solver_input.read_text(),
        subgroups=subgroups,
    )
    def on_message(msg):
        mtype = msg.get("type")
        mval = msg.get("value")
        if mtype == "num-states":
            assert type(mval) == int
            if num_cases != mval:
                logging.root.warning("Number of states reported by batch solver doesn't match number of cases in algs csv file.")
                # TODO: implement finding the duplicates

    result = run_batch(inp, node_path=node_path, on_message=on_message)
    for case in result.cases:
        solutions = sorted(case.solutions, key=lambda x: len(x.split()))[:20]
        case.solutions = solutions
    with open(json_file, "w") as file:
        json.dump(result.to_dict(), file)

    gen_jsons(colorizer_name, json_file, csv_file, data_root)
    relevant_files = [
        "algs_info.json",
        "algsets_info.json",
        "combined.json",
        "groups_info.json",
        "scrambles.json",
        "selected_algsets.json"
    ]
    alg_trainer_name = f"{puzzle}-{algset}-Trainer"
    alg_trainer_path = alg_trainers / alg_trainer_name
    if alg_trainer_path.is_dir():
        for file in relevant_files:
            shutil.copy(data_root / file, alg_trainer_path / file)
    if not alg_trainer_path.is_dir():
        create_new_trainer(trainer_path=alg_trainer_path, data_root=data_root, relevant_files=relevant_files, puzzle=puzzle, algset=algset)
    
def create_new_trainer(trainer_path: Path, data_root: Path, relevant_files: list[str], puzzle: str, algset: str):
    env = Environment(
        loader=PackageLoader("cubevis.scripts"),
        autoescape=select_autoescape()
    )
    template_keys = {}
    template_keys['max_algs_per_row'] = input()
    template_keys['pre_rotations'] = input()
    template_keys['post_rotations'] = input()
    template_keys['pre_moves'] = input()
    template_keys['post_moves'] = input()
    template_keys['puzzle'] = puzzle
    template_keys['algset'] = algset
    algsinfo = env.get_template("algsinfo.js.jinja").render(**template_keys)
    index = env.get_template("index.html.jinja").render(**template_keys)
    trainer_path.mkdir()
    (trainer_path / "algsinfo.js").write_text(algsinfo)
    (trainer_path / "index.html").write_text(index)
    for file in relevant_files:
        shutil.copy(data_root / file, trainer_path / file)
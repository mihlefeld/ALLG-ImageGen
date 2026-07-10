from bs4 import BeautifulSoup
import polars as pl

with open("data/FTO/LBT/lbt-algs.html") as file:
    soup = BeautifulSoup(file)

groups = soup.find_all(attrs={"class": "header", "colspan": "4"})
data = []
algset = "LBT"
case_id = 1
for group in groups:
    print(group.text)
    group_name = group.text
    alg_row = group.parent.next_sibling.next_sibling.next_sibling
    case_algs = [alg_div.find_all(text=True, recursive=False) for alg_div in alg_row.children]
    for case in case_algs:
        algs = "\n".join([alg.strip() for alg in case if alg.strip() != ""])
        if algs.startswith("Uhh"):
            case_id += 1
            continue
        data.append({
            "Algset": algset,
            "Group": group_name,
            "Name": str(case_id),
            "Algs": algs,
        })
        case_id += 1
    print(algs)

pl.DataFrame(data).write_csv("data/FTO/LBT/ftolbt.csv")
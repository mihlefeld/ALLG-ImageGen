import polars as pl

oblsheet = pl.read_csv("data/Sq1/OBL/sq1oblsheet.csv")
case_names = oblsheet['Name']

obls = [
    dict(name="1C", hasmirror=False, corners=1, edges=0, hasnegative=True),
    dict(name="Cadj", hasmirror=False, corners=2, edges=0, hasnegative=True),
    dict(name="Copp", hasmirror=False, corners=2, edges=0, hasnegative=True),
    dict(name="3C", hasmirror=False, corners=3, edges=0, hasnegative=True),
    dict(name="ecPair", hasmirror=True, corners=1, edges=1, hasnegative=True),
    dict(name="ceArrow", hasmirror=True, corners=1, edges=1, hasnegative=True),
    dict(name="Gem", hasmirror=False, corners=1, edges=2, hasnegative=True),
    dict(name="ceKnight", hasmirror=True, corners=1, edges=2, hasnegative=True),
    dict(name="ecAxe", hasmirror=True, corners=1, edges=2, hasnegative=True),
    dict(name="Squid", hasmirror=False, corners=1, edges=2, hasnegative=True),
    dict(name="ceThumb", hasmirror=True, corners=1, edges=3, hasnegative=True),
    dict(name="ecBunny", hasmirror=True, corners=1, edges=3, hasnegative=True),
    dict(name="Shell", hasmirror=False, corners=2, edges=1, hasnegative=True),
    dict(name="ceBird", hasmirror=True, corners=2, edges=1, hasnegative=True),
    dict(name="Hazard", hasmirror=False, corners=2, edges=1, hasnegative=True),
    dict(name="ecYoshi", hasmirror=True, corners=2, edges=1, hasnegative=True),
    dict(name="ecKite", hasmirror=True, corners=2, edges=2, hasnegative=False),
    dict(name="ceCut", hasmirror=True, corners=2, edges=2, hasnegative=False),
    dict(name="T", hasmirror=False, corners=2, edges=2, hasnegative=True),
    dict(name="ecN", hasmirror=True, corners=2, edges=2, hasnegative=False),
    dict(name="Tie", hasmirror=False, corners=2, edges=2, hasnegative=True),
]

def makeVariations(obl):
    variations = [obl]
    if obl['hasmirror']:
        new_name = obl['name'][:2][::-1] + obl['name'][2:]
        variations.append(
            dict(name=new_name, hasmirror=obl['hasmirror'], corners=obl['corners'], edges=obl['edges'], hasnegative=obl['hasnegative'])
        )
    for obl in list(variations):
        if obl['hasnegative']:
            new_name = "-" + obl['name']
            variations.append(
                dict(name=new_name, hasmirror=obl['hasmirror'], corners=4-obl['corners'], edges=4-obl['edges'], hasnegative=obl['hasnegative'])
            )
    return variations

def translate_thumbs(name: str):
    if "Thumb" in name:
        name = name.replace("ce", "cee").replace("ec", "eec")
    return name

all_obls = []
all_obls_names = []
for obl_top in obls:
    top_corners = obl_top['corners']
    top_edges = obl_top['edges']
    for obl_bottom in obls: 
        bot_corners = obl_bottom['corners']
        bot_edges = obl_bottom['edges']
        if top_corners != bot_corners or top_edges != bot_edges:
            continue
        top_variations = makeVariations(obl_top)
        bot_variations = makeVariations(obl_bottom)
        for var_top in top_variations:
            for var_bot in bot_variations:
                if var_top['corners'] != var_bot['corners'] or var_top['edges']  != var_bot['edges']:
                    continue
                if not var_top['hasnegative'] and var_bot['name'][0] == '-':
                    continue
                if not var_bot['hasnegative'] and var_top['name'][0] == '-':
                    continue
                if var_top['hasnegative'] and not var_top['hasmirror'] and var_top['name'][0] == '-':
                    continue
                if var_top['name'][0] == '-' and  var_bot['name'][0] == '-':
                    continue
                all_obls.append((var_top, var_bot))
                case_name = f"{translate_thumbs(var_top['name'])}|{translate_thumbs(var_bot['name'])}"
                all_obls_names.append(case_name)
                if case_name not in case_names:
                    print(case_name)
for case_name in case_names:
    if case_name not in all_obls_names:
        print(f"EXTRA ALG {case_name}")
print(len(all_obls))
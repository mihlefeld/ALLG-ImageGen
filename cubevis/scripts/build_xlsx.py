import xlsxwriter
import polars as pl
from cubevis.scripts.images import clean_alg, clean_alg_fto
from cubevis.colorizer import FTOLTColorizer
from pathlib import Path
import cairosvg
import io
tmp = Path("data/tmp")
tmp.mkdir(exist_ok=True, parents=True)
col = FTOLTColorizer()
df = pl.read_csv("test.csv")
grouped = df.group_by("Algset", "Group", maintain_order=True).all()
workbook = xlsxwriter.Workbook("LT.xlsx")

header_format = workbook.add_format()
header_format.set_bold()
header_format.set_font_size(16)
header_format.set_align("vcenter")
header_format.set_align("center")
header_format.set_bg_color("#e06666")
header_format.set_color("white")

image_format = workbook.add_format()
image_format.set_align("center")
image_format.set_align("vcenter")

setup_format = workbook.add_format()
setup_format.set_color("white")
setup_format.set_bg_color("#666666")

worksheet = workbook.add_worksheet()
cases = grouped.with_columns(pl.col("Algs").list.len())['Algs'].max()
worksheet.set_column_pixels(1, cases+1, width=300)

max_algs = df.select(pl.col("Algs").str.split("\n").list.len()).max()[0, 'Algs']
for i, row in enumerate(grouped.iter_rows(named=True)):
    first_row = i * (max_algs + 3)
    worksheet.merge_range(first_row=first_row, first_col=0, last_row=first_row, last_col=len(row['Name']), data=row['Group'], cell_format=header_format)
    worksheet.set_row_pixels(first_row, height=40)
    worksheet.set_row_pixels(first_row + 1, height=300)
    worksheet.write(first_row + 2, 0, "Name")
    worksheet.write(first_row + 3, 0, "Setup", setup_format)
    for j, (name, algs, setup) in enumerate(zip(row['Name'], row['Algs'], row['Setup'])):
        worksheet.write(first_row + 2, j + 1, name)
        worksheet.write(first_row + 3, j + 1, setup, setup_format)
        for k, alg in enumerate(algs.split("\n")):
            worksheet.write(first_row + 4 + k, j + 1, alg)
        svg_path = tmp / f"{name}.svg"
        png_path = tmp / f"{name}.png"
        if not png_path.is_file():
            first_alg = algs.split("\n")[0]
            first_alg_clean = clean_alg_fto(clean_alg(first_alg, col.cube))
            inverse_alg = col.inverse(first_alg_clean, svg_path)
            cairosvg.svg2png(
                url=svg_path.as_posix(),
                write_to=png_path.as_posix(),
                output_width=500,
            )
        worksheet.insert_image(
            first_row + 1, 
            j + 1, 
            source=png_path.as_posix(), 
            options={
                "object_position": 1,
                "x_offset": 5,
                "y_offset": 0,
                "x_scale": 0.55,
                "y_scale": 0.55
            }
        )


workbook.close()
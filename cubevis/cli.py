import typer 
from cubevis.scripts.jsons import gen_jsons
from cubevis.scripts.images import gen_images
from cubevis.scripts.combine_scrambles import write_missing_scrambles, combine_scrambles
from cubevis.scripts.bin_search_dupes import bin_search_dupes

app = typer.Typer()

app.command("jsons")(gen_jsons)
app.command("images")(gen_images)
app.command("write-missing")(write_missing_scrambles)
app.command("combine-missing")(combine_scrambles)
app.command("find-duplicates")(bin_search_dupes)



if __name__ == "__main__":
    app()
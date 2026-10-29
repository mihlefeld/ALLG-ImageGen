import typer

from cubevis.scripts.bin_search_dupes import bin_search_dupes
from cubevis.scripts.combine_scrambles import (combine_scrambles,
                                               write_missing_scrambles)
from cubevis.scripts.full_pipeline import full_pipeline
from cubevis.scripts.images import gen_images
from cubevis.scripts.jsons import gen_jsons

app = typer.Typer()

app.command("full")(full_pipeline)
app.command("jsons")(gen_jsons)
app.command("images")(gen_images)
app.command("write-missing")(write_missing_scrambles)
app.command("combine-missing")(combine_scrambles)
app.command("find-duplicates")(bin_search_dupes)



if __name__ == "__main__":
    app()
import typer 
from cubevis.scripts.get_jsons import get_jsons
from cubevis.scripts.gen import gen_images

app = typer.Typer()

app.command("jsons")(get_jsons)
app.command("images")(gen_images)




if __name__ == "__main__":
    app()
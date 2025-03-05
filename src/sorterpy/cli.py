"""Console script for sorterpy."""
import sorterpy

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for sorterpy."""
    console.print("Replace this message by putting your code into "
               "sorterpy.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()

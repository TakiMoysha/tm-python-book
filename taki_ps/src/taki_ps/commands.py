import os
import pathlib

import typer

from taki_ps.settings import Settings

BASE_DIR = pathlib.Path(__file__).parent

cli = typer.Typer()


@cli.command()
def init():
    print("Starting...")


if __name__ == "__main__":
    cli()

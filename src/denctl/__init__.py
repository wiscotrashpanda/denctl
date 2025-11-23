import typer

app = typer.Typer()


@app.callback()
def callback():
    """denctl - 🦝 automation CLI"""
    pass


@app.command()
def hello(name: str = typer.Argument("World", help="Name to greet")):
    """Say hello to someone."""
    typer.echo(f"Hello {name}!")


def main() -> None:
    app()

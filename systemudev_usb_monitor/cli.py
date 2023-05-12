import os
import tomllib

import typer

from .main import Udev

app = typer.Typer()


@app.command("run")
def run():
    with open(
        "{}/systemudev-usb-monitor/config.toml".format(os.environ["XDG_CONFIG_HOME"]),
        "rb",
    ) as toml_file:
        config = tomllib.load(toml_file)

    Udev(config["devices"]).run()


if __name__ == "__main__":
    app()

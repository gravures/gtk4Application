#!/usr/bin/env python3
"""Helper script for meson project definition."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, NoReturn

import tomli


def read(file: Path, path: str) -> Any | None:
    """Returns property from a toml file."""
    with file.open("r") as strm:
        config = tomli.loads(strm.read())

    _path = path.split("/")
    for entry in _path[:-1]:
        config = config.get(entry, None)
        if config is None:
            return None
    return config.get(_path[-1], None)


def exit_with_error(message) -> NoReturn:
    print(f"readtoml.py: {message}", sys.stderr)
    sys.exit(1)


def main():
    root = os.environ.get("MESON_SOURCE_ROOT")
    if not root:
        exit_with_error("must be run from within a meson build script")

    file = Path(root) / "pyproject.toml"
    if not file.exists():
        exit_with_error(f"File not found: {file}")

    try:
        prop = read(file, sys.argv[1])
    except Exception as e:
        exit_with_error(f"error reading pyproject.toml, {e}")

    if prop:
        if isinstance(prop, dict):
            prop = json.dumps(prop)
        sys.stdout.write(prop)
    else:
        exit_with_error(f"property {sys.argv[1]} not found")

    sys.exit(0)


if __name__ == "__main__":
    main()

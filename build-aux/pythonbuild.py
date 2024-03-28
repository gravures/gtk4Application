#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import NoReturn

import setuptools


def exit_with_error(message) -> NoReturn:
    me = Path(__file__).name
    print(f"{me}: {message}", file=sys.stderr)
    sys.exit(1)


def find_packages(where: Path) -> set[str]:
    modules = set(setuptools.find_packages(where=where))
    modules.update(setuptools.find_namespace_packages(where=where, include=["*"]))
    return modules


def find_modules(root: str, where: str) -> list[str]:
    _where = Path(root) / where
    return [
        str(e.relative_to(_where))
        for p in find_packages(_where)
        for e in (_where / Path(*p.split("."))).glob("*.py")
    ]


def main():
    root = os.environ.get("MESON_SOURCE_ROOT")
    if not root:
        exit_with_error("must be run from within a meson build script")

    where = sys.argv[1] if len(sys.argv) > 1 else "src"
    modules = "\n".join(find_modules(root, where))
    sys.stdout.write(modules)
    sys.exit(0)


if __name__ == "__main__":
    main()

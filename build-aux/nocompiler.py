from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import NoReturn


def exit_with_error(message) -> NoReturn:
    me = Path(__file__).name
    print(f"{me}: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    root = os.environ.get("MESON_SOURCE_ROOT")
    if not root:
        exit_with_error("must be run from within a meson build script")

    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.is_file():
            with path.open("r") as stream:
                sys.stdout.write(stream.read())
            sys.exit(0)
        else:
            exit_with_error(f"'{path}' is not an existing file")
    else:
        exit_with_error("must specify a file as argument")


if __name__ == "__main__":
    main()

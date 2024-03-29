#!/usr/bin/env python3
# Copyright 2024 Gilles Coissac
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import ClassVar, NoReturn, Self

from cairosvg import svg2png
from PIL import Image


# TODO: Handles double template small / large
# TODO: Handles different image formats for template


class IconGenerator:
    sizes: ClassVar[tuple[int, ...]] = ()
    formats: ClassVar[tuple[str, ...]] = ("png", "svg")

    def __new__(cls, template: Path, app_name: str, subdir: Path) -> Self:
        if cls is IconGenerator:
            if sys.platform == "darwin":
                cls = OsxIconGenerator
            elif "win" in sys.platform:
                cls = WindowsIconGenerator
            elif sys.platform.startswith("linux"):
                cls = LinuxIconGenerator
            else:
                raise RuntimeError("Unsupported platform")
        return object.__new__(cls)  # type: ignore

    def __init__(self, template: Path, app_name: str, subdir: Path) -> None:
        if not template.is_file():
            raise ValueError(f"{template.name} does not exist")

        if template.suffix not in (".svg", ".png"):
            raise ValueError(f"template must be svg or png, not {template.suffix}")

        self.template: Path = template
        self.subdir: Path = subdir
        self.package: Path = subdir
        self.app_name: str = app_name

    def ensure_path(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def generate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            if self.template.suffix == ".svg":
                template = Path(tmp) / f"{self.template.stem}.png"
                svg2png(
                    url=str(self.template),
                    write_to=str(template),
                    output_width=max(*self.sizes),
                    output_height=max(*self.sizes),
                )
            else:
                template = self.template

            img = Image.open(template)

            for size in self.sizes:
                img_rsz = img.resize(size=(size, size), resample=Image.LANCZOS)
                self.save_icon(self.app_name, size, img_rsz)

        self.pack(self.package)

    def pack(self, package: Path) -> None:
        return None

    def save_icon(self, name: str, size: int, img: Image.Image) -> None:
        return None


class OsxIconGenerator(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 32, 64, 128, 256, 512, 1024)

    def __init__(self, template: Path, app_name: str, subdir: Path) -> None:
        super().__init__(template, app_name, subdir)
        self.package = self.subdir / f"{self.app_name}.iconset"
        self.ensure_path(self.package)

    def save_icon(self, name: str, size: int, img: Image.Image) -> None:
        img.save(self.package / f"icon_{size}x{size}.png", bitmap_format="png")
        img.save(self.package / f"icon_{size // 2}x{size // 2}@2x.png", bitmap_format="png")

    def pack(self, package: Path) -> None:
        if iconutil := shutil.which("iconutil"):
            args = [
                iconutil,
                "-c",
                "icns",
                str(package),
                "-o",
                str(self.subdir / f"{self.app_name}.icns"),
            ]
            subprocess.run(args, shell=False, check=True, capture_output=True)  # noqa: S603
        else:
            raise OSError("iconutil program not found")


class LinuxIconGenerator(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 22, 24, 32, 36, 48, 64, 72, 96, 128, 192, 256, 512)

    def __init__(self, template: Path, app_name: str, subdir: Path) -> None:
        super().__init__(template, app_name, subdir)
        self.package = self.subdir / "hicolor"

    def save_icon(self, name: str, size: int, img: Image.Image) -> None:
        filepath = self.package / f"{size}x{size}" / "apps" / f"{name}.png"
        self.ensure_path(filepath.parent)
        img.save(filepath, bitmap_format="png")

    def pack(self, package: Path) -> None:
        return None


class WindowsIconGenerator(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 32, 48, 256)

    def save_icon(self, name: str, size: int, img: Image.Image) -> None:
        return NotImplemented


def exit_with_error(message) -> NoReturn:
    me = Path(__file__).name
    print(f"{me}: {message}", file=sys.stderr)
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=Path(__file__).stem,
        description="Generate application icons from an icon template file (svg or bitmap)",
    )
    parser.add_argument("template", help="icon template input file")
    parser.add_argument("appname", help="application name")
    parser.add_argument("subdir", help="output directory")

    return parser.parse_args()


def main():
    args = parse_args()
    try:
        gen = IconGenerator(
            Path(args.template),
            app_name=args.appname,
            subdir=Path(args.subdir),
        )
        gen.generate()
    except Exception as e:
        exit_with_error(f"error generating icons: {e}")
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

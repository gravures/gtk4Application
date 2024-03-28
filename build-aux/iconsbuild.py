#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from re import sub
from typing import ClassVar, NoReturn

from cairosvg import svg2png
from PIL import Image


class IconGenerator(ABC):
    sizes: ClassVar[tuple[int, ...]] = ()
    formats: ClassVar[tuple[str, ...]] = ("png", "svg")

    def __init__(self, template: Path, app_name: str, subdir: Path) -> None:
        if not template.is_file():
            raise ValueError(f"{template.name} does not exist")

        if template.suffix not in (".svg", ".png"):
            raise ValueError(f"template must be svg or png, not {template.suffix}")

        self.template: Path = template
        self.subdir: Path = subdir
        self.app_name = app_name

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

    @abstractmethod
    def save_icon(self, name: str, size: int, img: Image.Image) -> None: ...


class Osx(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 32, 64, 128, 256, 512, 1024)


class Linux(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 22, 24, 32, 36, 48, 64, 72, 96, 128, 192, 256, 512)

    def save_icon(self, name: str, size: int, img: Image.Image) -> None:
        filepath = self.subdir / "hicolor" / f"{size}x{size}" / "apps" / f"{name}.png"
        img.save(filepath, bitmap_format="png")


class Windows(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 32, 48, 256)

    def save_icon(self, name: str, size: int, img: Image.Image) -> None:
        return NotImplemented


def icon_generator_factory(template: Path, output: Path) -> IconGenerator:
    if sys.platform == "linux":
        return Linux(template, output)
    if sys.platform == "darwin":
        return Osx(template, output)
    if sys.platform == "win32":
        return Windows(template, output)
    raise RuntimeError("Unsupported platform")


def exit_with_error(message) -> NoReturn:
    me = Path(__file__).name
    print(f"{me}: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    src_root = os.environ.get("MESON_SOURCE_ROOT")
    build_root = os.environ.get("MESON_BUILD_ROOT")
    subdir = os.environ.get("MESON_SUBDIR")

    if not all((src_root, build_root, subdir)):
        exit_with_error("must be run from within a meson build script")

    if len(sys.argv) > 1:
        template = Path(sys.argv[1])
        app_name = sys.argv[2]
        subdir = Path(sys.argv[3])
        try:
            gen = icon_generator_factory(template, app_name=app_name, output=subdir)
            gen.generate()
        except Exception as e:
            exit_with_error(f"error generating icons: {e}")
    else:
        exit_with_error("must specify a file as argument")

    sys.exit(0)


if __name__ == "__main__":
    main()

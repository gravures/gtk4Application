#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, NoReturn, Self

from cairosvg import svg2png
from PIL import Image


# TODO: Handles double template small / large
# TODO: Handles different image formats for template


class IconGenerator(ABC):
    sizes: ClassVar[tuple[int, ...]] = ()
    formats: ClassVar[tuple[str, ...]] = ("png", "svg")

    def __new__(cls, template: Path, app_name: str, subdir: Path) -> Self:
        if cls is IconGenerator:
            if sys.platform == "darwin":
                cls = Osx
            elif "win" in sys.platform:
                cls = Windows
            elif sys.platform.startswith("linux"):
                cls = Linux
            else:
                raise RuntimeError("Unsupported platform")
        return object.__new__(cls)

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

    @abstractmethod
    def pack(self, package: Path) -> None: ...

    @abstractmethod
    def save_icon(self, name: str, size: int, img: Image.Image) -> None: ...


class Osx(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 32, 64, 128, 256, 512, 1024)

    def __init__(self, template: Path, app_name: str, subdir: Path) -> None:
        super().__init__(template, app_name, subdir)
        self.package = self.subdir / f"{self.name}.iconset"
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
                str(self.subdir / f"{self.name}.icns"),
            ]
            subprocess.run(args, shell=False, check=True, capture_output=True)
        else:
            raise OSError("iconutil program not found")


class Linux(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 22, 24, 32, 36, 48, 64, 72, 96, 128, 192, 256, 512)

    def __init__(self, template: Path, app_name: str, subdir: Path) -> None:
        super().__init__(template, app_name, subdir)
        self.package = self.subdir / "hicolor"

    def save_icon(self, name: str, size: int, img: Image.Image) -> None:
        filepath = self.package / f"{size}x{size}" / "apps" / f"{name}.png"
        self.ensure_path(filepath.parent)
        img.save(filepath, bitmap_format="png")

    def pack(self) -> None:
        return None


class Windows(IconGenerator):
    sizes: ClassVar[tuple[int, ...]] = (16, 32, 48, 256)

    def save_icon(self, name: str, size: int, img: Image.Image) -> None:
        return NotImplemented


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
            gen = IconGenerator(template, app_name=app_name, output=subdir)
            gen.generate()
        except Exception as e:
            exit_with_error(f"error generating icons: {e}")
    else:
        exit_with_error("must specify a file as argument")

    sys.exit(0)


if __name__ == "__main__":
    main()

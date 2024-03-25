# Python Gtk4 Application Example

A example for building a cross-platform [libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/index.html) and [Gtk4](https://docs.gtk.org/gtk4/index.html) application in python.

## Requirements

* micromamba
* conda-lock


## Building

```
conda-lock lock -f pyproject.toml
micromamba create --always-copy --prefix ./.venv --file conda-lock.yml
```

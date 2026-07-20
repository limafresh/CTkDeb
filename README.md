# CTkDeb

![Static Badge](https://img.shields.io/badge/No-PyInstaller-blue?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/Simple-GUI-blue?style=for-the-badge)

<p align="center">
    <img src="https://raw.githubusercontent.com/limafresh/CTkDeb/main/ctkdeb/icon.png" width="100" height="100">
</p>

The easiest way to create a DEB of your CustomTkinter project! You can create a small DEB without deep packaging experience.

## Install

```bash
pip install "CTkDeb[gui] @ git+https://github.com/limafresh/CTkDeb.git"
```

## Run

Run this in the project folder (relative to which the paths in the config are specified)

```
ctkdeb-gui
```

## GUI

![Screenshot](https://raw.githubusercontent.com/limafresh/CTkDeb/main/screenshot.png)

## CLI

```
ctkdeb config.json
```

Optional arguments:

- `--project-folder <path>`: if you run CTkDeb not from the project folder
- `--desktop-entry <path>`: if you want to put a ready-made .desktop file in the package, and not one generated from a JSON config

## Python

```python
from ctkdeb.packager import Packager

packager = Packager("config.json")
packager.create_deb()
```

Optional arguments:

- **project_folder**: *str*
- **desktop_entry**: *str*

## Other

App icon: Claude Sonnet 5.

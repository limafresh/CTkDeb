# CTkDeb

![Static Badge](https://img.shields.io/badge/No-PyInstaller-blue?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/Simple-GUI-blue?style=for-the-badge)

<p align="center">
    <img src="https://raw.githubusercontent.com/limafresh/CTkDeb/main/ctkdeb/icon.png" width="100" height="100">
</p>

A CustomTkinter app for easily packaging CustomTkinter, Tkinter, and other Python GUI projects into DEB and RPM packages for Linux. It has GUI, CLI, and Python modes. You can create a small DEB or RPM package without deep packaging experience.

## Install

```bash
pip install CTkDeb[gui]
```

- Creating **DEB** packages requires the `dpkg-deb` tool (pre-installed on most Debian-like systems, probably does not need to be installed separately).
- Creating **RPM** packages requires the `rpmbuild` tool.

## Run

Run this in the project folder (relative to which the paths in the config are specified)

```
ctkdeb-gui
```

## GUI

![Screenshot](https://raw.githubusercontent.com/limafresh/CTkDeb/main/screenshot.png)

## CLI

```
ctkdeb config.json --create deb
```

View all arguments:

```
ctkdeb --help
```

## Python

```python
from ctkdeb import Packager

packager = Packager("config.json")
packager.create_deb()
# or
packager.create_rpm("fedora")
```

View all supported RPM distros:

```python
from ctkdeb import show_supported_rpm_distros
show_supported_rpm_distros()
```

Arguments:

| Argument | Type | Description |
|-|-|-|
| **json_path** | *str* or *dict* | Path to the JSON config (or its dict), required |
| **project_folder** | *str* | Path to the project folder (if the command is not executed from it) |
| **desktop_entry** | *str* | Path to the custom desktop entry (or its text) |
| **output_folder** | *str* | Path to the output folder |

## Good to know

> [!TIP]
> Specifying pip dependencies is only recommended if they are written in pure Python (e.g. CTkMenuBar). If not, it's better to search for the required dependency in the distribution repositories and specify it as a DEB or RPM dependency. For example, for Pillow, specify `python3-pil` for DEB or `python3-pillow` for RPM (Fedora/Mageia) instead of `pillow` in the "Pip dependencies" line.

## FAQ

<details>
    <summary><b>Do I need to specify Python and GUI toolkits as dependencies?</b></summary>
    <br>

In any case, you don't need to specify Python; the tool will do it for you. If your project's GUI toolkit is among the available options in the "Project type" field, and you select that option, you do not need to specify the GUI toolkit either.
</details>

<details>
    <summary><b>Can I use CTkDeb to package PyQt projects?</b></summary>
    <br>
    
Yes, but you will have to find the correct names for the PyQt packages yourself and specify them in the dependencies. In "Project type" select "Other GUI".
</details>

<details>
    <summary><b>Can the tool be run on Windows?</b></summary>
    <br>
    
You can run it (for example, to create a config), but you cannot create packages on Windows.
</details>

## Other

App icon: Claude Sonnet 5 (with modifications by Claude Sonnet 5.5).

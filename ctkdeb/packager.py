import json
from pathlib import Path
import shutil
import tempfile
import subprocess

REQUIRED_FIELDS = {
    "app": ["name", "version", "entryPoint", "icon", "iconSize"],
    "desktopEntry": ["Name"]
}

def _pip_install_to_dir(target_dir: Path, dependencies: str):
    packages = dependencies.split()

    cmd = ["pip", "install", "--target", str(target_dir)] + packages
    subprocess.run(cmd)

    # Clean garbage
    for p in target_dir.rglob("*.py[co]"):
        p.unlink()
    for p in target_dir.rglob("__pycache__"):
        shutil.rmtree(p)

class Packager:
    def __init__(
        self,
        json_path: str,
        project_folder: str=None,
        desktop_entry: str=None,
    ):
        with open(json_path, "r", encoding="utf-8") as f:
            self.json = json.load(f)

        self._check_required_fields()

        if project_folder:
            self.project_folder = Path(project_folder)
        else:
            self.project_folder = Path.cwd()

        if desktop_entry:
            if Path(desktop_entry).exists():
                with open(desktop_entry, "r", encoding="utf-8") as f:
                    self.desktop_entry = f.read()
            else:
                self.desktop_entry = desktop_entry
        else:
            self.desktop_entry = self._create_desktop_entry()

    def _check_required_fields(self):
        for section, fields in REQUIRED_FIELDS.items():
            if section not in self.json:
                raise ValueError(f"Section '{section}' is missing")

            for field in fields:
                if not self.json[section].get(field):
                    raise ValueError(f"Field '{section}.{field}' is missing or empty")

    def _create_desktop_entry(self) -> str:
        basic_desktop_entry = f"""[Desktop Entry]
Type=Application
Version=1.0
Name={self.json['desktopEntry']['Name']}
Exec=python3 /opt/{self.project_folder.name}/{self.json['app']['entryPoint']} %f
Icon={self.json['app']['name']}
Terminal=false
"""

        # Converting basic desktop entry to dict
        lines = basic_desktop_entry.splitlines()

        entry_dict = {}
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)
                entry_dict[key] = value
            else:
                entry_dict[line] = None # for title

        # Update/add fields from json
        for key, value in self.json["desktopEntry"].items():
            entry_dict[key] = value

        # Convert back
        result_lines = []
        for key, value in entry_dict.items():
            if value is None:
                result_lines.append(key) # for title
            else:
                result_lines.append(f"{key}={value}")

        return "\n".join(result_lines)

    def create_deb(self):
        tmp_dir = tempfile.mkdtemp()

        package_dir = Path(tmp_dir) / self.json["app"]["name"]
        package_dir.mkdir()

        share_dir = package_dir / "usr" / "share"
        share_dir.mkdir(parents=True)

        print("Copying app files...")

        opt_dir = package_dir / "opt"
        shutil.copytree(self.project_folder, opt_dir / self.project_folder.name)

        print("Copying the icon...")

        apps_icons_dir = share_dir / "icons" / "hicolor" / self.json["app"]["iconSize"] / "apps"
        apps_icons_dir.mkdir(parents=True)

        icon_path = Path(self.json["app"]["icon"])
        new_icon_name = self.json["app"]["name"] + icon_path.suffix
        shutil.copy(self.project_folder / icon_path, apps_icons_dir / new_icon_name)

        print("Creating the desktop entry...")

        applications_dir = share_dir / "applications"
        applications_dir.mkdir()

        with open(applications_dir / (self.json["app"]["name"] + ".desktop"), "w", encoding="utf-8") as f:
            f.write(self.desktop_entry)

        print("Copying docs...")

        app_doc_dir = share_dir / "doc" / self.json["app"]["name"]
        app_doc_dir.mkdir(parents=True)

        for f in self.json["documentationFiles"]:
            shutil.copy(self.project_folder / f, app_doc_dir)

        print("Install CustomTkinter and pip dependencies...")

        entry_point = Path(self.json["app"]["entryPoint"])
        if len(entry_point.parts) == 1:
            d = opt_dir / self.project_folder.name
        else:
            d = opt_dir / self.project_folder.name / entry_point.parent

        dependencies = "customtkinter"
        if self.json["app"].get("pipDependencies"):
            dependencies += " " + self.json["app"]["pipDependencies"]

        _pip_install_to_dir(d, dependencies)

        print("Estimating package dir size...")

        size_bytes = sum(f.stat().st_size for f in package_dir.rglob("*") if f.is_file())
        size_kb = size_bytes // 1024

        print("Creating control file...")

        debian_dir = package_dir / "DEBIAN"
        debian_dir.mkdir()

        depends = "python3, python3-tk"
        if self.json["deb"].get("depends"):
            depends += ", " + self.json["deb"]["depends"]

        deb_control = f"""Package: {self.json['app']['name']}
Version: {self.json['app']['version']}
Section: {self.json['deb'].get('section') or 'unknown'}
Priority: optional
Depends: {depends}
Architecture: all
Essential: no
Installed-Size: {size_kb}
Maintainer: {self.json['deb'].get('maintainer') or 'Unknown <unknown@example.com>'}
Description: {self.json['deb'].get('description') or 'Packaged via CTkDeb'}
"""

        with open(debian_dir / "control", "w", encoding="utf-8") as f:
            f.write(deb_control)

        print("Creating DEB package...")

        subprocess.run(["dpkg-deb", "--build", package_dir])

        print("Moving DEB and removing tmp dir...")

        shutil.copy(Path(tmp_dir) / (self.json["app"]["name"] + ".deb"), Path.cwd())
        shutil.rmtree(tmp_dir)

        print("DEB successfully created!")

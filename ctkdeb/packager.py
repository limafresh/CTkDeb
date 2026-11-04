import json
from pathlib import Path
import shutil
import tempfile
import tarfile
import subprocess

REQUIRED_FIELDS = {
    "app": ["name", "version", "entryPoint", "icon", "iconSize"],
    "desktopEntry": ["Name"]
}

RPM_REQUIRES = {
    "fedora": {
        "base": "python3",
        "Tkinter": "python3-tkinter",
        "CustomTkinter": "python3-tkinter"
    },
    "mageia": {
        "base": "python3",
        "Tkinter": "tkinter3",
        "CustomTkinter": "tkinter3"
    },
    "openmandriva": {
        "base": "python",
        "Tkinter": "tkinter",
        "CustomTkinter": "python-customtkinter"
    }
}

def _pip_install_to_dir(target_dir: Path, dependencies: list):
    cmd = ["pip", "install", "--target", str(target_dir)] + dependencies
    subprocess.run(cmd)

    # Clean garbage
    for p in target_dir.rglob("*.py[co]"):
        p.unlink()
    for p in target_dir.rglob("__pycache__"):
        shutil.rmtree(p)

class Packager:
    def __init__(
        self,
        json_path: str | dict,
        project_folder: str | None = None,
        desktop_entry: str | None = None,
        output_folder: str | None = None
    ):
        if isinstance(json_path, str):
            with open(json_path, "r", encoding="utf-8") as f:
                self.json = json.load(f)
        elif isinstance(json_path, dict):
            self.json = json_path
        else:
            raise TypeError("'json_path' can only be str or dict.")

        self._check_required_fields()

        if project_folder:
            self.project_folder = Path(project_folder)
        else:
            self.project_folder = Path.cwd()

        if desktop_entry:
            try:
                if Path(desktop_entry).exists():
                    with open(desktop_entry, "r", encoding="utf-8") as f:
                        self.desktop_entry = f.read()
                else:
                    self.desktop_entry = desktop_entry
            except OSError:
                self.desktop_entry = desktop_entry
        else:
            self.desktop_entry = self._create_desktop_entry()

        if output_folder:
            self.output_folder = output_folder
        else:
            self.output_folder = Path.cwd()

        if self.json["app"].get("projectType"):
            self.project_type = self.json["app"]["projectType"]
        else:
            self.project_type = "CustomTkinter"

    def _check_required_fields(self):
        for section, fields in REQUIRED_FIELDS.items():
            if section not in self.json:
                raise ValueError(f"Section '{section}' is missing")

            for field in fields:
                if not self.json[section].get(field):
                    raise ValueError(f"Field '{section}.{field}' is missing or empty")

    def _create_desktop_entry(self) -> str:
        desktop_entry_dict = {
            "[Desktop Entry]": None,
            "Type": "Application",
            "Version": "1.0",
            "Name": self.json["desktopEntry"]["Name"],
            "Exec": f"{self.json['app']['name']} %f",
            "Icon": self.json["app"]["name"],
            "Terminal": "false"
        }

        for key, value in self.json["desktopEntry"].items():
            desktop_entry_dict[key] = value

        result_lines = []
        for key, value in desktop_entry_dict.items():
            if value is None:
                result_lines.append(key) # for title
            else:
                result_lines.append(f"{key}={value}")

        return "\n".join(result_lines)

    def create_deb(self):
        tmp_dir = tempfile.mkdtemp()

        package_dir = Path(tmp_dir) / self.json["app"]["name"]
        package_dir.mkdir()

        usr_dir = package_dir / "usr"
        usr_dir.mkdir()

        share_dir = usr_dir / "share"
        share_dir.mkdir()

        print("Copying app files...")

        opt_dir = package_dir / "opt"
        copy_path = opt_dir / self.project_folder.name

        shutil.copytree(self.project_folder, copy_path)
        self._delete_excluded_items(copy_path)

        print("Copying the icon...")

        apps_icons_dir = share_dir / "icons" / "hicolor" / self.json["app"]["iconSize"] / "apps"
        apps_icons_dir.mkdir(parents=True)

        shutil.copy(self.project_folder / self.json["app"]["icon"], apps_icons_dir / self._new_icon_name())

        print("Creating the wrapper script...")

        bin_dir = usr_dir / "bin"
        bin_dir.mkdir()

        script_path = bin_dir / self.json["app"]["name"]

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(self._wrapper_script())

        script_path.chmod(script_path.stat().st_mode | 0o111)

        print("Creating the desktop entry...")

        applications_dir = share_dir / "applications"
        applications_dir.mkdir()

        with open(applications_dir / (self.json["app"]["name"] + ".desktop"), "w", encoding="utf-8") as f:
            f.write(self.desktop_entry)

        print("Copying docs...")

        if self.json["documentationFiles"]:
            app_doc_dir = share_dir / "doc" / self.json["app"]["name"]
            app_doc_dir.mkdir(parents=True)

            for f in self.json["documentationFiles"]:
                shutil.copy(self.project_folder / f, app_doc_dir)

        print("Install CustomTkinter and pip dependencies...")

        dependencies = []

        if self.project_type == "CustomTkinter":
            dependencies.append("customtkinter")

        if self.json["app"].get("pipDependencies"):
            dependencies.extend(self.json["app"]["pipDependencies"].split())

        if dependencies:
            _pip_install_to_dir(self._pip_target_dir(opt_dir), dependencies)

        print("Estimating package dir size...")

        size_bytes = sum(f.stat().st_size for f in package_dir.rglob("*") if f.is_file())
        size_kb = size_bytes // 1024

        print("Creating control file...")

        debian_dir = package_dir / "DEBIAN"
        debian_dir.mkdir()

        depends = "python3"
        if self.project_type in ["Tkinter", "CustomTkinter"]:
            depends += ", python3-tk"
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

        shutil.move(Path(tmp_dir) / (self.json["app"]["name"] + ".deb"), self.output_folder)
        shutil.rmtree(tmp_dir)

        print("DEB successfully created!")

    def create_rpm(self, distribution: str):
        supported_distros = RPM_REQUIRES.keys()
        if distribution not in supported_distros:
            raise ValueError(f"Only {' '.join(supported_distros)} are supported.")

        tmp_dir = tempfile.mkdtemp()

        package_dir = Path(tmp_dir) / self.json["app"]["name"]
        package_dir.mkdir()

        print("Creating SPEC file...")

        requires = RPM_REQUIRES[distribution]["base"]
        if self.project_type != "Other GUI":
            requires += " " + RPM_REQUIRES[distribution][self.project_type]
        if self.json["rpmRequires"].get(distribution):
            requires += " " + self.json["rpmRequires"][distribution]

        docs_files_names = [Path(f).name for f in self.json["documentationFiles"]]

        spec = f"""Name: {self.json['app']['name']}
Version: {self.json['app']['version']}
Release: 1.{distribution}
Summary: {self.json['rpm'].get('summary') or 'Packaged via CTkDeb'}
License: {self.json['rpm'].get('license') or 'Unknown'}
Source0: {self.json['app']['name']}.tar
BuildArch: noarch
URL: {self.json['rpm'].get('url') or 'https://example.com'}
Requires: {requires}

%description
{self.json['rpm'].get('description') or 'This app is packaged via CTkDeb.'}

%prep
%setup -q -n {self.json['app']['name']}

%install
mkdir -p %{{buildroot}}/usr/bin
cp -r {self.json['app']['name']} %{{buildroot}}/usr/bin

mkdir -p %{{buildroot}}/opt
cp -r {self.project_folder.name} %{{buildroot}}/opt

mkdir -p %{{buildroot}}/usr/share/icons/hicolor/{self.json['app']['iconSize']}/apps
cp {self._new_icon_name()} %{{buildroot}}/usr/share/icons/hicolor/{self.json['app']['iconSize']}/apps

mkdir -p %{{buildroot}}/usr/share/applications
cp {self.json['app']['name']}.desktop %{{buildroot}}/usr/share/applications
{f"""
mkdir -p %{{buildroot}}/usr/share/doc/{self.json['app']['name']}
cp {' '.join(docs_files_names)} %{{buildroot}}/usr/share/doc/{self.json['app']['name']}
""" if docs_files_names else ''}
%files
/usr/bin/{self.json['app']['name']}
/opt/{self.project_folder.name}
/usr/share/icons/hicolor/{self.json['app']['iconSize']}/apps/{self._new_icon_name()}
/usr/share/applications/{self.json['app']['name']}.desktop
{''.join(f"/usr/share/doc/{self.json['app']['name']}/{f}\n" for f in docs_files_names)
if docs_files_names else ''}"""

        with open(package_dir / (self.json["app"]["name"] + ".spec"), "w", encoding="utf-8") as f:
            f.write(spec)

        print("Creating the wrapper script...")

        script_path = package_dir / self.json["app"]["name"]

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(self._wrapper_script())

        script_path.chmod(script_path.stat().st_mode | 0o111)

        print("Creating the desktop entry...")

        with open(package_dir / (self.json["app"]["name"] + ".desktop"), "w", encoding="utf-8") as f:
            f.write(self.desktop_entry)

        print("Copying app files...")

        copy_path = package_dir / self.project_folder.name

        shutil.copytree(self.project_folder, copy_path)
        self._delete_excluded_items(copy_path)

        print("Copying the icon...")

        shutil.copy(self.project_folder / self.json["app"]["icon"], package_dir / self._new_icon_name())

        print("Copying docs...")

        for f in self.json["documentationFiles"]:
            shutil.copy(self.project_folder / f, package_dir)

        print("Install CustomTkinter and pip dependencies...")

        dependencies = []

        if self.project_type == "CustomTkinter" and distribution != "openmandriva":
            dependencies.append("customtkinter")

        if self.json["app"].get("pipDependencies"):
            dependencies.extend(self.json["app"]["pipDependencies"].split())

        if dependencies:
            _pip_install_to_dir(self._pip_target_dir(package_dir), dependencies)

        print("Creating tarball...")

        tar_name = Path(tmp_dir) / (self.json["app"]["name"] + ".tar")

        with tarfile.open(tar_name, "w") as f:
            f.add(package_dir, arcname=self.json["app"]["name"])

        print("Creating RPM package...")

        subprocess.run(["rpmbuild", "-tb", tar_name, "--define", "_topdir " + tmp_dir])

        print("Moving RPM and removing tmp dir...")

        for f in (Path(tmp_dir) / "RPMS" / "noarch").glob("*.rpm"):
            shutil.move(str(f), self.output_folder)

        shutil.rmtree(tmp_dir)

        print("RPM successfully created!")

    def _new_icon_name(self) -> str:
        icon_path = Path(self.json["app"]["icon"])
        return self.json["app"]["name"] + icon_path.suffix

    def _wrapper_script(self) -> str:
        wrapper_script = f"""#!/usr/bin/env bash
python3 /opt/{self.project_folder.name}/{self.json['app']['entryPoint']} "$@"
"""

        return wrapper_script

    def _pip_target_dir(self, app_files_dir_parent: Path) -> Path:
        entry_point = Path(self.json["app"]["entryPoint"])

        if len(entry_point.parts) == 1:
            d = app_files_dir_parent / self.project_folder.name
        else:
            d = app_files_dir_parent / self.project_folder.name / entry_point.parent

        return d

    def _delete_excluded_items(self, path: Path):
        if not self.json.get("excluded"):
            return

        for name in self.json["excluded"]:
            target = path / name

            if target.exists():
                if target.is_file():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)

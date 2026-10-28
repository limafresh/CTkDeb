# CTkDeb changelog

## 0.9.0
- Added support for packaging not only CustomTkinter projects, but also Tkinter projects and those using other GUI toolkits (in the latter case, you will need to specify them manually in the dependencies)

## 0.8.0
- If there are no documentation files, the app folder in /usr/share/doc/ in DEB is not created

## 0.7.0
- Added support for adding excluded files and folders

## 0.6.0
- Added CTkProgressBar

## 0.5.1
- Slightly simplified _create_desktop_entry function

## 0.5.0
- Added support for creating RPMs (for Fedora, Mageia and OpenMandriva)

## 0.4.0
- You can now specify a config dictionary as json_path

## 0.3.1
- Fixed a bug where if you specify a long text as a desktop entry, Path(...).exists() does not hold

## 0.3.0
- Added output_folder argument

## 0.2.0
- Improved README.md
- Keys with empty values ​​are no longer saved in the config
- Added support for specifying desktop entry text instead of a path
- Simplified import
- Fixed bugs

## 0.1.1
- Fixed incorrect pip install command in README.md and added icon in pyproject.toml

## 0.1.0
- Initial version

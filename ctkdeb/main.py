from .packager import RPM_REQUIRES

def cli():
    import argparse
    from .packager import Packager

    parser = argparse.ArgumentParser(
        prog="CTkDeb",
        description="A tool for easily packaging CustomTkinter projects into DEB and RPM"
    )
    parser.add_argument("json", type=str, help="Path to the JSON config")
    parser.add_argument("-c", "--create", required=True, choices=["deb"] + list(RPM_REQUIRES.keys()))
    parser.add_argument("-pf", "--project-folder", type=str,
                        help="Path to the project folder (if the command is not executed from it)")
    parser.add_argument("-d", "--desktop-entry", type=str,
                        help="Path to the custom desktop entry (or its text)")
    parser.add_argument("-of", "--output-folder", type=str, help="Path to the output folder")

    args = parser.parse_args()

    packager = Packager(
        args.json,
        project_folder=args.project_folder,
        desktop_entry=args.desktop_entry,
        output_folder=args.output_folder
    )

    if args.create == "deb":
        packager.create_deb()
    elif args.create in RPM_REQUIRES.keys():
        packager.create_rpm(args.create)

def gui():
    from .gui import CTkDeb

    app = CTkDeb()
    app.mainloop()

def show_supported_rpm_distros():
    print("Supported RPM distros:")
    for distro in RPM_REQUIRES.keys():
        print(f"- '{distro}'")

if __name__ == "__main__":
    cli()

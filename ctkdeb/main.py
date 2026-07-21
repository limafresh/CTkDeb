def cli():
    import argparse
    from .packager import Packager

    parser = argparse.ArgumentParser(
        prog="CTkDeb",
        description="A tool for easily packaging CustomTkinter projects into DEBs"
    )
    parser.add_argument("json", type=str, help="Path to the JSON config")
    parser.add_argument("-pf", "--project-folder", type=str,
                        help="Path to the project folder (if the command is not executed from it)")
    parser.add_argument("-d", "--desktop-entry", type=str,
                        help="Path to the custom desktop entry (or its text)")

    args = parser.parse_args()

    packager = Packager(
        args.json,
        project_folder=args.project_folder,
        desktop_entry=args.desktop_entry
    )
    packager.create_deb()

def gui():
    from .gui import CTkDeb

    app = CTkDeb()
    app.mainloop()

if __name__ == "__main__":
    cli()

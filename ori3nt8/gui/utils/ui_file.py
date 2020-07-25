import subprocess

from ori3nt8.utils.resources import root_path


def compile_ui_files():
    ui_files = (root_path() / "ori3nt8" / "gui" / "ui").glob("**/*.ui")
    for ui_file in ui_files:
        cmd = [
            f"pyside2-uic",
            "-o", ui_file.with_name('Ui_' + ui_file.name).with_suffix('.py'),
            str(ui_file)
        ]
        process = subprocess.run(cmd)
        process.check_returncode()


if __name__ == '__main__':
    compile_ui_files()

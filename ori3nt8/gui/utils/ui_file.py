#  Copyright 2020 Nick Guletskii
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys

from PySide2.scripts.pyside_tool import uic

from ori3nt8.utils.resources import root_path


def compile_ui_files():
    ui_files = (root_path() / "ori3nt8" / "gui" / "ui").glob("**/*.ui")
    for ui_file in ui_files:
        sys.argv = [
            f"pyside2-uic",
            "-o", str(ui_file.with_name('Ui_' + ui_file.name).with_suffix('.py')),
            str(ui_file)
        ]
        assert uic() == 0


if __name__ == '__main__':
    compile_ui_files()

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
from pathlib import Path


def running_in_pyinstaller():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def root_path():
    if running_in_pyinstaller():
        return Path(sys._MEIPASS).absolute()
    return Path(__file__).parent.parent.parent.absolute()


def resource_path() -> Path:
    return root_path() / "resources"

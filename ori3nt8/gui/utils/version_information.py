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
import subprocess
from argparse import ArgumentParser
from pathlib import Path

from ori3nt8.utils.resources import resource_path


def get_version_tag(version_tag_path: Path = None):
    if version_tag_path is None:
        version_tag_path = resource_path() / "version_tag.txt"
    if version_tag_path.exists():
        return version_tag_path.read_text()
    return get_version_information_from_git()


def write_version_tag(version_tag_path: Path = None):
    if version_tag_path is None:
        version_tag_path = resource_path() / "version_tag.txt"
    version_tag_path.write_text(get_version_information_from_git())


def get_version_information_from_git():
    try:
        return subprocess.check_output(["git", "describe", "--tags"]).decode().strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "(Unknown version)"


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--output-path", type=Path, default=Path("resources") / "version_tag.txt")
    args = parser.parse_args()
    write_version_tag(args.output_path)

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

from PySide2.QtWidgets import QDialog

from ori3nt8.gui.ui.Ui_AboutDialog import Ui_AboutDialog
from ori3nt8.gui.utils.version_information import get_version_tag
from ori3nt8.utils.resources import resource_path


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        text = "Please compile a license rollup by running python3 -m ori3nt8.gui.utils.generate_license_rollup"
        rollup_path = resource_path() / "license_rollup.txt"
        if rollup_path.exists():
            text = "Licenses:\n\n" + rollup_path.read_text()
        self.ui.versionLabel.setText("Ori3nt8 " + get_version_tag())
        self.ui.licenseTextArea.setPlainText(text)

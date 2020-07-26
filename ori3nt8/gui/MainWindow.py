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

from pathlib import Path

from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon, QDesktopServices
from PySide2.QtWidgets import QMainWindow, QFileDialog, QFileSystemModel, QHeaderView, QMessageBox
from grundzeug.container import Injector
from grundzeug.container.di import Inject
from typing_extensions import Annotated

from ori3nt8.gui.AboutDialog import AboutDialog
from ori3nt8.gui.ImageContainerWidget import ImageContainerWidget
from ori3nt8.gui.ui.Ui_MainWindow import Ui_MainWindow
from ori3nt8.gui.utils.qtree import ModelIndexNavigator
from ori3nt8.utils.resources import resource_path

WEBSITE_URL = "https://ori3nt8.nickguletskii.com"


class MainWindow(QMainWindow):
    def __init__(self, injector: Annotated[Injector, Inject]):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        appIcon = QIcon(str(resource_path() / "ori3nt8.svg"))
        self.setWindowIcon(appIcon)

        self.ui.actionOpen_directory.triggered.connect(self.select_and_open_directory)
        self.ui.actionNext.triggered.connect(lambda: self.next_item())
        self.ui.actionPrevious.triggered.connect(self.previous_item)

        self.image_widget = injector.inject(ImageContainerWidget)(self.update_status_bar)
        self.ui.imageLayout.addWidget(self.image_widget, 1, 1)
        self.ui.actionRotate_clockwise.triggered.connect(self.image_widget.rotate_clockwise)
        self.ui.actionRotate_counterclockwise.triggered.connect(self.image_widget.rotate_counterclockwise)
        self.ui.actionAutomatically_apply.toggled.connect(self.image_widget.set_apply_automatically)
        self.ui.actionApply_suggested_orientation.triggered.connect(self.image_widget.apply_suggested_orientation)
        self.ui.actionWebsite.triggered.connect(self.launch_website)
        self.ui.actionAbout.triggered.connect(self.launch_about)

        self.file_tree_view_navigator = ModelIndexNavigator.for_selecting_current_item_in_tree_view(
            self.ui.fileTreeView
        )

    def launch_website(self):
        QDesktopServices.openUrl(QUrl(WEBSITE_URL))

    def launch_about(self):
        AboutDialog().exec_()

    def select_and_open_directory(self):
        dir = QFileDialog.getExistingDirectory(caption="Select the directory to process")

        button = QMessageBox.warning(
            self,
            f"Please make sure that you have BACKED UP your photos before opening them in Ori3nt8!",
            "Ori3nt8 is experimental and may ruin your EXIF metadata, or simply incorrectly "
            "rotate your photos. Please make sure that you have backed up the selected folder "
            "before continuing.",
            buttons=QMessageBox.Open | QMessageBox.Cancel,
            defaultButton=QMessageBox.Cancel
        )

        if button == QMessageBox.Open:
            self.open_directory(dir)

    def open_directory(self, dir):
        model = QFileSystemModel(self.ui.fileTreeView)
        model.setNameFilters(["*.jpg", "*.JPG"])
        model.setRootPath(dir)
        self.ui.fileTreeView.setModel(model)
        self.ui.fileTreeView.setRootIndex(model.index(dir))
        self.ui.fileTreeView.header().setStretchLastSection(False)
        self.ui.fileTreeView.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.fileTreeView.selectionModel().selectionChanged.connect(self.current_file_changed)
        self.ui.fileTreeView.hideColumn(1)
        self.ui.fileTreeView.hideColumn(2)
        self.ui.fileTreeView.hideColumn(3)
        self.ui.fileTreeView.hideColumn(4)

    def next_item(self):
        idx = self.ui.fileTreeView.currentIndex()
        self.file_tree_view_navigator.next_model_index(idx)

    def previous_item(self):
        idx = self.ui.fileTreeView.currentIndex()
        self.file_tree_view_navigator.prev_model_index(idx)

    def current_file_changed(self):
        path = self.ui.fileTreeView.model().filePath(self.ui.fileTreeView.currentIndex())
        self.image_widget.set_image_path(Path(path))

    def update_status_bar(self, message):
        self.ui.statusbar.showMessage(message)

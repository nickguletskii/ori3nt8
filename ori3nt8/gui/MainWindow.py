from pathlib import Path

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QFileDialog, QFileSystemModel, QHeaderView
from grundzeug.container import Injector
from grundzeug.container.di import Inject
from typing_extensions import Annotated

from ori3nt8.gui.ImageContainerWidget import ImageContainerWidget
from ori3nt8.gui.ui.Ui_MainWindow import Ui_MainWindow
from ori3nt8.gui.utils.qtree import ModelIndexNavigator
from ori3nt8.utils.resources import resource_path


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

        self.file_tree_view_navigator = ModelIndexNavigator.for_selecting_current_item_in_tree_view(
            self.ui.fileTreeView
        )

    def select_and_open_directory(self):
        dir = QFileDialog.getExistingDirectory(caption="Select the directory to process")
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

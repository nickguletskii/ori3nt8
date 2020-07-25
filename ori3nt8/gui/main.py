import sys
from typing import Tuple

from PySide2.QtWidgets import QApplication
from grundzeug.container import Container
from grundzeug.container.plugins import ContainerConverterResolutionPlugin, ContainerConfigurationResolutionPlugin
from grundzeug.converters import Converter

from ori3nt8.gui.inference.executors import AbstractExecutor, Caffe2Executor
from ori3nt8.gui.inference.preprocessing import PreprocessingPipeline
from ori3nt8.gui.metadata.common import AbstractMetadataStorage
from ori3nt8.gui.metadata.sql import SqliteMetadataStorage
from ori3nt8.gui.runnables.workers import ImageWorkers
from ori3nt8.gui.utils.ui_file import compile_ui_files
from ori3nt8.utils.resources import running_in_pyinstaller

if __name__ == "__main__":
    if not running_in_pyinstaller():
        compile_ui_files()
    app = QApplication(sys.argv)

    from ori3nt8.gui.MainWindow import MainWindow

    container = Container()

    container.add_plugin(ContainerConverterResolutionPlugin())
    container.register_instance[Converter[list, Tuple[float, float, float]]](tuple)
    config_plugin = ContainerConfigurationResolutionPlugin()
    container.add_plugin(config_plugin)

    container.register_type[AbstractExecutor, Caffe2Executor]()
    container.register_type[AbstractMetadataStorage, SqliteMetadataStorage]()
    container.register_type[ImageWorkers]()
    container.register_type[PreprocessingPipeline]()
    window = container.inject(MainWindow)()
    window.show()

    sys.exit(app.exec_())

from multiprocessing import Lock
from pathlib import Path
from typing import Callable, List

from PySide2.QtCore import QModelIndex, QTimer, Qt, QFileInfo, QDir
from PySide2.QtWidgets import QFileSystemModel, QTreeView


def _get_file_path_from_model_index(idx: QModelIndex):
    return idx.model().filePath(idx)


def _is_leaf(idx: QModelIndex):
    return not _is_dir(idx)


def _is_dir(idx: QModelIndex):
    return idx.model().isDir(idx)


def _iter_children(idx: QModelIndex):
    for i in range(idx.model().rowCount(idx)):
        yield idx.child(i, 0)


def _find_first_child(idx: QModelIndex, reverse: bool):
    model: QFileSystemModel = idx.model()
    files = list(_iter_children(idx))
    if len(files) == 0:
        return None

    # We need the children to be in the same order as in QFileSystemModel. Otherwise we will sometimes select a random
    # item in the directory.

    children = _qt_stort_files(files, reverse=reverse)

    for row in children:
        if model.isDir(row):
            return row
        if _is_item_selectable(row):
            return row
    return None


def _qt_stort_files(indexes: List[QModelIndex], reverse: bool) -> List[QModelIndex]:
    """
    Sorts the indexes according to the order provided by :py:class:`~PySide2.QtCore.QDir`.

    Parameters
    ----------
    indexes
        The indexes to sort.
    reverse
        Set to `True` to reverse the sort order.
    Returns
    -------
    `indexes`, sorted using the order defined in :py:class:`~PySide2.QtCore.QDir`.
    """
    first_child_path = _get_file_path_from_model_index(indexes[0])
    dir_path = Path(first_child_path).parent
    qt_file_name_order = QFileInfo(first_child_path).dir().entryList(
        QDir.Filter.NoFilter,
        QDir.SortFlag.DirsFirst | QDir.SortFlag.LocaleAware
    )
    file_name_order_lookup = {(dir_path / file).absolute(): i for i, file in enumerate(qt_file_name_order)}
    children = sorted(
        indexes,
        key=lambda x: file_name_order_lookup[Path(_get_file_path_from_model_index(x)).absolute()],
        reverse=reverse
    )
    return children


def _is_item_selectable(row):
    return (row.flags() & (Qt.ItemIsEnabled | Qt.ItemIsSelectable)) == (Qt.ItemIsEnabled | Qt.ItemIsSelectable)


def _next_sibling(idx: QModelIndex, reverse: bool):
    return idx.sibling(idx.row() + (-1 if reverse else 1), idx.column())


def _iter_siblings(idx: QModelIndex, reverse: bool):
    prev_idx = idx
    next_idx = _next_sibling(idx, reverse)
    while next_idx.isValid() \
            and next_idx.row() != prev_idx.row() \
            and next_idx.model().hasIndex(next_idx.row(), next_idx.column(), next_idx.parent()):
        yield next_idx
        prev_idx = next_idx
        next_idx = _next_sibling(next_idx, reverse)


class ModelIndexNavigator():
    def __init__(
            self,
            is_expanded_callback: Callable[[QModelIndex], None],
            expand_callback: Callable[[QModelIndex], None],
            final_item_callback: Callable[[QModelIndex], None]
    ):
        """
        Provides the functionality necessary to select the next or previous leaf in a
        :py:class:`~PySide2.QtWidgets.QTreeView.QTreeView` associated with a
        `~PySide2.QtWidgets.QFileSystemModel.QFileSystemMode` model.

        Parameters
        ----------
        is_expanded_callback
        expand_callback
        final_item_callback
        """
        self.is_expanded_callback = is_expanded_callback
        self.expand_callback = expand_callback
        self.final_item_callback = final_item_callback

        self._operation_queue = []
        self._action_queue = []
        self._queue_lock = Lock()

    @classmethod
    def for_selecting_current_item_in_tree_view(self, tree_view: QTreeView):
        return ModelIndexNavigator(
            is_expanded_callback=lambda x: tree_view.isExpanded(x),
            expand_callback=lambda x: tree_view.expand(x),
            final_item_callback=lambda x: tree_view.setCurrentIndex(x)
        )

    def _enqueue_action_and_pump_now(self, action):
        """
        Enqueues the action to be performed once the current action has been performed (i.e. the operation queue has
        been emptied).
        """
        try:
            self._queue_lock.acquire()
            self._action_queue.append(action)
        finally:
            self._queue_lock.release()
        self._pump()

    def _enqueue_operation_and_pump_later(self, action):
        """
        Enqueues an operation to be performed after Qt has done some background work.
        """
        self._operation_queue.append(action)
        QTimer.singleShot(0, self._pump)

    def _pump(self):
        """
        Tries to execute an operation from the operation queue, or start an action if it is empty.
        """
        try:
            action = None
            self._queue_lock.acquire()
            try:
                # First, we try to execute the operations enqueued by the previous action.
                action = self._operation_queue.pop(0)
            except IndexError as ie:
                try:
                    # If we are out of operations, check if we have an action to perform.
                    action = self._action_queue.pop(0)
                except IndexError as ie:
                    pass
            if action is not None:
                action()
        finally:
            self._queue_lock.release()

    def _select_first_leaf(self, idx: QModelIndex, reverse):
        assert idx is not None and idx.model() is not None

        if _is_leaf(idx):
            # Check if we can select this leaf. If we can't, continue to the next item.
            if not _is_item_selectable(idx):
                self._select_next_item(idx, reverse)
                return

            self.final_item_callback(idx)
            return

        def _select_first_leaf_later():
            self._select_first_leaf(idx, reverse)

        # If the node is not expanded, we need to expand it and wait for the children to load.
        if not self.is_expanded_callback(idx):
            self.expand_callback(idx)
            self._enqueue_operation_and_pump_later(_select_first_leaf_later)
            return

        # If the node is not completely loaded, we need to fetch more items and revisit this node.
        if idx.model().canFetchMore(idx):
            idx.model().fetchMore(idx)
            self._enqueue_operation_and_pump_later(_select_first_leaf_later)
            return

        first_child = _find_first_child(idx, reverse)
        if first_child is None:
            if idx.model().hasChildren(idx):
                self._enqueue_operation_and_pump_later(_select_first_leaf_later)
                return
            self._select_next_item(idx, reverse)
        else:
            self._select_first_leaf(first_child, reverse)

    def _select_next_item(self, idx: QModelIndex, reverse):
        if not idx.isValid():
            return

        # If there is a sibling, attempt to select the first leaf in the subtree, or, if there is no leaf, continue on
        # to the next item.
        for next_idx in _iter_siblings(idx, reverse):
            self._select_first_leaf(next_idx, reverse)
            return

        # Find the first ancestor with a sibling node
        parent_node = idx.parent()
        while parent_node is not None and parent_node.isValid() and not _next_sibling(parent_node, reverse).isValid():
            parent_node = parent_node.parent()

        # If no such ancestor exists, we're out of trees to explore, which means that there's no next leaf.
        if parent_node is None or not parent_node.isValid():
            return

        # Once we find the first sibling among ancestors, the next leaf will be the first leaf in the sibling's subtree.
        self._select_first_leaf(_next_sibling(parent_node, reverse), reverse)
        return

    def _root_action(self, idx: QModelIndex, reverse: bool):
        if not _is_leaf(idx):
            self._select_first_leaf(idx, reverse=reverse)
            return
        self._select_next_item(idx, reverse=reverse)

    def next_model_index(self, idx: QModelIndex) -> None:
        """
        Runs the `final_item_callback` on the next leaf in the model, if any.

        This method may schedule more work to be done asynchronously using :py:meth:`~PySide2.QtCore.QTimer.singleShot`.

        Parameters
        ----------
        idx
            `final_item_callback` will be called on the first leaf that succeeds `idx`.

        """
        self._enqueue_action_and_pump_now(lambda: self._root_action(idx, reverse=False))

    def prev_model_index(self, idx: QModelIndex) -> None:
        """
        Runs the `final_item_callback` on the previous leaf in the model, if any.

        This method may schedule more work to be done asynchronously using :py:meth:`~PySide2.QtCore.QTimer.singleShot`.

        Parameters
        ----------
        idx
            `final_item_callback` will be called on the first leaf that precedes `idx`.

        """
        self._enqueue_action_and_pump_now(lambda: self._root_action(idx, reverse=True))

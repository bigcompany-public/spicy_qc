from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QListView,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from spicy_qc.api import Tag
from spicy_qc.gui.utils import get_qt_app, get_qta_icon
from spicy_qc.widgets.container import ContainerDialog, ContainerWidget
from spicy_qc.widgets.tag_widget import TagWidget

if TYPE_CHECKING:
    from spicy_qc.widgets.spicyqc_widget import SpicyQcWidget


class TagListWidget(QFrame):
    def __init__(self, tag: Tag, item: QListWidgetItem):
        super().__init__()
        self.tag = tag
        self.item = item

        margin_layout = QVBoxLayout(self)
        margin_layout.setContentsMargins(0, 0, 0, 0)

        inner_frame = QFrame()
        inner_frame.setProperty("depth", "1")
        inner_frame.setContentsMargins(0, 0, 0, 0)
        inner_frame.setStyleSheet("")
        margin_layout.addWidget(inner_frame)
        self._layout = QHBoxLayout(inner_frame)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._widget = TagWidget(tag=tag)
        self._layout.addWidget(self._widget)
        self._layout.addStretch()
        self.update_color()

    def update_item_size_hint(self):
        """Call this after setItemWidget() so layout is finalized."""
        self.adjustSize()
        size = self.sizeHint()
        size.setHeight(size.height() + 2)
        self.item.setSizeHint(size)

    def update_color(self, grey_out=True):
        self._widget.update_preview(greyed_out=grey_out)


class TagList(QListWidget):
    def __init__(self, tag_filter_widget: TagFilterWidget):
        super().__init__(tag_filter_widget)
        self.tag_filter_widget = tag_filter_widget

        # UI
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setFlow(QListView.Flow.LeftToRight)
        self.setWrapping(True)
        self.setSpacing(1)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setSortingEnabled(False)

        # Signals
        self.itemSelectionChanged.connect(self.selection_changed)

    def selection_changed(self):
        for i in range(self.count()):
            item = self.item(i)
            widget: TagListWidget = self.itemWidget(item)  # type: ignore
            widget.update_color(grey_out=not item.isSelected())

    @property
    def all_widgets(self) -> list[TagListWidget]:
        widgets = []
        for i in range(self.count()):
            item = self.item(i)
            widget: TagListWidget = self.itemWidget(item)  # type: ignore
            widgets.append(widget)
        return widgets

    @property
    def selected_tags(self) -> list[str]:
        tags = []
        for i in range(self.count()):
            item = self.item(i)
            if not item.isSelected():
                continue
            widget: TagListWidget = self.itemWidget(item)  # type: ignore
            tags.append(widget.tag.tag)
        return tags


class TagFilterWidget(QWidget):
    confirmed: Signal = Signal(object)

    def __init__(self, tags: list[Tag], spicyqc_widget: SpicyQcWidget):
        super().__init__()
        self.tags = sorted(tags, key=lambda tag: tag.tag)
        self.spicyqc_widget = spicyqc_widget
        self.setup_ui()
        self.setup_initial_state()
        self.setup_signals()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.list_widget = TagList(self)
        layout.addWidget(self.list_widget)

    def setup_signals(self):
        self.list_widget.itemSelectionChanged.connect(self.spicyqc_widget.update_visible_columns)

    def setup_initial_state(self):
        self.update_items()

    def update_items(self):
        self.list_widget.clear()
        for tag in self.tags:
            item = QListWidgetItem()
            widget = TagListWidget(tag=tag, item=item)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

            # Now the widget is parented and layout is computable
            widget.update_item_size_hint()

    @property
    def selected_tags(self) -> list[str]:
        return self.list_widget.selected_tags

    @property
    def all_widgets(self) -> list[TagListWidget]:
        return self.list_widget.all_widgets


def show_dialog(tags: list[Tag]) -> list[str] | None:
    app = get_qt_app()
    icon = get_qta_icon(name="mdi.tag-text", scale_factor=1.25)
    widget = TagFilterWidget(tags)
    container = ContainerWidget(widget=widget, icon=icon, title="Tag Grid")
    dialog = ContainerDialog(container)
    widget.confirmed.connect(dialog.accept)
    if dialog.exec():
        return widget.selected_tags


if __name__ == "__main__":
    # For testing purposes
    tags = [
        Tag("hello"),
    ]

    show_dialog(tags)

"""Widgets used to render and select tags in the SpicyQC filter panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
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
    """A list item widget that displays a single tag inside a QListWidget."""

    def __init__(self, tag: Tag, item: QListWidgetItem):
        """Initialize a tag list item wrapper.

        Args:
            tag: Tag metadata to display.
            item: Backing QListWidgetItem associated with this widget.
        """
        super().__init__()
        self.tag = tag
        self.item = item

        margin_layout = QVBoxLayout(self)
        margin_layout.setContentsMargins(0, 0, 0, 0)

        inner_frame = QFrame()
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
        """Adjust the list item size hint after the widget has been parented."""
        self.adjustSize()
        size = self.sizeHint()
        size.setHeight(size.height() + 2)
        self.item.setSizeHint(size)

    def update_color(self, grey_out=True):
        """Update the display color of the tag item based on selection state."""
        self._widget.update_preview(greyed_out=grey_out)


class TagList(QListWidget):
    """A wrapped QListWidget that displays selectable tag items."""

    def __init__(self, tag_filter_widget: TagFilterWidget):
        """Initialize the tag list container.

        Args:
            tag_filter_widget: Parent widget that owns the tag list.
        """
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
        """Update item appearance whenever the selection changes."""
        for i in range(self.count()):
            item = self.item(i)
            widget: TagListWidget = self.itemWidget(item)  # type: ignore
            widget.update_color(grey_out=not item.isSelected())

    @property
    def all_widgets(self) -> list[TagListWidget]:
        """Return all TagListWidget instances currently in the list."""
        widgets = []
        for i in range(self.count()):
            item = self.item(i)
            widget: TagListWidget = self.itemWidget(item)  # type: ignore
            widgets.append(widget)
        return widgets

    @property
    def selected_tags(self) -> list[str]:
        """Return the tags currently selected by the user."""
        tags = []
        for i in range(self.count()):
            item = self.item(i)
            if not item.isSelected():
                continue
            widget: TagListWidget = self.itemWidget(item)  # type: ignore
            tags.append(widget.tag.tag)
        return tags


class TagFilterWidget(QWidget):
    """Widget that renders the tag selection filter panel."""

    confirmed: Signal = Signal(object)

    def __init__(self, tags: list[Tag], spicyqc_widget: SpicyQcWidget):
        """Initialize the tag filter widget.

        Args:
            tags: Tag metadata list to render.
            spicyqc_widget: Parent SpicyQC widget instance.
        """
        super().__init__()
        self.tags = sorted(tags, key=lambda tag: tag.tag)
        self.spicyqc_widget = spicyqc_widget
        self.setup_ui()
        self.setup_initial_state()
        self.setup_signals()

    def setup_ui(self) -> None:
        """Create the UI elements for the tag filter widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.list_widget = TagList(self)
        layout.addWidget(self.list_widget)

    def setup_signals(self):
        """Hook Qt signals from the tag list into the parent widget."""
        self.list_widget.itemSelectionChanged.connect(self.spicyqc_widget.update_visible_columns)

    def setup_initial_state(self):
        """Initialize the tag filter state and populate items."""
        self.update_items()

    def update_items(self):
        """Populate the tag list with widgets for each available tag."""
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
        """Return the list of tags selected in the filter panel."""
        return self.list_widget.selected_tags

    @property
    def all_widgets(self) -> list[TagListWidget]:
        """Return all tag list widgets currently displayed."""
        return self.list_widget.all_widgets


def show_dialog(tags: list[Tag]) -> list[str] | None:
    """Show a modal dialog that allows tag selection.

    Args:
        tags: List of tags to present to the user.

    Returns:
        The selected tag names, or None if the dialog was cancelled.
    """
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

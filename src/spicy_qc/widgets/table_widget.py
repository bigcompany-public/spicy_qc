"""Table widget and context menu helpers for SpicyQC criterion display."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import qtawesome
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QAbstractItemView, QMenu, QSizePolicy, QTableWidget

from spicy_qc.gui.utils import get_theme

if TYPE_CHECKING:
    from spicy_qc.widgets.criterion_widget import CriterionTableItem, CriterionWidget
    from spicy_qc.widgets.spicyqc_widget import SpicyQcWidget

THEME = get_theme()


class TableMenu(QMenu):
    """Context menu shown on right-click within the criterion table."""

    def __init__(self, table_widget: CriterionTableWidget):
        """Create a table context menu for the given table widget."""
        super().__init__(table_widget)
        self.table_widget = table_widget
        self.spicy_qc_widget = table_widget.spicy_qc_widget

        # Show Valid
        if self.table_widget.show_valid_criterions:
            action = self.addAction("Hide Valid Criterions")
            action.setIcon(qtawesome.icon("fa6s.toggle-off", color=THEME["icon_color"]))
            action.triggered.connect(self.hide_valid_criterions)
        else:
            action = self.addAction("Show Valid Criterions")
            action.setIcon(qtawesome.icon("fa6s.toggle-on", color=THEME["icon_color"]))
            action.triggered.connect(self.show_valid_criterions)

        # Collapse all
        action = self.addAction("Collapse All")
        action.setIcon(qtawesome.icon("mdi.arrow-collapse-vertical", color=THEME["icon_color"]))
        action.triggered.connect(self.collapse_all)

        # Sort by name
        action = self.addAction("Sort By Name")
        action.setIcon(qtawesome.icon("fa5s.sort-alpha-down", color=THEME["icon_color"]))
        action.triggered.connect(self.sort_by_name)

        # Sort by status
        action = self.addAction("Sort By Status")
        action.setIcon(qtawesome.icon("mdi.sort-bool-ascending-variant", color=THEME["icon_color"]))
        action.triggered.connect(self.sort_by_status)

        # Disable sorting
        action = self.addAction("Disable Sorting")
        action.setIcon(qtawesome.icon("mdi6.sort-variant-off", color=THEME["icon_color"]))
        action.triggered.connect(self.sort_by_index)

    def hide_valid_criterions(self):
        """Hide criterions that are currently marked as valid."""
        self.table_widget.show_valid_criterions = False
        self.spicy_qc_widget.update_visible_columns()

    def show_valid_criterions(self):
        """Show criterions that are currently marked as valid."""
        self.table_widget.show_valid_criterions = True
        self.spicy_qc_widget.update_visible_columns()

    def collapse_all(self):
        """Collapse all expandable criterion sections in the table."""
        for criterion_widget in self.spicy_qc_widget.criterion_widgets:
            criterion_widget.toggle_logs_button.collapse_frame()
            criterion_widget.toggle_assistant_button.collapse_frame()
            criterion_widget.toggle_documentation_button.collapse_frame()

    def sort_by_status(self):
        """Sort table rows by criterion status."""
        self.table_widget.sortByColumn(self.table_widget._status_column_index, Qt.SortOrder.AscendingOrder)

    def sort_by_name(self):
        """Sort table rows by criterion label."""
        self.table_widget.sortByColumn(self.table_widget._label_column_index, Qt.SortOrder.AscendingOrder)

    def sort_by_index(self):
        """Restore the original table order by index."""
        self.table_widget.sortByColumn(self.table_widget._index_column_index, Qt.SortOrder.AscendingOrder)


class CriterionTableWidget(QTableWidget):
    def __init__(self, spicy_qc_widget: SpicyQcWidget) -> None:
        """Initialize the criterion table used by the main widget."""
        super().__init__(spicy_qc_widget)
        self.spicy_qc_widget = spicy_qc_widget
        self.show_valid_criterions = True
        self._columns = ["label", "index", "status", "criterion"]
        self._label_column_index = self._columns.index("label")
        self._index_column_index = self._columns.index("index")
        self._status_column_index = self._columns.index("status")
        self._criterion_column_index = self._columns.index("criterion")
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumWidth(550)
        self.installEventFilter(self)
        self.setColumnCount(len(self._columns))
        self.setHorizontalHeaderLabels(self._columns)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        for i in range(len(self._columns) - 1):
            self.setColumnHidden(i, True)

    def get_criterion_widget_at_row(self, row: int) -> CriterionWidget:
        """Return the criterion widget contained in the given row."""
        return self.get_criterion_item_at_row(row).criterion_widget

    def get_criterion_item_at_row(self, row: int) -> CriterionTableItem:
        """Return the hidden criterion table item for the given row."""
        return self.item(row, self._criterion_column_index)  # type: ignore

    def selectedItems(self) -> List[CriterionTableItem]:
        """Return the list of selected table items with correct typing."""
        return super().selectedItems()  # type: ignore

    def contextMenuEvent(self, event: QEvent):
        """Show the table context menu when the user right-clicks."""
        menu = TableMenu(self)
        menu.exec_(event.globalPos())

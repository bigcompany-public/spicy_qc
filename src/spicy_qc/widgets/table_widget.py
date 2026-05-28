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
    def __init__(self, table_widget: CriterionTableWidget):
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

    def hide_valid_criterions(self):
        self.table_widget.show_valid_criterions = False
        self.spicy_qc_widget.update_visible_columns()

    def show_valid_criterions(self):
        self.table_widget.show_valid_criterions = True
        self.spicy_qc_widget.update_visible_columns()

    def collapse_all(self):
        for criterion_widget in self.spicy_qc_widget.criterion_widgets:
            criterion_widget.toggle_logs_button.collapse_frame()
            criterion_widget.toggle_assistant_button.collapse_frame()
            criterion_widget.toggle_documentation_button.collapse_frame()


class CriterionTableWidget(QTableWidget):
    def __init__(self, spicy_qc_widget: SpicyQcWidget) -> None:
        super().__init__(spicy_qc_widget)
        self.spicy_qc_widget = spicy_qc_widget
        self.show_valid_criterions = True
        self._columns = ["label", "criterion"]
        self._label_column_index = self._columns.index("label")
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
        return self.get_criterion_item_at_row(row).criterion_widget

    def get_criterion_item_at_row(self, row: int) -> CriterionTableItem:
        return self.item(row, self._criterion_column_index)  # type: ignore

    def selectedItems(self) -> List[CriterionTableItem]:
        return super().selectedItems()  # type: ignore

    def contextMenuEvent(self, event: QEvent):
        """
        This method pops a Qmenu widget when the user right clicks on the table
        """
        menu = TableMenu(self)
        menu.exec_(event.globalPos())

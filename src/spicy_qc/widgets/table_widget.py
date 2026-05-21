from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QAbstractItemView,
    QSizePolicy,
    QTableWidget,
)

if TYPE_CHECKING:
    from spicy_qc.widgets.spicy_qc_widget import SpicyQcWidget


class CriterionTableWidget(QTableWidget):
    def __init__(self, spicy_qc_widget: SpicyQcWidget) -> None:
        super().__init__(spicy_qc_widget)
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

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from spicy_qc.api import Criterion


class AssistantWidget(QWidget):
    def __init__(self, criterion: Criterion):
        super().__init__()
        self.setMaximumHeight(500)
        self.criterion = criterion

from PySide6.QtWidgets import QWidget

from spicy_qc.api import Criterion


class AssistantWidget(QWidget):
    def __init__(self, criterion: Criterion):
        super().__init__()
        self.criterion = criterion

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from spicy_qc.api import Criterion

if TYPE_CHECKING:
    from spicy_qc.widgets.criterion_widget import CriterionWidget
    from spicy_qc.widgets.spicyqc_widget import SpicyQcWidget


class AssistantWidget(QWidget):
    def __init__(self, criterion: Criterion):
        super().__init__()
        self.criterion = criterion
        self.spicy_qc_widget: SpicyQcWidget
        self.criterion_widget: CriterionWidget

"""Base class for criterion-specific assistant widgets."""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from spicy_qc.api import Criterion

if TYPE_CHECKING:
    from spicy_qc.widgets.criterion_widget import CriterionWidget
    from spicy_qc.widgets.spicyqc_widget import SpicyQcWidget


class AssistantWidget(QWidget):
    """
    Base widget for criterion assistant panels. That exposes the SpicyQC main widget and the Criterion widget.
    """

    def __init__(self, criterion: Criterion):
        """Initialize a Criterion assistant widget.

        Args:
            criterion: The Criterion instance that this assistant supports.
        """
        super().__init__()
        self.criterion = criterion
        self.spicy_qc_widget: SpicyQcWidget
        self.criterion_widget: CriterionWidget

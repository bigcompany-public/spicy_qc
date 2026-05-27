from functools import partial

from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QSizePolicy

from spicy_qc.api import Criterion, CriterionStatus, Warning
from spicy_qc.gui.utils import format_widgets
from spicy_qc.widgets.assistant_widget import AssistantWidget


def detect_objects_with_non_manifold_faces(criterion: Criterion):
    elements = ["cat", "ball", "house", "car"]
    for element in elements:
        criterion.add_warning(Warning("Geometry contains non-manifold faces", element))


class MyCustomAssistant(AssistantWidget):
    def __init__(self, criterion: Criterion):
        super().__init__(criterion)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        layout = QGridLayout(self)

        if self.criterion.status == CriterionStatus.WAITING:
            layout.addWidget(QLabel("The verification has not been done yet"))
            return

        if not self.criterion.warnings:
            layout.addWidget(QLabel("There is no warnings"))

        for i, warning in enumerate(self.criterion.warnings):
            label = QLabel(warning.element)
            label.setProperty("status", "important")
            layout.addWidget(label, i, 0)
            layout.addWidget(QLabel(warning.message), i, 1)
            button = QPushButton("Highlight in viewport")
            button.setProperty("status", "important")
            layout.addWidget(button, i, 2)
            message = f"Highlighting {warning.element}"
            button.clicked.connect(partial(print, message))

        format_widgets(self)


criterion = Criterion(
    label="Non-Manifold Faces",
    description="This criterion detects non-manifold faces in geometries",
    verify_callback=detect_objects_with_non_manifold_faces,
    tags=["mesh"],
    is_optional=False,
    assistant_widget=MyCustomAssistant,
)

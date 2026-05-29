from functools import partial

from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QSizePolicy

from spicy_qc import AssistantWidget, Criterion, CriterionStatus, Warning, format_widgets


def detect_non_manifold_geometries(criterion: Criterion):
    elements = ["cat", "ball", "house", "car"]
    for element in elements:
        criterion.add_warning(Warning("Geometry is non-manifold", element))


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
    label="Non-Manifold Geometries",
    description="This criterion detects non-manifold geometries in the scene",
    verify_callback=detect_non_manifold_geometries,
    tags=["mesh"],
    is_optional=False,
    assistant_widget=MyCustomAssistant,
)

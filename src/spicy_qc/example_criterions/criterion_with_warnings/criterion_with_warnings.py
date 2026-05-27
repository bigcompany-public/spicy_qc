import random
from functools import partial
from typing import Any

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout

from spicy_qc.api import Criterion, Warning
from spicy_qc.widgets.assistant_widget import AssistantWidget


def function_with_warnings(criterion: Criterion):
    criterion.add_warning(Warning("something is wrong", "element1"))
    criterion.add_warning(Warning("something is also wrong", "element2"))
    criterion.add_warning(Warning("something is also wrong", "element3"))
    criterion.add_warning(Warning("something is also wrong", "element4"))
    criterion.add_warning(Warning("something is also wrong", "element5"))
    criterion.add_warning(Warning("something is also wrong", "element6"))
    criterion.add_warning(Warning("something is also wrong", "element7"))
    criterion.add_warning(Warning("something is also wrong", "element8"))
    criterion.add_warning(Warning("something is also wrong", "element9"))
    criterion.add_warning(Warning("something is also wrong", "element10"))


class MyCustomAssistant(AssistantWidget):
    def __init__(self, criterion: Criterion):
        super().__init__(criterion)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Hello, I'm the assistant."))

        if not criterion.warnings:
            layout.addWidget(QLabel("There is no warnings"))

        warnings = criterion.warnings[: int(random.random() * 10)]
        for warning in warnings:
            layout.addWidget(QLabel(warning.element))
            layout.addWidget(QLabel(warning.message))
            button = QPushButton("Fix")
            button.setProperty("status", "important")
            layout.addWidget(button)
            button.clicked.connect(partial(self.fix, warning.element))

    def fix(self, element: Any):
        print(f"Fixing {element}")


criterion_with_warnings = Criterion(
    label="Criterion with warnings",
    description="This criterion will have warnings",
    verify_callback=function_with_warnings,
    tags=["mesh"],
    is_optional=False,
    assistant_widget=MyCustomAssistant,
)

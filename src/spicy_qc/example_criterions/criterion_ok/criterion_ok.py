from PySide6.QtWidgets import QLabel

from spicy_qc.api import Criterion


def function_ok(criterion: Criterion):
    print("Everything was fine here.")


assistant = QLabel("Hello")
assistant.setFixedHeight(100)
assistant.setFixedWidth(100)
# assistant.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))

criterion_ok = Criterion(
    label="Criterion working fine",
    description="This criterion will run without warning/errors",
    verify_callback=function_ok,
    tags=["mesh", "rig", "other"],
    is_optional=False,
    assistant_widget=assistant,
    documentation="# Everything is OK! \n\nIn this criterion, everything will work just fine",
)

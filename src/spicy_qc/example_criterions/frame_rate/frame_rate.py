import os

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout

from spicy_qc import AssistantWidget, Criterion, CriterionStatus, Warning, monitor_action

PROPER_FRAMERATE = 25.0


# Verification Callback
def check_frame_rate(criterion: Criterion):
    framerate = float(os.environ.get("SQPICYQC_FRAMERATE", 24))
    if framerate != PROPER_FRAMERATE:
        criterion.add_warning(Warning(f"Wrong framerate : {framerate} (should be {PROPER_FRAMERATE})"))


# Documentation
documentation = """
# Scene Frame Rate

(This Criterion is a placeholder for demonstration purposes)

If the framerate is wrong, press "Set Proper Framerate" in the assistant tab.
"""


# Assistant Widget
class Assistant(AssistantWidget):
    def __init__(self, criterion: Criterion):
        super().__init__(criterion)
        layout = QVBoxLayout(self)

        if self.criterion.status == CriterionStatus.WAITING:
            layout.addWidget(QLabel("The verification has not been done yet"))
            return

        if not self.criterion.warnings:
            layout.addWidget(QLabel(f"The frame rate of the scene is correct ({PROPER_FRAMERATE})"))
            return

        message = self.criterion.warnings[0].message
        layout.addWidget(QLabel(message))
        button = QPushButton("Set Proper Framerate")
        button.setFixedWidth(150)
        layout.addWidget(button)
        button.clicked.connect(self.set_proper_framerate)

    @monitor_action
    def set_proper_framerate(self):
        os.environ["SQPICYQC_FRAMERATE"] = str(PROPER_FRAMERATE)
        # Re-run the verification to update the status/assistant
        self.criterion_widget.verify()


criterion = Criterion(
    label="Scene Frame Rate",
    description="This Criterion verifies the frame rate of the scene",
    verify_callback=check_frame_rate,
    tags=["scene"],
    assistant_widget=Assistant,
    documentation=documentation,
)

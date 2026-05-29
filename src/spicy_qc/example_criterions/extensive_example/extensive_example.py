from functools import partial
from typing import Any

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from spicy_qc import AssistantWidget, Criterion, CriterionStatus, Warning, format_widgets, monitor_action


def function_with_warnings(criterion: Criterion):
    criterion.add_warning(Warning("Something is wrong", "element1"))
    criterion.add_warning(Warning("Something is also wrong", "element2"))
    criterion.add_warning(Warning("Something is very wrong", "element3"))
    criterion.add_warning(Warning("Oh no, it is also wrong!", "element4"))
    criterion.add_warning(Warning("Wrong... Wrong... Wrong...", "element5"))
    criterion.add_warning(Warning("How can there be so much warnings?", "element6"))
    criterion.add_warning(Warning("It worked! ... Just kidding, it didn't", "element7"))
    criterion.add_warning(Warning("You get the idea now. Wrong again", "element8"))
    criterion.add_warning(Warning("Warning, it is wrong, as usual", "element9"))
    criterion.add_warning(Warning("And alas, all was wrong", "element10"))


class MyCustomAssistant(AssistantWidget):
    def __init__(self, criterion: Criterion):
        super().__init__(criterion)

        layout = QVBoxLayout(self)
        title_label = QLabel("Example Assistant Widget")
        # SpicyQC's stylesheets uses properties.
        # Feel free to explore the stylesheet in the utils.py file to see what styling options are available
        title_label.setProperty("status", "H2")
        layout.addWidget(title_label)

        # The AssistantWidget is updated when the "verify" button is pressed
        # You can use it to your advantage and make a layout for the various scenarios
        # Here if the Criterion has not been verified yet
        if self.criterion.status == CriterionStatus.WAITING:
            layout.addWidget(QLabel("The verification has not been done yet"))
            return

        # Or here, if the verification raised no warning
        if not criterion.warnings:
            layout.addWidget(QLabel("There is no warnings"))
            return

        # Each warning has two attributes : "element" (the item causing the issue) and "message"
        # You can use them to build your UI
        element_fixing_frame = QFrame()
        element_fixing_frame.setProperty("depth", "2")
        layout.addWidget(element_fixing_frame)
        grid_layout = QGridLayout(element_fixing_frame)
        for i, warning in enumerate(criterion.warnings):
            # Add element label
            element_label = QLabel(warning.element)
            element_label.setProperty("status", "error")
            grid_layout.addWidget(element_label, i, 0)

            # Add message label
            message_label = QLabel(warning.message)
            message_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred))
            grid_layout.addWidget(message_label, i, 1)

            # Add fix button
            fix_button = QPushButton("Fix")
            fix_button.setProperty("status", "important")
            grid_layout.addWidget(fix_button, i, 2)
            fix_button.clicked.connect(partial(self.fix, warning.element))

            # Be creative, if you need to add extra features other than fixing, please do so!
            select_button = QPushButton("Select")
            select_button.setProperty("status", "important")
            grid_layout.addWidget(select_button, i, 3)
            select_button.clicked.connect(partial(self.select, warning.element))

            troubleshoot_button = QPushButton("Troubleshoot")
            troubleshoot_button.setProperty("status", "important")
            grid_layout.addWidget(troubleshoot_button, i, 4)
            troubleshoot_button.clicked.connect(partial(self.troubleshoot, warning.element))

        # SpicyQC comes with a few options to help you format the way widget looks
        # In this example, it will recursively look into all child widgets, and set the height of buttons
        format_widgets(self)

    @monitor_action
    def fix(self, element: Any):
        print(f"Fixing {element}")

    @monitor_action
    def select(self, element: Any):
        print(f"Selecting {element}")

    @monitor_action
    def troubleshoot(self, element: Any):
        print(f"Troubleshooting {element}")
        raise RuntimeError("There is nothing to troubleshoot. Let's demonstrate how exceptions are handled instead")


criterion = Criterion(
    label="Extensive Example",
    description="This Criterion provides extensive examples of Assistant and Documentation Usage",
    verify_callback=function_with_warnings,
    tags=["example"],
    is_optional=False,
    assistant_widget=MyCustomAssistant,
)

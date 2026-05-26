from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import qtawesome
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,  # noqa: F401
    QSizePolicy,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from spicy_qc.api import Criterion, CriterionStatus
from spicy_qc.gui.utils import format_widgets, get_theme
from spicy_qc.widgets.documentation_widget import DocumentationWidget

if TYPE_CHECKING:
    from spicy_qc.widgets.spicyqc_widget import SpicyQcWidget

THEME = get_theme()


class ToggleAreaButton(QPushButton):
    def __init__(
        self,
        area_name: str,
        criterion_widget: CriterionWidget,
        collapsible_frame: QFrame,
    ):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setProperty("status", "invisible")
        self.area_name = area_name.capitalize()
        self.criterion_widget = criterion_widget
        self.collapsible_frame = collapsible_frame
        self.collapsed = True
        self.update_look()
        self.clicked.connect(self.toggle_area)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(0)
        self.setStyleSheet("margin:0px; padding:3px")

    def expand_frame(self):
        self.collapsed = False
        self.update()

    def collapse_frame(self):
        self.collapsed = True
        self.update()

    def toggle_area(self):
        self.collapsed = not self.collapsed
        self.update()

    def update(self):
        self.update_look()
        self.update_collapsible_frame()
        self.criterion_widget.update_row_height()

    def update_look(self):
        self.setText(f"Show {self.area_name}" if self.collapsed else f"Hide {self.area_name}")
        icon_name = "fa6s.caret-right" if self.collapsed else "fa6s.caret-down"
        self.setIcon(qtawesome.icon(icon_name, color=THEME["icon_color"]))

    def update_collapsible_frame(self):
        self.collapsible_frame.setHidden(self.collapsed)


class CriterionTableItem(QTableWidgetItem):
    """
    This object is only here to recover the row of the selected criterion widget
    CriterionWidgets have no row() method, so we need to find a workaround
    """

    def __init__(self):
        super().__init__()
        self.criterion_widget: CriterionWidget


class CriterionWidget(QFrame):
    def __init__(
        self,
        criterion: Criterion,
        spicy_qc_widget: SpicyQcWidget,
    ):
        super().__init__()
        self.spicy_qc_widget = spicy_qc_widget
        self.table_widget = self.spicy_qc_widget.table_widget
        self.criterion = criterion
        self.table_item: CriterionTableItem | None = None
        self.icon_toggle_collapsed = qtawesome.icon("fa6s.caret-right", scale_factor=1.2, color=THEME["icon_color"])
        self.icon_toggle_expanded = qtawesome.icon("fa6s.caret-down", scale_factor=1.2, color=THEME["icon_color"])
        self.collapsed_height: int = 10
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        # Add a container with a few pixels of margin to make the selection more visually clear
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 0, 0, 0)

        # Layout with the "main frame" and the frame that appears when expanded
        container_frame = QFrame()
        container_frame.setProperty("depth", "4")
        layout.addWidget(container_frame)
        container_layout = QVBoxLayout(container_frame)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Main frame
        main_frame = QFrame()
        container_layout.addWidget(main_frame)
        self.main_layout = QVBoxLayout(main_frame)
        self.main_layout.setContentsMargins(6, 2, 2, 2)
        self.main_layout.setSpacing(3)

        # sub-frames
        frame_top = QFrame()
        frame_top_layout = QHBoxLayout(frame_top)
        frame_top_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(frame_top)

        frame_left = QFrame()
        frame_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        frame_left_layout = QVBoxLayout(frame_left)
        frame_left_layout.setContentsMargins(0, 0, 0, 0)
        frame_left_layout.setSpacing(2)
        frame_top_layout.addWidget(frame_left)

        frame_right = QFrame()
        frame_right_layout = QVBoxLayout(frame_right)
        frame_right_layout.setContentsMargins(0, 0, 0, 0)
        frame_top_layout.addWidget(frame_right)

        subframe_right = QFrame()
        subframe_right_layout = QHBoxLayout(subframe_right)
        subframe_right_layout.setContentsMargins(0, 0, 0, 0)
        frame_right_layout.addWidget(subframe_right)
        # frame_right_layout.addStretch()

        # Name & description
        label = QLabel(self.criterion.label)
        frame_left_layout.addWidget(label)
        description = QLabel(self.criterion.description)
        description.setProperty("status", "secondary")
        frame_left_layout.addWidget(description)

        # Verify Button
        self.verify_button = QPushButton("Verify")
        self.verify_button.setProperty("status", "important")
        subframe_right_layout.addWidget(self.verify_button)

        # Status label
        self.status_label = QLabel()
        size = 24
        self.status_label.setFixedSize(size, size)
        subframe_right_layout.addWidget(self.status_label)
        self.update_status_label()

        # Toggle buttons frame
        toggle_areas_frame = QFrame()
        toggle_areas_layout = QHBoxLayout(toggle_areas_frame)
        toggle_areas_layout.setContentsMargins(0, 0, 0, 0)
        toggle_areas_layout.setSpacing(0)
        frame_left_layout.addWidget(toggle_areas_frame)

        # HIDDEN Assistant Frame
        self.assistant_frame = QFrame()
        self.assistant_frame.setFixedHeight(170)
        self.assistant_frame.setProperty("depth", "4")
        self.assistant_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        assistant_frame_layout = QVBoxLayout(self.assistant_frame)  # noqa: F841
        assistant_frame_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.addWidget(self.assistant_frame)
        # assistant_frame_scroll_area = QScrollArea()
        # assistant_frame_layout.addWidget(assistant_frame_scroll_area)
        # assistant_frame_area_contents = QWidget()
        # assistant_frame_scroll_area.setWidget(assistant_frame_area_contents)
        # assistant_layout = QVBoxLayout(assistant_frame_area_contents)
        self.assistant_frame.setHidden(True)

        # Insert assistant widget
        if self.criterion.assistant_widget:
            self.criterion.assistant_widget.setStyleSheet("background-color:red")
            assistant_frame_layout.addWidget(self.criterion.assistant_widget)
            # assistant_frame_layout.addStretch()
        else:
            print("NO ASSISTANT")

        # self.assistant_widget = AssistantWidget(criterion_widget=self,)

        # HIDDEN Log Frame
        self.log_frame = QFrame()
        self.log_frame.setProperty("depth", "4")
        self.log_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        log_frame_layout = QVBoxLayout(self.log_frame)  # noqa: F841
        log_frame_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.addWidget(self.log_frame)
        self.log_frame.setHidden(True)

        self.stdout_view = QPlainTextEdit()
        self.stdout_view.setProperty("status", "code")
        self.stdout_view.setReadOnly(True)
        self.stdout_view.setFixedHeight(200)
        log_frame_layout.addWidget(self.stdout_view)
        self.stdout_view.setPlainText("Verification was not done yet")

        # HIDDEN documentation Frame
        self.documentation_frame = QFrame()
        self.documentation_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.documentation_frame.setProperty("depth", "4")
        documentation_frame_layout = QVBoxLayout(self.documentation_frame)  # noqa: F841
        documentation_frame_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.addWidget(self.documentation_frame)
        self.documentation_frame.setHidden(True)

        # Documentation widget
        documentation = DocumentationWidget(self)
        documentation_frame_layout.addWidget(documentation)

        # Toggle Assistant Button
        self.toggle_assistant_button = ToggleAreaButton("assistant", self, self.assistant_frame)
        toggle_areas_layout.addWidget(self.toggle_assistant_button)
        if not self.criterion.assistant_widget:
            self.toggle_assistant_button.setDisabled(True)

        # Toggle Logs Button
        self.toggle_logs_button = ToggleAreaButton("logs", self, self.log_frame)
        toggle_areas_layout.addWidget(self.toggle_logs_button)
        if not self.criterion.logs:
            self.toggle_logs_button.setDisabled(True)

        # Toggle Documentation Button
        self.toggle_documentation_button = ToggleAreaButton("documentation", self, self.documentation_frame)
        toggle_areas_layout.addWidget(self.toggle_documentation_button)
        if not self.criterion.documentation:
            self.toggle_documentation_button.setHidden(True)

        # Stretch
        toggle_areas_layout.addStretch()

        # Format widgets
        format_widgets(self)

    def verify(self):
        self.criterion.verify()
        self.update_status_label()
        self.update_stdout_line_edit()

    def setup_signals(self):
        self.verify_button.clicked.connect(self.verify_button_clicked)
        self.toggle_assistant_button.clicked.connect(self.assistant_button_clicked)
        self.toggle_logs_button.clicked.connect(self.logs_button_clicked)
        self.toggle_documentation_button.clicked.connect(self.documentation_button_clicked)

    def assistant_button_clicked(self):
        self.toggle_documentation_button.collapse_frame()
        self.toggle_logs_button.collapse_frame()

    def documentation_button_clicked(self):
        self.toggle_assistant_button.collapse_frame()
        self.toggle_logs_button.collapse_frame()

    def logs_button_clicked(self):
        self.toggle_documentation_button.collapse_frame()
        self.toggle_assistant_button.collapse_frame()

    def verify_button_clicked(self):
        self.update_selection()
        self.spicy_qc_widget.verify_selected_criterions()

    def update_selection(self):
        if self not in self.spicy_qc_widget.selected_criterion_widgets:
            self.table_widget.clearSelection()
            self.table_widget.selectRow(self.current_row)

    def update_stdout_line_edit(self):
        self.stdout_view.setPlainText(self.criterion.logs)

    def update_row_height(self):
        top_height = 80
        assistant_height = self.assistant_frame.height() + self.main_layout.spacing()
        assistant_multiplier = int(self.assistant_frame.isVisible())
        log_height = self.log_frame.sizeHint().height() + self.main_layout.spacing()
        log_multiplier = int(self.log_frame.isVisible())
        documentation_height = self.documentation_frame.sizeHint().height() + self.main_layout.spacing()
        documentation_multiplier = int(self.documentation_frame.isVisible())

        total_height = (
            top_height
            + (documentation_height * documentation_multiplier)
            + (assistant_height * assistant_multiplier)
            + (log_height * log_multiplier)
        )
        self.table_widget.setRowHeight(self.current_row, total_height)

    def update_status_label(self):
        color = {
            CriterionStatus.WAITING: THEME["disabled"],
            CriterionStatus.OK: THEME["ok"],
            CriterionStatus.WARNING: THEME["warning"],
            CriterionStatus.ERROR: THEME["error"],
        }[self.criterion.status]

        icon_name = {
            CriterionStatus.WAITING: "ri.question-fill",
            CriterionStatus.OK: "ri.checkbox-circle-fill",
            CriterionStatus.WARNING: "ri.error-warning-fill",
            CriterionStatus.ERROR: "ri.close-circle-fill",
        }[self.criterion.status]
        icon = qtawesome.icon(icon_name, color=color)
        size = self.status_label.width()
        pixmap = icon.pixmap(size, size)
        self.status_label.setPixmap(pixmap)

    @property
    def current_row(self) -> int:
        if not self.table_item:
            return -1
        return self.table_item.row()


class AssistantWidget(QWidget):
    def __init__(
        self,
        criterion_widget: CriterionWidget,
        element_selection_callback: Callable,
        element_hightlight_callback: Callable,
    ):
        super().__init__()
        self.setMaximumHeight(500)
        self.criterion_widget = criterion_widget
        self.criterion = self.criterion_widget.criterion
        self.element_selection_callback = element_selection_callback
        self.element_hightlight_callback = element_hightlight_callback

    def setup_ui(self):
        layout = self.layout()
        if layout:
            layout.deleteLater()

        main_layout = QVBoxLayout(self)

        if self.criterion.status == CriterionStatus.WAITING:
            self.setup_ui_waiting()

    def setup_ui_waiting(self):
        pass

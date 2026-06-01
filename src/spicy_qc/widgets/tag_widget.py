"""Widget used to render tag badges and preview tag colors."""

import qtawesome
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
)

from spicy_qc.api import Tag


class TagWidget(QFrame):
    """A small badge-style widget used to display tag names and icons."""

    def __init__(self, tag: Tag, size: int = 22):
        """Initialize a tag badge widget.

        Args:
            tag: Tag metadata used to render the widget.
            size: Base height and icon size of the badge.
        """
        super().__init__()
        self.tag = tag
        self._size = size
        self.setup_ui()
        self.update_preview()

    def setup_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self._size)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.icon_label = QLabel()
        self.text_label = QLabel(self.tag.tag)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setMargin(2)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

    def update_preview(self, greyed_out: bool = False):
        """Update the widget appearance to reflect the tag state.

        Args:
            greyed_out: Whether to render the badge in a disabled style.
        """
        # Adjust colors if greyed out
        tag_color = self.tag.tag_color
        tag_text_color = self.tag.tag_text_color
        tag_icon_color = self.tag.tag_icon_color
        if greyed_out:
            tag_color = "#8A8A8A"
            tag_text_color = "#222222"
            tag_icon_color = "#222222"

        # Set text value
        self.text_label.setText(self.tag.tag)

        # Set icon
        if self.tag.tag_icon:
            try:
                icon = qtawesome.icon(self.tag.tag_icon, color=tag_icon_color)
                self.icon_label.setPixmap(icon.pixmap(int(self._size * 0.9), int(self._size * 0.9)))
                self.icon_label.setHidden(False)
            except Exception:
                self.icon_label.setHidden(True)
        else:
            self.icon_label.setHidden(True)

        # Set stylesheet
        right_padding = self._size / 2
        left_padding = right_padding if self.icon_label.isHidden() else right_padding / 2

        self.setStyleSheet(
            f"""
            background-color: {tag_color};
            color: {tag_text_color};
            font-weight: bold;
            font-size:{int(self._size * 0.5)}px;
            border-radius: {int(self._size / 2)}px;
            padding-left:{left_padding}px;
            padding-right:{right_padding}px;
            """
        )
        self.text_label.setStyleSheet(
            """
            background-color: none;
            padding-left:0px;
            padding-right:0px;
            """
        )
        self.icon_label.setStyleSheet(
            """
            padding-left:0px;
            padding-right:0px;
            background-color: none;
            """
        )

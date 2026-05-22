from __future__ import annotations

import io
import sys
import traceback
from contextlib import redirect_stdout
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, Callable

from qtpy.QtWidgets import QWidget


@dataclass
class Tag:
    tag: str
    tag_icon: str = "fa5s.circle"
    tag_color: str = "#4FAB38"
    tag_text_color: str = "#FFFFFF"
    tag_icon_color: str = "#FFFFFF"


class CriterionStatus(StrEnum):
    WAITING = auto()
    OK = auto()
    WARNING = auto()
    ERROR = auto()


class Criterion:
    def __init__(
        self,
        label: str,
        description: str,
        verify_callback: Callable,
        tags: list[str] | None = None,
        is_optional: bool = False,
        fixing_assistant: QWidget | None = None,
        documentation: str = "",
    ) -> None:
        self.label = label
        self.description = description
        self.verify_callback = verify_callback
        self.tags = tags or []
        self.is_optional = is_optional
        self.fixing_assistant = fixing_assistant
        self.documentation = documentation

        # Set intial values
        self.logs: str = "This Criterion has not been verified yet"
        self.status = CriterionStatus.WAITING
        self.warnings: list[Warning] = []

    def add_warning(self, warning: Warning):
        print(warning.message)
        self.warnings.append(warning)

    def verify(self):
        # Clear Warnings
        self.warnings = []

        # Capture stdout to extract lines that are related to this Criterion
        f = TeeStream(sys.stdout)
        with redirect_stdout(f):
            print(f"Verifying {self.label}")
            try:
                self.verify_callback(self)
                self.status = CriterionStatus.OK
            except:  # noqa: E722
                print(traceback.format_exc())
                self.status = CriterionStatus.ERROR

        if self.warnings:
            self.status = CriterionStatus.WARNING

        self.logs = f.getvalue().strip()


class Warning:
    def __init__(self, message: str, element: Any = None) -> None:
        self.message = message
        self.element = element


class TeeStream(io.StringIO):
    """A stream that writes to both an internal buffer and a target stream."""

    def __init__(self, target):
        super().__init__()
        self._target = target

    def write(self, s):
        self._target.write(s)
        self._target.flush()
        return super().write(s)

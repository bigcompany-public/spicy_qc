from __future__ import annotations

import inspect
import io
import sys
import time
import traceback
from contextlib import redirect_stdout
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Callable

from PySide6.QtWidgets import QWidget


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
        assistant_widget: QWidget | None = None,
        documentation: str = "",
    ) -> None:
        self.label = label
        self.description = description
        self.verify_callback = verify_callback
        self.tags = tags or []
        self.is_optional = is_optional
        self.assistant_widget = assistant_widget

        # Capture the file in which a Criterion instance was created
        caller_frame = inspect.stack()[1]
        self._source_file = Path(caller_frame.filename)

        # Get documentation from the documentation.md file next to the criterion instance py file if none is provided
        self.documentation = documentation or self.get_documentation()

        # Set intial values
        self.logs: str = "This Criterion has not been verified yet"
        self.status = CriterionStatus.WAITING
        self.warnings: list[Warning] = []

    def get_documentation(self) -> str:
        path = self._source_file.with_name("documentation.md")
        if not path.exists():
            return ""
        return path.read_text()

    def add_warning(self, warning: Warning):
        print(warning.message)
        self.warnings.append(warning)

    def clear_warnings(self):
        self.warnings = []

    def verify(self):
        self.clear_warnings()
        self.run_verification_while_capturing_stdout()

    def run_verification_while_capturing_stdout(self):
        print("." * 30)
        f = TeeStream(sys.stdout)
        with redirect_stdout(f):
            self.run_verification_with_timer()
        self.logs = f.getvalue().strip()

    def run_verification_with_timer(self):
        start_time = time.perf_counter()
        self.run_verification_and_set_status()
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Verification took {total_time:.4f} seconds")

    def run_verification_and_set_status(self):
        print(f"Verifying {self.label}")
        try:
            self.verify_callback(self)
            self.status = CriterionStatus.OK
        except:  # noqa: E722
            print(traceback.format_exc().strip())
            self.status = CriterionStatus.ERROR

        if self.warnings:
            self.status = CriterionStatus.WARNING


class Warning:
    def __init__(self, message: str, element: Any = None) -> None:
        self.message = message
        self.element = element


class TeeStream(io.StringIO):
    """A stream that writes to both an internal buffer and a target stream."""

    def __init__(self, target):
        super().__init__()
        self._target: io.StringIO = target

    def write(self, s):
        self._target.write(s)
        self._target.flush()
        return super().write(s)

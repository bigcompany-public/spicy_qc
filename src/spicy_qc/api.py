"""Core models, verification helpers, and utilities for SpicyQC.

This module defines the base classes used by the SpicyQC application,
including criterion definitions, verification status handling, stdout
capture support, and a convenience decorator for monitored assistant actions.
"""

from __future__ import annotations

import inspect
import io
import sys
import time
import traceback
from dataclasses import dataclass
from enum import StrEnum, auto
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Type

from pyqttoast import Toast, ToastPreset

if TYPE_CHECKING:
    from spicy_qc.widgets.assistant_widget import AssistantWidget


@dataclass
class Tag:
    """Defines a tag used to group and display Criterions."""

    tag: str
    tag_icon: str = "fa5s.circle"
    tag_color: str = "#4FAB38"
    tag_text_color: str = "#FFFFFF"
    tag_icon_color: str = "#FFFFFF"


class CriterionStatus(StrEnum):
    """Lists the available statuses for Criterions"""

    WAITING = auto()
    OK = auto()
    WARNING = auto()
    ERROR = auto()


class Criterion:
    """Represents a quality criterion that SpicyQC can verify.

    A Criterion wraps the metadata and verification callback for a single
    quality check. It also captures documentation and logs generated during
    verification.
    """

    def __init__(
        self,
        label: str,
        description: str,
        verify_callback: Callable,
        tags: list[str] | None = None,
        is_optional: bool = False,
        assistant_widget: Type[AssistantWidget] | None = None,
        documentation: str = "",
    ) -> None:
        """Initialize a new Criterion instance.

        Args:
            label: Human-readable criterion title.
            description: Short description of the criterion.
            verify_callback: Callable used to verify the criterion.
            tags: List of tag names associated with the criterion.
            is_optional: Whether the criterion is optional.
            assistant_widget: Optional widget class for the Assistant panel.
            documentation: Optional markdown documentation content.
        """
        self.label = label
        self.description = description
        self.verify_callback = verify_callback
        self.tags = tags or ["no tags"]
        self.is_optional = is_optional
        self.assistant_widget = assistant_widget

        # Capture the file in which a Criterion instance was created
        caller_frame = inspect.stack()[1]
        self._source_file = Path(caller_frame.filename)

        # Get documentation from the documentation.md file next to the criterion instance py file if none is provided
        self.documentation = (documentation or self.get_documentation()).strip()

        # Set intial values
        self.logs: str = "This Criterion has not been verified yet"
        self.status = CriterionStatus.WAITING
        self.warnings: list[Warning] = []

    def get_documentation(self) -> str:
        """Load documentation text from a sibling markdown file.

        Returns:
            The resolved markdown documentation string, or an empty string
            when the documentation file does not exist.
        """
        path = self._source_file.with_suffix(".md")
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def add_warning(self, warning: Warning):
        """Record a Warning generated during Criterion verification."""
        print(warning.message)
        self.warnings.append(warning)

    def clear_warnings(self):
        """Clear all warnings from the criterion."""
        self.warnings = []

    def verify(self):
        """Execute the criterion verification callback and capture output."""
        self.clear_warnings()
        self.run_verification_while_capturing_stdout()

    def run_verification_while_capturing_stdout(self):
        """Run verification while capturing stdout into the Criterion logs."""
        print("." * 30)
        with CaptureStdout() as stdout:
            self.run_verification_with_timer()

        self.logs = stdout.text()

    def run_verification_with_timer(self):
        """Run the verification callback and log elapsed time."""
        start_time = time.perf_counter()
        self.run_verification_and_set_status()
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Verification took {total_time:.4f} seconds")

    def run_verification_and_set_status(self):
        """Run the verification callback and set the criterion status."""
        print(f"Verifying {self.label}")
        try:
            self.verify_callback(self)
            self.status = CriterionStatus.OK
        except Exception:
            print(traceback.format_exc().strip())
            self.status = CriterionStatus.ERROR

        if self.warnings:
            self.status = CriterionStatus.WARNING


class Warning:
    """Represents a warning emitted during criterion verification."""

    def __init__(self, message: str, element: Any = None) -> None:
        """Create a new warning instance.

        Args:
            message: Description of the warning.
            element: Optional related element or object.
        """
        self.message = message
        self.element = element


class CaptureStdout:
    """Context manager that captures stdout while still writing to the original stream."""

    def __init__(self):
        """Create a new stdout capture context."""
        self._buffer = io.StringIO()
        self._original_stdout = None

    def __enter__(self):
        self._original_stdout = sys.stdout
        self._tee = _TeeStream(self._original_stdout, self._buffer)
        sys.stdout = self._tee
        return self

    def __exit__(self, *args):
        sys.stdout = self._original_stdout
        self._tee = None

    def text(self) -> str:
        """Return the captured stdout text."""
        return self._buffer.getvalue().strip()


class _TeeStream(io.RawIOBase):
    """Internal stream that writes to both a target and a buffer."""

    def __init__(self, target, buffer):
        self._target = target
        self._buffer = buffer

    def write(self, s):
        self._target.write(s)
        self._target.flush()
        self._buffer.write(s)
        return len(s)


def monitor_action(func):
    """Decorator that captures stdout into the Criterion logs, and shows a Toast if an exception is raised"""

    @wraps(func)
    def wrapper(self: AssistantWidget, *args, **kwargs):
        with CaptureStdout() as stdout:
            try:
                func(self, *args, **kwargs)
            except Exception:
                print(traceback.format_exc())
                toast = Toast(self.spicy_qc_widget)
                toast.setPositionRelativeToWidget(self.spicy_qc_widget)
                toast.setDuration(3000)
                toast.setTitle("SpicyQC")
                toast.setText("An error occured. Check logs for more details")
                toast.applyPreset(ToastPreset.ERROR_DARK)  # Apply style preset
                toast.show()
        self.criterion_widget.criterion.logs += f"\n{stdout.text()}"
        self.criterion_widget.update_stdout_text()

    return wrapper

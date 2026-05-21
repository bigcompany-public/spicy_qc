from dataclasses import dataclass
from enum import StrEnum, auto

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
        tags: list[str],
        is_optional: bool = False,
        fixing_assistant: QWidget | None = None,
        documentation: str = "",
    ) -> None:
        self.label = label
        self.description = description
        self.tags = tags
        self.is_optional = is_optional
        self.fixing_assistant = fixing_assistant
        self.documentation = documentation
        self.logs: str = ""

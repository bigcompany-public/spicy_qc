from spicy_qc.api import Criterion, Tag
from spicy_qc.gui.utils import get_qt_app, get_spyciqc_icon
from spicy_qc.widgets.container import ContainerDialog, ContainerWidget
from spicy_qc.widgets.spicyqc_widget import SpicyQcWidget


def show_spicyqc_dialog(criterions: list[Criterion], tags: list[Tag]) -> None:
    app = get_qt_app()  # noqa: F841
    widget = SpicyQcWidget(criterions, tags)
    container = ContainerWidget(widget, title="SpicyQC", icon=get_spyciqc_icon())
    dialog = ContainerDialog(container)
    dialog.exec()


def main():
    from spicy_qc.example_config import criterions, tags

    show_spicyqc_dialog(criterions, tags)

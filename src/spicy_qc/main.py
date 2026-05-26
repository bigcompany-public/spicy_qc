import importlib.util
import sys
from pathlib import Path

from spicy_qc.api import Criterion, Tag
from spicy_qc.gui.utils import get_qt_app, get_spicyqc_icon
from spicy_qc.widgets.container import ContainerDialog, ContainerWidget
from spicy_qc.widgets.spicyqc_widget import SpicyQcWidget


def get_config_from_path(path: Path | str) -> tuple[list[Tag], list[Criterion]]:
    path = Path(path)
    tags = get_tags_from_path(path)
    criterions = get_criterions_from_path(path)
    return (tags, criterions)


def get_tags_from_path(path: Path) -> list[Tag]:
    py_file = path / "tags.py"
    if not py_file.exists():
        raise FileNotFoundError(f"Path does not exist: {py_file}")

    # Import py file as module
    module_name = "spicyqc.tags"
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore

    # Get Criterion tags from module
    tags = getattr(module, "tags")
    return tags


def get_criterions_from_path(path: Path) -> list[Criterion]:
    criterions = []
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    # Iterate over subdirectories and look for criterions
    for subdir in path.iterdir():
        if not subdir.is_dir():
            continue
        if subdir.name.startswith("__"):  # Ignore pycache
            continue
        criterion_name = subdir.name
        module_name = f"spicyqc.{criterion_name}"
        py_file = subdir / f"{criterion_name}.py"

        # Import py file as module
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        module = importlib.util.module_from_spec(spec)  # type: ignore
        sys.modules[module_name] = module
        spec.loader.exec_module(module)  # type: ignore

        # Get Criterion instance from module
        criterion = getattr(module, criterion_name)
        criterions.append(criterion)

    return criterions


def show_spicyqc_dialog(criterions: list[Criterion], tags: list[Tag]) -> None:
    app = get_qt_app()  # noqa: F841
    widget = SpicyQcWidget(criterions, tags)
    container = ContainerWidget(widget, title="SpicyQC", icon=get_spicyqc_icon())
    dialog = ContainerDialog(container)
    dialog.exec()


def main():
    # App needs to be intanciated here, because some widgets are creating within the configuration
    app = get_qt_app()  # noqa: F841
    tags, criterions = get_config_from_path(Path(__file__).parent / "example_criterions")
    show_spicyqc_dialog(criterions, tags)


if __name__ == "__main__":
    main()

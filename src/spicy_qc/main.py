"""Application entrypoints for loading SpicyQC configuration and launching the dialog."""

import importlib.util
import sys
from pathlib import Path

from spicy_qc.api import Criterion, Tag
from spicy_qc.gui.utils import get_qt_app, get_spicyqc_icon
from spicy_qc.widgets.container import ContainerDialog, ContainerWidget
from spicy_qc.widgets.spicyqc_widget import SpicyQcWidget


def get_config_from_path(path: Path | str) -> tuple[list[Criterion], list[Tag]]:
    """Load criterion and tag configuration from a directory.

    Args:
        path: Path to a SpicyQC configuration folder.

    Returns:
        A tuple containing the list of criterions and the list of tags.
    """
    path = Path(path)
    criterions = get_criterions_from_path(path)
    tags = get_tags_from_path(path)
    return (criterions, tags)


def get_tags_from_path(path: Path) -> list[Tag]:
    """Load tags from a tags.py configuration file.

    Args:
        path: Path to the configuration folder.

    Returns:
        A list of Tag instances defined in the tags.py file.
    """
    py_file = path / "tags.py"
    if not py_file.exists():
        return []

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
    """Load criterions from subdirectories under the given path.

    Args:
        path: Path containing criterion subdirectories.

    Returns:
        A list of Criterion instances imported from each subdirectory.
    """
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
        criterion = getattr(module, "criterion")
        criterions.append(criterion)

    return criterions


def show_spicyqc_dialog(
    criterions: list[Criterion],
    tags: list[Tag] | None = None,
    tag_selection: list[str] | None = None,
    tag_whitelist: list[str] | None = None,
    tag_blacklist: list[str] | None = None,
    lock: bool = False,
) -> None:
    """Create and display the SpicyQC dialog.

    Args:
        criterions: Criterions to display in the dialog.
        tags: Optional global tag definitions.
        tag_selection: Optional tags to preselect.
        tag_whitelist: Optional tag names allowed for display.
        tag_blacklist: Optional tag names excluded from display.
        lock: Whether to lock the filtering controls.
    """
    app = get_qt_app()  # noqa: F841
    widget = SpicyQcWidget(
        criterions=criterions,
        tags=tags,
        tag_selection=tag_selection,
        tag_whitelist=tag_whitelist,
        tag_blacklist=tag_blacklist,
        lock=lock,
    )
    container = ContainerWidget(widget, title="SpicyQC", icon=get_spicyqc_icon())
    dialog = ContainerDialog(container)
    dialog.exec()


def example():
    """Load the example configuration and launch the SpicyQC UI."""
    # App needs to be intanciated here, because some widgets are creating within the configuration
    app = get_qt_app()  # noqa: F841
    criterions, tags = get_config_from_path(Path(__file__).parent / "example_criterions")
    show_spicyqc_dialog(
        criterions,
        tags,
        tag_selection=["scene", "mesh"],
        tag_whitelist=[],
        tag_blacklist=[],
        lock=False,
    )


if __name__ == "__main__":
    example()

from spicy_qc.api import Criterion, Tag, Warning

tags = [
    Tag("mesh", "mdi.grid", "#4FAB38", "#FFFFFF", "#FFFFFF"),
    Tag("material", "mdi.alpha-m-circle", "#388AAB", "#FFFFFF", "#FFFFFF"),
    Tag("rig", "mdi6.bone", "#AB38AB", "#FFFFFF", "#FFFFFF"),
]


def function_ok(criterion: Criterion):
    print("Tout fonctionne")


def function_with_warnings(criterion: Criterion):
    criterion.add_warning(Warning("something is wrong", "element1"))
    criterion.add_warning(Warning("something is also wrong", "element2"))


def function_with_error(criterion: Criterion):
    print("Trying a triple backflip... Just watch !")
    raise RuntimeError("FUK DIS SHEET")


criterions: list[Criterion] = [
    Criterion(
        label="Test That Works",
        description="Just Testing Stuff",
        verify_callback=function_ok,
        tags=["rig"],
        documentation="Yolo",
    ),
    Criterion(
        label="Test With Warnings",
        description="Just Testing Stuff",
        verify_callback=function_with_warnings,
        tags=["mesh"],
    ),
    Criterion(
        label="Test With Error",
        description="Just Testing Stuff",
        verify_callback=function_with_error,
        tags=["mesh"],
    ),
]

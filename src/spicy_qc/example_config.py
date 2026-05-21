from spicy_qc.api import Criterion, Tag

tags = [
    Tag("mesh", "mdi.grid", "#4FAB38", "#FFFFFF", "#FFFFFF"),
    Tag("material", "mdi.alpha-m-circle", "#388AAB", "#FFFFFF", "#FFFFFF"),
    Tag("rig", "mdi6.bone", "#AB38AB", "#FFFFFF", "#FFFFFF"),
]

criterions: list[Criterion] = [
    Criterion(label="Test1", description="Just Testing Stuff", tags=["yolo"], documentation="Yolo"),
    Criterion(label="Test2", description="Just Testing Stuff", tags=["yolo"]),
]

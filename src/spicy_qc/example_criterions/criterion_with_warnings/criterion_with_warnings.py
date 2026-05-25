from spicy_qc.api import Criterion, Warning


def function_with_warnings(criterion: Criterion):
    criterion.add_warning(Warning("something is wrong", "element1"))
    criterion.add_warning(Warning("something is also wrong", "element2"))


criterion_with_warnings = Criterion(
    label="Criterion with warnings",
    description="This criterion will have warnings",
    verify_callback=function_with_warnings,
    tags=["mesh"],
    is_optional=False,
    assistant_widget=None,
)

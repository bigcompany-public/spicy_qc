from spicy_qc.api import Criterion


def function_ok(criterion: Criterion):
    print("Everything was fine here.")


criterion_ok = Criterion(
    label="Criterion working fine",
    description="This criterion will run without warning/errors",
    verify_callback=function_ok,
    tags=["mesh", "rig", "other"],
    is_optional=False,
    assistant_widget=None,
    documentation="# Everything is OK! \n\nIn this criterion, everything will work just fine",
)

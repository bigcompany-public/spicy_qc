from spicy_qc.api import Criterion


def function_with_error(criterion: Criterion):
    print("Attempting something risky.")
    print("Brace yourself for the error!")
    raise RuntimeError("Something went horribly wrong :(")


criterion_with_error = Criterion(
    label="Criterion with error",
    description="This criterion will raise an error",
    verify_callback=function_with_error,
    tags=["material"],
    is_optional=False,
    assistant_widget=None,
)

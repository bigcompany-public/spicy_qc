from spicy_qc import Criterion


def function_with_error(criterion: Criterion):
    print("Attempting something risky.")
    print("Brace yourself for the error!")
    raise RuntimeError("Something went horribly wrong :(")


criterion = Criterion(
    label="Criterion with error",
    description="This criterion will raise an error",
    verify_callback=function_with_error,
    tags=["example"],
    is_optional=True,
)

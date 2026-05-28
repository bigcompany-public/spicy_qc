# TD/Dev Documentation

## Creating Criterions

Create a new `spicyqc_config.py` :memo: file so we can create our first `Criterion`. We will start with the most simple Criterion as possible and iterate over it.

=== "python"
    ```python
    from spicy_qc import Criterion, show_spicyqc_dialog

    def verify_stuff(criterion: Criterion):
        print("Verifying Stuff...")
        print("Success!")

    criterion = Criterion(
        label="Simple Criterion",
        description="Criterion for demonstration purposes",
        verify_callback=verify_stuff
    )

    show_spicyqc_dialog(criterions=[criterion])
    ```

In this piece of code, we have done three things so far:

- Write the function that will be triggered when the `Verify` button is pressed.

    ??? question "What is the `criterion` argument?"
        For now, the `verify_stuff` function does basically nothing, but a `criterion` object will later be used to pass warnings and errors around.  

- Create a new Criterion, in which we fetch the function we wrote.
- Open the SpicyQC dialog, to which we provided our sole Criterion.

!!! success "Here is the result"
    SpicyQC shows up, with a single Criterion that has a name, a description, and a working `Verify` button.

    ![first_criterion_1](img/first_criterion_1.png)

## Adding Warnings

The `criterion` argument of the `verify_stuff` function now comes into play. We can use it to raise warnings.

=== "python"
    ```python
    from spicy_qc import Criterion, Warning, show_spicyqc_dialog

    def verify_stuff(criterion: Criterion):
        print("Verifying Stuff...")
        criterion.add_warning(Warning("Oh no, something went wrong with a few elements in the scene"))
        criterion.add_warning(Warning(message='The object "Knife" has a problem', element="knife"))
        criterion.add_warning(Warning(message='The object "Spoon" has a problem', element="spoon"))
        criterion.add_warning(Warning(message='The object "Fork" has a problem', element="fork"))
        print("Failure...")

    criterion = Criterion(
        label="Simple Criterion",
        description="Criterion for demonstration purposes",
        verify_callback=verify_stuff
    )

    show_spicyqc_dialog(criterions=[criterion])
    ```

!!! success "Here is the result"
    The `Verify` button now displays the ![warning](img/warning.png) label, and the warnings can be read in the logs.

    ![first_criterion_2](img/first_criterion_2.png)


## Creating An Assistant

Let's now provide the user an Assistant widget to help him resolve the issues revealed by the verification process.

=== "python"
    ```python
    # Import additional objects and function to create the UI
    from spicy_qc import AssistantWidget, Criterion, CriterionStatus, Warning, show_spicyqc_dialog
    from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout
    from functools import partial

    def verify_stuff(criterion: Criterion):
        ...

    # Create a PySide6 widget where you basically do anything you want
    class CustomAssistant(AssistantWidget):
        def __init__(self, criterion: Criterion):
            super().__init__(criterion)
            layout = QVBoxLayout(self)
            self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

            if self.criterion.status == CriterionStatus.WAITING:
                layout.addWidget(QLabel("The verification has not been done yet"))
                return

            for warning in self.criterion.warnings:
                if warning.element:
                    button = QPushButton(f"Fix {warning.element}")
                    layout.addWidget(button)
                    button.clicked.connect(partial(self.fix_element, warning.element))

        def fix_element(self, element):
            print(f"Fixing {element}")


    # Pass the newly created class to the Criterion, so it is added to the GUI
    criterion = Criterion(
        label="Simple Criterion",
        description="Criterion for demonstration purposes",
        verify_callback=verify_stuff,
        assistant_widget=CustomAssistant,
    )

    show_spicyqc_dialog(criterions=[criterion])
    ```
import random

from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QLineEdit,
    QSizePolicy,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from spicy_qc.api import Criterion, Tag
from spicy_qc.widgets.criterion_widget import CriterionTableItem, CriterionWidget
from spicy_qc.widgets.table_widget import CriterionTableWidget
from spicy_qc.widgets.tag_filter_widget import TagFilterWidget


class SpicyQcWidget(QWidget):
    def __init__(self, criterions: list[Criterion], tags: list[Tag], is_preset: bool = False):
        super().__init__()
        self.criterions = criterions
        self.tags = tags
        self.ensure_unique_tags()
        self.create_missing_tags()
        self.filter_tags()
        self.is_preset = is_preset
        self.criterion_widgets: list[CriterionWidget] = []
        self.setup_ui()
        self.setup_initial_state()
        self.setup_signals()

    def setup_initial_state(self):
        self.select_all_tags()
        self.create_criterion_widgets()

    def select_all_tags(self):
        self.tag_filter_widget.list_widget.selectAll()

    def ensure_unique_tags(self):
        """Raises an error if a tag name is used multiple time"""
        tag_names = [tag.tag for tag in self.tags]
        for tag_name in tag_names:
            number = tag_names.count(tag_name)
            if number > 1:
                raise ValueError(f'Tag "{tag_name}" cannot be used multiple times')

    def create_missing_tags(self):
        colors = [
            "#29C2AD",
            "#2D9C5B",
            "#327EBD",
            "#2660A1",
            "#352F8F",
            "#A623B8",
            "#8D2455",
            "#AA2A2A",
            "#C06C0C",
            "#97AF11",
        ]
        for criterion in self.criterions:
            for tag_name in criterion.tags:
                available_tag_names = [tag.tag for tag in self.tags]
                if tag_name not in available_tag_names:
                    new_tag = Tag(tag=tag_name, tag_color=random.choice(colors))
                    self.tags.append(new_tag)

    def filter_tags(self):
        """Filters out tags that are used in no Criterion"""
        available_tag_names = [tag.tag for tag in self.tags]
        filtered_tag_names: set[str] = set()
        for criterion in self.criterions:
            for tag_name in criterion.tags:
                if tag_name not in available_tag_names:
                    raise ValueError(
                        f'{criterion.label} : Tag "{tag_name}" is not part of the available tags : {available_tag_names}'
                    )
                filtered_tag_names.add(tag_name)

        self.tags = [tag for tag in self.tags if tag.tag in filtered_tag_names]

    def setup_ui(self):
        self.setMinimumHeight(600)
        self._layout = QVBoxLayout(self)

        # Filtering Options
        self.filtering_frame = QFrame()
        self.filtering_frame.setProperty("depth", "0")
        self.filtering_frame.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self._layout.addWidget(self.filtering_frame)
        filtering_layout = QVBoxLayout(self.filtering_frame)

        filter_form_frame = QFrame()
        filter_form_layout = QFormLayout(filter_form_frame)
        filter_form_layout.setContentsMargins(0, 0, 0, 0)
        filtering_layout.addWidget(filter_form_frame)

        ## Search Bar
        self.line_edit_search = QLineEdit()
        self.line_edit_search.setMaximumWidth(180)
        filter_form_layout.addRow("QuickSearch", self.line_edit_search)

        ## Tags
        self.tag_filter_widget = TagFilterWidget(tags=self.tags, spicyqc_widget=self)
        height = 70 if len(self.tags) > 4 else 35
        self.tag_filter_widget.setFixedHeight(height)
        filter_form_layout.addRow("Tags", self.tag_filter_widget)

        # Criterions
        criterion_frame = QFrame()
        criterion_frame.setProperty("depth", "0")
        criterion_frame.setMinimumHeight(20)
        criterion_frame.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        criterion_frame_layout = QVBoxLayout(criterion_frame)
        criterion_frame_layout.setContentsMargins(2, 2, 2, 2)
        self._layout.addWidget(criterion_frame)

        self.table_widget = CriterionTableWidget(self)
        criterion_frame_layout.addWidget(self.table_widget)

    def setup_signals(self):
        self.line_edit_search.textChanged.connect(self.line_edit_search_changed)

    def line_edit_search_changed(self):
        self.update_visible_columns()

    def update_visible_columns(self):
        for row in range(self.table_widget.rowCount()):
            criterion_widget = self.table_widget.get_criterion_widget_at_row(row)
            self.table_widget.setRowHidden(row, not self.should_be_visible(criterion_widget))

    def create_criterion_widgets(self):
        for criterion in self.criterions:
            self.add_criterion_widget(criterion)

    def should_be_visible(self, criterion_widget: CriterionWidget) -> bool:
        return self.matches_tag_selection(criterion_widget) and self.matches_search(criterion_widget)

    def matches_tag_selection(self, criterion_widget: CriterionWidget) -> bool:
        return any([tag in self.selected_tag_names for tag in criterion_widget.criterion.tags])

    def matches_search(self, criterion_widget: CriterionWidget) -> bool:
        search_string = self.line_edit_search.text().lower().strip()
        if not search_string:
            return True
        return search_string in criterion_widget.criterion.label.lower()

    def get_criterion_widgets_to_show(self) -> list[CriterionWidget]:
        filtered_widgets: list[CriterionWidget] = []

        # Filter by tag
        if self.selected_tag_names:
            for widget in self.criterion_widgets:
                if any([tag in self.selected_tag_names for tag in widget.criterion.tags]):
                    filtered_widgets.append(widget)
        else:
            filtered_widgets = self.criterion_widgets.copy()

        # Filter by search
        search_string = self.line_edit_search.text().lower()
        if search_string:
            filtered_widgets = [
                widget for widget in filtered_widgets if search_string in widget.criterion.label.lower()
            ]

        return filtered_widgets

    @property
    def selected_tag_names(self) -> list[str]:
        return self.tag_filter_widget.selected_tags

    def add_criterion_widget(self, criterion: Criterion):
        criterion_widget = CriterionWidget(criterion=criterion, spicy_qc_widget=self)
        row_number = self.table_widget.rowCount()
        self.table_widget.insertRow(row_number)

        # label item
        label_item = QTableWidgetItem()
        label_item.setText(criterion_widget.criterion.label)
        self.table_widget.setItem(row_number, self.table_widget._label_column_index, label_item)

        # criterion item
        criterion_item = CriterionTableItem()

        # Pass item to the CriterionWidget and vice versa to allow row manipulation later on
        criterion_widget.table_item = criterion_item
        criterion_item.criterion_widget = criterion_widget

        # Add item & widget to the table
        self.table_widget.setItem(row_number, self.table_widget._criterion_column_index, criterion_item)
        self.table_widget.setCellWidget(row_number, self.table_widget._criterion_column_index, criterion_widget)

        # Update row height once all widgets are properly inserted to the table
        criterion_widget.update_row_height()

    @property
    def selected_criterion_widgets(self) -> list[CriterionWidget]:
        return [item.criterion_widget for item in self.table_widget.selectedItems()]

    def verify_selected_criterions(self):
        for criterion_widget in self.selected_criterion_widgets:
            criterion_widget.verify()

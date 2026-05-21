from qtpy.QtWidgets import QFormLayout, QFrame, QLabel, QLineEdit, QSizePolicy, QTableWidgetItem, QVBoxLayout, QWidget

from spicy_qc.api import Criterion, Tag
from spicy_qc.widgets.criterion_widget import CriterionTableItem, CriterionWidget
from spicy_qc.widgets.table_widget import CriterionTableWidget
from spicy_qc.widgets.tag_filter_widget import TagFilterWidget


class SpicyQcWidget(QWidget):
    def __init__(self, criterions: list[Criterion], tags: list[Tag], is_preset: bool = False):
        super().__init__()
        self.criterions = criterions
        self.tags = tags
        self.is_preset = is_preset
        self.criterion_widgets: list[CriterionWidget] = []
        self.setup_ui()
        self.setup_initial_state()

    def setup_ui(self):
        self._layout = QVBoxLayout(self)
        label_title = QLabel("SpicyQC")
        label_title.setProperty("tag", "H2")
        # self._layout.addWidget(label_title)

        # Filtering Options
        self.filtering_frame = QFrame()
        self.filtering_frame.setProperty("depth", "0")
        self.filtering_frame.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self._layout.addWidget(self.filtering_frame)
        filtering_layout = QVBoxLayout(self.filtering_frame)
        label_filters = QLabel("Filters")
        label_filters.setProperty("tag", "H4")
        # filtering_layout.addWidget(label_filters)

        filter_form_frame = QFrame()
        filter_form_layout = QFormLayout(filter_form_frame)
        filter_form_layout.setContentsMargins(0, 0, 0, 0)
        filtering_layout.addWidget(filter_form_frame)

        ## Search Bar
        self.line_edit_search = QLineEdit()
        self.line_edit_search.setMaximumWidth(180)
        filter_form_layout.addRow("QuickSearch", self.line_edit_search)

        ## Tags
        self.tag_filter_widget = TagFilterWidget(tags=self.tags)
        height = 70 if len(self.tags) > 7 else 35
        self.tag_filter_widget.setFixedHeight(height)
        filter_form_layout.addRow("Tags", self.tag_filter_widget)
        # filtering_layout.addWidget(self.tag_filter_widget)

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

    def setup_initial_state(self):
        self.update_items()

    def update_items(self):
        for criterion in self.criterions:
            self.add_criterion(criterion)

    def add_criterion(self, criterion: Criterion):
        row_number = self.table_widget.rowCount()
        self.table_widget.insertRow(row_number)

        # label item
        item = QTableWidgetItem()
        item.setText(criterion.label)
        self.table_widget.setItem(row_number, self.table_widget._label_column_index, item)

        # Create criterion widget
        item = CriterionTableItem()
        job_widget = CriterionWidget(criterion=criterion, spicy_qc_widget=self, table_item=item)
        self.table_widget.setItem(row_number, self.table_widget._criterion_column_index, item)
        self.table_widget.setCellWidget(row_number, self.table_widget._criterion_column_index, job_widget)

        # Update row height once all widgets are properly inserted to the table
        job_widget.update_row_height()

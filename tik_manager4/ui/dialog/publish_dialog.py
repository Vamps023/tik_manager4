"""Dialogs for publishing files."""

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import HeaderLabel, ResolvedText, TikButtonBox, TikButton, TikIconButton

from tik_manager4.ui.dialog.feedback import Feedback


class PublishSceneDialog(QtWidgets.QDialog):
    """Publishes the current scene."""
    def __init__(self, project_object, *args, **kwargs):
        """Initialize the PublishSceneDialog."""
        super(PublishSceneDialog, self).__init__(*args, **kwargs)

        # instanciate the publisher class
        self.feedback = Feedback(parent=self)
        self.project = project_object
        self.project.publisher.resolve()

        self.check_eligibility()

        self.setWindowTitle("Publish Scene")


        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)

        self.header_layout = QtWidgets.QVBoxLayout()
        self.master_layout.addLayout(self.header_layout)

        self.body_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(self.body_layout)

        # squish everything to the top
        self.master_layout.addStretch()

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(self.buttons_layout)

        splitter = QtWidgets.QSplitter(self)
        splitter.setHandleWidth(3)

        self.body_layout.addWidget(splitter)
        splitter.setFrameShape(QtWidgets.QFrame.NoFrame)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        # left body widget and layout
        left_body_widget = QtWidgets.QWidget(splitter)
        left_body_widget.setMinimumHeight(500)
        left_body_layout = QtWidgets.QVBoxLayout(left_body_widget)

        self.left_body_header_layout = QtWidgets.QVBoxLayout()
        left_body_layout.addLayout(self.left_body_header_layout)

        # create a scroll area
        left_body_scroll_area = QtWidgets.QScrollArea(splitter)
        left_body_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        left_body_scroll_area.setFrameShadow(QtWidgets.QFrame.Sunken)
        left_body_scroll_area.setWidgetResizable(True)

        left_body_scroll_area_widget_contents = QtWidgets.QWidget()

        self.left_body_scroll_area_v_lay = QtWidgets.QVBoxLayout(
            left_body_scroll_area_widget_contents
        )


        left_body_scroll_area.setWidget(left_body_scroll_area_widget_contents)
        left_body_layout.addWidget(left_body_scroll_area)


        # right body widget and layout
        right_body_widget = QtWidgets.QWidget(splitter)
        right_body_widget.setMinimumHeight(500)
        right_body_layout = QtWidgets.QVBoxLayout(right_body_widget)

        self.right_body_header_layout = QtWidgets.QVBoxLayout()
        right_body_layout.addLayout(self.right_body_header_layout)

        # create a scroll area
        right_body_scroll_area = QtWidgets.QScrollArea(splitter)
        right_body_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        right_body_scroll_area.setFrameShadow(QtWidgets.QFrame.Sunken)
        right_body_scroll_area.setWidgetResizable(True)

        right_body_scroll_area_widget_contents = QtWidgets.QWidget()

        self.right_body_scroll_area_v_lay = QtWidgets.QVBoxLayout(
            right_body_scroll_area_widget_contents
        )

        right_body_scroll_area.setWidget(right_body_scroll_area_widget_contents)
        right_body_layout.addWidget(right_body_scroll_area)

        # self.right_body_layout = QtWidgets.QVBoxLayout(right_body_widget)
        # self.right_body_layout.setContentsMargins(10, 2, 10, 10)

        self.build_ui()

        self.resize(1000, 600)

    def check_eligibility(self):
        """Checks if the current scene is eligible for publishing."""
        if not self.project.publisher._work_object:
            self.feedback.pop_info(title="Non-valid Scene", text="Current Scene does not belong to a 'Work'. It is required to save scenes as a 'Work' before publishing.")
            # destroy the dialog. make it dispappear
            self.close()
            self.deleteLater()
            # raise Exception("Current Scene does not belong to a 'Work'. It is required to save scenes as a 'Work' before publishing.")
            return

    def build_ui(self):
        header = HeaderLabel("Publish Scene")
        header.set_color("orange")
        self.header_layout.addWidget(header)

        # resolved path
        path = self.project.publisher.relative_scene_path or "Path Not Resolved"
        path_label = ResolvedText(path)
        self.header_layout.addWidget(path_label)
        path_label.set_color("gray")
        name = self.project.publisher.publish_name or "Name Not Resolved"
        name_label = ResolvedText(name)
        name_label.set_color("green")
        self.header_layout.addWidget(name_label)

        # -- TEST --
        # put some test buttons inside left and right body layouts
        # left body layout
        # validations label
        # validations_label = HeaderLabel("Validations")
        validations_label = QtWidgets.QLabel("Validations")
        validations_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.left_body_header_layout.addWidget(validations_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.left_body_header_layout.addWidget(separator)

        # ADD VALIDATIONS HERE
        # -------------------
        for validator_name, validator in self.project.publisher.validators.items():
            validate_row = ValidateRow(validator_object=validator)
            self.left_body_scroll_area_v_lay.addLayout(validate_row)
        # for i in range(5):
        #     validate_row = ValidateRow()
        #     self.left_body_scroll_area_v_lay.addLayout(validate_row)
        # -------------------
        self.left_body_scroll_area_v_lay.addStretch()


        # left_body_header = TikButton("Left Body Header")
        # right body layout
        extracts_label = QtWidgets.QLabel("Extracts")
        extracts_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.right_body_header_layout.addWidget(extracts_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.right_body_header_layout.addWidget(separator)

        # ADD EXTRACTS HERE
        # -------------------
        for i in range(5):
            extract_row = ExtractRow()
            self.right_body_scroll_area_v_lay.addLayout(extract_row)
        # right_body_header = TikButton("Right Body Header")
        # self.right_body_scroll_area_v_lay.addWidget(right_body_header)
        # -------------------
        self.right_body_scroll_area_v_lay.addStretch()



        # buttons layout
        # self.buttons_layout.addStretch()
        button_box = TikButtonBox()
        button_box.addButton("Validate", QtWidgets.QDialogButtonBox.YesRole)
        button_box.addButton("Publish", QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.buttons_layout.addWidget(button_box)

        # SIGNALS
        button_box.rejected.connect(self.reject)

class ValidateRow(QtWidgets.QHBoxLayout):
    """Custom Layout for validation rows."""
    def __init__(self, validator_object, *args, **kwargs):
        """Initialize the ValidateRow."""
        super(ValidateRow, self).__init__(*args, **kwargs)
        self.validator = validator_object
        self.build_widgets()
        self.update_state()

    def build_widgets(self):
        """Build the widgets."""
        # status icon
        # create a vertical line with color
        self.status_icon = QtWidgets.QFrame()
        # make it gray
        self.status_icon.setStyleSheet("background-color: gray;")
        # set the width to 10px
        self.status_icon.setFixedWidth(10)
        self.addWidget(self.status_icon)

        # checkbox
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setChecked(True)
        self.addWidget(self.checkbox)

        # button
        self.button = TikButton(text=self.validator.nice_name or self.validator.name)
        # stretch it to the layout
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.button.setFixedHeight(26)
        self.addWidget(self.button)

        # maintenance icons
        self.info_pb = TikIconButton(icon_name="info.png")
        self.info_pb.set_size(26)
        self.select_pb = TikIconButton(icon_name="select.png")
        self.select_pb.set_size(26)
        self.fix_pb = TikIconButton(icon_name="fix.png")
        self.fix_pb.set_size(26)
        self.addWidget(self.info_pb)
        self.addWidget(self.select_pb)
        self.addWidget(self.fix_pb)

        # SIGNALS
        self.checkbox.stateChanged.connect(self.update_state)
        self.button.clicked.connect(self.validate)
        self.info_pb.clicked.connect(self.pop_info)
        self.fix_pb.clicked.connect(self.fix)
        self.select_pb.clicked.connect(self.select)

    def validate(self):
        """Validate the validator."""
        print("VALIDATING...")
        self.validator.validate()
        self.update_state()

    def pop_info(self):
        """Pop up an information dialog for informing the user what went wrong."""
        information = self.validator.info()
        # TODO: make this a dialog

    def fix(self):
        """Auto Fix the scene."""
        print("FIXING...")
        self.validator.fix()
        self.validator.validate()
        if self.validator.state != "passed":
            # TODO: dialog or some kind of feedback
            pass
        self.update_state()

    def select(self):
        """Select the objects related to the validator."""
        print("SELECTING...")
        self.validator.select()
        self.update_state()

    def update_state(self):
        """Update the availablity of the buttons."""

        _autofixable = self.validator.autofixable
        _ignorable = self.validator.ignorable
        _selectable = self.validator.selectable
        _state = self.validator.state

        # update the buttons
        if not _ignorable:
            self.checkbox.setCheckState(QtCore.Qt.Checked)
            self.checkbox.setEnabled(False)

        if self.checkbox.isChecked():
            self.button.setEnabled(True)
        else:
            self.status_icon.setStyleSheet("background-color: gray;")
            self.button.setEnabled(False)
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)
            return

        if _state == "passed":
            self.status_icon.setStyleSheet("background-color: green;")
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)

        elif _state == "idle":
            self.status_icon.setStyleSheet("background-color: gray;")
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)

        else:
            _fail_colour = "yellow" if _ignorable else "red"
            self.status_icon.setStyleSheet("background-color: {};".format(_fail_colour))
            if _autofixable:
                self.fix_pb.setEnabled(True)
            else:
                self.fix_pb.setEnabled(False)
            if _selectable:
                self.select_pb.setEnabled(True)
            else:
                self.select_pb.setEnabled(False)
            self.info_pb.setEnabled(True)


class ExtractRow(QtWidgets.QHBoxLayout):
    """Custom Layout for extract rows."""
    def __init__(self, extract_object=None, *args, **kwargs):
        """Initialize the ExtractRow."""
        super(ExtractRow, self).__init__(*args, **kwargs)
        self.extract = extract_object
        self.build_widgets()

    def build_widgets(self):
        """Build the widgets."""
        # status icon
        # create a vertical line with color
        self.status_icon = QtWidgets.QFrame()
        # make it gray
        self.status_icon.setStyleSheet("background-color: gray;")
        # set the width to 10px
        self.status_icon.setFixedWidth(10)
        self.addWidget(self.status_icon)

        # checkbox
        self.checkbox = QtWidgets.QCheckBox()
        self.addWidget(self.checkbox)

        # button
        self.label = HeaderLabel(text="Source") # TODO: change this with self.extractor.name
        # stretch it to the layout
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.label.setFixedHeight(32)
        self.addWidget(self.label)

        # maintenance icons
        self.info = TikIconButton(icon_name=self.label.text().lower(), circle=True)
        self.info.set_size(32)
        self.addWidget(self.info)






# test this dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick
    tik = tik_manager4.initialize("Standalone")



    app = QtWidgets.QApplication(sys.argv)

    _style_file = pick.style_file()
    dialog = PublishSceneDialog(tik.project, styleSheet=str(_style_file.readAll(), "utf-8"))


    dialog.show()

    sys.exit(app.exec_())
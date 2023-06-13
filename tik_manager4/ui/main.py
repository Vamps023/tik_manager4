"""Main UI for Tik Manager 4."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

from tik_manager4.ui.mcv.project import TikProjectLayout
from tik_manager4.ui.mcv.subproject_tree import TikSubProjectLayout
from tik_manager4.ui.mcv.task_tree import TikTaskLayout
from tik_manager4.ui.mcv.category import TikCategoryLayout
from tik_manager4.ui.mcv.version import TikVersionLayout
from tik_manager4.ui.dialog.project_dialog import NewProjectDialog, SetProjectDialog
from tik_manager4.ui.dialog.login import LoginDialog
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui import pick
import tik_manager4._version as version
import tik_manager4


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, dcc="Standalone"):
        super(MainUI, self).__init__()

        self.setWindowTitle("Tik Manager {}".format(version.__version__))
        self.tik = tik_manager4.initialize(dcc)
        self.feedback = Feedback(self)
        # set window size
        self.resize(1200, 800)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        # set style
        _style_file = pick.style_file()
        self.setStyleSheet(str(_style_file.readAll(), 'utf-8'))

        # define layouts
        self.master_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.title_layout = QtWidgets.QHBoxLayout()

        self.user_layout = QtWidgets.QHBoxLayout()

        self.project_layout = QtWidgets.QHBoxLayout()

        self.main_layout = QtWidgets.QVBoxLayout()
        # splitter = QtWidgets.QSplitter(self.central_widget, orientation=QtCore.Qt.Horizontal)
        splitter = CustomSplitter(QtCore.Qt.Horizontal, self.central_widget)
        # splitter.setHandleWidth(50)
        # test = pick.pixmap("arrow_left.png")
        # test_label = QtWidgets.QLabel(splitter)
        # test_label.setPixmap(test)
        # splitter = QtWidgets.QSplitter(self.central_widget, orientation=QtCore.Qt.Horizontal, objectName='splitter', frameShape=QtWidgets.QFrame.StyledPanel, frameShadow=QtWidgets.QFrame.Plain)

        self.main_layout.addWidget(splitter)

        subproject_tree_widget = QtWidgets.QWidget(splitter)
        self.subproject_tree_layout = QtWidgets.QVBoxLayout(subproject_tree_widget)
        self.subproject_tree_layout.setContentsMargins(0, 0, 0, 0)

        # # Create a label for the splitter handle
        # splitter_label = QtWidgets.QLabel(splitter)
        # splitter_label.setAlignment(QtCore.Qt.AlignCenter)
        # splitter_label.setText("<>")

        task_tree_widget = QtWidgets.QWidget(splitter)
        self.task_tree_layout = QtWidgets.QVBoxLayout(task_tree_widget)
        self.task_tree_layout.setContentsMargins(2, 2, 2, 2)

        category_widget = QtWidgets.QWidget(splitter)
        self.category_layout = QtWidgets.QVBoxLayout(category_widget)
        self.category_layout.setContentsMargins(2, 2, 2, 2)

        version_widget = QtWidgets.QWidget(splitter)
        self.version_layout = QtWidgets.QVBoxLayout(version_widget)
        self.version_layout.setContentsMargins(2, 2, 2, 2)

        self.buttons_layout = QtWidgets.QHBoxLayout()

        self.master_layout.addLayout(self.title_layout)
        self.master_layout.addLayout(self.user_layout)
        self.master_layout.addLayout(self.project_layout)
        self.master_layout.addLayout(self.main_layout)
        self.master_layout.addLayout(self.buttons_layout)

        self.project_mcv = None
        self.subprojects_mcv = None
        self.tasks_mcv = None
        self.categories_mcv = None
        self.versions_mcv = None

        self.initialize_mcv()
        self.build_menu_bar()

        self.resume_last_selection()

    def resume_last_selection(self):
        """Resume the last selection from the user settings."""
        # project is getting handled by the project object.
        # subproject
        subproject_id = self.tik.user.last_subproject
        if subproject_id:
            # self.tik.project.find_sub_by_id(subproject_id)
            state = self.subprojects_mcv.sub_view.select_by_id(subproject_id)
            if state:
                # if its successfully set, then select the last task
                task_id = self.tik.user.last_task
                if task_id:
                    state = self.tasks_mcv.task_view.select_by_id(task_id)
                    if state:
                    #     # if its successfully set, then select the last category
                        category_index = self.tik.user.last_category or 0
                        self.categories_mcv.set_category_by_index(category_index)
                        work_id = self.tik.user.last_work
                        if work_id:
                            state = self.categories_mcv.work_tree_view.select_by_id(work_id)
                            if state:
                                # if its successfully set, then select the last version
                                version_id = self.tik.user.last_version
                                if version_id:
                                    self.versions_mcv.set_version(version_id)

    def initialize_mcv(self):
        self.project_mcv = TikProjectLayout(self.tik.project)
        self.project_layout.addLayout(self.project_mcv)

        self.subprojects_mcv = TikSubProjectLayout(self.tik.project)
        self.subprojects_mcv.sub_view.hide_columns(["id", "path"])
        self.subproject_tree_layout.addLayout(self.subprojects_mcv)

        self.tasks_mcv = TikTaskLayout()
        self.tasks_mcv.task_view.hide_columns(["id", "path"])
        self.task_tree_layout.addLayout(self.tasks_mcv)

        self.categories_mcv = TikCategoryLayout()
        self.categories_mcv.work_tree_view.hide_columns(["id", "path"])
        self.category_layout.addLayout(self.categories_mcv)

        self.versions_mcv = TikVersionLayout()
        self.version_layout.addLayout(self.versions_mcv)

        self.project_mcv.set_project_btn.clicked.connect(self.on_set_project)
        self.project_mcv.recent_projects_btn.clicked.connect(self.on_recent_projects)
        self.subprojects_mcv.sub_view.item_selected.connect(self.tasks_mcv.task_view.set_tasks)
        self.subprojects_mcv.sub_view.add_item.connect(self.tasks_mcv.task_view.add_task)
        self.tasks_mcv.task_view.item_selected.connect(self.categories_mcv.set_task)
        self.categories_mcv.work_tree_view.item_selected.connect(self.versions_mcv.set_base)

    # override the closeEvent to save the window state
    def closeEvent(self, event):
        self.tik.user.last_subproject = None
        self.tik.user.last_task = None
        self.tik.user.last_category = None
        self.tik.user.last_work = None
        self.tik.user.last_version = None

        self.tik.user.last_project = self.tik.project.name
        # get the currently selected subproject
        _subproject_item = self.subprojects_mcv.sub_view.get_selected_item()
        if _subproject_item:
            self.tik.user.last_subproject = _subproject_item.subproject.id
            _task_item = self.tasks_mcv.task_view.get_selected_item()
            if _task_item:
                # self.tik.user.last_task = _task_item.task.reference_id
                self.tik.user.last_task = _task_item.task.id
                # TODO: Should we consider getting the category name instead of the index?
                # If someone changes the category order, the index will be wrong
                # Do we care?
                _category_index = self.categories_mcv.get_category_index()
                # we can always safely write the category index
                self.tik.user.last_category = _category_index
                _work_item = self.categories_mcv.work_tree_view.get_selected_item()
                if _work_item:
                    self.tik.user.last_work = _work_item.work.id
                    _version_nmb = self.versions_mcv.get_selected_version()
                    # we can always safely write the version number
                    self.tik.user.last_version = _version_nmb

        self.tik.user.resume.apply_settings()
        event.accept()

    def build_menu_bar(self):
        """Build the menu bar."""
        menu_bar = QtWidgets.QMenuBar(self, geometry=QtCore.QRect(0, 0, 1680, 18))
        self.setMenuBar(menu_bar)
        # menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        tools_menu = menu_bar.addMenu("Tools")
        help_menu = menu_bar.addMenu("Help")

        # File Menu
        create_project = QtWidgets.QAction("&Create New Project", self)
        file_menu.addAction(create_project)
        file_menu.addSeparator()
        user_login = QtWidgets.QAction("&User Login", self)
        file_menu.addAction(user_login)
        set_project = QtWidgets.QAction("&Set Project", self)
        file_menu.addAction(set_project)
        placeholder = QtWidgets.QAction("PLACEHOLDER", self)
        tools_menu.addAction(placeholder)

        # Tools Menu

        # Help Menu
        about = QtWidgets.QAction("&About", self)
        help_menu.addAction(about)
        online_docs = QtWidgets.QAction("&Online Documentation", self)
        help_menu.addAction(online_docs)
        help_menu.addSeparator()
        check_for_updates = QtWidgets.QAction("&Check for Updates", self)
        help_menu.addAction(check_for_updates)

        # SIGNALS
        create_project.triggered.connect(self.on_create_new_project)
        user_login.triggered.connect(self.on_login)
        set_project.triggered.connect(self.on_set_project)

    def refresh_project(self):
        """Refresh the project ui."""
        self.project_mcv.refresh()
        self.refresh_subprojects()

    def refresh_subprojects(self):
        """Refresh the subprojects' ui."""
        self.subprojects_mcv.refresh()
        self.refresh_tasks()

    def refresh_tasks(self):
        """Refresh the tasks' ui."""
        self.tasks_mcv.refresh()
        self.refresh_categories()

    def refresh_categories(self):
        """Refresh the categories' ui."""
        self.categories_mcv.clear()
        self.refresh_versions()

    def refresh_versions(self):
        """Refresh the versions' ui."""
        self.versions_mcv.refresh()

    def on_recent_projects(self):
        dialog = SetProjectDialog(self.tik, parent=self)
        if dialog.recents_pop_menu():
            self.refresh_project()

    def on_set_project(self):
        """Launch the set project dialog."""
        dialog = SetProjectDialog(self.tik, parent=self)
        dialog.show()
        if dialog.exec_():
            self.tik.project = dialog.main_object
            # refresh main ui
        self.refresh_project()

    def on_create_new_project(self):
        """Create a new project."""
        # check the user permissions
        if self.tik.project._check_permissions(level=3) != -1:
            dialog = NewProjectDialog(self.tik, parent=self)
            dialog.show()
            if dialog.exec_():
                self.tik.project = dialog.main_object
        else:
            message, title = self.tik.project.log.get_last_message()
            self.feedback.pop_info(title.capitalize(), message)
            return

    def on_login(self):
        """Login."""
        dialog = LoginDialog(self.tik, parent=self)
        dialog.show()

# class CustomSplitterHandle(QtWidgets.QSplitterHandle):
#     def __init__(self, orientation, parent=None):
#         super().__init__(orientation, parent)
#         self.setFixedHeight(16)  # Set the desired height for the handle
#
#     def paintEvent(self, event):
#         painter = QtGui.QPainter(self)
#         painter.fillRect(event.rect(), QtCore.Qt.lightGray)
#
#         # Load and draw the custom image
#         # image_path = "path_to_image.png"
#         pixmap = pick.pixmap("arrow_left_disabled.png")
#         handle_rect = self.rect()
#         pixmap_rect = QtCore.QRect(QtCore.QPoint(0, 0), pixmap.size())
#         pixmap_rect.moveCenter(handle_rect.center())
#         painter.drawPixmap(pixmap_rect, pixmap)
#
#
# class CustomSplitter(QtWidgets.QSplitter):
#     def __init__(self, orientation, parent=None):
#         super().__init__(orientation, parent)
#
#         self.handle = CustomSplitterHandle(orientation, self)
#         self.setHandleWidth(16)  # Set the desired width for the handle


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = MainUI()
    main.show()
    sys.exit(app.exec_())

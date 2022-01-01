import hashlib
import logging
import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.commons import Commons
from tik_manager4.ui import feedback

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

FEED = feedback.Feedback()


class User(object):
    _authenticated = False
    _permission_level = 0

    def __init__(self, commons_directory=None):
        super(User, self).__init__()
        self.settings = Settings()
        self.bookmarks = Settings()
        self.states = Settings()  # is this necessary anymore??
        self.user_directory = None
        self.common_directory = commons_directory  # this is only for programmatically set the commons
        self.commons = None

        self._active_user = None
        # self._password_authenticated = False
        self._validate_user_data()

    @property
    def directory(self):
        return self.user_directory

    @property
    def is_authenticated(self):
        return bool(self._authenticated)

    @classmethod
    def __authenticate_user(cls, state):
        cls._authenticated = state

    @classmethod
    def __set_permission_level(cls, level):
        cls._permission_level = level

    def _validate_user_data(self):
        """Finds or creates user directories and files"""

        _user_root = os.path.expanduser('~')
        self.user_directory = os.path.normpath(os.path.join(_user_root, "TikManager4"))
        if not os.path.isdir(os.path.normpath(self.user_directory)):
            os.makedirs(os.path.normpath(self.user_directory))
        self.settings.settings_file = os.path.join(self.user_directory, "userSettings.json")
        self.bookmarks.settings_file = os.path.join(self.user_directory, "bookmarks.json")

        # Check if the common folder defined in the user settings
        self.common_directory = self.common_directory or self.settings.get_property("commonFolder")
        if not self.common_directory or not os.path.isdir(self.common_directory):
            # if it is not overridden while creating the object ask it from the user
            if not self.common_directory:
                FEED.pop_info(title="Set Commons Directory", text="Commons Directory is not defined. "
                                                                  "Press Continue to select Commons Directory",
                              button_label="Continue")
                self.common_directory = FEED.browse_directory()
            assert self.common_directory, "Commons Directory must be defined to continue"
            self.settings.edit_property("commonFolder", self.common_directory)

        self.commons = Commons(self.common_directory)

        # set the default keys for missing ones
        for key, val in self.commons.manager.get_property("defaultUserSettings").items():
            if not self.settings.get_property(key=key):
                self.settings.add_property(key=key, val=val)

        for key, val in self.commons.manager.get_property("defaultBookmarks").items():
            if not self.bookmarks.get_property(key=key):
                self.bookmarks.add_property(key=key, val=val)

        # set the active user
        active_user = self.bookmarks.get_property("activeUser")
        state, msg = self.set_active_user(active_user, save_to_db=False)
        if state == -1:
            self.set_active_user("Generic", save_to_db=False)
        # if active_user not in self.commons.get_users():
        #     active_user = "Generic"
        # self.set_active_user(active_user, save_to_db=False)

        self.settings.apply_settings()
        self.bookmarks.apply_settings()
        return 1

    def get_active_user(self):
        """Returns the currently active user"""
        return self._active_user

    def set_active_user(self, user_name, password=None, save_to_db=True):
        """Sets the active user to the session"""

        # check if the user exists in common database
        if user_name in self.commons.get_users():
            if password is not None: # try to authenticate the active user
                if self.check_password(user_name, password):
                    self.__authenticate_user(True)
                else:
                    return -1, log.warning("Wrong password provided for user %s" % user_name)
            else:
                self.__authenticate_user(False) # make sure it is not authenticated if no password
            self._active_user = user_name
            if save_to_db:
                self.bookmarks.edit_property("activeUser", self._active_user)
            self.__set_permission_level(self.commons.check_user_permission_level(user_name))
            return user_name, "Success"
        else:
            return -1, log.warning("User %s cannot set because it does not exist in commons database")

    def create_new_user(self, new_user_name, new_user_initials, new_user_password, permission_level,
                        active_user_password=None):
        """Creates a new user and stores it in database"""

        # first check the permissions of active user - Creating new user requires level 3 permissions
        if self._permission_level < 3:
            return -1, log.warning("User %s has no permission to create new users" % self._active_user)

        # Don't allow non-authenticated users to go further
        if active_user_password:
            self.__authenticate_user(self.check_password(self._active_user, active_user_password))
        if not self.is_authenticated:
            return -1, log.warning("Active user is not authenticated or the password is wrong")

        if new_user_name in self.commons.users.all_properties:
            return -1, log.error("User %s already exists. Aborting" % new_user_name)
        user_data = {
            "initials": new_user_initials,
            "pass": self.__hash_pass(new_user_password),
            "permissionLevel": permission_level
        }
        self.commons.users.add_property(new_user_name, user_data)
        self.commons.users.apply_settings()
        return 1, "Success"

    def delete_user(self, user_name):
        """Removes the user from database"""
        if user_name in self.commons.users.all_properties:
            return -1, log.error("%s does not exist. Aborting" % user_name)
        self.commons.users.delete_property(user_name)
        self.commons.users.apply_settings()

    def change_user_password(self, old_password, new_password, user_name=None):
        """Changes the user password"""
        user_name = user_name or self._active_user
        if self.__hash_pass(old_password) == self.commons.users.get_property(user_name).get("pass"):
            self.commons.users.get_property(user_name)["pass"] = self.__hash_pass(new_password)
            self.commons.users.apply_settings()
        else:
            return -1, log.error("Old password for %s does not match" %user_name)
        pass

    def check_password(self, user_name, password):
        """checks the given password against the hashed password"""
        hashed_pass = self.__hash_pass(password)
        if self.commons.users.get_property(user_name).get("pass", "") == hashed_pass:
            return True
        else:
            return False

    def add_project_bookmark(self, project_name, path):
        """Adds the given project to the user bookmark database"""

        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")

        all_bookmark_names = [x.get("name") for x in bookmark_list]
        if project_name in all_bookmark_names:
            return -1, log.warning("Project %s already exists in user bookmarks" % project_name)

        bookmark_list.append({"name": project_name, "path": path})
        self.bookmarks.edit_property(project_name, bookmark_list)
        self.bookmarks.apply_settings()
        return 1, "Project %s added to bookmarks" % project_name

    def delete_project_bookmark(self, project_name):
        """Removes the project from user bookmarks"""

        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")

        for bookmark in bookmark_list:
            if bookmark.get("name") == project_name:
                bookmark_list.pop(bookmark)
                self.bookmarks.edit_property(project_name, bookmark_list)
                return 1, "Project %s removed from bookmarks" % project_name
        return -1, log.warning("Project %s does not exist in bookmarks. Aborting" % project_name)

    def __hash_pass(self, password):
        """Hashes the password"""
        return hashlib.sha1(str(password).encode('utf-8')).hexdigest()

    # def get_project_bookmarks(self):
    #     """Returns list of dictionaries """
    #     return self.bookmarks.get_property("bookmarkedProjects")

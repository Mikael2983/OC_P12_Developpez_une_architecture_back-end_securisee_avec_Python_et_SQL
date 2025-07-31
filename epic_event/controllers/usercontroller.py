"""
Controller module for managing user authentication in the CLI application.

Handles login logic, verifying user credentials using the Collaborator model
and interacting with the CLI through ApplicationView.
"""

from epic_event.views.application_view import ApplicationView
from epic_event.models.collaborator import Collaborator


class UserController:
    """
    Controller responsible for user authentication.

    Uses the `Collaborator` model to verify credentials and interact
    with the user via the CLI interface.
    """

    def __init__(self, SESSION):
        """
        Initialize the user controller with the session state.

        Args:
            SESSION (dict): Global session dictionary used by the CLI app.
        """
        self.app_view = ApplicationView(SESSION)

    def connexion(self, session):
        """
        Authenticate the user by checking credentials from the input menu.

        Prompts the user for their full name and password, and checks them
        against stored data. If authentication fails, displays an error message.

        Args:
            session (Session): SQLAlchemy database session.

        Returns:
            Collaborator | None: The authenticated user object if successful,
                                 or None if authentication fails.
        """
        username, password = self.app_view.display_connection_menu()
        users = session.query(Collaborator).filter_by(full_name=username).all()

        if users:
            user = users[0]

            if user.check_password(password):
                return user
            else:
                self.app_view.display_error_message(
                    "identifiant et/ou mot de passe incorrect")
                self.app_view.break_point()
                return None

        else:
            self.app_view.display_error_message(
                "identifiant et/ou mot de passe incorrect")
            self.app_view.break_point()
            return None

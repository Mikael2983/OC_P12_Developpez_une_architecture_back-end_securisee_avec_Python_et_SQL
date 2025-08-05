"""
Controller module for managing collaborators in the CLI application.

This module handles the creation of `Collaborator` instances based on
user input. It performs minimal validation and relies on the
`ApplicationView` to interact with the user in the terminal.
"""
from typing import Union

from epic_event.models.collaborator import Collaborator
from epic_event.views.application_view import ApplicationView


class CollaboratorController:
    """
    Business controller for managing collaborators.

    Uses the `Collaborator` ORM model and the CLI view `ApplicationView`
    to construct collaborator instances from user-provided data.
    """

    def __init__(self, SESSION):
        """
        Initialize the controller with the current session.

        Args:
            SESSION (dict): Dictionary holding the application's session state.
        """
        self.app_view = ApplicationView(SESSION)

    def create(self, data: dict) -> Union[Collaborator, None]:
        """
        Create a new `Collaborator` instance from the provided data.

        Ensures required fields are present before instantiation.
        If validation fails, displays an error message and returns None.

        Args:
            data (dict): Dictionary containing the collaborator's attributes.

        Returns:
            Collaborator | None: A ready-to-save `Collaborator` instance,
                                 or None if validation fails.
        """
        if not (data["full_name"]
                and data["email"]
                and data["role"]
                and data["password"]):
            self.app_view.display_error_message(
                "Champs obligatoires invalides ou manquants.")
            self.app_view.break_point()
            return None

        collaborator = Collaborator(
            full_name=data["full_name"],
            email=data["email"],
            role=data["role"],
            password=data["password"]
        )

        return collaborator

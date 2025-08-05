"""
Controller dedicated to client management in the CLI application.

This module allows you to create a client instance from the entered data
by the user, applying a minimum validation on mandatory fields.
It relies on the ORM model `Client` and the CLI view `ApplicationView` for
display.
"""
from datetime import date
from typing import Union

from epic_event.models.client import Client

from epic_event.views.application_view import ApplicationView


class ClientController:
    """
    Business controller for customer management.

    Interacts with the `Client` model and the `ApplicationView`view
    to create client objects from the provided data
    by the user.
    """
    def __init__(self, SESSION: dict):
        """
        Initializes the client controller with the user session.

        Args:
            SESSION (dict): Session dictionary containing the current state
                of the application.
        """
        self.app_view = ApplicationView(SESSION)

    def create(self, data: dict) -> Union[Client, None]:
        """
        Create an instance `Client` from the entered data.

        Checks that the mandatory fields are present before instantiating the
            model.
        In case of an error, displays a message and returns None.

        Args:
            data (dict): User data containing the attributes of the client.

        Returns:
            Client | None: A `Client` instance ready to be added to the
                database, or None in case of failed validation.
        """

        if not (data["full_name"]
                and data["email"]
                and data["id_commercial"]):
            self.app_view.display_error_message(
                "Champs obligatoires invalides ou manquants.")
            self.app_view.break_point()
            return None

        client = Client(
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            company_name=data["company_name"],
            created_date=date.today(),
            last_contact_date=data["last_contact_date"],
            id_commercial=data["id_commercial"]
        )

        return client




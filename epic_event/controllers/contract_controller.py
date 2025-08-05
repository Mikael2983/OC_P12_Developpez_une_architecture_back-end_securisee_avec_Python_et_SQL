"""
Controller module for managing contracts in the CLI application.

This module handles the creation of `Contract` instances based on user input,
with minimal validation logic and interaction through the CLI view.

"""
from datetime import date
from typing import Union

from epic_event.models.contract import Contract
from epic_event.views.application_view import ApplicationView


class ContractController:
    """
    Business controller for handling contract creation logic.

    Uses the `Contract` ORM model and the `ApplicationView` to process user
    input and produce contract objects to be persisted in the database.
    """

    def __init__(self, SESSION):
        """
        Initialize the contract controller with the session state.

        Args:
            SESSION (dict): Global session dictionary used by the CLI app.
        """
        self.app_view = ApplicationView(SESSION)

    def create(self, data: dict) -> Union[Contract, None]:
        """
        Create a new `Contract` instance from user-provided data.

        Validates required fields (client ID, total and due amounts, and signed
         status).
        If validation fails, displays an error message and returns None.

        Args:
            data (dict): Dictionary containing contract data fields.

        Returns:
            Contract | None: A new `Contract` object ready to be saved,
                             or None if validation fails.
        """

        if (not data.get("client_id") or
                not data.get("total_amount") or
                not data.get("amount_due") or
                data.get("signed") is None):

            self.app_view.display_error_message(
                "Champs obligatoires invalides ou manquants.")
            self.app_view.break_point()
            return None

        contract = Contract(
            client_id=data["client_id"],
            total_amount=data["total_amount"],
            amount_due=data["amount_due"],
            signed=data["signed"],
            created_date=date.today()
        )
        return contract

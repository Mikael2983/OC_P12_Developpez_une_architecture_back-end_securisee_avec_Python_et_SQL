"""
Controller module for managing events in the CLI application.

This module handles the creation of `Event` instances based on user input,
with minimal validation logic and interaction through the `ApplicationView`
CLI.
"""
from typing import Union

from epic_event.models.event import Event
from epic_event.views.application_view import ApplicationView


class EventController:
    """
    Business controller for handling event creation logic.

    Uses the `Event` ORM model and the `ApplicationView` to process user input
    and create event objects to be persisted in the database.
    """

    def __init__(self, SESSION):
        """
        Initialize the event controller with the session state.

        Args:
            SESSION (dict): Global session dictionary used by the CLI app.
        """
        self.app_view = ApplicationView(SESSION)

    def create(self, data: dict) -> Union[Event, None]:
        """
        Create a new `Event` instance from user-provided data.

        Validates required fields (title, start and end dates, location,
        participants, contract ID).
        In case of an error, displays a message and returns None.

        Args:
            data (dict): Dictionary containing event data fields.

        Returns:
            Event | None: A new `Event` object ready to be saved,
                          or None if validation fails.
        """
        if not (data["title"]
                and data["start_date"]
                and data["end_date"]
                and data["location"]
                and data["participants"]
                and data["contract_id"]):

            self.app_view.display_error_message(
                "Champs obligatoires invalides ou manquants.")
            self.app_view.break_point()
            return None

        event = Event(
            title=data["title"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            location=data["location"],
            participants=data["participants"],
            notes=data["notes"],
            contract_id=data["contract_id"]
        )
        return event

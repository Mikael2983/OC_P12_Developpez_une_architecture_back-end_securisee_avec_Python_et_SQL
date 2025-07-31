"""Event ORM model with validation, error handling, and relationships."""
import logging
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, relationship

from epic_event.models import Collaborator, Contract
from epic_event.models.base import Base
from epic_event.models.entity import Entity

logger = logging.getLogger(__name__)


class Event(Base, Entity):
    """
    ORM model for managing scheduled events, linked to contracts and support
    collaborators.

    Attributes:
        id (int): Primary key.
        title (str): Title of the event.
        start_date (date): Start date of the event.
        end_date (date): End date of the event.
        location (str): Location string.
        participants (int): Number of participants.
        notes (str): Optional notes.
        archived (bool): Soft delete flag.
        contract_id (int): Foreign key to the contract.
        support_id (int): Foreign key to the support collaborator.
    """

    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String)
    participants = Column(Integer, default=0)
    notes = Column(Text)
    archived = Column(Boolean, default=False)

    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    support_id = Column(Integer, ForeignKey('collaborators.id'))

    contract = relationship("Contract", back_populates="event")
    support = relationship("Collaborator", back_populates="events")

    def __str__(self):
        return f"l'événement {self.title}"

    @staticmethod
    def get_field():
        """
        Returns the list of an event’s fields with their labels for display.

        Each item is a list composed of two strings:
            - the technical name of the field used in ORM model,
            - its readable label intended for the user interface.

        Format:
            [["field_name", "Label"], ...]
        """
        return [["id", "Id"],
                ["contract_id", "Id du Contract"],
                ["title", "Titre"],
                ["start_date", "Date de début"],
                ["end_date", "Date de fin"],
                ["location", "Lieu"],
                ["participants", "Participants"],
                ["notes", "Notes"],
                ["support_id", "Id de l'Organisateur"],
                ["archived", "Archivé"]
                ]

    @property
    def formatted_archived(self):
        """ Formatted a Boolean into a String"""
        if self.archived:
            return "OUI"
        return "NON"

    @property
    def formatted_start_date(self):
        """ Formatted datetime into european format"""
        return self.start_date.strftime("%d-%m-%Y %H:%M")

    @property
    def formatted_start_time(self):
        """ Formatted datetime into european format"""
        return self.start_date.strftime("%H:%M")

    @property
    def formatted_end_date(self):
        """ Formatted datetime into european format"""
        return self.end_date.strftime("%d-%m-%Y %H:%M")

    @property
    def formatted_end_time(self):
        """ Formatted datetime into european format"""
        return self.end_date.strftime("%H:%M")

    @staticmethod
    def validate_title(title: str) -> tuple[None, str] | tuple[str, None]:
        """
        Validate that the event has a non-empty title.
        Args:
           title (str): title of the event.

        Raises:
            ValueError: If title is missing or only whitespace.
        """
        if not title or not title.strip():
            error = "Title is required."
            logger.exception(error)
            return None, error
        return title, None

    @staticmethod
    def validate_start_date(
            start_date: datetime
    ) -> tuple[None, str] | tuple[datetime, None]:
        """
        Validate the start date of the event.

        Raises:
            ValueError: If dates are not of type `datetime` or in the expected
             string format,
        """

        if isinstance(start_date, datetime):
            return start_date, None

        if isinstance(start_date, str):

            try:
                start_date = start_date.replace("/", "-")
                start_tested_date = datetime.strptime(
                    start_date.strip(),
                    "%d-%m-%Y %H:%M")
                return start_tested_date, None

            except ValueError:
                msg_error = (f"Date invalide ou au mauvais format (attendu : "
                             f"JJ-MM-AAAA HH:MM) : {start_date}")
                logger.exception(msg_error)
                return None, msg_error

        msg_error = ("La date doit être une instance de `datetime` ou une "
                     "chaîne au format attendu.")

        return None, msg_error

    @staticmethod
    def validate_end_date(
            end_date: datetime,
            start_date: datetime
    ) -> tuple[None, str] | tuple[datetime, None]:
        """
        Validate the end dates of the event.

        Raises:
            ValueError: If dates are not of type `datetime` or in the expected
                    string format, or if start_date > end_date.
        """

        def _parse_strict_datetime(value):

            if isinstance(value, datetime):
                return value, None

            if isinstance(value, str):

                try:
                    value = value.replace("/", "-")
                    tested_end_date = datetime.strptime(
                        value.strip(),
                        "%d-%m-%Y %H:%M"
                    )
                    return tested_end_date, None

                except ValueError:
                    msg_error = (f"Date invalide ou au mauvais format "
                                 f"(attendu : JJ-MM-AAAA HH:MM) : {value}")
                    logger.exception(msg_error)
                    return None, msg_error

            msg_error = ("La date doit être une instance de `datetime` ou une "
                         "chaîne au format attendu.")
            return None, msg_error

        end_date, error = _parse_strict_datetime(end_date)

        if end_date:

            if start_date > end_date:
                error = ("La date de début ne peut pas être postérieure à la "
                         "date de fin.")
                logger.exception(error)
                return None, error

            return end_date, None

        return None, error

    @staticmethod
    def validate_participants(
            participants: str
    ) -> tuple[None, str] | tuple[int, None]:
        """
        Ensure that the number of participants is a non-negative integer.

        Args:
            participants str: number of participants.
        Returns :
            participants: a validated number of participants
        Raises:
            ValueError: If participants is not a positive integer.
        """
        try:
            participants = int(participants)
        except (ValueError, TypeError) as e:
            logger.exception(e)
            return None, e

        if participants < 0:
            msg_error = "Participants must be a positive integer."
            logger.exception(msg_error)
            return None, msg_error

        return participants, None

    @staticmethod
    def validate_contract_id(
            db: Session,
            user: Collaborator,
            contract_id: Column[int]
    ) -> tuple[None, str] | tuple[Column[int], None]:
        """
        Check that the contract exists and is signed.

        Args:
            db (Session): SQLAlchemy session.
            contract_id (int): contract id related to the event.
            user (Collaborator): the connected user

        Returns:
            contract_id (int): a validated contract id.

        Raises:
            ValueError: If contract is not found or not signed.
            SQLAlchemyError : If a database error occurs during the query.

        """
        try:

            contracts = Contract.filter_by_fields(db, id=contract_id)

        except SQLAlchemyError as error:
            return None, error

        if not contracts:
            error = f"Contract ID {contract_id} not found."
            logger.exception(error)
            return None, error

        contract = contracts[0]

        if contract.event:
            error = "this contract already has a linked event"
            return None, error

        if not contract.signed:
            error = "The contract must be signed before assigning to an event."
            logger.exception(error)
            return None, error

        if contract.client.commercial != user and user.role != "admin":
            error = ("you aren't allow to create events for the other "
                     "commercial clients")
            return None, error

        return contract_id, None

    @staticmethod
    def validate_location(location: str):
        return str(location), None

    @staticmethod
    def validate_notes(notes):
        return str(notes), None

    @staticmethod
    def validate_support_id(
            db: Session,
            support_id: Column[int]
    ) -> tuple[None, str] | tuple[int, None] | tuple[None, None]:
        """
        Validate that the support collaborator exists and has the correct role.

        Args:
            db (Session): SQLAlchemy session.
            support_id: id of the collaborator from the support service

        Raises:
            ValueError: If the collaborator is not valid or not in the support
             role.
            SQLAlchemyError : If a database error occurs during the query.
        """
        if support_id is not None:

            try:
                with db.no_autoflush:
                    collaborator = db.query(Collaborator).filter_by(
                        id=support_id).first()

            except SQLAlchemyError as e:
                logger.exception(e)
                return None, e

            if not collaborator:
                error = f"Collaborator ID {support_id} not found."
                logger.exception(error)
                return None, error

            if collaborator.role != "support":
                error = ("The selected collaborator is not in the 'support'"
                         " role.")
                logger.exception(error)
                raise ValueError(error)
            return support_id, None

        return None, None

    @staticmethod
    def validate_archived(archived: str) -> tuple[bool, None]:
        accepted = ["y", "yes", "true", "o", 'oui']
        return archived.lower() in accepted, None

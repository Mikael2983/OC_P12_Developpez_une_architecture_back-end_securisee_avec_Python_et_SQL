"""Contract ORM model with validation, error handling, and relationships."""
import logging

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from epic_event.models import Client
from epic_event.models.database import Base
from epic_event.models.entity import Entity

logger = logging.getLogger(__name__)


class Contract(Base, Entity):
    """
    ORM model representing a service contract tied to a client and optionally
    an event.

    Attributes:
        id (int): Primary key.
        total_amount (str): Total contract amount (stored as string but
            validated as float).
        amount_due (str): Amount due (stored as string but validated as float).
        created_date (date): Date the contract was created.
        signed (bool): Whether the contract has been signed.
        archived (bool): Whether the contract is archived.
        client_id (int): Foreign key to the Client.
    """

    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    total_amount = Column(String, nullable=False)
    amount_due = Column(String, nullable=False)
    created_date = Column(Date)
    signed = Column(Boolean, nullable=False, default=False)
    archived = Column(Boolean, default=False)

    client = relationship("Client", back_populates="contracts")
    event = relationship(
        "Event",
        back_populates="contract",
        uselist=False
    )

    def __str__(self):
        return f"le contract {self.id} du client {self.client.company_name}"

    @property
    def formatted_archived(self):
        """ Formatted Boolean into a String"""
        if self.archived:
            return "OUI"
        return "NON"

    @property
    def formatted_signed(self):
        """ Formatted Boolean into a String"""
        if self.signed:
            return "OUI"
        return "NON"

    @staticmethod
    def get_fields(role, purpose: str) -> list[list[str]]:
        """
        Returns the list of a contract’s fields with their labels for display.

        Each item is a list composed of two strings:
            - the technical name of the field used in the ORM model,
            - its readable label intended for the user interface.

        Args:
            purpose: purpose (str): Either 'list' (default) or "create" or
                'modify' to apply stricter filters.
            role: the connected user's role.
        Returns:
            fields: A list of editable fields, as [field, translation] pairs.

        Format:
            [["field_name", "Label"], ...]
        """
        all_fields = [
            ["id", "Id"],
            ["client_id", "Id du client"],
            ["client.company_name", "Client"],
            ["total_amount", "Montant total"],
            ["amount_due", "Montant dû"],
            ["created_date", "Date de Creation"],
            ["signed", "Signature"],
            ["archived", "Archivé"]
        ]

        excepted_fields = {
            "list": [
                ["client_id", "Id du client"],
                ["archived", "Archivé"]
            ],
            "create": [
                ["id", "Id"],
                ["client.company_name", "Client"],
                ["created_date", "Date de Creation"],
                ["archived", "Archivé"]
            ],
            "modify": [
                ["id", "Id"],
                ["client_id", "Id du client"],
                ["client.company_name", "Client"],
                ["created_date", "Date de Creation"],
                ["archived", "Archivé"]
            ]
        }

        fields = [field for field in all_fields if
                  field not in excepted_fields[purpose]]

        if role == "admin" and purpose != "create":
            fields.append(["archived", "Archivé"])

        if role not in ["admin", "gestion"] and purpose != "list":
            fields = []

        return fields

    @property
    def formatted_created_date(self):
        """ Formatted date into european format"""
        return self.created_date.strftime("%d-%m-%Y")

    @staticmethod
    def validate_signed(signed: Column[bool]) -> tuple[bool, None]:
        """
        Convert string representation of a boolean to a Python boolean.

        Args:
            signed (str): A string like 'True' or 'False'.

        Returns:
            bool: The corresponding boolean value.
        """
        if not isinstance(signed, bool):
            accepted_signed = ['y', 'yes', 'oui', "true", "o"]
            return signed.lower() in accepted_signed, None
        return signed, None

    @staticmethod
    def validate_total_amount(total_amount: str) -> tuple[None, str] | tuple[
        str, None]:
        """
        Validate total and due amounts.

        Args:
            total_amount: Total amount, expected to be convertible to float.

        Returns:
            total_amount: The validated amount or None.
            error: If inputs are not valid numbers or business constraints
             fail else None.
        """
        try:
            total = float(total_amount)
        except (TypeError, ValueError):
            error = "total amount must be valid numeric values."
            logger.exception(error)
            return None, error

        if total < 0:
            error = "Amount must be positive."
            logger.exception(error)
            return None, error

        return str(total_amount), None

    @staticmethod
    def validate_amount_due(
            total_amount: str,
            amount_due: str
    ) -> tuple[None, str] | tuple[str, None]:
        """
        Validate total and due amounts.

        Args:
            total_amount: Total amount, expected to be convertible to float.
            amount_due: Amount due, expected to be convertible to float.
        Returns:
            amount_due : The validated amount or None.
            Error: If inputs are not valid numbers or business constraints
             fail.
        """
        try:
            total = float(total_amount)
            due = float(amount_due)
        except (TypeError, ValueError):
            error = "Amounts must be valid numeric values."
            logger.exception(error)
            return None, error

        if due < 0:
            error = "Amounts must be positive."
            logger.exception(error)
            return None, error
        if due > total:
            error = "Amount due cannot exceed total amount."
            logger.exception(error)
            return None, error

        return str(amount_due), None

    @staticmethod
    def validate_client_id(
            db: Session,
            client_id: int
    ) -> tuple[None, str] | tuple[int, None]:
        """
        Validate that the client ID exists in the database.

        Args:
            db (Session): SQLAlchemy session.
            client_id: id of the client
        Returns:

             client_id : a validated client id.

             msg_error : a error message to display.
        Raises:
            ValueError: If client_id is not set or client does not exist.
            SQLAlchemyError : If a database error occurs during the query.
        """

        if not client_id:
            error = "Missing client_id."
            logger.exception(error)
            return None, error

        with db.no_autoflush:
            client = db.query(Client).filter_by(id=client_id).first()

        if not client:
            error = f"No client found with id={client_id}."
            logger.exception(error)
            return None, error

        return client_id, None

    @staticmethod
    def validate_archived(archived: str) -> tuple[bool, None]:
        accepted = ["y", "yes", "true", "o", 'oui']
        return archived.lower() in accepted, None

"""Client ORM model with validation, error handling, and relationships."""
import logging
import re
from datetime import date, datetime
from typing import Optional, Union

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from epic_event.models.collaborator import Collaborator
from epic_event.models.database import Base
from epic_event.models.entity import Entity

logger = logging.getLogger(__name__)


class Client(Base, Entity):
    """
    ORM model representing a client with validation, error handling,
    and relationships to contracts and collaborators.

    Attributes:
        id (int): Primary key identifier.
        full_name (str): Full name of the client.
        email (str): Email address of the client.
        phone (Optional[str]): Optional phone number.
        company_name (Optional[str]): Optional name of the client company.
        created_date (Optional[date]): Date when the client was created.
        last_contact_date (Optional[date]): Date of the last contact with the client.
        id_commercial (Optional[int]): Foreign key to the commercial collaborator.
        archived (bool): Indicates if the client is archived.
    """

    __tablename__ = 'clients'

    id: int = Column(Integer, primary_key=True)
    full_name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False, unique=True)
    phone: Optional[str] = Column(String)
    company_name: Optional[str] = Column(String)
    created_date: Optional[date] = Column(Date)
    last_contact_date: Optional[date] = Column(Date)
    id_commercial: Optional[int] = Column(Integer,
                                          ForeignKey('collaborators.id'))
    archived: bool = Column(Boolean, default=False)

    contracts = relationship("Contract", back_populates="client")
    commercial = relationship("Collaborator", back_populates="clients")

    def __str__(self):
        return f"le client {self.company_name} representé par {self.full_name}"

    @staticmethod
    def get_fields(role, purpose: str) -> list[list[str]]:
        """
        Returns the list of a client’s fields with their labels for display.

        Each item is a list composed of two strings:
            - the technical name of the field used in ORM model,
            - its readable label intended for the user interface.

        Args:
            purpose: purpose (str): Either 'list' (default) or "create" or
                'modify' to apply stricter filters.
            role: the connected user's role.

        Returns :
            fields: A list of editable fields, as [field, translation] pairs.

        Format:
            [["field_name", "Label"], ...]
        """
        all_fields = [
            ["id", "Id"],
            ["full_name", "Nom du contact"],
            ["email", "Email"],
            ["phone", "Téléphone"],
            ["company_name", "Société"],
            ["created_date", "Date de création"],
            ["last_contact_date", "Dernier contact"],
            ["commercial.full_name", "Commercial"],
            ["id_commercial", "Id Commercial"],
            ["archived", "Archivé"]
        ]
        excepted_fields = {
            "list": [
                ["id_commercial", "Id Commercial"],
                ["archived", "Archivé"]
            ],
            "create": [
                ["id", "Id"],
                ["commercial.full_name", "Commercial"],
                ["created_date", "Date de création"],
                ["archived", "Archivé"]
            ],
            "modify": [
                ["id", "Id"],
                ["commercial.full_name", "Commercial"],
                ["archived", "Archivé"]
            ]
        }

        fields = [field for field in all_fields if
                  field not in excepted_fields[purpose]]

        if role == "admin" and purpose != "create":
            fields.append(["archived", "Archivé"])

        if role not in ["admin", "commercial"] and purpose != "list":
            fields = []

        return fields

    @property
    def formatted_archived(self):
        """ Formatted Boolean into a String"""
        if self.archived:
            return "OUI"
        return "NON"

    @property
    def formatted_created_date(self):
        """ Formatted date into european format"""
        return self.created_date.strftime("%d-%m-%Y")

    @property
    def formatted_last_contact_date(self):
        """ Formatted date into european format"""
        return self.last_contact_date.strftime("%d-%m-%Y")

    @staticmethod
    def validate_full_name(
            full_name: str
    ) -> tuple[None, str] | tuple[str, None]:
        """
        Validates that the full name is not empty, is alphabetical and unique.
        Args:
            full_name: the name to check.

        Raises:
            ValueError: If the name is not a valid string format.
        """
        if not full_name or not full_name.strip():
            msg_error = "Full name must not be empty."
            logger.exception(msg_error)
            return None, msg_error

        if not re.fullmatch(
                r"[A-Za-zÀ-ÖØ-öø-ÿ\- ]+", full_name):
            msg_error = "Full name must be alphabetical."
            logger.exception(msg_error)
            return None, msg_error

        return full_name, None

    @staticmethod
    def validate_email(email: str) -> tuple[None, str] | tuple[str, None]:
        """
        Validate the type and the format of an email.

        Args:
            email (str): The email address to validate.

        Raises:
            ValueError: If the email is not a string or its format is invalid.
        Returns:
            email (str): validate email
        """
        if not isinstance(email, str):
            msg_error = "L'email doit être une chaîne de caractères."
            logger.exception(msg_error)
            return None, msg_error

        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            msg_error = f"Format d'email invalide: {email}"
            logger.exception(msg_error)
            return None, msg_error

        return email, None

    @staticmethod
    def validate_phone(phone: str) -> tuple[None, str] | tuple[str, None]:
        """
        Validates a French phone number in national or international format.

        Args:
            phone (str): The phone number to validate.

        Raises:
            ValueError: If the phone number is not a string or if it does not
                        match the expected French phone number formats.
        Returns:
            phone (str): validate phone number
        """

        if not isinstance(phone, str):
            msg_error = ("Le numéro de téléphone doit être une chaîne de "
                         "caractères.")
            logger.exception(msg_error)
            return None, msg_error

        phone = phone.replace(" ", "")
        national = r"^0[1-9](?:[ .-]?\d{2}){4}$"
        international = r"^\+33[1-9](?:[ .-]?\d{2}){4}$"

        if not (re.fullmatch(national, phone) or re.fullmatch(international,
                                                              phone)):
            msg_error = f"Numéro de téléphone invalide : {phone}"
            logger.exception(msg_error)
            return None, msg_error

        return phone, None

    @staticmethod
    def validate_company_name(company_name: str) -> (
            tuple[None, str] | tuple[str, None]):
        """Validates the company name string.
        Args:
            company_name (str): The company name to validate.

        Raises:
            ValueError: If the company name is not a string or if it's empty'.
        Returns:
            company (str): validate company name
        """
        if not isinstance(company_name, str) or not company_name.strip():
            msg_error = "Le nom de l'entreprise est invalide ou vide."
            logger.exception(msg_error)
            return None, msg_error

        return company_name, None

    @staticmethod
    def validate_last_contact_date(last_contact_date: Union[date, str]) -> \
            tuple[None, str] | tuple[date, None]:
        """
        Validates and converts a value into a `date` object.

        Args:
            last_contact_date (Union[date, str]): The date to validate,
                either as a `date` object or as a string in the format
                "DD-MM-YYYY"

        Returns:
            last_contact_date: The validated `date` object.

        Raises:
            ValueError: If the input is neither a `date` nor a valid string in
                        the "DD-MM-YYYY" format.

        """

        if isinstance(last_contact_date, date):
            return last_contact_date, None
        if isinstance(last_contact_date, str):
            try:
                last_contact_date = last_contact_date.replace(
                    "/", "-"
                )
                return datetime.strptime(
                    last_contact_date.strip(), "%d-%m-%Y"
                ).date(), None
            except ValueError:
                msg_error = (f"Date invalide ou au mauvais format "
                             f"(attendu : JJ-MM-AAAA) : {last_contact_date}")
                logger.exception(msg_error)
                return None, msg_error
        msg_error = "La date doit être une instance de `date` ou une chaîne."
        logger.exception(msg_error)
        return None, msg_error

    @staticmethod
    def validate_archived(archived: str) -> tuple[bool, None]:
        accepted = ["y", "yes", "true", "o", 'oui']
        return archived.lower() in accepted, None

    @staticmethod
    def validate_id_commercial(
            db: Session,
            id_commercial: int
    ) -> tuple[None, str] | tuple[int, None]:
        """
        Validate that the commercial ID exists in the database when admin
        create client.

        Args:
            db (Session): SQLAlchemy session.
            id_commercial: id of the commercial
        Returns:

             commercial_id : a validated commercial id.
             msg_error : a error message to display.
        """

        if not id_commercial:
            error = "Missing commercial id."
            logger.exception(error)
            return None, error

        with db.no_autoflush:
            commercial = db.query(Collaborator).filter_by(
                id=int(id_commercial)
            ).first()

        if not commercial or commercial.role != "commercial":
            error = f"No commercial found with id={id_commercial}."
            logger.exception(error)
            return None, error

        return id_commercial, None

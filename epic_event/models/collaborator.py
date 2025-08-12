"""
Collaborator ORM model with validation, error handling, and relationships.
"""
import logging
import re

import bcrypt
from sqlalchemy import Boolean, Column, Integer, LargeBinary, String
from sqlalchemy.orm import Session, relationship

from epic_event.models.database import Base
from epic_event.models.entity import Entity

SERVICES = ["gestion", "commercial", "support"]
logger = logging.getLogger(__name__)


class Collaborator(Base, Entity):
    """
    ORM model representing a Collaborator with validation, error handling,
    and secure password handling.

    Attributes:
        id (int): Primary key identifier.
        password (bytes): Bcrypt-hashed password.
        full_name (str): Unique full name of the collaborator.
        email (str): Unique email address.
        role (str): Role of the collaborator (e.g., support, commercial).
        archived (bool): Archive status.
    """

    __tablename__ = 'collaborators'

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False, unique=True)
    password = Column(LargeBinary(60), nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False)
    archived = Column(Boolean, default=False)

    events = relationship(
        "Event",
        back_populates="support",
        foreign_keys="Event.support_id"
    )

    clients = relationship("Client", back_populates="commercial")

    def __str__(self):
        return f"le collaborateur {self.full_name} du service {self.role}"

    @property
    def formatted_archived(self):
        """ Formatted a Boolean into a String"""
        if self.archived:
            return "OUI"
        return "NON"

    @staticmethod
    def get_fields(role, purpose: str) -> list[list[str]]:
        """
        Returns the list of a collaborator’s fields with their labels for
        display.

        Each item is a list composed of two strings:
            - the technical name of the field used in the ORM model,
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
            ['full_name', "Nom"],
            ['password', "Mot de passe"],
            ['email', "Email"],
            ['role', "Service"],
            ["archived", "Archivé"]
        ]
        excepted_fields = {
            "list": [
                ['password', "Mot de passe"],
                ["archived", "Archivé"]
            ],
            "create": [
                ["id", "Id"],
                ["archived", "Archivé"]
            ],
            "modify": [
                ["id", "Id"],
                ['password', "Mot de passe"],
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

    @staticmethod
    def validate_full_name(
            db: Session, full_name: str
    ) -> tuple[None, str] | tuple[str, None]:
        """
        Validates that the full name is not empty, is alphabetical and unique.
        Args:
            db (Session): SQLAlchemy session instance.
            full_name (string): full_name to validate
        Returns:
            name (str): a validate full_name
            Error: If the fullname is neither unique nor a valid string
                        format.

        """
        if not full_name or not full_name.strip():
            msg_error = "ValueError : Full name must not be empty."
            return None, msg_error

        # Autorise les lettres, accents, tirets, apostrophes et espaces
        pattern = r"[A-Za-zÀ-ÖØ-öø-ÿ' \-]+"
        if not re.fullmatch(pattern, full_name):
            msg_error = (
                "Full name must contain only letters, spaces, hyphens or "
                "apostrophes.")
            logger.exception(msg_error)
            return None, msg_error

        with db.no_autoflush:
            existing = db.query(Collaborator).filter(
                Collaborator.full_name == full_name
            ).first()

        if existing:
            msg_error = "This full name is already in use."
            logger.exception(msg_error)
            return None, msg_error

        return full_name, None

    @staticmethod
    def validate_email(db: Session, email: str) -> (
            tuple[None, str] | tuple[str, None]):
        """
        Validate the type and the format of an email.

        Args:
            db (Session): SQLAlchemy session instance.
            email (str): The email address to validate.
        Returns:
            mail (str): a validate mail
            Error: If the email is not a string or its format is invalid
                or already in use.
        """

        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(pattern, email or ""):
            error = "Invalid email address format."
            logger.exception(error)
            return None, error

        with db.no_autoflush:
            existing_email = db.query(Collaborator).filter(
                Collaborator.email == email
            ).first()

        if existing_email:
            error = "This email address is already in use."
            logger.exception(error)
            return None, error

        return email, None

    @staticmethod
    def validate_role(role: str) -> tuple[None, str] | tuple[str, None]:
        """
        Validates that the assigned role is among the allowed services.
        args:
            role: the collaborator's role
        Returns:
            role (str): a validate role

        raises: ValueError: if the role is not in the list of possible roles
        """

        if role not in SERVICES and role != "admin":
            error = f"Invalid role '{role}'. Must be one of: {SERVICES}."
            logger.exception(error)
            return None, error
        return role, None

    @staticmethod
    def validate_password(
            password: str
    ) -> tuple[None, str] | tuple[bytes, None]:
        """
        Hashes and stores the given password.

        Args:
            password (str): The plain-text password.

        Raises:
            TypeError: If the password is not a string.
            ValueError: If the password is too long for bcrypt.
        """
        if not password or not password.strip():
            msg_error = "ValueError : password must not be empty."
            return None, msg_error

        salt = bcrypt.gensalt()
        if not isinstance(password, str):
            error = "Password must be a string."
            logger.exception(error)
            return None, error
        if len(password) > 72:
            error = "Password exceeds bcrypt maximum length of 72 characters."
            logger.exception(error)
            return None, error

        password = bcrypt.hashpw(password.encode("utf-8"), salt)

        return password, None

    @staticmethod
    def validate_archived(archived: str) -> tuple[bool, None]:
        accepted = ["y", "yes", "true", "o", 'oui']
        return archived.lower() in accepted, None

    def check_password(self, raw_password: str) -> bool:
        """
        Verifies the given raw password against the stored hash.

        Args:
            raw_password (str): The plain-text password to verify.

        Returns:
            bool: True if the password matches, False otherwise.

        Raises:
            TypeError: If the password is not a string.
            ValueError: If  not a valid bcrypt hash
        """

        if not isinstance(raw_password, str):
            raise TypeError("Password must be a string.")

        try:
            return bcrypt.checkpw(raw_password.encode("utf-8"),
                                  self.password)

        except (ValueError, TypeError) as e:
            logger.exception("Password verification failed: %s", e)
            return False

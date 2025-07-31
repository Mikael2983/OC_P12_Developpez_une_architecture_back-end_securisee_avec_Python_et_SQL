"""
Entity ORM Utilities Module.

This module provides a reusable base class `Entity` for SQLAlchemy ORM models.
It encapsulates common operations such as:

- Filtering records based on nested field relationships (with `__` syntax).
- Sorting by both simple and nested attributes using dot notation.
- Validating and persisting changes with robust error handling.
- Soft-deleting records by toggling an `archived` flag.
- Resolving dotted field paths for deeply nested attribute access.

Classes:
    Entity: Abstract base class for domain models that provides high-level
            database operations.

Typical usage example:

    class Client(Entity, Base):
        __tablename__ = "clients"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        archived = Column(Boolean, default=False)

        def validate_all(self, db):
            ...

    # Then you can use:
    clients = Client.filter_by_fields(session, name="John")
    clients = Client.order_by_fields(session, "name")
    client.update(session, name="Jane Doe")
    client.save(session)
    Client.soft_delete(session, client_id)

"""

import logging
from typing import Any, Dict, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

logger = logging.getLogger(__name__)


class Entity:
    """
    Base class for ORM models providing reusable filtering,
    sorting, saving, updating, and soft deleting features,
    with support for joined relationships and dotted path resolution.
    """

    @staticmethod
    def _resolve(obj: Any, attr_path: str) -> Any:
        """
        Resolves a dotted attribute path (e.g., "user.name") on an object.

        Args:
            obj: Base object to resolve from.
            attr_path: Dotted attribute path.

        """
        current = obj
        for attr in attr_path.split("."):
            if current is None:
                return ""
            current = getattr(current, attr, None)
            if current is None:
                return ""
        return current

    @classmethod
    def filter_by_fields(cls,
                         db: Session,
                         archived: bool = False,
                         **filters: Dict[str, Any]
                         ) -> List[Any]:
        """
        Filter instances based on field-value pairs, supporting nested
        relationships.

        Args:
            db: SQLAlchemy session.
            archived: Include archived objects if True.
            **filters: Key-value pairs where keys may include relations via '.'

        Returns:
            List of filtered ORM instances.

        raise : AttributeError if wrong field in filters
                SQLAlchemyError : If a database error occurs during the query.
        """
        try:
            query = db.query(cls)
            relations = set()

            if hasattr(cls, "archived") and not archived:
                query = query.filter(cls.archived.is_(False))

            for field_path, value in filters.items():
                path_parts = field_path.split(".")
                current_model = cls
                relation_chain = []

                for part in path_parts[:-1]:
                    attr = getattr(current_model, part)
                    relation_chain.append(attr)
                    current_model = attr.property.mapper.class_

                final_attr = getattr(current_model, path_parts[-1])

                for rel in relation_chain:
                    query = query.join(rel)

                query = query.filter(final_attr == value)
                relations.update(path_parts[:-1])

            for rel in relations:
                if hasattr(cls, rel):
                    query = query.options(joinedload(getattr(cls, rel)))

            if cls.__name__ == "Collaborator":
                query = query.filter(~(cls.id == 1))

            return query.all()

        except (AttributeError, SQLAlchemyError) as e:
            logger.exception(e)
            raise

    @classmethod
    def order_by_fields(cls,
                        db: Session,
                        field_path: str,
                        descending: bool = False,
                        archived: bool = False
                        ) -> List[Any]:
        """
        Return all objects ordered by a specified field, including nested
        fields.

        Args:
            db: SQLAlchemy session.
            field_path: Dot-separated field path (e.g. "user.name").
            descending: Sort in descending order if True.
            archived: Include archived records if True.

        Returns:
            Sorted list of ORM instances.

        Raises:
            SQLAlchemyError : If a database error occurs during the query.
        """
        try:
            query = db.query(cls)

            if cls.__name__ == "Collaborator":
                query = query.filter(~(cls.role == "admin"))

            if hasattr(cls, "archived") and not archived:
                with db.no_autoflush:
                    query = query.filter(cls.archived.is_(False))

            if "." in field_path:
                relation = field_path.split(".")[0]
                if hasattr(cls, relation):
                    with db.no_autoflush:
                        query = query.options(
                            joinedload(getattr(cls, relation))
                        )

            results = query.all()

        except SQLAlchemyError as e:
            logger.exception(e)
            raise

        return sorted(results,
                      key=lambda obj: cls._resolve(obj, field_path),
                      reverse=descending
                      )

    def save(self, db: Session) -> str:
        """
        Validate and persist the instance to the database.

        Args:
            db: SQLAlchemy session.

        Returns:
            SQLAlchemyError : If a database error occurs during the commit.
            success str : if the instance is saved
        """
        try:
            db.add(self)
            db.commit()
            logger.info("%s a été créé", self.__class__)
        except SQLAlchemyError as e:
            logger.exception(
                "database error occurs during save: %s.",
                e)
            db.rollback()
            return f"Erreur de base de données lors de la création: {e}."

        return "success"

    def update(self, db: Session) -> str:
        """
        Update the instance with given attributes and persist changes.

        Args:
            db: SQLAlchemy session.

        Returns:
            SQLAlchemyError : If a database error occurs during the commit.
            success message string if entity has been update
        """
        try:
            db.commit()

        except SQLAlchemyError as e:
            db.rollback()
            logger.exception(e)
            return f"Erreur de base de données lors de la modification: {e}."

        logger.info("%s a été mis à jour", self)
        return "success"

    def soft_delete(self, db: Session) -> str:
        """
        Soft deletes an instance by setting 'archived' field to True.

        Args:
            db: SQLAlchemy session.
        Returns:
            Message success: if entity has been archived
        Raises:
            AttributeError: if instance doesn't have the attribute 'archived'
            SQLAlchemyError: If a database error occurs during the commit.
        """
        try:
            self.archived = True
            db.commit()

        except (SQLAlchemyError, AttributeError) as e:
            db.rollback()
            logger.exception(e)
            return f"SQLAlchemyError: {e}"

        logger.info("%s a été archivé", self)
        return "success"

    def hard_delete(self, db: Session) -> str:
        """
        permanently deletes an instance of the database.

        Args:
            db: SQLAlchemy session.
        Returns:
            success message if the instance has been deleted
        Raises:
            SQLAlchemyError: If a database error occurs during the commit.
        """
        try:
            db.delete(self)
            db.commit()
            logger.info("%s a été supprimé", self)
        except SQLAlchemyError as e:
            db.rollback()
            logger.exception(e)
            return f"SQLAlchemyError: {e}"

        return "success"

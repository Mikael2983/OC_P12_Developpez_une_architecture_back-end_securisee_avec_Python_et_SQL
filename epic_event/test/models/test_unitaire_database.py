"""Unit tests for the Database connection module in Epic Event."""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch

from epic_event.models.database import Database


def test_database_initialization_defaults():
    db = Database()
    assert db.db_url == "sqlite:///epic_event.db"
    assert db.engine is not None
    assert db.Base is not None
    assert db.SessionLocal is not None
    assert db.session is None


def test_get_session_returns_session_instance():
    db = Database()
    session = db.get_session()
    assert isinstance(session, Session)
    assert session is db.get_session()


@patch("epic_event.models.database.Base.metadata.create_all")
def test_initialize_database_success(mock_create_all):
    db = Database()
    db.initialize_database()
    mock_create_all.assert_called_once_with(db.engine)


@patch("epic_event.models.database.Base.metadata.create_all",
       side_effect=SQLAlchemyError("DB Error"))
def test_initialize_database_failure(mock_create_all):
    db = Database()
    with pytest.raises(SQLAlchemyError):
        db.initialize_database()


import os
import time
from pathlib import Path
import pytest
import atexit
import psutil
from sqlalchemy import Engine, inspect

from sqlalchemy.exc import SQLAlchemyError

from epic_event.models import Client, Collaborator, Contract, Database, Event
from epic_event.models.base import Base
from epic_event.models.utils import load_test_data_in_database
from epic_event.settings import DATABASES


@pytest.fixture(scope="function")
def db_session():
    """Database session using a shared SQLite file."""
    db = Database(DATABASES["test"], use_null_pool=True)
    db.initialize_database()
    session = db.get_session()
    load_test_data_in_database(session)

    yield session

    session.rollback()
    session.close()

    Base.metadata.drop_all(bind=db.engine)
    db.dispose()


@pytest.fixture(scope="function")
def seed_data_collaborator(db_session):
    admin = db_session.query(Collaborator).filter_by(role="admin").first()

    gestion = db_session.query(Collaborator).filter_by(role="gestion").first()

    commercial = db_session.query(Collaborator).filter_by(
        role="commercial").first()

    support = db_session.query(Collaborator).filter_by(role="support").first()

    return {"admin": admin,
            "gestion": gestion,
            "commercial": commercial,
            "support": support
            }


@pytest.fixture(scope="function")
def seed_data_client(db_session):
    """return client from the database."""

    client = db_session.query(Client).first()
    return client


@pytest.fixture(scope="function")
def seed_data_contract(db_session):
    signed_contract = db_session.query(Contract).filter(
        Contract.signed.is_(True),
        Contract.event == None
    ).first()

    not_signed_contract = db_session.query(Contract).filter(
        Contract.signed.is_(False),
        Contract.event == None
    ).first()

    contract_with_event = db_session.query(Contract).filter(
        Contract.signed.is_(True),
        Contract.event != None
    ).first()

    return [signed_contract, not_signed_contract, contract_with_event]


@pytest.fixture(scope="function")
def seed_data_event(db_session, seed_data_collaborator, seed_data_contract):
    event = db_session.query(Event).first()

    return event
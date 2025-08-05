import pytest

from epic_event.models import Client, Collaborator, Contract, Database, Event
from epic_event.models.database import Base
from epic_event.models.utils import load_data_in_database


@pytest.fixture(scope="function")
def db_path(tmp_path):
    """
    Crée un fichier de base de données SQLite temporaire par test pour éviter
    les verrous partagés et interférences entre tests.
    """
    db_file = tmp_path / "test_database.db"
    yield str(db_file)


@pytest.fixture(scope="function")
def db_session(db_path):
    """
    Base de données isolée par test avec NullPool pour minimiser les verrous.
    """
    db = Database(db_path, use_null_pool=True)
    db.initialize_database()
    session = db.get_session()
    load_data_in_database(session)

    try:
        yield session
    finally:
        try:
            session.rollback()
        except Exception:
            pass
        try:
            session.close()
        except Exception:
            pass
        try:
            Base.metadata.drop_all(bind=db.engine)
        except Exception:
            pass
        try:
            db.engine.dispose()
        except Exception:
            pass


@pytest.fixture(scope="function")
def seed_data_collaborator(db_session):
    result: dict[str, Collaborator] = {}
    users = db_session.query(Collaborator).all()
    for user in users:
        role = user.role
        if role not in result:
            result[role] = user
        else:
            result[f"{user.role}2"] = user

    return result


@pytest.fixture(scope="function")
def seed_data_client(db_session):
    client = db_session.query(Client).first()
    if not client:
        pytest.skip("Aucun client dans la base de données de test.")
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
    if not event:
        pytest.skip("Aucun événement dans la base de données de test.")
    return event

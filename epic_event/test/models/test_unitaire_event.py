"""Unit tests for the Event ORM model"""
from types import SimpleNamespace

import pytest
from datetime import datetime

from epic_event.models import Collaborator
from epic_event.models.event import Event


# ---------- Static Display Fields ----------
@pytest.mark.parametrize(
    "role,purpose,expected_fields",
    [
        ("commercial", "list", [
            ["id", "Id"],
            ["contract.client.company_name", "Client"],
            ["contract_id", "N° du Contrat"],
            ["title", "Titre"],
            ["start_date", "Date de début"],
            ["end_date", "Date de fin"],
            ["location", "Lieu"],
            ["participants", "Nombre de participants"],
            ["notes", "Notes"],
            ["support.full_name", "Organisateur"],
        ]),
        ("commercial", "create", [
            ["contract_id", "N° du Contrat"],
            ["title", "Titre"],
            ["start_date", "Date de début"],
            ["end_date", "Date de fin"],
            ["location", "Lieu"],
            ["participants", "Nombre de participants"],
            ["notes", "Notes"],
        ]),

        ("support", "list", [
            ["id", "Id"],
            ["contract.client.company_name", "Client"],
            ["contract_id", "N° du Contrat"],
            ["title", "Titre"],
            ["start_date", "Date de début"],
            ["end_date", "Date de fin"],
            ["location", "Lieu"],
            ["participants", "Nombre de participants"],
            ["notes", "Notes"],
            ["support.full_name", "Organisateur"],
        ]),
        ("support", "modify", [
            ["title", "Titre"],
            ["start_date", "Date de début"],
            ["end_date", "Date de fin"],
            ["location", "Lieu"],
            ["participants", "Nombre de participants"],
            ["notes", "Notes"],
        ]),
        ("gestion", "list", [
            ["id", "Id"],
            ["contract.client.company_name", "Client"],
            ["contract_id", "N° du Contrat"],
            ["title", "Titre"],
            ["start_date", "Date de début"],
            ["end_date", "Date de fin"],
            ["location", "Lieu"],
            ["participants", "Nombre de participants"],
            ["notes", "Notes"],
            ["support.full_name", "Organisateur"],
        ]),

        ("gestion", "modify", [
            ["support_id", "Id de l'Organisateur"],
        ]),
        ("admin", "list", [
            ["id", "Id"],
            ["contract.client.company_name", "Client"],
            ["contract_id", "N° du Contrat"],
            ["title", "Titre"],
            ["start_date", "Date de début"],
            ["end_date", "Date de fin"],
            ["location", "Lieu"],
            ["participants", "Nombre de participants"],
            ["notes", "Notes"],
            ["support.full_name", "Organisateur"],
            ["archived", "Archivé"],
        ]),
        ("admin", "create", [
            ["contract_id", "N° du Contrat"],
            ["title", "Titre"],
            ["start_date", "Date de début"],
            ["end_date", "Date de fin"],
            ["location", "Lieu"],
            ["participants", "Nombre de participants"],
            ["notes", "Notes"],
        ]),
        ("admin", "modify", [
            ["title", "Titre"],
            ["start_date", "Date de début"],
            ["end_date", "Date de fin"],
            ["location", "Lieu"],
            ["participants", "Nombre de participants"],
            ["notes", "Notes"],
            ["support_id", "Id de l'Organisateur"],
            ["archived", "Archivé"],
        ]),
    ],
)
def test_event_get_fields_roles(role, purpose, expected_fields):
    fields = Event.get_fields(role, purpose)
    assert sorted(fields) == sorted(expected_fields)


# ---------- validate_title ----------
def test_validate_title_empty():
    _, error = Event.validate_title("")
    assert error == "Title is required."


def test_validate_title_ok():
    title, error = Event.validate_title("Conférence")
    assert title == "Conférence"
    assert error is None


# ---------- validate_start_date ----------
def test_validate_start_date_invalid_format():
    _, error = Event.validate_start_date("2024/01/01 15:00")
    assert "Date invalide ou au mauvais format" in error


def test_validate_start_date_ok():
    dt, error = Event.validate_start_date("01-01-2024 15:00")
    assert isinstance(dt, datetime)
    assert error is None


# ---------- validate_end_date ----------
def test_validate_end_date_wrong_order():
    start = datetime(2024, 1, 10, 10, 0)
    end = datetime(2024, 1, 9, 10, 0)
    _, error = Event.validate_end_date(end, start)
    assert "La date de début ne peut pas être postérieure" in error


def test_validate_end_date_invalid_string():
    _, error = Event.validate_end_date(
        "99-99-9999 00:00", datetime.now()
    )
    assert "Date invalide ou au mauvais format" in error


def test_validate_end_date_ok():
    start = datetime(2024, 1, 1, 10, 0)
    end, error = Event.validate_end_date("01-01-2024 12:00", start)
    assert isinstance(end, datetime)
    assert error is None


# ---------- validate_participants ----------
def test_validate_participants_not_integer():
    _, error = Event.validate_participants("abc")
    assert isinstance(error, ValueError)


def test_validate_participants_negative():
    _, error = Event.validate_participants("-5")
    assert "Participants must be a positive integer." in error


def test_validate_participants_ok():
    value, error = Event.validate_participants("150")
    assert value == 150
    assert error is None


# ---------- validate_contract_id ----------
def test_validate_contract_id_not_found(db_session, seed_data_collaborator):
    user = seed_data_collaborator["commercial"]
    _, error = Event.validate_contract_id(db_session, user, 999)
    assert "Contract ID 999 not found." in error


def test_validate_contract_id_unsigned_contract(db_session, seed_data_contract,
                                                seed_data_collaborator):
    contract = seed_data_contract[1]
    user = contract.client.commercial
    _, error = Event.validate_contract_id(db_session, user, contract.id)
    assert "must be signed" in error


def test_validate_contract_id_event_already_exists(db_session,
                                                   seed_data_contract,
                                                   seed_data_collaborator):
    contract = seed_data_contract[2]
    user = contract.client.commercial
    _, error = Event.validate_contract_id(db_session, user, contract.id)
    assert "already has a linked event" in error


def test_validate_contract_id_different_commercial(db_session,
                                                   seed_data_contract,
                                                   seed_data_collaborator):
    commercial2 = Collaborator(
        full_name="Michel",
        email="michel@epic_event.com",
        role="commercial")
    commercial2.password, _ = commercial2.validate_password("password")
    db_session.add(commercial2)
    db_session.commit()

    contract = seed_data_contract[0]
    wrong_user = commercial2
    _, error = Event.validate_contract_id(db_session, wrong_user, contract.id)
    assert "you aren't allow to create events" in error


def test_validate_contract_id_ok(db_session, seed_data_contract,
                                 seed_data_collaborator):
    contract = seed_data_contract[0]
    user = contract.client.commercial
    result, error = Event.validate_contract_id(db_session, user, contract.id)
    assert result == contract.id
    assert error is None


# ---------- validate_support_id ----------
def test_validate_support_id_not_found(db_session):
    _, error = Event.validate_support_id(db_session, 999)
    assert "Collaborator ID 999 not found." in error


def test_validate_support_id_wrong_role(db_session, seed_data_collaborator):
    wrong_user = seed_data_collaborator["commercial"]
    with pytest.raises(ValueError, match="not in the 'support' role"):
        Event.validate_support_id(db_session, wrong_user.id)


def test_validate_support_id_ok(db_session, seed_data_collaborator):
    support = seed_data_collaborator["support"]
    support_id, error = Event.validate_support_id(db_session, support.id)
    assert support_id == support.id
    assert error is None


# ---------- validate_archived ----------
def test_validate_archived_true_values():
    for v in ["y", "yes", "true", "o", "oui"]:
        val, err = Event.validate_archived(v)
        assert val is True
        assert err is None


def test_validate_archived_false():
    val, err = Event.validate_archived("no")
    assert val is False

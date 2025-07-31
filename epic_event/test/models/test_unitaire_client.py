"""Unit tests for the Client ORM model"""

import pytest
import logging
from datetime import date
from epic_event.models.client import Client

logger = logging.getLogger("models.client")


def test_str_representation():
    client = Client(company_name="Client_test", full_name="John Doe")
    assert str(client) == "le client Client_test representé par John Doe"


def test_formatted_archived_property():
    client = Client(archived=True)
    assert client.formatted_archived == "OUI"

    client.archived = False
    assert client.formatted_archived == "NON"


def test_formatted_created_date():
    client = Client(created_date=date(2024, 5, 15))
    assert client.formatted_created_date == "15-05-2024"


def test_formatted_last_contact_date():
    client = Client(last_contact_date=date(2024, 5, 20))
    assert client.formatted_last_contact_date == "20-05-2024"


# --------------------------
# Validation Tests
# --------------------------

def test_validate_full_name_valid():
    name, error = Client.validate_full_name("Jean Dupont")
    assert name == "Jean Dupont"
    assert error is None


@pytest.mark.parametrize("bad_name", ["", "  ", "123", "@@@", None])
def test_validate_full_name_invalid(bad_name, caplog):
    with caplog.at_level(logging.ERROR):
        name, error = Client.validate_full_name(bad_name)
        assert name is None
        assert "Full name" in error
        assert any("Full name" in message for message in caplog.messages)


def test_validate_email_valid():
    email, error = Client.validate_email("jean.dupont@example.com")
    assert email == "jean.dupont@example.com"
    assert error is None


@pytest.mark.parametrize("bad_email",
                         ["", "not-an-email", 123, "@missing.com"])
def test_validate_email_invalid(bad_email, caplog):
    with caplog.at_level(logging.ERROR):
        email, error = Client.validate_email(bad_email)
        assert email is None
        assert "email" in error.lower()


def test_validate_phone_valid_national():
    phone, error = Client.validate_phone("0601020304")
    assert phone == "0601020304"
    assert error is None


def test_validate_phone_valid_international():
    phone, error = Client.validate_phone("+33601020304")
    assert phone == "+33601020304"
    assert error is None


@pytest.mark.parametrize("bad_phone", ["123", "+33", None, "abcdef"])
def test_validate_phone_invalid(bad_phone, caplog):
    with caplog.at_level(logging.ERROR):
        phone, error = Client.validate_phone(bad_phone)
        assert phone is None
        assert "téléphone" in error.lower()


def test_validate_company_name_valid():
    company, error = Client.validate_company_name("OpenAI France")
    assert company == "OpenAI France"
    assert error is None


@pytest.mark.parametrize("bad_company", ["", "  ", None])
def test_validate_company_name_invalid(bad_company, caplog):
    with caplog.at_level(logging.ERROR):
        company, error = Client.validate_company_name(bad_company)
        assert company is None
        assert "entreprise" in error.lower()


def test_validate_last_contact_date_valid_str():
    val, err = Client.validate_last_contact_date("25-07-2025")
    assert val == date(2025, 7, 25)
    assert err is None


def test_validate_last_contact_date_valid_obj():
    d = date(2025, 7, 25)
    val, err = Client.validate_last_contact_date(d)
    assert val == d
    assert err is None


@pytest.mark.parametrize("bad_date", ["2025-07-25", "notadate", 123, None])
def test_validate_last_contact_date_invalid(bad_date, caplog):
    with caplog.at_level(logging.ERROR):
        val, err = Client.validate_last_contact_date(bad_date)
        assert val is None
        assert "date" in err.lower()


@pytest.mark.parametrize("input_value, expected", [
    ("yes", True), ("o", True), ("non", False), ("", False), ("NO", False)
])
def test_validate_archived(input_value, expected):
    result, _ = Client.validate_archived(input_value)
    assert result == expected


def test_update_client_archived(seed_data_client, db_session):
    client = seed_data_client
    original_archived = client.archived
    client.archived = not original_archived
    result = client.update(db_session)
    assert result == "success"
    assert db_session.query(Client).filter_by(id=client.id).first().archived != original_archived
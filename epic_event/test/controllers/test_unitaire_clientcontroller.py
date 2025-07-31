"""Unit tests for ClientController"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from epic_event.controllers.clientcontroller import ClientController
from epic_event.models.client import Client


@pytest.fixture
def mock_cli_session():
    return {"user": MagicMock()}


@pytest.fixture
def controller(mock_cli_session):
    with patch("epic_event.views.application_view.ApplicationView") as MockView:
        return ClientController(mock_cli_session)


def test_create_client_success(controller):
    valid_data = {
        "full_name": "Alice Dupont",
        "email": "alice@example.com",
        "phone": "0123456789",
        "company_name": "Dupont SARL",
        "last_contact_date": date(2024, 1, 15),
        "id_commercial": 1
    }

    client = controller.create(valid_data)
    assert isinstance(client, Client)
    assert client.full_name == "Alice Dupont"
    assert client.created_date == date.today()
    assert client.id_commercial == 1


@pytest.mark.parametrize("missing_field",
                         ["full_name", "email", "id_commercial"])
def test_create_client_missing_required_fields(controller, missing_field):
    data = {
        "full_name": "Alice Dupont",
        "email": "alice@example.com",
        "phone": "0123456789", "company_name": "Dupont SARL",
        "last_contact_date": date(2024, 1, 15),
        "id_commercial": 1,
        missing_field: ""}

    with patch.object(controller.app_view,
                      "display_error_message") as mock_error, \
            patch.object(controller.app_view, "break_point"):
        client = controller.create(data)

    assert client is None
    mock_error.assert_called_once_with(
        "Champs obligatoires invalides ou manquants.")

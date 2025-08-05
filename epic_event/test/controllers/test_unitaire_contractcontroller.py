"""Unit tests for ContractController"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from epic_event.controllers.contract_controller import ContractController
from epic_event.models.contract import Contract


@pytest.fixture
def mock_cli_session():
    return {"user": MagicMock()}


@pytest.fixture
def controller(mock_cli_session):
    with patch("epic_event.views.application_view.ApplicationView") as MockView:
        return ContractController(mock_cli_session)


def test_create_contract_success(controller):
    valid_data = {
        "client_id": 1,
        "total_amount": "5000",
        "amount_due": "1500",
        "signed": True
    }

    contract = controller.create(valid_data)

    assert isinstance(contract, Contract)
    assert contract.client_id == 1
    assert contract.total_amount == "5000"
    assert contract.amount_due == "1500"
    assert contract.signed is True
    assert contract.created_date == date.today()


@pytest.mark.parametrize("missing_field", ["client_id", "total_amount", "amount_due"])
def test_create_contract_missing_required_fields(controller, missing_field):
    data = {
        "client_id": 1,
        "total_amount": "5000",
        "amount_due": "5000",
        "signed": True,
        missing_field: None
    }

    with patch.object(controller.app_view, "display_error_message") as mock_error, \
         patch.object(controller.app_view, "break_point"):
        result = controller.create(data)

    assert result is None
    mock_error.assert_called_once_with("Champs obligatoires invalides ou manquants.")


def test_create_contract_signed_is_none(controller):
    invalid_data = {
        "client_id": 1,
        "total_amount": "5000.0",
        "amount_due": "1500.0",
        "signed": None
    }

    with patch.object(controller.app_view, "display_error_message") as mock_error, \
         patch.object(controller.app_view, "break_point"):
        result = controller.create(invalid_data)

    assert result is None
    mock_error.assert_called_once_with("Champs obligatoires invalides ou manquants.")
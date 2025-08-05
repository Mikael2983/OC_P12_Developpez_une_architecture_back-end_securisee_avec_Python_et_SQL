"""Unit tests for CollaboratorController"""

import pytest
from unittest.mock import MagicMock, patch

from epic_event.controllers.collaborator_controller import CollaboratorController
from epic_event.models.collaborator import Collaborator


@pytest.fixture
def mock_cli_session():
    return {"user": MagicMock()}


@pytest.fixture
def controller(mock_cli_session):
    with patch("epic_event.views.application_view.ApplicationView") as MockView:
        return CollaboratorController(mock_cli_session)


def test_create_collaborator_success(controller):
    valid_data = {
        "full_name": "Jean Martin",
        "email": "jean.martin@example.com",
        "role": "admin",
        "password": "securepass123"
    }

    collaborator = controller.create(valid_data)

    assert isinstance(collaborator, Collaborator)
    assert collaborator.full_name == "Jean Martin"
    assert collaborator.email == "jean.martin@example.com"
    assert collaborator.role == "admin"
    assert collaborator.password == "securepass123"


@pytest.mark.parametrize("missing_field", ["full_name", "email", "role", "password"])
def test_create_collaborator_missing_required_fields(controller, missing_field):
    data = {
        "full_name": "Jean Martin",
        "email": "jean.martin@example.com",
        "role": "admin",
        "password": "securepass123",
        missing_field: ""}

    with patch.object(controller.app_view, "display_error_message") as mock_error, \
         patch.object(controller.app_view, "break_point"):
        result = controller.create(data)

    assert result is None
    mock_error.assert_called_once_with("Champs obligatoires invalides ou manquants.")
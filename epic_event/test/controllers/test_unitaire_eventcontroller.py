"""Unit tests for EventController"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from epic_event.controllers.eventcontroller import EventController
from epic_event.models.event import Event


@pytest.fixture
def mock_cli_session():
    return {"user": MagicMock()}


@pytest.fixture
def controller(mock_cli_session):
    with patch("epic_event.views.application_view.ApplicationView"):
        return EventController(mock_cli_session)


def test_create_event_success(controller):
    valid_data = {
        "title": "Annual Gala",
        "start_date": date(2025, 10, 1),
        "end_date": date(2025, 10, 3),
        "location": "Paris",
        "participants": 250,
        "notes": "Formal dress code",
        "contract_id": 42
    }

    event = controller.create(valid_data)

    assert isinstance(event, Event)
    assert event.title == "Annual Gala"
    assert event.start_date == date(2025, 10, 1)
    assert event.end_date == date(2025, 10, 3)
    assert event.location == "Paris"
    assert event.participants == 250
    assert event.notes == "Formal dress code"
    assert event.contract_id == 42


@pytest.mark.parametrize("missing_field", [
    "title", "start_date", "end_date", "location", "participants", "contract_id"
])
def test_create_event_missing_required_fields(controller, missing_field):
    data = {
        "title": "Annual Gala",
        "start_date": date(2025, 10, 1),
        "end_date": date(2025, 10, 3),
        "location": "Paris",
        "participants": 250, "notes": "Formal dress code",
        "contract_id": 42,
        missing_field: None
    }

    with patch.object(
            controller.app_view,
            "display_error_message") as mock_error, \
         patch.object(controller.app_view, "break_point"):

        result = controller.create(data)

    assert result is None
    mock_error.assert_called_once_with(
        "Champs obligatoires invalides ou manquants.")

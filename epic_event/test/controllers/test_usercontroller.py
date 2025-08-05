"""Unit tests for UserController """

import pytest
from unittest.mock import patch, MagicMock

from epic_event.controllers.user_controller import UserController
from epic_event.models.collaborator import Collaborator


@pytest.fixture
def mock_cli_session():
    return {"user": MagicMock()}


@pytest.fixture
def controller(mock_cli_session):
    with patch("epic_event.views.application_view.ApplicationView") as MockView:
        instance = UserController(mock_cli_session)
        instance.app_view = MockView.return_value
        yield instance


def test_connexion_success(controller, db_session, seed_data_collaborator):
    user = seed_data_collaborator["gestion"]
    controller.app_view.display_connection_menu.return_value = (user.full_name, "alicepass")

    result = controller.connexion(db_session)

    assert isinstance(result, Collaborator)
    assert result.full_name == user.full_name


def test_connexion_incorrect_password(controller, db_session, seed_data_collaborator):
    user = seed_data_collaborator["commercial"]
    controller.app_view.display_connection_menu.return_value = (user.full_name, "wrong-password")

    result = controller.connexion(db_session)

    assert result is None
    controller.app_view.display_error_message.assert_called_once_with(
        "identifiant et/ou mot de passe incorrect"
    )
    controller.app_view.break_point.assert_called_once()


def test_connexion_user_not_found(controller, db_session):
    controller.app_view.display_connection_menu.return_value = ("Inexistant", "any")

    result = controller.connexion(db_session)

    assert result is None
    controller.app_view.display_error_message.assert_called_once_with(
        "utilisateur introuvable"
    )
    controller.app_view.break_point.assert_called_once()

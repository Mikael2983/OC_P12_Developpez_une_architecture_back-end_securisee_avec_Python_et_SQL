"""Unit tests for MainController"""
import pytest
from unittest.mock import MagicMock, patch

from epic_event.controllers.maincontroller import MainController


@pytest.fixture
def mock_session():
    return {"show_archived": False}


@pytest.fixture
def mock_sqlalchemy_session():
    return MagicMock()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.role = "admin"
    user.full_name = "Admin User"
    return user


@pytest.fixture
def controller(mock_session, mock_sqlalchemy_session):
    with patch("epic_event.views.application_view.ApplicationView"), \
            patch("epic_event.controllers.entitycontroller.EntityController"), \
            patch("epic_event.controllers.usercontroller.UserController"), \
            patch("epic_event.views.client_view.ClientView"), \
            patch("epic_event.views.collaborator_view.CollaboratorView"), \
            patch("epic_event.views.contract_view.ContractView"), \
            patch("epic_event.views.event_view.EventView"):
        return MainController(mock_sqlalchemy_session)


def test_run_exits_on_choice_2(controller):
    with patch.object(controller.app_view, "choose_option", return_value="2"), \
            patch.object(controller.app_view,
                         "display_home_menu") as mock_menu:
        controller.run()
        mock_menu.assert_called_once()


def test_run_valid_login_flow(controller):
    with patch.object(controller.app_view,
                      "choose_option",
                      side_effect=["1", "5", "2"]) as mock_choice, \
            patch.object(
                controller.user_controller,
                "connexion") as mock_handle_connection:
        controller.run()
        mock_handle_connection.assert_called_once()
        assert mock_choice.call_count == 3


def test_handle_entity_action_valid_entity(controller, mock_user):
    with patch.object(controller.app_view, "choose_option",
                      side_effect=["1", "5"]), \
            patch.object(controller,
                         "handle_user_role_action") as mock_handle_user_role_action:
        controller.handle_entity_action(mock_user)

        mock_handle_user_role_action.assert_called_with(mock_user,
                                                        "collaborator")


def test_handle_user_role_action_invokes_correct_action(controller, mock_user):
    mock_user.role = "commercial"
    mock_user.full_name = "Jean Dupont"

    with patch.object(controller.entity_controller,
                      "list_entity") as mock_list, \
            patch.object(controller.entity_controller,
                         "filter_by_field_entity") as mock_filter, \
            patch.object(controller.entity_controller,
                         "order_by_field_entity"), \
            patch.object(controller.entity_controller,
                         "show_details_entity") as mock_details, \
            patch.object(controller.entity_controller, "create_entity"), \
            patch.object(controller.app_view, "display_menu_role"), \
            patch.object(controller.app_view, "ask_id", side_effect=["1"]), \
            patch.object(
                controller.app_view,
                "choose_option",
                side_effect=["1", "3", "4", "5", "2"]
            ), \
            patch("builtins.input", return_value=""):
        controller.handle_user_role_action(mock_user, "client")
        mock_details.assert_called()


def test_handle_user_role_action_invalid_role(controller, mock_user):
    mock_user.role = "unauthorized"
    with patch.object(controller.app_view,
                      "display_error_message") as mock_display_error:
        controller.handle_user_role_action(mock_user, "client")
        mock_display_error.assert_called_with(
            "Rôle utilisateur non pris en charge : unauthorized")


def test_details_entity_calls_subactions(controller, mock_user):
    mock_user.role = "admin"
    mock_user.full_name = "Admin User"

    with patch.object(controller.app_view, "choose_option",
                      side_effect=["3", "4"]), \
            patch.object(controller.entity_controller,
                         "show_details_entity") as mock_show_details_entity, \
            patch.object(controller.app_view, "break_point"):
        controller.details_entity(mock_user, 'client')

        args, kwargs = mock_show_details_entity.call_args
        assert args[1] == "client"


def test_show_archived_toggle(controller):
    assert not controller.SESSION["show_archived"]
    controller.show_archived()
    assert controller.SESSION["show_archived"]
    controller.show_archived()
    assert not controller.SESSION["show_archived"]

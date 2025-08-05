"""Unit tests for EntityController"""

import pytest
from unittest.mock import MagicMock, patch

from epic_event.controllers.entity_controller import EntityController
from epic_event.models import Client, Collaborator, Contract, Event
from epic_event.test.conftest import seed_data_collaborator


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.role = "admin"
    user.id = 1
    return user


@pytest.fixture
def entity_controller(mock_user):
    mock_session = {"show_archived": False}
    controller = EntityController(mock_session)
    return controller


def test_get_model_returns_correct_class():
    assert EntityController.get_model("client") == Client
    assert EntityController.get_model("collaborator") == Collaborator
    assert EntityController.get_model("contract") == Contract
    assert EntityController.get_model("event") == Event


def test_list_entity_returns_error_on_empty_list(entity_controller, session,
                                                 mock_user):
    with patch.object(Client, "filter_by_fields", return_value=[]), \
            patch.object(entity_controller.views["client"],
                         "display_entity_list"), \
            patch.object(entity_controller.app_view, "clear_console"):
        error = entity_controller.list_entity(
            session,
            "client",
            mock_user
        )

        assert error == "aucun élément disponible"


def test_create_entity_success(entity_controller, session, mock_user):
    controller = entity_controller

    mock_model = MagicMock()
    mock_model.get_fields.return_value = [["name", "Name"]]

    mock_user.role = "other"

    with patch.object(controller, "get_model", return_value=mock_model), \
            patch.object(controller, "validate_field",
                         return_value=("validated_value", None)), \
            patch.object(controller, "list_entity", return_value=None), \
            patch.object(controller.app_view, "ask_information",
                         return_value="test"), \
            patch.object(controller.app_view, "clear_console"), \
            patch.object(controller.app_view, "display_informative_message"), \
            patch.object(controller.app_view, "display_error_message"), \
            patch.object(controller.app_view,
                         "display_success_message") as mock_success, \
            patch.object(controller.app_view, "break_point"), \
            patch.object(controller.controllers["client"],
                         "create") as mock_create:
        mock_instance = MagicMock()
        mock_instance.save.return_value = "success"
        mock_create.return_value = mock_instance

        controller.create_entity(session, mock_user, "client")

        mock_create.assert_called_once_with({"name": "validated_value"})
        mock_instance.save.assert_called_once_with(session)
        mock_success.assert_called_once_with("client créé avec succès.")


def test_delete_entity_archives_non_admin(entity_controller, session,
                                          mock_user):
    controller = entity_controller
    mock_user.role = "commercial"

    mock_instance = MagicMock()
    mock_instance.soft_delete.return_value = "success"
    mock_instance.hard_delete.return_value = "should not be called"

    mock_model = MagicMock()
    mock_model.filter_by_fields.return_value = [mock_instance]

    with patch.object(controller, "get_model", return_value=mock_model), \
            patch.object(controller, "list_entity"), \
            patch.object(controller.views["client"],
                         "display_entity_list"), \
            patch.object(controller.app_view, "ask_id",
                         side_effect=["1", None]), \
            patch.object(controller.app_view, "valide_choice_menu",
                         return_value=True), \
            patch.object(controller.app_view, "display_success_message"), \
            patch.object(controller.app_view, "break_point"):
        controller.delete_entity(session, mock_user, "client")

        mock_instance.soft_delete.assert_called_once()
        mock_instance.hard_delete.assert_not_called()


def test_validate_field_with_no_validator_returns_error():
    class DummyModel:
        __name__ = "Client"

    field = ["non_existent", "NonExistent"]
    session = MagicMock()
    user = MagicMock()
    data = {}

    value, error = EntityController.validate_field(DummyModel, field, session,
                                                   user, data)
    assert value is None
    assert "n'a pas de méthode" in error


def test_modify_entity_denies_permission(
        entity_controller,
        db_session,
        seed_data_collaborator,
        seed_data_client
):
    controller = entity_controller
    gestionnaire = seed_data_collaborator["gestion"]
    client = seed_data_client


    with patch.object(controller.views["client"], "display_entity_list"), \
            patch.object(controller.app_view, "ask_id",
                         side_effect=[str(client.id), None]), \
            patch("epic_event.permission.has_object_permission",
                  return_value=False), \
            patch.object(Client, "get_fields",
                         return_value=[["name", "Nom"]]), \
            patch.object(controller.app_view,
                         "display_error_message") as mock_error, \
            patch.object(controller.app_view, "break_point"), \
            patch.object(controller.app_view, "clear_console"):
        controller.modify_entity(db_session, gestionnaire, "client")

        mock_error.assert_called()


def test_order_by_field_entity(entity_controller, session, seed_data_collaborator,
                               seed_data_client):
    controller = entity_controller
    user = seed_data_collaborator["gestion"]
    client = seed_data_client
    controller.views["client"] = MagicMock()
    mock_model = MagicMock()
    # fournir des fields pour que choose_field = 2 soit valide
    mock_model.get_fields.return_value = [
        ["id", "Id"],
        ["something", "Quelque chose"],
        ["name", "Nom"],
        ["other", "Autre"],
        ["foo", "Foo"],
        ["bar", "Bar"],
    ]

    mock_model.order_by_fields.return_value = [client]

    with patch.object(controller, "get_model", return_value=mock_model), \
            patch.object(controller, "list_entity"), \
            patch.object(controller.app_view, "clear_console"), \
            patch.object(controller.app_view, "display_list_field_menu"), \
            patch.object(controller.app_view, "choose_field", return_value=5), \
            patch.object(controller.app_view, "ask_descending_order",
                         return_value=True), \
            patch.object(controller.app_view, "break_point"):

        controller.views["client"].SESSION = {"show_archived": False}

        controller.order_by_field_entity(user, session, "client")

        mock_model.order_by_fields.assert_called_once_with(session, "bar",
                                                           True)
        controller.views["client"].display_entity_list.assert_called_once_with(
            [client])


def test_filter_by_field_entity(entity_controller, session,
                                seed_data_collaborator):
    controller = entity_controller
    user = seed_data_collaborator["gestion"]
    controller.views["dummy"] = MagicMock()
    mock_model = MagicMock()

    mock_model.get_fields.return_value = [
        ["id", "Id"],
        ["name", "Nom"],
        ["email", "Email"],
        ["phone", "Téléphone"],
        ["company", "Compagnie"],
        ["field_to_filter", "Champ à filtrer"],
    ]
    mock_model.filter_by_fields.return_value = ["filtered item",
                                                "objet filtré"]

    with patch.object(controller, "get_model", return_value=mock_model), \
            patch.object(controller, "list_entity"), \
            patch.object(controller.app_view, "clear_console"), \
            patch.object(controller.app_view, "display_list_field_menu"), \
            patch.object(controller.app_view, "choose_field", return_value=5), \
            patch.object(controller.app_view, "ask_filter_value",
                         return_value=("field_to_filter", "valeur")), \
            patch.object(controller.views["dummy"], "display_entity_list"), \
            patch.object(controller.app_view, "break_point"):
        controller.filter_by_field_entity(user, session, "dummy")

        mock_model.filter_by_fields.assert_called_once_with(
            session, controller.SESSION["show_archived"],
            field_to_filter="valeur"
        )
        controller.views["dummy"].display_entity_list.assert_called_once_with(
            ["filtered item", "objet filtré"])


def test_show_details_entity_displays_related_data(entity_controller,
                                                   db_session,
                                                   seed_data_client,
                                                   seed_data_collaborator):
    controller = entity_controller
    user = seed_data_collaborator["gestion"]
    client = seed_data_client
    client_id = client.id

    with patch.object(controller.app_view, "ask_id",
                      side_effect=[str(client_id), None]), \
            patch.object(controller.app_view, "clear_console"), \
            patch.object(controller.app_view, "break_point") as mock_break, \
            patch.object(controller.views["contract"],
                         "display_entity_list") as mock_contracts_view, \
            patch.object(controller.views["collaborator"],
                         "display_entity_list") as mock_collaborator_view:
        controller.show_details_entity(user, db_session, "client")

        mock_contracts_view.assert_called()
        mock_collaborator_view.assert_called()
        mock_break.assert_called()

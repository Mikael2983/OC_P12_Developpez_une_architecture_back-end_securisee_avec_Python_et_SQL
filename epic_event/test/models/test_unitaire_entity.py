"""Unit tests for the Entity base ORM operations."""

import pytest
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch, MagicMock

from sqlalchemy.testing import fixture

from epic_event.controllers.entity_controller import EntityController
from epic_event.models import Collaborator
from epic_event.models.entity import Entity


@pytest.fixture
def entity_controller():
    SESSION = {"show_archived": False}
    controller = EntityController(SESSION)
    return controller


# ---------- Save Operation ----------
def test_save_success(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    result = user.save(db_session)
    assert result == "success"
    assert db_session.query(Collaborator).filter_by(id=user.id).count() == 1


def test_save_sqlalchemy_error(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    with patch.object(db_session, "commit",
                      side_effect=SQLAlchemyError("Commit failed")):
        result = user.save(db_session)
        assert "Erreur de base de données" in result


# ---------- Update Operation ----------
def test_update_success(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    user.full_name = "Updated Name"
    result = user.update(db_session)
    assert result == "success"
    assert db_session.query(Collaborator).filter_by(
        id=user.id).first().full_name == "Updated Name"


def test_update_sqlalchemy_error(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    user.full_name = "Erreur Update"
    with patch.object(db_session, "commit",
                      side_effect=SQLAlchemyError("Update failed")):
        result = user.update(db_session)
        assert "Erreur de base de données" in result


# ---------- Soft Delete Operation ----------
def test_soft_delete_success(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    result = user.soft_delete(db_session)
    assert result == "success"
    assert db_session.query(Collaborator).filter_by(
        id=user.id).first().archived is True


def test_soft_delete_sqlalchemy_error(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    with patch.object(db_session, "commit",
                      side_effect=SQLAlchemyError("Soft failed")):
        result = user.soft_delete(db_session)
        assert "SQLAlchemyError" in result


# ---------- Hard Delete Operation ----------
def test_hard_delete_success(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    clone = Collaborator(
        full_name="Hard Delete",
        email="hard@example.com",
        role="support"
    )
    clone.password, _ = clone.validate_password("password")
    clone.save(db_session)
    result = clone.hard_delete(db_session)
    assert result == "success"
    assert db_session.query(Collaborator).filter_by(
        email="hard@example.com").count() == 0


def test_hard_delete_sqlalchemy_error(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    with patch.object(db_session, "commit",
                      side_effect=SQLAlchemyError("Hard failed")):
        result = user.hard_delete(db_session)
        assert "SQLAlchemyError" in result


# ---------- Filter By Fields ----------

def test_filter_by_field_entity_success(entity_controller, db_session, seed_data_collaborator):
    controller = entity_controller
    user = seed_data_collaborator["gestion"]
    controller.views["dummy"] = MagicMock()
    mock_model = MagicMock()
    mock_model.get_fields.return_value = [["name", "Nom"], ["email", "Email"]]

    filtered_items = ["item1", "item2"]
    mock_model.filter_by_fields.return_value = filtered_items

    with patch.object(controller, "get_model", return_value=mock_model), \
            patch.object(controller, "list_entity") as mock_list_entity, \
            patch.object(controller.app_view, "clear_console"), \
            patch.object(controller.app_view, "display_list_field_menu"), \
            patch.object(controller.app_view, "choose_field", return_value=0), \
            patch.object(controller.app_view, "ask_filter_value",
                         return_value=("name", "Alice")), \
            patch.object(controller.views["dummy"],
                         "display_entity_list") as mock_display, \
            patch.object(controller.app_view, "break_point"):
        controller.SESSION = {"show_archived": False}

        controller.filter_by_field_entity(user, db_session, "dummy")

        mock_model.filter_by_fields.assert_called_once_with(db_session, False,
                                                            name="Alice")
        mock_display.assert_called_once_with(filtered_items)


def test_filter_by_field_entity_invalid_choice(
    entity_controller,
    db_session,
    seed_data_collaborator,
):
    controller = entity_controller
    user = seed_data_collaborator["gestion"]

    controller.views["dummy"] = MagicMock()

    mock_model = MagicMock()
    mock_model.get_fields.return_value = [["name", "Nom"]]

    with patch.object(controller, "get_model", return_value=mock_model), \
         patch.object(controller, "list_entity"), \
         patch.object(controller.app_view, "clear_console"), \
         patch.object(controller.app_view, "display_list_field_menu"), \
         patch.object(controller.app_view, "choose_field", return_value=999), \
         patch.object(controller.app_view, "display_error_message") as mock_error, \
         patch.object(controller.app_view, "break_point"):

        controller.SESSION = {"show_archived": False}
        controller.filter_by_field_entity(user, db_session, "dummy")

        mock_error.assert_called_once_with("Champ invalide.")
        mock_model.filter_by_fields.assert_not_called()
        controller.views["dummy"].display_entity_list.assert_not_called()


# ---------- Order By Fields ----------
def test_order_by_field_entity_success(entity_controller, db_session,
                                       seed_data_collaborator):
    controller = entity_controller
    user = seed_data_collaborator["gestion"]
    mock_model = MagicMock()
    controller.views["dummy"] = MagicMock()
    mock_model.get_fields.return_value = [["name", "Nom"], ["date", "Date"]]
    ordered_items = ["a", "b"]
    mock_model.order_by_fields.return_value = ordered_items

    with patch.object(controller, "get_model", return_value=mock_model), \
            patch.object(controller, "list_entity"), \
            patch.object(controller.app_view, "clear_console"), \
            patch.object(controller.app_view, "display_list_field_menu"), \
            patch.object(controller.app_view, "choose_field", return_value=1), \
            patch.object(controller.app_view, "ask_descending_order",
                         return_value=True), \
            patch.object(controller.views["dummy"],
                         "display_entity_list") as mock_display, \
            patch.object(controller.app_view, "break_point"):
        controller.order_by_field_entity(user, db_session, "dummy")

        mock_model.order_by_fields.assert_called_once_with(db_session, "date",
                                                           True)
        mock_display.assert_called_once_with(ordered_items)


def test_order_by_field_entity_invalid_choice(entity_controller, db_session,
                                              seed_data_collaborator):
    controller = entity_controller
    user = seed_data_collaborator["gestion"]

    controller.views["dummy"] = MagicMock()
    mock_model = MagicMock()
    mock_model.get_fields.return_value = [["name", "Nom"]]

    with patch.object(controller, "get_model", return_value=mock_model), \
            patch.object(controller, "list_entity"), \
            patch.object(controller.app_view, "clear_console"), \
            patch.object(controller.app_view, "display_list_field_menu"), \
            patch.object(controller.app_view, "choose_field", return_value=5), \
            patch.object(controller.app_view,
                         "ask_descending_order") as mock_desc, \
            patch.object(controller.views["dummy"],
                         "display_entity_list") as mock_display, \
            patch.object(controller.app_view,
                         "display_error_message") as mock_error, \
            patch.object(controller.app_view, "break_point"):
        controller.order_by_field_entity(user, db_session, "dummy")

        mock_error.assert_called_once_with("Champ invalide.")
        mock_desc.assert_not_called()
        mock_model.order_by_fields.assert_not_called()
        mock_display.assert_not_called()


def test_order_by_fields_asc(seed_data_collaborator, db_session):
    results = Collaborator.order_by_fields(
        db_session,
        "full_name")
    assert [obj.full_name for obj in results] == ["Alice Martin",
                                                  "Bruno Lefevre",
                                                  "Chloé Dubois",
                                                  "David Morel",
                                                  "Emma Bernard"]


def test_order_by_fields_desc(seed_data_collaborator, db_session):
    results = Collaborator.order_by_fields(
        db_session,
        "full_name",
        descending=True,
        archived=True
    )

    full_name_ordered_list = [obj.full_name for obj in results]

    assert full_name_ordered_list == ["Emma Bernard", "David Morel",
                                      "Chloé Dubois", "Bruno Lefevre",
                                      "Alice Martin"]


def test_order_by_fields_attribute_error(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    results = Collaborator.order_by_fields(db_session, "non_existent")
    assert user in results


# ---------- Path Resolution ----------
def test_resolve_valid_path():
    class Dummy:
        def __init__(self):
            self.inner = type("Inner", (), {"value": "OK"})()

    assert Entity._resolve(Dummy(), "inner.value") == "OK"


def test_resolve_invalid_path():
    assert Entity._resolve(None, "x.y") == ""

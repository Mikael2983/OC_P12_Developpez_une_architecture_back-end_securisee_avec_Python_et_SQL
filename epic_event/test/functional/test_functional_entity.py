import pytest
from unittest.mock import MagicMock
from epic_event.controllers.main_controller import MainController
from epic_event.controllers.entity_controller import EntityController
from epic_event.models import Collaborator, Client, Contract


# ---------- Functional Test: MainController Entity Navigation ----------
def test_handle_entity_action_valid_choice(seed_data_collaborator):
    user = seed_data_collaborator["admin"]

    app_view = MagicMock()
    app_view.choose_field.side_effect = [0, 4]
    app_view.clear_console.return_value = None
    app_view.display_informative_message.return_value = None
    app_view.display_entity_menu.return_value = None

    mc = MainController(session=MagicMock())
    mc.app_view = app_view
    mc.handle_user_role_action = MagicMock()

    mc.handle_entity_action(user)

    mc.handle_user_role_action.assert_called_with(user, "collaborator")


def test_handle_entity_action_invalid_choice(seed_data_collaborator):
    user = seed_data_collaborator["admin"]
    app_view = MagicMock()
    app_view.choose_field.side_effect = [10, 4]
    app_view.clear_console.return_value = None
    app_view.display_entity_menu.return_value = None

    mc = MainController(session=MagicMock())
    mc.app_view = app_view
    mc.handle_user_role_action = MagicMock()

    mc.handle_entity_action(user)
    mc.handle_user_role_action.assert_not_called()


def test_handle_user_role_action_invalid_role():
    session = MagicMock()
    app_view = MagicMock()

    mc = MainController(session=session)
    mc.app_view = app_view

    fake_user = Collaborator(role="ghost", full_name="Ghost")
    mc.handle_user_role_action(fake_user, "client")
    app_view.display_error_message.assert_called_once_with("R\u00f4le utilisateur non pris en charge : ghost")


def test_show_archived_toggle():
    mc = MainController(session=MagicMock())
    mc.SESSION = {"show_archived": False}
    mc.show_archived()
    assert mc.SESSION["show_archived"] is True
    mc.show_archived()
    assert mc.SESSION["show_archived"] is False


# ---------- Integration Test: EntityController get_model_fields ----------
def test_collaborator_get_fields_default_list_excludes_password(seed_data_collaborator):
    """
    Par défaut (list) pour un support, le champ 'password' doit être absent.
    On vérifie aussi que chaque champ retourné est une paire [clé, label].
    """
    user = seed_data_collaborator["support"]
    fields = Collaborator.get_fields(user.role, "list")
    assert all(isinstance(f, list) for f in fields)
    assert not any(f[0] == "password" for f in fields), "Le champ password ne doit pas apparaître en 'list' pour support."


def test_collaborator_get_fields_create_includes_password_for_admin(seed_data_collaborator):
    """
    Pour un admin en contexte 'create', le champ 'password' doit être présent.
    """
    user = seed_data_collaborator["admin"]
    fields = Collaborator.get_fields(user.role, "create")
    assert any(f[0] == "password" for f in fields), "Le champ password doit apparaître en 'create' pour admin."

# ---------- Integration Test: EntityController list_entity Filtering ----------
def test_list_entity_contract_filters_commercial(seed_data_collaborator, db_session):
    ec = EntityController(SESSION={"show_archived": False})
    user = seed_data_collaborator["commercial"]
    entity = "contract"
    ec.views[entity].display_entity_list = MagicMock()
    result = ec.list_entity(db_session, entity, user)
    assert result in [None, "aucun \u00e9l\u00e9ment disponible"]


def test_list_entity_event_filters_support(seed_data_collaborator, db_session):
    ec = EntityController(SESSION={"show_archived": False})
    user = seed_data_collaborator["support"]
    entity = "event"
    ec.views[entity].display_entity_list = MagicMock()
    result = ec.list_entity(db_session, entity, user, purpose="modify")
    assert result in [None, "aucun \u00e9l\u00e9ment disponible"]


def test_validate_field_dynamic(seed_data_collaborator, db_session):
    user = seed_data_collaborator["admin"]
    field = ["email", "Email"]
    data = {"email": "test@example.com"}
    Model = Collaborator
    val, err = EntityController.validate_field(Model, field, db_session, user, data)
    assert err is None or val == data["email"]


def test_validate_field_missing():
    field = ["nonexistent", "Missing"]
    data = {"nonexistent": "X"}
    val, err = EntityController.validate_field(Client, field, MagicMock(), MagicMock(), data)
    assert val is None
    assert "validate_nonexistent" in err


def test_get_model():
    assert EntityController.get_model("client") == Client
    assert EntityController.get_model("contract") == Contract

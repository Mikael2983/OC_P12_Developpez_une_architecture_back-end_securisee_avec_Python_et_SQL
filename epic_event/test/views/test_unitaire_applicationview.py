import pytest
from unittest.mock import patch, MagicMock
from epic_event.views.application_view import ApplicationView



@pytest.fixture
def mock_session():
    return {"show_archived": False}


@pytest.fixture
def app_view(mock_session):
    return ApplicationView(SESSION=mock_session)

# === Tests des menu ===
def test_display_home_menu(app_view):
    app_view.utils_view.display_styled_menu = MagicMock()
    app_view.display_home_menu()
    app_view.utils_view.display_styled_menu.assert_called_once()


def test_display_entity_menu(app_view):
    app_view.utils_view.display_styled_menu = MagicMock()
    app_view.display_entity_menu()
    app_view.utils_view.display_styled_menu.assert_called_once()


def test_display_menu_details(app_view):
    app_view.utils_view.display_styled_menu = MagicMock()
    app_view.display_menu_details("client")
    app_view.utils_view.display_styled_menu.assert_called_once()


# === Tests d’entrée utilisateur ===


@patch("builtins.input", return_value="testuser")
@patch("rich.console.Console.input", side_effect=["user", "pass"])
def test_display_connection_menu(mock_input, builtins_input, app_view):
    username, password = app_view.display_connection_menu()
    assert username == "user"
    assert password == "pass"


@patch("rich.console.Console.input", return_value="2")
def test_choose_option(mock_input, app_view):
    assert app_view.choose_option() == "2"


@patch("rich.console.Console.input", return_value="y")
def test_valide_choice_menu_yes(mock_input, app_view):
    assert app_view.valide_choice_menu() is True


@patch("rich.console.Console.input", return_value="n")
def test_valide_choice_menu_no(mock_input, app_view):
    assert app_view.valide_choice_menu() is False


@patch("rich.console.Console.input", return_value="123")
def test_ask_id(mock_input, app_view):
    result = app_view.ask_id("client")
    assert result == "123"


@patch("rich.console.Console.input", return_value="value")
def test_ask_information(mock_input, app_view):
    result = app_view.ask_information("email")
    assert result == "value"


@patch("rich.console.Console.input", return_value="Y")
def test_ask_descending_order_yes(mock_input, app_view):
    assert app_view.ask_descending_order() is True


@patch("rich.console.Console.input", return_value="n")
def test_ask_descending_order_no(mock_input, app_view):
    assert app_view.ask_descending_order() is False


# === Tests de filtres et champs ===
@patch("rich.console.Console.input", side_effect=["john"])
def test_ask_filter_field_and_value_valid(mock_input, app_view):
    mapping = ["name", "Nom"]
    field, value = app_view.ask_filter_value(mapping)
    assert field == "name"
    assert value == "john"


@patch("rich.console.Console.input", return_value="   ")
def test_ask_filter_field_and_value_empty_string(mock_input, app_view):
    mapping = ["name", "Nom"]
    field, value = app_view.ask_filter_value(mapping)
    assert field == "name"
    assert value == ""


# === Tests d’affichage de message===
@patch("epic_event.views.application_view.print")
def test_display_success_message(mock_print, app_view):
    app_view.utils_view.apply_rich_style = MagicMock(return_value="styled msg")
    app_view.display_success_message("Success")
    mock_print.assert_called_with("styled msg")


@patch("epic_event.views.application_view.print")
def test_display_error_message(mock_print, app_view):
    app_view.utils_view.apply_rich_style = MagicMock(return_value="error msg")
    app_view.display_error_message("Error")
    mock_print.assert_called_with("error msg")


@patch("epic_event.views.application_view.print")
def test_display_informative_message(mock_print, app_view):
    app_view.utils_view.apply_rich_style = MagicMock(return_value="info msg")
    app_view.display_informative_message("Info")
    mock_print.assert_called_with("info msg")


# === Test console clear et pause ===
@patch("os.system")
def test_clear_console(mock_system):
    ApplicationView.clear_console()
    mock_system.assert_called()


@patch("epic_event.views.application_view.print")
@patch("builtins.input", return_value="")
def test_break_point(mock_input, mock_print, app_view):
    app_view.utils_view.apply_rich_style = MagicMock(return_value="pause")

    app_view.break_point()

    mock_print.assert_called_once_with("pause")
    mock_input.assert_called_once()


# === Tests de menus dynamiques ===

def test_display_dict_field_choice_menu(app_view):
    entity_mapping = ["email", "Email"]
    app_view.utils_view.display_styled_menu = MagicMock()
    app_view.display_list_field_menu(entity_mapping, "order")
    app_view.utils_view.display_styled_menu.assert_called_once()


def test_display_modify_field_choice_menu(app_view):
    entity_fields = [["email", "Email"], ["name", "Name"]]
    app_view.utils_view.display_styled_menu = MagicMock()
    app_view.display_modify_field_menu(entity_fields)
    app_view.utils_view.display_styled_menu.assert_called_once()


# === Test rôle/menus conditionnels ===

def test_display_menu_role_admin(app_view):
    mock_options = ["details", "create", "modify"]
    app_view.utils_view.display_styled_menu = MagicMock()
    app_view.display_entity_menu_role("admin", "client", mock_options)
    app_view.utils_view.display_styled_menu.assert_called_once()


def test_display_menu_role_toggle_archive(app_view, mock_session):
    mock_session["show_archived"] = True
    mock_options = ["details", "create", "modify"]
    app_view.utils_view.display_styled_menu = MagicMock()
    app_view.display_entity_menu_role(
        "admin",
        "contract",
        mock_options
    )
    app_view.utils_view.display_styled_menu.assert_called_once()

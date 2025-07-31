import pytest
from unittest.mock import patch

from epic_event.views.utils_view import UtilsView


# === Test de apply_rich_style ===
def test_apply_rich_style_returns_correct_format():
    message = "Hello"
    style = "bold red"
    styled = UtilsView.apply_rich_style(message, style)
    assert styled == "[bold red]Hello[/bold red]"


# === Tests de display_styled_menu ===
# === Cas complet (avec tout) ===
@patch("epic_event.views.utils_view.print")
def test_display_styled_menu_with_all(mock_print):
    view = UtilsView()
    header = "MENU"
    request = "Choisissez une option :"
    text_list = ["1. Créer", "2. Modifier"]

    view.display_styled_menu(header, request, text_list)

    assert mock_print.call_count == 5
    assert "[bold blue]" in mock_print.call_args_list[0][0][0]
    assert "-" * len(header) in mock_print.call_args_list[1][0][0]
    assert "[yellow]" in mock_print.call_args_list[2][0][0]
    assert "    1. Créer" in mock_print.call_args_list[3][0][0]


# === Cas sans header ===
@patch("epic_event.views.utils_view.print")
def test_display_styled_menu_without_header(mock_print):
    view = UtilsView()
    request = "Choix ?"
    text_list = ["Option A"]

    view.display_styled_menu(None, request, text_list)

    assert mock_print.call_count == 2
    assert "[yellow]" in mock_print.call_args_list[0][0][0]
    assert "    Option A" in mock_print.call_args_list[1][0][0]


# === Cas sans request ===
@patch("epic_event.views.utils_view.print")
def test_display_styled_menu_without_request(mock_print):
    view = UtilsView()
    header = "Options"
    text_list = ["X", "Y"]

    view.display_styled_menu(header, None, text_list)

    assert mock_print.call_count == 4
    assert "-" * len(header) in mock_print.call_args_list[1][0][0]


# === Cas vide (pas de header, pas de request) ===
@patch("epic_event.views.utils_view.print")
def test_display_styled_menu_only_text(mock_print):
    view = UtilsView()
    text_list = ["Juste un choix"]

    view.display_styled_menu("", "", text_list)

    assert mock_print.call_count == 1
    assert "    Juste un choix" in mock_print.call_args[0][0]


@patch("epic_event.views.utils_view.print")
def test_display_styled_menu_empty_text(mock_print):
    view = UtilsView()
    view.display_styled_menu("Titre", "Demande", [])

    assert mock_print.call_count == 3

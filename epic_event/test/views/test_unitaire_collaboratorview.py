import pytest
from unittest.mock import patch, MagicMock
from epic_event.views.collaborator_view import CollaboratorView


# ======= FIXTURES =======

@pytest.fixture
def mock_session_show_archived():
    return {"show_archived": True}

@pytest.fixture
def mock_session_hide_archived():
    return {"show_archived": False}

@pytest.fixture
def collaborators_with_archived():
    mock1 = MagicMock()
    mock1.id = 1
    mock1.full_name = "Alice Dupont"
    mock1.email = "alice@example.com"
    mock1.role = "commercial"
    mock1.formatted_archived = "Non"

    mock2 = MagicMock()
    mock2.id = 2
    mock2.full_name = "Bob Martin"
    mock2.email = "bob@example.com"
    mock2.role = "support"
    mock2.formatted_archived = "Oui"

    return [mock1, mock2]

@pytest.fixture
def view_with_archived(mock_session_show_archived):
    return CollaboratorView(SESSION=mock_session_show_archived)

@pytest.fixture
def view_without_archived(mock_session_hide_archived):
    return CollaboratorView(SESSION=mock_session_hide_archived)


# === Test de mapping ===
def test_mapping_keys(view_with_archived):
    assert isinstance(view_with_archived.mapping, dict)
    assert view_with_archived.mapping["1"] == ["id", "Id"]
    assert view_with_archived.mapping["4"] == ["role", "Service"]


# === Tests de display_entity_list ===
# === Sans archivés ===
@patch("rich.console.Console.print")
def test_display_entity_list_without_archived(mock_print, view_without_archived, collaborators_with_archived):
    view_without_archived.display_entity_list(collaborators_with_archived)


    args, kwargs = mock_print.call_args
    table = args[0]
    assert "archivé" not in [col.header for col in table.columns]
    assert table.row_count == 2


# === Avec archivés ===
@patch("rich.console.Console.print")
def test_display_entity_list_with_archived(mock_print, view_with_archived, collaborators_with_archived):
    view_with_archived.display_entity_list(collaborators_with_archived)

    args, kwargs = mock_print.call_args
    table = args[0]
    headers = [col.header for col in table.columns]
    assert "archivé" in headers
    assert table.row_count == 2


# === Test d’un collaborateur vide ===
@patch("rich.console.Console.print")
def test_display_entity_list_empty(mock_print, view_with_archived):
    view_with_archived.display_entity_list([])

    args, _ = mock_print.call_args
    table = args[0]
    assert table.row_count == 0
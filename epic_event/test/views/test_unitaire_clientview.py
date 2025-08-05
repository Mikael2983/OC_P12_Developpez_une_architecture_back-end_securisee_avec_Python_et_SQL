import pytest
from unittest.mock import MagicMock, patch
from epic_event.views.client_view import ClientView


# ======= FIXTURES =======

@pytest.fixture
def session_with_archived():
    return {"show_archived": True}


@pytest.fixture
def session_without_archived():
    return {"show_archived": False}


@pytest.fixture
def client_view_with_archived(session_with_archived):
    return ClientView(SESSION=session_with_archived)


@pytest.fixture
def client_view_without_archived(session_without_archived):
    return ClientView(SESSION=session_without_archived)


@pytest.fixture
def mock_clients():
    commercial = MagicMock()
    commercial.full_name = "Paul Durand"

    client1 = MagicMock()
    client1.id = 1
    client1.full_name = "Alice Martin"
    client1.email = "alice@example.com"
    client1.phone = "0123456789"
    client1.company_name = "Company A"
    client1.formatted_created_date = "2024-05-01"
    client1.formatted_last_contact_date = "2024-07-01"
    client1.commercial = commercial
    client1.formatted_archived = "Non"

    client2 = MagicMock()
    client2.id = 2
    client2.full_name = "Bob Leroy"
    client2.email = "bob@example.com"
    client2.phone = "0987654321"
    client2.company_name = "Company B"
    client2.formatted_created_date = "2023-03-15"
    client2.formatted_last_contact_date = "2024-06-10"
    client2.commercial = commercial
    client2.formatted_archived = "Oui"

    return [client1, client2]


# === Tests de display_entity_list ===
# === Sans archivés ===
@patch("rich.console.Console.print")
def test_display_entity_list_without_archived(mock_print,
                                              client_view_without_archived,
                                              mock_clients):
    client_view_without_archived.display_entity_list(mock_clients)

    args, kwargs = mock_print.call_args
    table = args[0]

    headers = [col.header for col in table.columns]
    assert "archivé" not in headers
    assert table.row_count == 2


# === Avec archivés ===
@patch("rich.console.Console.print")
def test_display_entity_list_with_archived(mock_print,
                                           client_view_with_archived,
                                           mock_clients):
    client_view_with_archived.display_entity_list(mock_clients)

    args, kwargs = mock_print.call_args
    table = args[0]

    headers = [col.header for col in table.columns]
    assert "archivé" in headers
    assert table.row_count == 2


# === Liste vide ===
@patch("rich.console.Console.print")
def test_display_entity_list_empty(mock_print, client_view_with_archived):
    client_view_with_archived.display_entity_list([])

    args, _ = mock_print.call_args
    table = args[0]
    assert table.row_count == 0

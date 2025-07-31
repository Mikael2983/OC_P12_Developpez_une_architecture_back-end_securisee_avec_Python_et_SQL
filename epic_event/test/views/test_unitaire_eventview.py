import pytest
from unittest.mock import MagicMock, patch
from epic_event.views.event_view import EventView


# ======= FIXTURES =======

@pytest.fixture
def session_with_archived():
    return {"show_archived": True}


@pytest.fixture
def session_without_archived():
    return {"show_archived": False}


@pytest.fixture
def event_view_with_archived(session_with_archived):
    return EventView(SESSION=session_with_archived)


@pytest.fixture
def event_view_without_archived(session_without_archived):
    return EventView(SESSION=session_without_archived)


@pytest.fixture
def mock_events():
    client = MagicMock()
    client.company_name = "Société X"

    contract = MagicMock()
    contract.id = 42
    contract.client = client

    support = MagicMock()
    support.full_name = "Jean Dupuis"

    event1 = MagicMock()
    event1.id = 1
    event1.contract = contract
    event1.contract_id = 42
    event1.title = "Salon Paris"
    event1.formatted_start_date = "2025-01-10"
    event1.formatted_end_date = "2025-01-12"
    event1.location = "Paris Expo"
    event1.participants = 100
    event1.notes = "Stand principal Hall 3"
    event1.support = support
    event1.formatted_archived = "Non"

    event2 = MagicMock()
    event2.id = 2
    event2.contract = contract
    event2.contract_id = 42
    event2.title = "Conférence Tech"
    event2.formatted_start_date = "2025-02-15"
    event2.formatted_end_date = "2025-02-16"
    event2.location = "Lyon"
    event2.participants = 80
    event2.notes = "Prévoir badge speaker"
    event2.support = None
    event2.formatted_archived = "Oui"

    return [event1, event2]


# === Test de mapping ===
def test_mapping_structure(event_view_with_archived):
    mapping = event_view_with_archived.mapping
    assert mapping["1"] == ["id", "Id"]
    assert mapping["4"] == ["end_date", "date de fin"]
    assert mapping["9"] == ["support.full_name", "Organisateur"]


# === Tests de display_entity_list ===
# === Sans archivés ===
@patch("rich.console.Console.print")
def test_display_entity_list_without_archived(mock_print,
                                              event_view_without_archived,
                                              mock_events):
    event_view_without_archived.display_entity_list(mock_events)

    args, _ = mock_print.call_args
    table = args[0]

    headers = [col.header for col in table.columns]
    assert "archivé" not in headers
    assert table.row_count == 2


# === Avec archivés ===
@patch("rich.console.Console.print")
def test_display_entity_list_with_archived(mock_print,
                                           event_view_with_archived,
                                           mock_events):
    event_view_with_archived.display_entity_list(mock_events)

    args, _ = mock_print.call_args
    table = args[0]

    headers = [col.header for col in table.columns]
    assert "archivé" in headers
    assert table.row_count == 2


# === Cas avec support None ===

@patch("rich.table.Table.add_row")
@patch("rich.console.Console.print")
def test_display_entity_list_support_none(mock_print,mock_add_row,
                                          event_view_without_archived,
                                          mock_events):
    event_with_no_support = mock_events[1]
    event_with_no_support.support = None
    assert event_with_no_support.support is None

    event_view_without_archived.display_entity_list([event_with_no_support])

    mock_add_row.assert_called_once()
    args = mock_add_row.call_args.args

    assert any("A définir" in arg for arg in args), \
        f"Aucun champ ne contient 'A définir' dans {args}"

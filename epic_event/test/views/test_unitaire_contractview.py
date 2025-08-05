import pytest
from unittest.mock import MagicMock, patch
from epic_event.views.contract_view import ContractView


@pytest.fixture
def session_with_archived():
    return {"show_archived": True}


@pytest.fixture
def session_without_archived():
    return {"show_archived": False}


@pytest.fixture
def contract_view_with_archived(session_with_archived):
    return ContractView(SESSION=session_with_archived)


@pytest.fixture
def contract_view_without_archived(session_without_archived):
    return ContractView(SESSION=session_without_archived)


@pytest.fixture
def mock_contracts():
    client = MagicMock()
    client.company_name = "Entreprise ABC"

    contract1 = MagicMock()
    contract1.id = 1
    contract1.client = client
    contract1.total_amount = "5000€"
    contract1.amount_due = "1000€"
    contract1.formatted_created_date = "2024-01-01"
    contract1.formatted_signed = "Oui"
    contract1.formatted_archived = "Non"

    contract2 = MagicMock()
    contract2.id = 2
    contract2.client = client
    contract2.total_amount = "3000€"
    contract2.amount_due = "0€"
    contract2.formatted_created_date = "2023-12-15"
    contract2.formatted_signed = "Oui"
    contract2.formatted_archived = "Oui"

    return [contract1, contract2]


# === Tests de display_entity_list ===
# === Without archived ===
@patch("rich.console.Console.print")
def test_display_entity_list_without_archived(mock_print,
                                              contract_view_without_archived,
                                              mock_contracts):
    contract_view_without_archived.display_entity_list(mock_contracts)

    args, _ = mock_print.call_args
    table = args[0]

    headers = [col.header for col in table.columns]
    assert "archivé" not in headers
    assert table.row_count == 2


# === with archived ===
@patch("rich.console.Console.print")
def test_display_entity_list_with_archived(mock_print,
                                           contract_view_with_archived,
                                           mock_contracts):
    contract_view_with_archived.display_entity_list(mock_contracts)

    args, _ = mock_print.call_args
    table = args[0]

    headers = [col.header for col in table.columns]
    assert "archivé" in headers
    assert table.row_count == 2


# === Liste vide ===
@patch("rich.console.Console.print")
def test_display_entity_list_empty(mock_print, contract_view_with_archived):
    contract_view_with_archived.display_entity_list([])

    args, _ = mock_print.call_args
    table = args[0]
    assert table.row_count == 0

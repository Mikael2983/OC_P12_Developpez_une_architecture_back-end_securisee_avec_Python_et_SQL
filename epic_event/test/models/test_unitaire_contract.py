from datetime import date

import pytest
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch

from epic_event.models import Contract, Client


# ---------- String Representation ----------
def test_contract_str():
    client = Client(company_name="TestCorp")
    contract = Contract(id=1, client=client)
    assert str(contract) == "le contract 1 du client TestCorp"


# ---------- Formatted Properties ----------
def test_formatted_archived():
    assert Contract(archived=True).formatted_archived == "OUI"
    assert Contract(archived=False).formatted_archived == "NON"


def test_formatted_signed():
    assert Contract(signed=True).formatted_signed == "OUI"
    assert Contract(signed=False).formatted_signed == "NON"


def test_formatted_created_date():
    contract = Contract(created_date=date(2024, 12, 31))
    assert contract.formatted_created_date == "31-12-2024"


# ---------- Static Display Fields ----------
def test_get_field():
    fields = Contract.get_field()
    expected = ["id", "client_id", "total_amount", "amount_due",
                "created_date", "signed", "archived"]
    assert [f[0] for f in fields] == expected


# ---------- Validation: Signed ----------
def test_validate_signed_str():
    for val in ["oui", "y", "yes", "true", "o"]:
        assert Contract.validate_signed(val)[0] is True
    assert Contract.validate_signed("non")[0] is False


def test_validate_signed_bool():
    assert Contract.validate_signed(True) == (True, None)
    assert Contract.validate_signed(False) == (False, None)


# ---------- Validation: Total Amount ----------
def test_validate_total_amount_valid():
    assert Contract.validate_total_amount("123.45") == ("123.45", None)


def test_validate_total_amount_negative():
    _, err = Contract.validate_total_amount("-100")
    assert "positive" in err.lower()


def test_validate_total_amount_invalid():
    _, err = Contract.validate_total_amount("abc")
    assert "numeric" in err.lower()


# ---------- Validation: Amount Due ----------
def test_validate_amount_due_valid():
    assert Contract.validate_amount_due("1000", "500") == ("500", None)


def test_validate_amount_due_exceeds():
    _, err = Contract.validate_amount_due("100", "200")
    assert "cannot exceed" in err.lower()


def test_validate_amount_due_negative():
    _, err = Contract.validate_amount_due("100", "-50")
    assert "positive" in err.lower()


def test_validate_amount_due_invalid():
    _, err = Contract.validate_amount_due("abc", "xyz")
    assert "numeric" in err.lower()


# ---------- Validation: Client ID ----------
def test_validate_client_id_valid(db_session, seed_data_client):
    valid_id, err = Contract.validate_client_id(db_session,
                                                seed_data_client.id)
    assert valid_id == seed_data_client.id
    assert err is None


def test_validate_client_id_missing(db_session):
    _, err = Contract.validate_client_id(db_session, None)
    assert "missing" in err.lower()


def test_validate_client_id_not_found(db_session):
    _, err = Contract.validate_client_id(db_session, 99999)
    assert "no client found" in err.lower()


# ---------- Validation: Archived ----------
def test_validate_archived():
    for val in ["oui", "o", "yes", "true", "y"]:
        assert Contract.validate_archived(val)[0] is True
    for val in ["non", "n", "false"]:
        assert Contract.validate_archived(val)[0] is False


# ---------- Save Operation ----------

def test_save_contract_success(seed_data_contract, db_session):
    contract = seed_data_contract[0]  # signed, no event
    contract.amount = 9999
    result = contract.save(db_session)
    assert result == "success"
    assert db_session.query(Contract).filter_by(
        id=contract.id).first().amount == 9999


def test_save_contract_sqlalchemy_error(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    with patch.object(db_session, "commit",
                      side_effect=SQLAlchemyError("Commit failed")):
        result = contract.save(db_session)
        assert "Erreur de base de données" in result


# ---------- Update Operation ----------

def test_update_contract_success(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    contract.amount = 2024
    result = contract.update(db_session)
    assert result == "success"
    assert db_session.query(Contract).filter_by(
        id=contract.id).first().amount == 2024


def test_update_contract_sqlalchemy_error(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    with patch.object(db_session, "commit",
                      side_effect=SQLAlchemyError("Update failed")):
        result = contract.update(db_session)
        assert "Erreur de base de données" in result


# ---------- Soft Delete Operation ----------

def test_soft_delete_contract_success(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    result = contract.soft_delete(db_session)
    assert result == "success"
    assert db_session.query(Contract).filter_by(
        id=contract.id).first().archived is True


def test_soft_delete_contract_sqlalchemy_error(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    with patch.object(db_session, "commit",
                      side_effect=SQLAlchemyError("Soft failed")):
        result = contract.soft_delete(db_session)
        assert "SQLAlchemyError" in result


# ---------- Hard Delete Operation ----------

def test_hard_delete_contract_success(db_session, seed_data_client):
    contract = Contract(
        total_amount="2000",
        amount_due="2000",
        signed=True,
        client_id=seed_data_client.id
    )
    db_session.add(contract)
    db_session.commit()
    result = contract.hard_delete(db_session)
    assert result == "success"
    assert db_session.query(Contract).filter_by(id=contract.id).count() == 0


def test_hard_delete_contract_sqlalchemy_error(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    with patch.object(db_session, "commit",
                      side_effect=SQLAlchemyError("Hard failed")):
        result = contract.hard_delete(db_session)
        assert "SQLAlchemyError" in result


# ---------- Filter By Fields ----------

def test_filter_by_fields_contract(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    results = Contract.filter_by_fields(db_session, signed=True)
    assert contract in results


def test_filter_by_fields_archived_contract(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    contract.archived = True
    db_session.commit()
    results = Contract.filter_by_fields(db_session, archived=True)
    assert contract in results


def test_filter_by_fields_invalid_attr_contract(db_session):
    with pytest.raises(AttributeError):
        Contract.filter_by_fields(db_session, invalid_attr=True)


# ---------- Order By Fields ----------

def test_order_by_fields_contract_asc(db_session, seed_data_client):
    c1 = Contract(total_amount="1000", amount_due="0", signed=False,
                  client_id=seed_data_client.id)
    c2 = Contract(total_amount="2000", amount_due="2000", signed=False,
                  client_id=seed_data_client.id)
    db_session.add_all([c1, c2])
    db_session.commit()
    results = Contract.order_by_fields(db_session, "total_amount")
    assert results[0].total_amount <= results[1].total_amount


def test_order_by_fields_contract_desc(db_session, seed_data_client):
    c1 = Contract(total_amount="1000", amount_due="2025-10-01", signed=False,
                  client_id=seed_data_client.id)
    c2 = Contract(total_amount="2000", amount_due="2025-10-02", signed=False,
                  client_id=seed_data_client.id)
    db_session.add_all([c1, c2])
    db_session.commit()
    results = Contract.order_by_fields(db_session, "amount", descending=True)
    assert results[0].total_amount <= results[1].total_amount


def test_order_by_fields_invalid_attr(seed_data_contract, db_session):
    contract = seed_data_contract[0]
    results = Contract.order_by_fields(db_session, "non_field")
    assert contract in results

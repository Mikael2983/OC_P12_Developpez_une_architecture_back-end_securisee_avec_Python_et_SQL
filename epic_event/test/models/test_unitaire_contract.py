import pytest
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch

from epic_event.models import Contract


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

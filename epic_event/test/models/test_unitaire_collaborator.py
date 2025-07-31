"""""Unit tests for the Entity base ORM operations."""

import pytest
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch

from epic_event.models import Collaborator
from epic_event.models.entity import Entity


# ---------- Save Operation ----------

def test_save_success(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    result = user.save(db_session)
    assert result == "success"
    assert db_session.query(Collaborator).count() >= 1


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
    db_session.delete(user)
    db_session.commit()
    clone = Collaborator(full_name="Hard Delete", email="hard@example.com",
                         role="support")
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

def test_filter_by_fields(seed_data_collaborator, db_session):
    results = Collaborator.filter_by_fields(db_session, full_name="Alice")
    assert all(r.full_name == "Alice" for r in results)
    assert all(r.archived is False for r in results)


def test_filter_by_fields_include_archived(db_session):
    archived = Collaborator(full_name="Michel", email="archived@example.com",
                            role="support", archived=True)
    archived.password, _ = archived.validate_password("password")
    db_session.add(archived)
    db_session.commit()
    results = Collaborator.filter_by_fields(db_session, archived=True,
                                            full_name="Michel")
    assert len(results) == 1


def test_filter_by_fields_attribute_error(db_session):
    with pytest.raises(AttributeError):
        Collaborator.filter_by_fields(db_session, ghost_field="value")


# ---------- Order By Fields ----------

def test_order_by_fields_asc(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    user.full_name = "Anna"
    other = Collaborator(full_name="Zoe", email="zoe@example.com",
                         role="support")
    other.password, _ = other.validate_password("password")
    db_session.add(other)
    db_session.commit()
    results = Collaborator.order_by_fields(db_session, "full_name")
    names = [obj.full_name for obj in results]
    assert names.index("Anna") < names.index("Zoe")


def test_order_by_fields_desc(seed_data_collaborator, db_session):
    user = seed_data_collaborator["support"]
    user.full_name = "Anna"
    other = Collaborator(full_name="Zoe", email="zoe@example.com",
                         role="support")
    other.password, _ = other.validate_password("password")
    db_session.add(other)
    db_session.commit()
    results = Collaborator.order_by_fields(db_session, "full_name",
                                           descending=True)
    names = [obj.full_name for obj in results]
    assert names.index("Anna") > names.index("Zoe")


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

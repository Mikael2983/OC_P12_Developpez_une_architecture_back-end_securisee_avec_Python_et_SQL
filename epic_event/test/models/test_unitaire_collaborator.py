"""""Unit tests for the Entity base ORM operations."""
import bcrypt
import pytest
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch

from epic_event.models import Collaborator
from epic_event.models.entity import Entity


# ---------- String Representation ----------
def test_collaborator_str():
    c = Collaborator(full_name="John Doe", role="support")
    assert str(c) == "le collaborateur John Doe du service support"


# ---------- Formatted Archived ----------
def test_formatted_archived():
    assert Collaborator(archived=True).formatted_archived == "OUI"
    assert Collaborator(archived=False).formatted_archived == "NON"


# ---------- Get Fields ----------
def test_get_field():
    expected = ["id", "full_name", "password", "email", "role", "archived"]
    fields = [f[0] for f in Collaborator.get_field()]
    assert fields == expected


# ---------- Validate Full Name ----------
def test_validate_full_name_valid(db_session):
    name, err = Collaborator.validate_full_name(db_session, "Jean Dupont")
    assert name == "Jean Dupont"
    assert err is None


def test_validate_full_name_empty(db_session):
    _, err = Collaborator.validate_full_name(db_session, "")
    assert "must not be empty" in err


def test_validate_full_name_invalid_chars(db_session):
    _, err = Collaborator.validate_full_name(db_session, "John@123")
    assert "only letters" in err


def test_validate_full_name_duplicate(db_session, seed_data_collaborator):
    existing = seed_data_collaborator["gestion"]
    _, err = Collaborator.validate_full_name(db_session, existing.full_name)
    assert "already in use" in err


# ---------- Validate Email ----------
def test_validate_email_valid(db_session):
    email, err = Collaborator.validate_email(db_session, "test@example.com")
    assert email == "test@example.com"
    assert err is None


def test_validate_email_invalid_format(db_session):
    _, err = Collaborator.validate_email(db_session, "bademail")
    assert "invalid email" in err.lower()


def test_validate_email_duplicate(db_session, seed_data_collaborator):
    _, err = Collaborator.validate_email(db_session,
                                         seed_data_collaborator["gestion"].email)
    assert "already in use" in err


# ---------- Validate Role ----------
def test_validate_role_valid():
    for role in ["gestion", "commercial", "support", "admin"]:
        assert Collaborator.validate_role(role)[0] == role


def test_validate_role_invalid():
    _, err = Collaborator.validate_role("fake")
    assert "invalid role" in err.lower()


# ---------- Validate Password ----------
def test_validate_password_valid():
    hashed, err = Collaborator.validate_password("secure123")
    assert bcrypt.checkpw("secure123".encode(), hashed)
    assert err is None


def test_validate_password_empty():
    _, err = Collaborator.validate_password("")
    assert "must not be empty" in err


def test_validate_password_too_long():
    long_pwd = "x" * 73
    _, err = Collaborator.validate_password(long_pwd)
    assert "maximum length" in err


# ---------- Check Password ----------
def test_check_password_correct():
    plain_pwd = "hello123"
    hashed = bcrypt.hashpw(plain_pwd.encode(), bcrypt.gensalt())
    c = Collaborator(password=hashed)
    assert c.check_password("hello123") is True


def test_check_password_incorrect():
    hashed = bcrypt.hashpw("abc".encode(), bcrypt.gensalt())
    c = Collaborator(password=hashed)
    assert c.check_password("wrong") is False


def test_check_password_invalid_type():
    c = Collaborator(password=b"anything")
    with pytest.raises(TypeError):
        c.check_password(123)


# ---------- Validate Archived ----------
def test_validate_archived():
    for val in ["yes", "y", "true", "o", "oui"]:
        assert Collaborator.validate_archived(val)[0] is True
    for val in ["non", "n", "false", "no"]:
        assert Collaborator.validate_archived(val)[0] is False


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

import pytest
from epic_event.models import Collaborator
from epic_event.permission import has_object_permission


# ---------- Collaborator Permissions ----------
def test_admin_has_all_rights(seed_data_collaborator):
    admin = seed_data_collaborator["admin"]
    other = Collaborator(id=999)
    assert has_object_permission(admin, "delete", other)


def test_gestion_can_modify_other_collaborator(seed_data_collaborator):
    gestion = seed_data_collaborator["gestion"]
    other = Collaborator(id=888)
    assert has_object_permission(gestion, "modify", other)


def test_collaborator_can_modify_self(seed_data_collaborator):
    user = seed_data_collaborator["support"]
    assert has_object_permission(user, "modify", user)


def test_collaborator_cannot_modify_others(seed_data_collaborator):
    user = seed_data_collaborator["support"]
    other = Collaborator(id=999)
    assert has_object_permission(user, "modify", other) is False


def test_collaborator_can_change_own_password(seed_data_collaborator):
    user = seed_data_collaborator["commercial"]
    assert has_object_permission(user, "password", user)


def test_collaborator_cannot_change_others_password(seed_data_collaborator):
    user = seed_data_collaborator["support"]
    other = Collaborator(id=999)
    assert has_object_permission(user, "password", other) is False


# ---------- Client Permissions ----------
def test_client_commercial_owns_client(seed_data_collaborator,
                                       seed_data_client):
    commercial = seed_data_collaborator["commercial"]
    seed_data_client.commercial = commercial
    assert has_object_permission(commercial, "modify", seed_data_client)


def test_client_support_cannot_modify_client(seed_data_collaborator,
                                             seed_data_client):
    support = seed_data_collaborator["support"]
    seed_data_client.commercial = Collaborator(id=998)
    assert has_object_permission(support, "modify", seed_data_client) is False


# ---------- Contract Permissions ----------
def test_contract_gestion_can_modify(seed_data_collaborator,
                                     seed_data_contract):
    gestion = seed_data_collaborator["gestion"]
    contract = seed_data_contract[0]
    assert has_object_permission(gestion, "modify", contract)


def test_contract_commercial_cannot_modify(seed_data_collaborator,
                                           seed_data_contract):
    commercial = seed_data_collaborator["commercial"]
    contract = seed_data_contract[0]
    assert has_object_permission(commercial, "modify", contract) is False


# ---------- Event Permissions ----------
def test_event_support_owns_event(seed_data_collaborator, seed_data_event):
    support = seed_data_collaborator["support"]
    seed_data_event.support = support
    assert has_object_permission(support, "modify", seed_data_event)


def test_event_gestion_can_update(seed_data_collaborator, seed_data_event):
    gestion = seed_data_collaborator["gestion"]
    assert has_object_permission(gestion, "update", seed_data_event)


def test_event_commercial_cannot_modify(seed_data_collaborator,
                                        seed_data_event):
    commercial = seed_data_collaborator["commercial"]
    assert has_object_permission(commercial, "modify",
                                 seed_data_event) is False

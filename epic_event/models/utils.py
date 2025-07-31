"""
Database Seeding Module for Epic Events.

This module provides helper functions to populate the database with initial or
test data for development and functional testing purposes. It creates default
users (collaborators), clients, contracts, and events using SQLAlchemy ORM.

Functions:
    - load_data_in_database(session): Seeds the database with production-like
        default data.
    - load_test_data_in_database(session): Inserts mock/test records for unit
        and integration testing.
    - load_super_user(session): Ensures an admin user exists with predefined
        credentials.

Data includes:
    - Collaborators: Roles include 'admin', 'gestion', 'commercial', and 'support'.
    - Clients: Linked to commercial collaborators.
    - Contracts: Some signed, others pending.
    - Events: Attached to signed contracts and supported by support collaborators.

Usage:
    from epic_event.db_seed import load_data_in_database
    load_data_in_database(session)

Notes:
    - Existing records are checked to avoid duplication.
    - `flush()` is used where necessary to populate relationships before inserts.
    - Passwords are hashed using `validate_password()` method of the `Collaborator` model.

Warning:
    These functions should not be used in production environments unless
    explicitly required.
"""
from datetime import date, timedelta, datetime

from sqlalchemy.orm import Session

from epic_event.models import Client, Collaborator, Contract, Event


def load_data_in_database(session: Session):
    # === Collaborators ===
    collaborators = session.query(Collaborator).all()
    if not collaborators:
        collaborators = []
        password, _ = Collaborator.validate_password("adminpass")
        collaborator = Collaborator(
            full_name="Admin User",
            email="admin@epicevent.com",
            role="admin",
            password=password
        )

        collaborators.append(collaborator)
        password, _ = Collaborator.validate_password("alicepass")
        collaborator = Collaborator(
            full_name="Alice Martin",
            email="alice@epicevent.com",
            role="gestion",
            password=password
        )
        collaborators.append(collaborator)
        password, _ = Collaborator.validate_password("brunopass")
        collaborator = Collaborator(
            full_name="Bruno Lefevre",
            email="bruno@epicevent.com",
            role="commercial",
            password=password
        )
        collaborators.append(collaborator)
        password, _ = Collaborator.validate_password("chloepass")
        collaborator = Collaborator(
            full_name="Chloé Dubois",
            email="chloe@epicevent.com",
            role="commercial",
            password=password
        )
        collaborators.append(collaborator)
        password, _ = Collaborator.validate_password("davidpass")
        collaborator = Collaborator(
            full_name="David Morel",
            email="david@epicevent.com",
            role="support",
            password=password
        )
        collaborators.append(collaborator)
        password, _ = Collaborator.validate_password("emmapass")
        collaborator = Collaborator(
            full_name="Emma Bernard",
            email="emma@epicevent.com",
            role="support",
            password=password
        )
        collaborators.append(collaborator)

        session.add_all(collaborators)
        session.flush()

        # === Clients ===
        clients = [
            Client(full_name="Jean Dupont",
                   email="jean@nova.com",
                   phone="0102030405",
                   company_name="Entreprise Nova",
                   created_date=date(2025, 3, 25),
                   last_contact_date=date(2025, 3, 25),
                   id_commercial=collaborators[3].id),

            Client(full_name="Sophie Durant",
                   email="sophie@techline.com",
                   phone="0605040302",
                   company_name="Techline SARL",
                   created_date=date(2025, 4, 1),
                   last_contact_date=date(2025, 4, 1),
                   id_commercial=collaborators[2].id),

            Client(full_name="Marc Petit",
                   email="marc@alphacorp.com",
                   phone="0758493021",
                   company_name="AlphaCorp",
                   created_date=date(2025, 4, 15),
                   last_contact_date=date(2025, 4, 15),
                   id_commercial=collaborators[3].id),
        ]
        session.add_all(clients)
        session.flush()

        # === Contracts ===
        contracts = [
            Contract(total_amount="10000", amount_due="0",
                     created_date=date(2025, 4, 15),
                     signed=True, client_id=clients[0].id),

            Contract(total_amount="8500", amount_due="0",
                     created_date=date(2025, 4, 25),
                     signed=True, client_id=clients[1].id),

            Contract(total_amount="12000", amount_due="0",
                     created_date=date(2025, 5, 8),
                     signed=True, client_id=clients[2].id),

            Contract(total_amount="15000", amount_due="0",
                     created_date=date(2025, 5, 30),
                     signed=True, client_id=clients[0].id),

            Contract(total_amount="9500", amount_due="0",
                     created_date=date(2025, 6, 3),
                     signed=True, client_id=clients[1].id),

            Contract(total_amount="6000", amount_due="6000",
                     created_date=date(2025, 7, 13),
                     signed=True, client_id=clients[2].id),

            Contract(total_amount="11000", amount_due="11000",
                     created_date=date(2025, 7, 18),
                     signed=False, client_id=clients[0].id),
        ]
        session.add_all(contracts)
        session.flush()

        # === Events ===
        events = [
            Event(title="Conférence TechNova",
                  start_date=datetime.strptime(
                      "08-06-2025 09:00", "%d-%m-%Y %H:%M"
                  ),
                  end_date=datetime.strptime(
                      "10-06-2025 18:00", "%d-%m-%Y %H:%M"
                  ),
                  location="Paris", participants=150,
                  notes="Conférence terminée avec succès.",
                  contract_id=contracts[0].id,
                  support_id=collaborators[5].id),

            Event(title="Salon des Innovations",
                  start_date=datetime.strptime(
                      "18-06-2025 10:00", "%d-%m-%Y %H:%M"
                  ),
                  end_date=datetime.strptime(
                      "20-06-2025 17:00", "%d-%m-%Y %H:%M"
                  ),
                  location="Lyon", participants=200,
                  notes="Salon très fréquenté.",
                  contract_id=contracts[1].id,
                  support_id=collaborators[4].id),

            Event(title="Séminaire Alpha",
                  start_date=datetime.strptime(
                      "28-06-2025 08:30", "%d-%m-%Y %H:%M"),
                  end_date=datetime.strptime(
                      "30-06-2025 17:30", "%d-%m-%Y %H:%M"),
                  location="Bordeaux", participants=100,
                  notes="Retour très positif.",
                  contract_id=contracts[2].id,
                  support_id=collaborators[5].id),

            Event(title="Forum Digital",
                  start_date=datetime.strptime(
                      "23-07-2025 09:00", "%d-%m-%Y %H:%M"
                  ),
                  end_date=datetime.strptime(
                      "24-07-2025 17:00", "%d-%m-%Y %H:%M"
                  ),
                  location="Marseille", participants=80,
                  notes="Préparation en cours.",
                  contract_id=contracts[3].id,
                  support_id=collaborators[4].id),

            Event(title="Atelier Startups",
                  start_date=datetime.strptime(
                      "28-07-2025 14:00", "%d-%m-%Y %H:%M"
                  ),
                  end_date=datetime.strptime(
                      "29-07-2025 18:00", "%d-%m-%Y %H:%M"
                  ),
                  location="Nice", participants=120,
                  notes="Inscription ouverte.",
                  contract_id=contracts[4].id,
                  support_id=None),
        ]
        session.add_all(events)
        session.commit()


def load_test_data_in_database(session: Session):
    # === Collaborators ===
    admin = session.query(Collaborator).filter_by(
        role="admin").first()
    if not admin:
        password, _ = Collaborator.validate_password("adminpass")
        admin = Collaborator(
            full_name="Admin User",
            email="admin@example.com",
            role="admin",
            password=password
        )
        session.add(admin)
        session.commit()

    gestion = session.query(Collaborator).filter_by(
        email="alice@example.com"
    ).first()
    if not gestion:
        password, _ = Collaborator.validate_password("mypassword")
        gestion = Collaborator(
            full_name="Alice",
            email="alice@example.com",
            role="gestion",
            password=password
        )
        session.add(gestion)

    commercial = session.query(Collaborator).filter_by(
        email="dup@example.com"
    ).first()
    if not commercial:
        password, _ = Collaborator.validate_password("mypassword")
        commercial = Collaborator(
            full_name="Dup",
            email="dup@example.com",
            role="commercial",
            password=password
        )

        session.add(commercial)

    support = session.query(Collaborator).filter_by(
        email="bob@example.com"
    ).first()
    if not support:
        password, _ = Collaborator.validate_password("mypassword")
        support = Collaborator(
            full_name="Bob",
            email="bob@example.com",
            role="support",
            password=password
        )

        session.add(support)

    archived_collab = session.query(Collaborator).filter_by(
        archived=True
    ).first()

    if not archived_collab:
        password, _ = Collaborator.validate_password("mypassword")
        archived_collab = Collaborator(
            full_name="Toto",
            email="toto@example.com",
            role="gestion",
            password=password,
            archived=True
        )
        session.add(archived_collab)

    session.commit()

    # === Client ===
    client = session.query(Client).filter_by(email="client@test.com").first()
    if not client:
        client = Client(
            full_name="Client Test",
            email="client@test.com",
            phone="0102030405",
            company_name="TestCorp",
            created_date=date.today() - timedelta(days=10),
            last_contact_date=date.today(),
            id_commercial=commercial.id
        )
        session.add(client)
        session.commit()

    # === Contracts ===
    contracts = session.query(Contract).filter_by(client_id=client.id).all()
    if not contracts:
        signed_contract = Contract(
            total_amount="100",
            amount_due="50",
            created_date=date.today() - timedelta(days=10),
            signed=True,
            client_id=client.id
        )
        not_signed_contract = Contract(
            total_amount="200",
            amount_due="100",
            created_date=date.today() - timedelta(days=5),
            signed=False,
            client_id=client.id
        )
        contract_with_event = Contract(
            total_amount="300",
            amount_due="150",
            created_date=date.today(),
            signed=True,
            client_id=client.id
        )
        session.add_all([signed_contract,
                         not_signed_contract,
                         contract_with_event
                         ])
        session.commit()

    # === Event ===
    contract_with_event = session.query(Contract).filter_by(
        total_amount="300",
        client_id=client.id
    ).first()

    existing_event = session.query(Event).filter_by(
        contract_id=contract_with_event.id
    ).first()

    if not existing_event:
        event = Event(
            title="Annual Gala",
            start_date=datetime.strptime(
                "08-06-2025 09:00", "%d-%m-%Y %H:%M"
            ),
            end_date=datetime.strptime(
                "10-06-2025 18:00", "%d-%m-%Y %H:%M"
            ),
            location="Paris",
            participants=100,
            notes="Formal event",
            contract_id=contract_with_event.id,
            support_id=support.id
        )
        session.add(event)
        session.commit()


def load_super_user(session):
    # === Collaborators ===
    admin = session.query(Collaborator).filter_by(
        email="admin@example.com").first()
    if not admin:
        password, _ = Collaborator.validate_password("adminpass")
        admin = Collaborator(full_name="Admin User",
                             email="admin@example.com",
                             role="admin",
                             password=password
                             )
        session.add(admin)
    session.commit()

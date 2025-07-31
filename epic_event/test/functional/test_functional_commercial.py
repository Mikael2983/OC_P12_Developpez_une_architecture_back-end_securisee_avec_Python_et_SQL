import re
import sys

import pexpect.popen_spawn


def expect_prompt(child, prompt_text):
    pattern = re.compile(
        rf".*{re.escape(prompt_text)}.*",
        re.IGNORECASE)
    child.expect(pattern)


def init_programme():
    child = pexpect.popen_spawn.PopenSpawn(
        "python main.py test",
        encoding="cp1252",
        timeout=10
    )
    child.logfile = sys.stdout
    return child


def commercial_connexion(child):
    child.sendline("1")
    child.expect("Nom d'utilisateur")
    child.sendline("Dup")
    child.expect("Password")
    child.sendline("mypassword")


def test_commercial_create_client(db_session):
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    commercial_connexion(child)

    # Menu entité
    child.expect("1. Collaborateur")
    child.expect("2. Client")
    child.expect("3. Contrat")
    child.expect("4. Événement")
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")
    # Aller dans Collaborateur
    child.sendline("2")

    child.expect("1. Afficher les détails")
    child.expect("2. Créer un nouveau client")
    child.expect("3. Modifier un client")
    child.expect("4. Supprimer un client")
    child.expect("5. Retour")
    expect_prompt(child, "Sélectionnez une option:")
    # Créer un collaborateur
    child.sendline("2")

    child.expect("Nom")
    child.sendline("Arthur Simon")
    child.expect("Email")
    child.sendline("arthur@compagny2test.com")
    child.expect("Téléphone")
    child.sendline("0202020202")
    child.expect("Société")
    child.sendline("Company2Test")
    child.expect("Dernier contact")
    child.sendline("02-07-2025")

    expect_prompt(child, "créé avec succès.")
    expect_prompt(child, "appuyer sur une touche pour continuer")

    # Retour au menu principal
    child.sendline("")
    child.sendline("5")
    child.expect("1. Collaborateur")
    expect_prompt(child, "Sélectionnez une option:")

    # Déconnexion
    child.sendline("5")
    child.expect("1- Se connecter")
    child.expect("2. Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Quitter
    child.sendline("2")
    child.expect(pexpect.EOF)


def test_commercial_create_event(db_session, seed_data_contract):
    # Lance le programme

    contract = seed_data_contract[0]

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    commercial_connexion(child)

    # Menu entité
    child.expect("1. Collaborateur")
    child.expect("2. Client")
    child.expect("3. Contrat")
    child.expect("4. Événement")
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")
    # Aller dans événements
    child.sendline("4")

    child.expect("1. Afficher les détails")
    child.expect("2. Créer un nouveau événement")
    child.expect("3. Retour")
    expect_prompt(child, "Sélectionnez une option:")

    # Créer un contrat
    child.sendline("2")

    child.expect("Id du Contract")
    child.sendline(str(contract.id))
    child.expect("Titre")
    child.sendline("anniversaire 50ans")
    child.expect("Date de début")
    child.sendline("25/09/2025 09:00")
    child.expect("Date de fin")
    child.sendline("25-09-2025 21:00")
    child.expect("Lieu")
    child.sendline("Lieu test")
    child.expect("Participants")
    child.sendline("200")
    child.expect("Notes")
    child.sendline("exemple de notes")

    expect_prompt(child, "créé avec succès.")
    expect_prompt(child, "appuyer sur une touche pour continuer")
    child.sendline("")
    # Retour au menu principal

    child.sendline("5")
    child.expect("1. Collaborateur")
    expect_prompt(child, "Sélectionnez une option:")

    # Déconnexion
    child.sendline("5")

    child.expect("2. Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Quitter
    child.sendline("2")
    child.expect(pexpect.EOF)


def test_commercial_create_event_with_no_signed_contract(db_session, seed_data_contract):
    # Lance le programme

    contract = seed_data_contract[0]

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    commercial_connexion(child)

    # Menu entité
    child.expect("1. Collaborateur")
    child.expect("2. Client")
    child.expect("3. Contrat")
    child.expect("4. Événement")
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")
    # Aller dans événements
    child.sendline("4")

    child.expect("1. Afficher les détails")
    child.expect("2. Créer un nouveau événement")
    child.expect("3. Retour")
    expect_prompt(child, "Sélectionnez une option:")

    # Créer un contrat
    child.sendline("2")

    child.expect("Id du Contract")
    child.sendline(str(contract.id))
    child.expect("Titre")
    child.sendline("anniversaire 50ans")
    child.expect("Date de début")
    child.sendline("25/09/2025 09:00")
    child.expect("Date de fin")
    child.sendline("25-09-2025 21:00")
    child.expect("Lieu")
    child.sendline("Lieu test")
    child.expect("Participants")
    child.sendline("200")
    child.expect("Notes")
    child.sendline("exemple de notes")

    expect_prompt(child, "créé avec succès.")
    expect_prompt(child, "appuyer sur une touche pour continuer")
    child.sendline("")
    # Retour au menu principal

    child.sendline("5")
    child.expect("1. Collaborateur")
    expect_prompt(child, "Sélectionnez une option:")

    # Déconnexion
    child.sendline("5")
    child.expect("1- Se connecter")
    child.expect("2. Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Quitter
    child.sendline("2")
    child.expect(pexpect.EOF)

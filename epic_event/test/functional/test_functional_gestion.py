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


def gestion_connexion(child):
    child.sendline("1")
    child.expect("Nom d'utilisateur")
    child.sendline("Alice")
    child.expect("Password")
    child.sendline("mypassword")


def test_gestion_create_collaborator(db_session):
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    gestion_connexion(child)

    # Menu entité
    child.expect("1. Collaborateur")
    child.expect("2. Client")
    child.expect("3. Contrat")
    child.expect("4. Événement")
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")
    # Aller dans Collaborateur
    child.sendline("1")

    child.expect("1. Afficher les détails")
    child.expect("2. Créer un nouveau collaborateur")
    child.expect("3. Modifier un collaborateur")
    child.expect("4. Supprimer un collaborateur")
    child.expect("5. Retour")
    expect_prompt(child, "Sélectionnez une option:")
    # Créer un collaborateur
    child.sendline("2")

    child.expect("Nom")
    child.sendline("Jean Dupont")
    child.expect("Mot de passe")
    child.sendline("pass1234")
    child.expect("Email")
    child.sendline("jean@exemple.com")
    child.expect("Service")
    child.sendline("commercial")

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


def test_gestion_create_contract(db_session):
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    gestion_connexion(child)

    # Menu entité
    child.expect("1. Collaborateur")
    child.expect("2. Client")
    child.expect("3. Contrat")
    child.expect("4. Événement")
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")
    # Aller dans Contrat
    child.sendline("3")

    child.expect("1. Afficher les détails")
    child.expect("2. Créer un nouveau contrat")
    child.expect("3. Modifier un contrat")
    child.expect("4. Supprimer un contrat")
    child.expect("5. Retour")
    expect_prompt(child, "Sélectionnez une option:")
    # Créer un contrat
    child.sendline("2")

    child.expect("Id du client")
    child.sendline("1")
    child.expect("Montant total")
    child.sendline("3000")
    child.expect("Montant dû")
    child.sendline("3000")
    child.expect("Signature")
    child.sendline("non")

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

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


def support_connexion(child, password):
    child.sendline("1")
    child.expect("Nom d'utilisateur")
    child.sendline("Bob")
    child.expect("Password")
    child.sendline(password)


def test_support_modify_password():
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    support_connexion(child, "mypassword")

    # Menu entité
    child.expect("1. Collaborateur")
    child.expect("2. Client")
    child.expect("3. Contrat")
    child.expect("4. Événement")
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")
    # Aller dans Collaborateur
    child.sendline("1")
    child.expect("2. Modifier un collaborateur")
    child.sendline("2")
    child.expect("id du collaborateur")
    # Try unknown id
    child.sendline("1")
    child.expect("collaborateur introuvable.")

    # Try wrong id
    child.sendline("2")
    child.expect("Vous n'avez pas l'autorisation")

    child.sendline("4")
    child.expect("1. mot de passe")

    child.sendline("1")
    expect_prompt(child, "veuillez renseigner mot de passe")
    child.sendline("bobpass")
    child.expect("Le champ password a été mis à jour")
    child.sendline("")
    child.expect("3. Enregistrer")
    child.sendline("3")
    child.sendline("3")
    child.sendline("5")
    child.sendline("1")
    child.sendline("Bob")
    child.sendline("bobpass")
    child.expect("Bienvenue Bob - Service : support")


def test_support_modify_event():
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    support_connexion(child, "bobpass")

    # Menu entité
    child.expect("1. Collaborateur")
    child.expect("2. Client")
    child.expect("3. Contrat")
    child.expect("4. Événement")
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")

    # Aller dans Événement
    child.sendline("4")

    # Modifier un événement
    child.expect("2. Modifier un événement")
    child.sendline("2")
    # Sélectionner l'événement
    child.expect("entrer l'id du événement")
    child.sendline("1")
    # Sélectionner le champ participants
    child.expect("5. Participants")
    child.sendline("5")
    child.sendline("150")
    child.sendline("")
    # Sélectionner le champ Notes
    child.expect("6. Notes")
    child.sendline("6")
    child.sendline("event's notes updated")
    child.sendline("")
    child.expect("8. Enregistrer")
    child.sendline("8")

    child.expect("4. Retour")
    child.sendline("4")
    # déconnexion
    child.sendline("5")
    # quitter
    child.sendline("2")

    child.expect(pexpect.EOF)


def test_support_modify_wrong_event():
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    support_connexion(child, "bobpass")

    # Menu entité
    child.expect("1. Collaborateur")
    child.expect("2. Client")
    child.expect("3. Contrat")
    child.expect("4. Événement")
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")

    # Aller dans Événement
    child.sendline("4")

    # Modifier un événement
    child.expect("2. Modifier un événement")
    child.sendline("2")
    # Sélectionner l'événement
    child.expect("entrer l'id du événement")
    child.sendline("2")
    child.expect("événement introuvable.")

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
        "python main.py test ",
        encoding="cp1252",
        timeout=10
    )
    child.logfile = sys.stdout
    return child


def admin_connexion(child):
    child.sendline("1")
    child.expect("Nom d'utilisateur")
    child.sendline("Admin User")
    child.expect("Password")
    child.sendline("adminpass")


def test_admin_create_collaborator(db_session):
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    admin_connexion(child)

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
    child.expect("5. Afficher les archives")
    child.expect("6. Retour")
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
    child.sendline("6")
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


def test_admin_modify_collaborator(db_session):
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    admin_connexion(child)

    # Menu entité
    child.expect("1. Collaborateur")
    expect_prompt(child, "Sélectionnez une option:")

    # Aller dans menu collaborateurs admin
    child.sendline("1")

    child.expect("3. Modifier un collaborateur")
    expect_prompt(child, "Sélectionnez une option:")

    # Modifier un collaborateur
    child.sendline("3")

    # sélectionner un collaborateur
    expect_prompt(child, "id du collaborateur")
    child.sendline("4")

    # sélectionner un champ
    expect_prompt(child, "Sélectionnez le champs à modifier")
    child.expect("1. Nom")
    child.expect("2. Mot de passe")
    child.expect("3. Email")
    child.expect("4. Service")
    child.expect("5. Archivé")
    child.expect("6. Retour")
    child.expect("7. Enregistrer")
    expect_prompt(child, "Sélectionnez une option:")

    # sélection du champ Nom
    child.sendline("1")
    child.expect("veuillez renseigner Nom")

    child.sendline("Dup")
    expect_prompt(child, "This full name is already in use.")

    # child.sendline("Robert")
    child.sendline("1")
    child.expect("veuillez renseigner Nom")
    child.sendline("Robert")

    expect_prompt(child, "a été mis à jour (non sauvegardé)")
    expect_prompt(child, "appuyer sur une touche pour continuer")
    child.sendline("")

    # Retour au menu collaborateur admin

    child.sendline("7")
    child.expect("1. Afficher les détails")
    child.expect("2. Créer un nouveau collaborateur")
    child.expect("3. Modifier un collaborateur")
    child.expect("4. Supprimer un collaborateur")
    child.expect("5. Afficher les archives")
    child.expect("6. Retour")
    expect_prompt(child, "Sélectionnez une option:")

    child.sendline("6")
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


def test_admin_delete_collaborator(db_session):
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    admin_connexion(child)

    # Menu entité
    child.expect("1. Collaborateur")
    expect_prompt(child, "Sélectionnez une option:")

    # Aller dans menu collaborateurs admin
    child.sendline("1")

    child.expect("5. Afficher les archives")
    child.expect("6. Retour")
    expect_prompt(child, "Sélectionnez une option:")

    # Afficher les archives
    child.sendline("5")
    child.expect("5. Masquer les archives")

    # Supprimer un collaborateur
    child.sendline("4")

    # sélectionner l'id de collaborateur
    child.expect("id du collaborateur")
    child.sendline("5")

    expect_prompt(child, "voulez-vous effectuer cette opération?")
    child.sendline("y")

    expect_prompt(child, "supprimé avec succès.")
    child.sendline("")

    # Retour au menu principal
    child.expect("6. Retour")
    child.sendline("6")

    # Déconnexion
    child.expect("1. Collaborateur")
    expect_prompt(child, "Sélectionnez une option:")
    child.sendline("5")

    # Quitter
    child.expect("2. Quitter")
    expect_prompt(child, "Sélectionnez une option:")
    child.sendline("2")

    child.expect(pexpect.EOF)


def test_admin_create_client(db_session, seed_data_collaborator):
    # Lance le programme

    child = init_programme()

    commercial = seed_data_collaborator["commercial"]

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    admin_connexion(child)

    # Menu entité

    child.expect("2. Client")

    expect_prompt(child, "Sélectionnez une option:")

    # Aller dans Collaborateur
    child.sendline("2")
    child.expect("2. Créer un nouveau client")
    expect_prompt(child, "Sélectionnez une option:")

    # Créer un collaborateur
    child.sendline("2")

    child.expect("Nom du contact")
    child.sendline("Arthur Simon")
    child.expect("Email")
    child.sendline("arthursimon@exemple.com")
    child.expect("Téléphone")
    child.sendline("0101010101")
    child.expect("Société")
    child.sendline("Company1Test")
    child.expect("Dernier contact")
    child.sendline("02-07-2025")
    child.expect("Id Commercial")
    child.sendline(str(commercial.id))

    expect_prompt(child, "créé avec succès.")
    expect_prompt(child, "appuyer sur une touche pour continuer")
    child.sendline("")
    # Retour au menu principal
    child.expect("6. Retour")
    child.sendline("6")

    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")

    # Déconnexion
    child.sendline("5")
    child.expect("2. Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Quitter
    child.sendline("2")
    child.expect(pexpect.EOF)


def test_admin_create_contract(db_session):
    # Lance le programme

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    child.expect("2- Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    admin_connexion(child)

    # Menu entité
    child.expect("3. Contrat")
    expect_prompt(child, "Sélectionnez une option:")

    # Aller dans Contrat
    child.sendline("3")
    child.expect("2. Créer un nouveau contrat")
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
    child.sendline("")
    # Retour au menu principal

    child.sendline("6")
    child.expect("1. Collaborateur")
    expect_prompt(child, "Sélectionnez une option:")

    # Déconnexion
    child.sendline("5")
    child.expect("2. Quitter")
    expect_prompt(child, "Sélectionnez une option:")

    # Quitter
    child.sendline("2")
    child.expect(pexpect.EOF)


def test_admin_create_event(db_session, seed_data_contract):
    # Lance le programme

    contract = seed_data_contract[0]

    child = init_programme()

    # Étape 1 : Accueil
    child.expect("1- Se connecter")
    expect_prompt(child, "Sélectionnez une option:")

    # Connexion
    admin_connexion(child)

    # Menu Role
    child.expect("4. Événement")
    expect_prompt(child, "Sélectionnez une option:")
    child.sendline("4")

    # Menu Entity
    child.expect("2. Créer un nouveau événement")
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
    child.expect("6. Retour")
    child.sendline("6")

    # Déconnexion
    child.expect("5. Déconnexion")
    expect_prompt(child, "Sélectionnez une option:")
    child.sendline("5")

    # Quitter
    child.expect("2. Quitter")
    expect_prompt(child, "Sélectionnez une option:")
    child.sendline("2")

    child.expect(pexpect.EOF)

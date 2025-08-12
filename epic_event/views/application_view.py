"""
Module for managing user interface display and input for an event management
 CLI application.
 """
import pwinput
from rich.console import Console
from rich import print

from epic_event.settings import (TEXT_STYLE, REQUEST_STYLE, SUCCESS_STYLE,
                                 ERROR_STYLE, translate_entity)
from epic_event.views.utils_view import UtilsView


class ApplicationView:
    """
    Handles all user interface logic, including displaying menus, prompting
    for input and showing messages in a stylized format using the Rich library.
    """

    def __init__(self, SESSION: dict):
        """
        Initialize the ApplicationView with a SESSION dictionary and required
        utilities.
        """
        self.console = Console()
        self.utils_view = UtilsView()
        self.SESSION = SESSION

    def display_home_menu(self):
        """
        Display the main home menu with options to log in or quit the
        application.
        """
        header = "Bienvenue dans votre outil de gestion d'événements"
        request = "Que souhaitez vous faire?"
        text = ["1- Se connecter", "2- Quitter"]
        self.utils_view.display_styled_menu(header, request, text)

    def display_connection_menu(self):
        """
        Prompt the user to input their username and password for login.

        Returns:
            tuple: A tuple containing the username and password.
        """
        self.utils_view.apply_rich_style(
            "Connexion utilisateur", TEXT_STYLE)

        username = self.console.input(
            self.utils_view.apply_rich_style(
                "Nom d'utilisateur :",
                TEXT_STYLE
            ))

        print(self.utils_view.apply_rich_style(
            "Password :", TEXT_STYLE))
        password = pwinput.pwinput(prompt="", mask="*")

        return username, password

    def choose_option(self) -> str:
        """
        Prompt the user to select an option from a menu.

        Returns:
            str: The selected option input by the user.
        """
        return self.console.input(
            self.utils_view.apply_rich_style(
                "Sélectionnez une option:",
                REQUEST_STYLE
            ))

    def choose_field(self) -> int:
        """
        Prompt the user to select an option from a menu.

        Returns:
            int: The index of the field selected in the list fields.
        """
        while True:
            choice = self.console.input(
                self.utils_view.apply_rich_style(
                    "Sélectionnez une option:",
                    REQUEST_STYLE
                ))
            try:
                choice = int(choice)
                break

            except ValueError:
                self.display_error_message("saisie non valide")
                continue

        return int(abs(choice) - 1)

    def valide_choice_menu(self):
        """
        Ask the user to confirm an operation.

        Returns:
            bool: True if the user confirms (Y), False otherwise.
        """
        while True:
            valid = self.console.input(
                self.utils_view.apply_rich_style(
                    "voulez-vous effectuer cette opération? (Y/N) ",
                    REQUEST_STYLE)
            ).lower()
            if valid in {"y", "n"}:
                return valid == 'y'

    @staticmethod
    def clear_console():
        """
        Clear the console screen, depending on the operating system.
        """
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def break_point(self):
        """
        Pause execution and wait for the user to press a key before continuing.
        """
        print(self.utils_view.apply_rich_style(
            "appuyer sur une touche pour continuer", TEXT_STYLE))
        input()

    def display_success_message(self, message):
        """
        Display a success message using the success style.

        Args:
            message (str): The success message to display.
        """
        print(self.utils_view.apply_rich_style(message, SUCCESS_STYLE))

    def display_error_message(self, message):
        """
        Display an error message using the error style.

        Args:
            message (str): The error message to display.
        """
        print(self.utils_view.apply_rich_style(message, ERROR_STYLE))

    def display_informative_message(self, message):
        """Display an informative message using the default text style.

        Args:
            message (str): The message to display.
        """
        print(self.utils_view.apply_rich_style(message, TEXT_STYLE))

    def display_entity_menu(self):
        """
        Display the main entity selection menu
        (Collaborators, Clients, Contracts, Events).
        """
        header = f"--- Menu EpicEvent ---"
        request = "Sélectionnez une catégorie ?"

        text = [f"{i + 1}. {item.capitalize()}" for i, (key, item) in
                enumerate(translate_entity.items())]
        text.append(f"{len(translate_entity) + 1}. Déconnexion")

        self.utils_view.display_styled_menu(header, request, text)

    def display_entity_menu_role(self, role, entity_name, options):
        """
        Displays a context menu based on the user’s role and the entity
        concerned.

        This method dynamically generates an interactive menu adapted to the
        role (`admin`, `commercial`, etc.) and to the manipulated entity
        (`client`, `event, etc.), by listing the available actions
        (details, creation, modification, deletion, etc.).

        For administrators, it also adds an option to show or hide archives,
        depending on the current state stored in
        `self.SESSION["show_archived"]`.

        Args:
            role (str): The role of the logged in user.
            entity_name (str): The name of the target entity (
                e.g. 'client', 'contract', etc.).
            options (list): List of actions available to the user on this
                            entity.
                            Each element is a string

        Display:
            - A custom header with the role.
            - A numbered menu of possible options.
            - A "Show/Hide archives" option for administrators.
            - A "Back" option at the end.

        Example of generated menu:

        --- Menu Admin ---
            1. Afficher les détails
            2. Créer un nouveau client
            3. Modifier un client
            4. Supprimer un client
            5. Afficher les archives
            6. Retour
        """
        translated_entity = translate_entity[entity_name]

        header = f"--- Menu {translated_entity.capitalize()} ---"
        request = "Sélectionnez une option ?"

        display_options = {"details": "Afficher les détails",
                           "create": f"Créer un nouveau {translated_entity}",
                           "modify": f"Modifier un {translated_entity}",
                           "delete": f"Supprimer un {translated_entity}"}

        text = [f"{i + 1}. {display_options[option]}" for i, option in
                enumerate(options)]

        list_number = len(options) + 1

        if role == "admin":
            if self.SESSION["show_archived"]:
                text.append(f"{list_number}. Masquer les archives")
            else:
                text.append(f"{list_number}. Afficher les archives")
            list_number += 1

        text.append(f"{list_number}. Retour")

        self.utils_view.display_styled_menu(header, request, text)

    def display_menu_details(self):
        """
        Display detail menu options for a given entity.

        """
        header = f"--- Menu détails ---"
        request = "Sélectionnez une option:"

        text = [
            "1. Filtrer par champs",
            "2. Trier par champs",
            "3. Afficher les détails",
            "4. Retour"]

        self.utils_view.display_styled_menu(header, request, text)

    def ask_id(self, entity_name):
        """
        Prompt the user to enter an entity ID.

        Args:
            entity_name (str): The name of the entity type.

        Returns:
            str: The entered ID or empty string to go back.
        """
        name = translate_entity[entity_name]
        message = f"entrer l'id du {name} (taper 'enter' pour revenir):"
        return self.console.input(
            self.utils_view.apply_rich_style(
                message,
                TEXT_STYLE))

    def ask_information(self, information):
        """
        Prompt the user to input a value for a specific piece of information.

        Args:
            information (str): The label for the information to request.

        Returns:
            str: The entered value, or an empty string if nothing is entered.
        """
        value = self.console.input(
            self.utils_view.apply_rich_style(
                f"veuillez renseigner {information}:",
                TEXT_STYLE))
        if value:
            return value
        return ""

    def ask_descending_order(self):
        """
        Ask the user whether to sort in descending order.

        Returns:
            bool: True if the user chooses descending, False otherwise.
        """
        response = self.console.input(
            self.utils_view.apply_rich_style(
                "Trier par ordre décroissant ? (Y/N) : ",
                TEXT_STYLE)).lower()
        return response.lower() in ["y", "yes", "o", "oui"]

    def ask_filter_value(self, field):
        """
        Prompt the user to provide a value to filter by.

        Args:
            field (list): A list of ORM field keys to list of
                [ORM field, display name].

        Returns:
            tuple: A tuple containing the ORM field and the value.
        """
        orm_field, display_name = field
        value = self.console.input(
            self.utils_view.apply_rich_style(
                f"Saisir la valeur pour '{display_name}' : ",
                TEXT_STYLE
            ))
        return orm_field, value.strip()

    def display_list_field_menu(self, entity_fields: list, purpose):
        """
        For order request.
        Display a field selection menu based on a list of entity fields.

        Args:
            entity_fields (list): A list of list containing field metadata.
            purpose (str): the reason why the user needs the menu
                ( order or filter)
        Returns:
            Any: The result from the styled menu utility.
        """
        header = "--- Menu de sélection des champs ---"

        if purpose == "order":
            request = "Sélectionnez un critère de tri:"

        if purpose == "filter":
            request = "Choisissez un champ à filtrer: "

        if purpose == "modify":
            request = "Choisissez un champ à modifier: "

        text = [f"{i + 1}. {entity_fields[i][1]}" for i in
                range(len(entity_fields))]
        text.append(f"{len(entity_fields) + 1}. Retour")

        self.utils_view.display_styled_menu(header, request, text)

    def display_modify_field_menu(self, entity_fields: list):
        """
        For modify request
        Display a field selection menu based on a list of entity fields.

        Args:
            entity_fields (list): A list of list containing field metadata.

        Returns:
            Any: The result from the styled menu utility.
        """
        header = "--- Menu de sélection des champs ---"
        request = "Sélectionnez le champs à modifier"

        text = [f"{i + 1}. {entity_fields[i][1]}" for i in
                range(len(entity_fields))]
        text.append(f"{len(entity_fields) + 1}. Retour")
        text.append(f"{len(entity_fields) + 2}. Enregistrer")

        self.utils_view.display_styled_menu(header, request, text)

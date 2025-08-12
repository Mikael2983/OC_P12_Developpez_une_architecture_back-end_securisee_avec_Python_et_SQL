"""
CLI controller main module.

Coordinates interactions between the user, command line views,
the business controllers (user, entities) and the database via
SQLAlchemy.
Manages authentication, dynamic menus by role, and operations on
the entities.
"""
from sqlalchemy.orm import Session

from epic_event.controllers.entity_controller import EntityController
from epic_event.controllers.user_controller import UserController
from epic_event.models import Collaborator

from epic_event.permission import permissions
from epic_event.views.collaborator_view import CollaboratorView
from epic_event.views.contract_view import ContractView
from epic_event.views.event_view import EventView
from epic_event.views.application_view import ApplicationView
from epic_event.views.client_view import ClientView

from epic_event.settings import SESSION, ENTITIES


class MainController:
    """
    Main controller of the application in command line.

    Initializes views, secondary controllers and manages the life cycle
    of the application, from the homepage to CRUD operations according to the
    roles.
    """

    def __init__(self, session: Session):
        """
        Initializes the components of the CLI application.

        Args:
            session (Session): SQLAlchemy session for database access.
        """
        self.SESSION = SESSION  # Variable d'environnement
        self.app_view = ApplicationView(self.SESSION)
        self.entity_controller = EntityController(self.SESSION)
        self.client_view = ClientView(self.SESSION)
        self.collaborator_view = CollaboratorView(self.SESSION)
        self.contract_view = ContractView(self.SESSION)
        self.event_view = EventView(self.SESSION)
        self.user_controller = UserController(self.SESSION)
        self.session = session  # session SQL

    def run(self):
        """
        Starts the main loop of the CLI program.

        Displays the home menu, manages the user’s connection,
        then redirects to the entities menu or leaves the application.
        """
        while True:
            self.app_view.clear_console()
            self.app_view.display_home_menu()
            choix = self.app_view.choose_option()
            if choix == "1":
                user = self.user_controller.connexion(self.session)

                if not user:
                    continue

                self.SESSION["user"] = user
                self.app_view.clear_console()
                self.handle_entity_action(user)

            elif choix == "2":
                self.SESSION["user"] = None
                break

    def handle_entity_action(self, user: Collaborator):
        """
        Displays the main entity selection menu and delegates user actions
        based on the selected entity.

        This method serves as the main navigation point after a user logs in.
        It presents a list of available entities (e.g., collaborators,
        clients, contracts, events) that the user can interact with.

        The method runs in a loop until the user chooses to exit the entity
        menu.

        Args:
            user (Collaborator): The authenticated user currently interacting
                with the system.

        Behavior:
            - Clears the console and welcomes the user with their name and
                role.
            - Displays a menu of available entities.
            - Waits for the user to select an entity.
            - If a valid entity is selected, delegates to
                `handle_user_role_action()` to handle role-specific logic and
                permissions for that entity.
            - If the user chooses to exit (option 5), the loop breaks.
        """

        while True:
            self.app_view.clear_console()
            self.app_view.display_informative_message(
                f"Bienvenue {user.full_name} - Service : {user.role}")
            self.app_view.display_entity_menu()
            choice = self.app_view.choose_field()

            if choice >= len(ENTITIES):  # choice of disconnection
                break

            entity_name = ENTITIES[choice]

            if entity_name:
                self.handle_user_role_action(user, entity_name)
            else:
                continue

    def handle_user_role_action(self, user, entity_name):
        """
        Displays the menu of actions available for a specific entity, based on
        the user's role.

        This method manages the interaction loop for a given entity (e.g.,
        clients, contracts), dynamically displaying the allowed actions for the
        current user, and invoking the corresponding controller methods based
        on the user's selection.

        Args:
            user (Collaborator): The currently authenticated user.
            entity_name (str): The name of the entity to be handled
                (e.g., 'client', 'contract').

        Behavior:
            - Verifies that the user's role is authorized to interact with the
                entity.
            - Displays the list of items for the selected entity.
            - Shows a role-specific menu of actions (e.g., view details,
                create, modify).
            - For admin users, includes an additional option to show/hide
                archived records.
            - Waits for user input and dynamically resolves and executes the
                corresponding method.
            - If the selected action is invalid or not callable, displays an
                error message.

        Notes:
            - Actions are dynamically constructed and executed using `eval()`
                based on the selected index and role permissions.
            - The loop continues until the user selects the "Back" option.
            - Invalid role access triggers an error message and exits the
                method early.
        """
        controller = ["self",
                      "self.entity_controller",
                      "self.entity_controller",
                      "self.entity_controller"]

        role = user.role.lower()

        if role not in permissions[entity_name]:
            self.app_view.display_error_message(
                f"Rôle utilisateur non pris en charge : {role}")
            return

        while True:
            self.app_view.clear_console()
            self.app_view.display_informative_message(
                f"Bienvenue {user.full_name} - Service : {user.role}")
            self.entity_controller.list_entity(
                self.session,
                entity_name
            )
            options = permissions[entity_name][role]

            self.app_view.display_entity_menu_role(user.role, entity_name,
                                                   options)

            choice = self.app_view.choose_option()

            try:
                int(choice)
            except ValueError:
                continue

            if int(choice) > len(options):
                if user.role == "admin" and int(choice) == len(options) + 1:
                    self.show_archived()
                    continue
                else:
                    break

            index = int(choice) - 1
            action_string = options[index]
            action_controller = controller[index]
            function_result_str = f"{action_controller}.{action_string}_entity"

            kwargs = {
                "user": user,
                "entity_name": entity_name,
                "session": self.session
            }

            action = eval(function_result_str)

            if callable(action):
                action(**kwargs)
            else:
                self.app_view.display_error_message("Option invalide.")
                self.app_view.break_point()

    def details_entity(self, user, entity_name, **kwargs):
        """
        Manages advanced consultation actions: filtering, sorting, details.

        Args:
            user (Collaborator): Authenticated user.
            entity_name (str): Name of the entity concerned.
        """
        menu_details = {
            "1": lambda: self.entity_controller.filter_by_field_entity(
                user,
                self.session,
                entity_name),
            "2": lambda: self.entity_controller.order_by_field_entity(
                user,
                self.session,
                entity_name),
            "3": lambda: self.entity_controller.show_details_entity(
                user,
                self.session,
                entity_name),
            "4": "Retour"
        }
        while True:
            self.app_view.clear_console()
            self.app_view.display_informative_message(
                f"Bienvenue {user.full_name} - Service : {user.role}")
            self.entity_controller.list_entity(
                self.session,
                entity_name
            )

            self.app_view.display_menu_details()
            choice = self.app_view.choose_option()

            action = menu_details.get(choice)

            if action == "Retour":
                break
            elif callable(action):
                action()
            else:
                self.app_view.display_error_message("Option invalide.")
                self.app_view.break_point()

    def show_archived(self):
        """
        Enables or disables the display of archived entities in the session.
        """
        if self.SESSION["show_archived"]:
            self.SESSION["show_archived"] = False
        else:
            self.SESSION["show_archived"] = True

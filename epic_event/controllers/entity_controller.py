"""
Entitycontroller module

This module contains the business logic to handle the main entities
from the Epic Event CRM application (Collaborator, Client, Contract, Event).

It acts as a centralized controller between the presentation layer (console)
and the ORM models. It allows displaying, creating, updating and
removal of entities, while taking into account the permissions and roles
connected users.

Main features:
- Conditional display of entities according to roles (admin, commercial,
    management, support)
- Application of business filters (e.g. unassigned events, signed contracts)
- Access control to modifiable fields according to roles and entities
- Management of business or integrity errors
- Calls to dynamic views according to the manipulated entity

Classes:
    - EntityController: single entry point to interact with entities.

Dependencies:
    - SQLAlchemy for managing ORM sessions and requests
    - renderer for Command Line Interface views
    - models for ORM entities
    - permissions for access rules

This module is used in the application’s main controller to orchestrate
interactions between the command line user, business logic and database.
"""
import inspect
from typing import Union

from sqlalchemy.orm import Session

from epic_event.controllers.client_controller import ClientController
from epic_event.controllers.collaborator_controller import \
    CollaboratorController
from epic_event.controllers.contract_controller import ContractController
from epic_event.controllers.event_controller import EventController
from epic_event.models import Client, Collaborator, Contract, Event
from epic_event.permission import has_object_permission
from epic_event.views.application_view import ApplicationView
from epic_event.views.client_view import ClientView
from epic_event.views.collaborator_view import CollaboratorView
from epic_event.views.contract_view import ContractView
from epic_event.views.event_view import EventView
from epic_event.settings import translate_entity


class EntityController:
    """
    Main controller for managing entities (Client, Collaborator, Contract,
    Event) and delegating calls to respective view/controller layers.
    """

    def __init__(self, SESSION):
        """
        Initialize controllers and views for all entities.
        Args:
            SESSION (dict): Global session dictionary used by the CLI app.
        """
        self.SESSION = SESSION
        self.controllers = {
            "client": ClientController(self.SESSION),
            "collaborator": CollaboratorController(self.SESSION),
            "contract": ContractController(self.SESSION),
            "event": EventController(self.SESSION),
        }
        self.views = {
            "client": ClientView(self.SESSION),
            "collaborator": CollaboratorView(self.SESSION),
            "contract": ContractView(self.SESSION),
            "event": EventView(self.SESSION),
        }
        self.app_view = ApplicationView(self.SESSION)

    @staticmethod
    def get_model(entity_name: str
                  ) -> Union[Client, Collaborator, Contract, Event]:
        """
        Return the model class based on the entity name.
        Args:
            entity_name (str): Name of the entity Keys of entities.
        Returns: ORM Model
        """

        return eval(entity_name.capitalize())

    @staticmethod
    def validate_field(Model: Union[Client, Collaborator, Contract, Event],
                       field: list[str],
                       session: Session,
                       user: Collaborator,
                       data: dict) -> Union[tuple[str, None], tuple[None, str]]:
        """
        Validate a field's value using the model's custom validation method
        if it exists.

        Dynamically checks if the model defines a method named
        'validate_<fieldname>'. If such a method is found, it inspects the
        required parameters and prepares the arguments based on the method
        signature, including session, user, or field values from input data.

        Args:
            Model (BaseModel): The SQLAlchemy model class.
            field (list): A list containing the field name and its display
                label.
            session (Session): SQLAlchemy session instance.
            user (Collaborator): The current user performing the operation.
            data (dict): The current state of the form or field values.

        Returns:
            tuple: (validated_value, None) if validation is defined,
                   otherwise returns (None, error_message).
        """
        method_name = f"validate_{field[0]}"
        if hasattr(Model, method_name):
            method = getattr(Model, method_name)
            sig = inspect.signature(method)
            args = [
                session if param.annotation.__name__ == "Session"
                else user if name == "user"
                else data.get(name)
                for name, param in sig.parameters.items()
            ]

            return method(*args)

        error = f"le {field[1]} n'a pas de méthode 'validate_{field[0]}"
        return None, error

    def list_entity(
            self,
            session: Session,
            entity_name: str,
            user: Collaborator = None,
            purpose: str = "list"
    ) -> str | None:
        """
        Display a list of entities, filtered by user role and intent (view or
         modify).

        This method merges both listing and update-specific entity filtering
        rules.
        Rules vary depending on the entity, user role, and purpose
        ('list' or 'modify').

        Args:
            session (Session): SQLAlchemy session.
            entity_name (str): Name of the entity to display (e.g., 'clients').
            user (Collaborator, optional): Connected user.
            purpose (str): Either 'list' (default) or 'modify' to apply
                stricter filters.

        Returns:
            str | None: Error message if list is empty, otherwise None.

        Side Effects:
            Clears the console and displays the filtered list.
        """
        Model = self.get_model(entity_name)
        model_view = self.views[entity_name]
        filters = {}

        if user:
            role = user.role

            if purpose == "list":
                if role == "commercial" and entity_name == "contract":

                    filters = {
                        "signed": True,
                        "client.commercial": user,
                        "event": None
                    }

                elif role == "gestion" and entity_name == "event":

                    filters = {"support_id": None}

            elif purpose == "modify":
                if (entity_name == "collaborator"
                        and role not in ["admin", "gestion"]):
                    filters = {"id": user.id}

                elif entity_name == "client":
                    filters = {"commercial": user}

                elif entity_name == "event" and role == "support":
                    filters = {"support": user}

                elif role == "admin":
                    filters = {}

        items = Model.filter_by_fields(session,
                                       self.SESSION["show_archived"],
                                       **filters
                                       )
        error = None if items else "aucun élément disponible"

        self.app_view.clear_console()
        model_view.display_entity_list(items)
        return error

    def filter_by_field_entity(self, user, session, entity_name, **kwargs):
        """
        Filter and display a list of entities based on a selected field and
        value.

        Prompts the user to select a field from the model's mapping and enter
        a filter value.
        The resulting filtered list is then displayed to the user.

        Args:
            user (Collaborator): the connected user
            session (Session): SQLAlchemy session object.
            entity_name (str): The name of the entity to filter.

        Side Effects:
            Prompts for input, displays the filtered list, and pauses the
            interface.
        """
        Model = self.get_model(entity_name)
        model_view = self.views[entity_name]
        entity_fields = Model.get_fields(user.role, "list")

        self.app_view.clear_console()
        self.list_entity(session, entity_name)
        self.app_view.display_list_field_menu(entity_fields, "filter")
        choice = self.app_view.choose_field()

        try:
            asked_field = entity_fields[choice]
        except (TypeError, IndexError):
            self.app_view.display_error_message("Champ invalide.")
            return

        field, value = self.app_view.ask_filter_value(
            asked_field)

        if field and value:
            items = Model.filter_by_fields(session,
                                           self.SESSION["show_archived"],
                                           **{field: value})
            self.app_view.clear_console()
            model_view.display_entity_list(items)
            self.app_view.break_point()

    def order_by_field_entity(self, user, session, entity_name, **kwargs):
        """
        Display entity list ordered by a selected field.

        Prompts the user to choose a field from the model's display mapping
        and optionally select descending order. Retrieves and displays the
        sorted list of entities based on that field.

        Args:
            user (Collaborator): The connected user
            session (Session): SQLAlchemy session object.
            entity_name (str): The name of the entity to sort
            (e.g., 'contracts').

        Side Effects:
            Clears the console, prompts user input, and displays the sorted
            entity list.
        """
        Model = self.get_model(entity_name)
        model_view = self.views[entity_name]
        fields = Model.get_fields(user.role, "list")

        self.app_view.clear_console()
        self.list_entity(session, entity_name)

        self.app_view.display_list_field_menu(fields, "order")
        choice = self.app_view.choose_field()

        try:
            asked_field = fields[choice]
        except (TypeError, IndexError):
            self.app_view.display_error_message("Champ invalide.")
            return

        if asked_field:
            descending = self.app_view.ask_descending_order()
            items = Model.order_by_fields(session, asked_field[0], descending)
            self.app_view.clear_console()
            model_view.display_entity_list(items)
            self.app_view.break_point()

    def create_entity(self, session, user, entity_name, **kwargs):
        """
            Create a new entity instance based on user input.

            Prompts the user for input for each field defined in the model,
            validates the data if applicable, and persists the new instance
            to the database. Handles foreign key dependencies and user-based
            default assignments (e.g., commercial ID).

            Args:
                session (Session): SQLAlchemy session object.
                user (Collaborator): The currently authenticated user.
                entity_name (str): The name of the entity to create
                (e.g., 'contracts').

            Side Effects:
                Prompts user for input, displays errors or confirmation,
                and commits or rolls back the session.
            """
        self.app_view.clear_console()
        Model = self.get_model(entity_name)
        model_controller = self.controllers[entity_name]
        fields = Model.get_fields(user.role, "create")
        data = {}

        for field in fields:
            if "client_id" in field or "contract_id" in field:
                ref_entity = "client" if "client_id" in field else "contract"
                error = self.list_entity(session, ref_entity, user)
                if error:
                    self.app_view.display_error_message(error)
                    self.app_view.break_point()
                    return

        self.app_view.display_informative_message("taper 'quit' pour quitter")
        i = 0
        while i < len(fields):
            field = fields[i]

            if field[0] == "id_commercial" and user.role == "commercial":
                data[field[0]] = user.id
                i += 1
                continue

            data[field[0]] = self.app_view.ask_information(field[1])
            if data[field[0]] == "quit":
                break

            validated, error = self.validate_field(Model, field, session, user,
                                                   data)
            if validated is not None:
                data[field[0]] = validated
                i += 1
            else:
                self.app_view.display_error_message(error)

        item = model_controller.create(data)
        response = item.save(session)

        if response == "success":

            self.app_view.display_success_message(
                f"{translate_entity[entity_name]} créé avec succès.")
        else:
            self.app_view.display_error_message(response)

        self.app_view.break_point()

    def modify_entity(self, session, user, entity_name, **kwargs):
        """
        Modify an existing entity instance.

        This method allows a user to update editable fields of a selected
        entity instance,
        according to their role permissions. Validates each updated field
        before applying changes.

        Args:
            session (Session): SQLAlchemy session object.
            user (Collaborator): The currently authenticated user.
            entity_name (str): The name of the entity to modify

        Side Effects:
            Displays entity details and update prompts.
            Applies changes to the database if committed.
        """
        Model = self.get_model(entity_name)
        model_view = self.views[entity_name]

        error = self.list_entity(
            session,
            entity_name,
            user,
            "modify"
        )

        if error:
            self.app_view.display_error_message(error)
            self.app_view.break_point()
            return

        while True:
            entity_id = self.app_view.ask_id(entity_name)
            if not entity_id:
                return

            instances = Model.filter_by_fields(session,
                                               self.SESSION["show_archived"],
                                               id=entity_id)
            if not instances:
                self.app_view.display_error_message(
                    f"{translate_entity[entity_name]} introuvable.")
                continue

            entity = instances[0]
            if not has_object_permission(user, "update", entity):
                name = translate_entity[entity_name]
                self.app_view.display_error_message(
                    f"Vous n'avez pas l'autorisation de modifier ce {name}")
                continue
            break

        fields = Model.get_fields(user.role, "modify")
        if entity == user:
            if user.role in ["admin", "gestion"]:
                fields.insert(1, ["password", "Mot de passe"])
            else:
                fields.append(["password", "Mot de passe"])

        data = {field[0]: getattr(entity, field[0]) for field in fields}

        while True:
            self.app_view.clear_console()
            model_view.display_entity_list([entity])
            self.app_view.display_modify_field_menu(fields)
            choice = self.app_view.choose_field()

            if choice < len(fields):  # a selected field from the menu

                field = fields[choice]

                # displays the specific table to guide the user’s choice.
                dict_ref_entity = {
                    "client_id": "client",
                    "contract_id": "contract",
                    "support_id": "collaborator"
                }

                for ref_key in dict_ref_entity:
                    if ref_key in field:
                        ref_entity = dict_ref_entity[ref_key]
                        error = self.list_entity(session, ref_entity, user)
                        if error:
                            self.app_view.display_error_message(error)
                            self.app_view.break_point()
                            continue

                data[field[0]] = self.app_view.ask_information(field[1])
                validated, error = self.validate_field(Model, field, session,
                                                       user, data)
                if validated is not None:
                    setattr(entity, field[0], validated)
                    self.app_view.display_success_message(
                        f"Le champ {field[0]} a été mis à jour "
                        f"(non sauvegardé)")
                    self.app_view.break_point()
                else:
                    self.app_view.display_error_message(error)

            if int(choice) == len(fields):  # the cancel option from the menu
                session.refresh(entity)
                break

            elif int(choice) == len(fields) + 1:   # the save option from the menu
                response = entity.update(session)

                if response == "success":
                    self.app_view.display_success_message(
                        f"{translate_entity[entity_name]} a été enregistré "
                        f"avec succès.")
                else:
                    self.app_view.display_error_message(response)
                    continue
                break

    def delete_entity(self, session, user, entity_name, **kwargs):
        """
        Delete or archive an entity instance based on user role.

        If the user is an admin, the entity is permanently deleted from the
        database.
        Otherwise, the entity is marked as archived.
        Before deletion, the method confirms the target entity exists and
        displays it.

        Args:
            session (Session): SQLAlchemy session object.
            user (Collaborator): The currently authenticated user.
            entity_name (str): The name of the entity to delete
            (e.g., 'clients').

        Raises:
            IntegrityError: If a database constraint prevents deletion.

        Side Effects:
            Displays entity information, confirmation prompts, and success or
            error messages.
            Commits or rolls back the transaction depending on the outcome.
        """
        Model = self.get_model(entity_name)
        model_view = self.views[entity_name]

        while True:
            self.list_entity(session, entity_name)
            entity_id = self.app_view.ask_id(entity_name)
            if not entity_id:
                break

            instances = Model.filter_by_fields(session,
                                               self.SESSION["show_archived"],
                                               id=entity_id)
            if not instances:
                self.app_view.display_error_message(
                    f"{translate_entity[entity_name]} introuvable")
                continue

            instance = instances[0]
            if not has_object_permission(user, "delete", instance):
                name = translate_entity[entity_name]
                self.app_view.display_error_message(
                    f"Vous n'avez pas l'autorisation de supprimer ce {name}")
                self.app_view.break_point()
                continue

            model_view.display_entity_list([instance])

            if user.role == "admin":
                self.app_view.display_error_message(
                    "Attention, cette suppression est définitive.")

            if self.app_view.valide_choice_menu():

                if user.role != "admin":
                    response = instance.soft_delete(session)
                else:
                    response = instance.hard_delete(session)

                if response == "success":
                    self.app_view.display_success_message(
                        f"{translate_entity[entity_name]} supprimé avec "
                        f"succès.")
                else:
                    self.app_view.display_error_message(response)

                self.app_view.break_point()
                break
            else:
                break

    def show_details_entity(self, user, session, entity_name, **kwargs):
        """
        Display a single entity instance along with its related entities.
        Automatically detects relationships and calls appropriate view.

        Args:
            user (Collaborator): the connected user
            session (Session): SQLAlchemy session object.
            entity_name (str): The name of the entity to show details
            (e.g., 'clients').

        """
        Model = self.get_model(entity_name)
        model_view = self.views[entity_name]

        while True:
            self.list_entity(session, entity_name)
            entity_id = self.app_view.ask_id(entity_name)
            if not entity_id:
                break

            instances = Model.filter_by_fields(session,
                                               self.SESSION["show_archived"],
                                               id=entity_id)
            if not instances:
                self.app_view.display_error_message(
                    f"{translate_entity[entity_name]} introuvable")
                continue

            instance = instances[0]
            self.app_view.clear_console()
            model_view.display_entity_list([instance])

            related_map = {
                "clients": self.views["client"],
                "events": self.views["event"],
                "contracts": self.views["contract"],
                "commercial": self.views["collaborator"],
                "event": self.views["event"],
                "client": self.views["client"],
                "contract": self.views["contract"],
                "support": self.views["collaborator"],

            }

            for attr_name, view in related_map.items():
                if hasattr(instance, attr_name):
                    related_data = getattr(instance, attr_name)
                    if related_data:
                        if isinstance(related_data, list):
                            view.display_entity_list(related_data)
                        else:
                            view.display_entity_list([related_data])

            if entity_name == "event":
                client = instance.contract.client
                self.views["client"].display_entity_list([client])

            self.app_view.break_point()
            break

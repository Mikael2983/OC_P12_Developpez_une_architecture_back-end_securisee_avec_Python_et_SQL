"""
Module client_view

Provides the ClientView class responsible for displaying client
information in a styled table format using the Rich library.
"""
from rich.console import Console
from rich.table import Table

from epic_event.settings import (TITLE_STYLE, REQUEST_STYLE, TEXT_STYLE,
                                 SUCCESS_STYLE)
from epic_event.views.utils_view import UtilsView


class ClientView:
    """
    View class to handle the presentation of client data in the console.

    Attributes:
        console (Console): Rich Console instance for styled output.
        utils_view (UtilsView): Instance of utility view class for styled
            messages.
        SESSION (dict): Session dictionary controlling display options.
        mapping (dict): Mapping of user input keys to client attributes and
            labels.
    """

    def __init__(self, SESSION):
        """
        Initializes a ClientView instance.

        Args:
            SESSION (dict): Session state dict controlling options like
                            whether to show archived clients.
        """
        self.SESSION = SESSION
        self.console = Console()
        self.utils_view = UtilsView()
        self.mapping = {
            "1": ["id", "Id"],
            "2": ["full_name", "Nom du contact"],
            "3": ["email", "Email"],
            "4": ["phone", "Téléphone"],
            "5": ["company_name", "Compagnie"],
            "6": ["created_date", "Date de création"],
            "7": ["last_contact_date", "Dernier contact"],
            "8": ["commercial.full_name", "Commercial"],
        }

    def display_entity_list(self, clients):
        """
        Displays a list of clients in a styled table.

        The table includes columns for ID, name, email, and service/role.
        If the session indicates to show archived clients, an
        additional column is shown.

        Args:
            clients (list): List of objects Client.
        """
        if len(clients) == 1:
            title = "Détails du client"
        else:
            title = "Liste des clients"

        table = Table(title=title,
                      title_style=TITLE_STYLE,
                      header_style=REQUEST_STYLE
                      )

        table.add_column(
            "id",
            justify="center",
            style=TEXT_STYLE,
            max_width=10
        )
        table.add_column(
            "Nom du contact",
            justify="center",
            style=SUCCESS_STYLE,
            max_width=15
        )
        table.add_column(
            "email",
            justify="center",
            style=SUCCESS_STYLE,
            max_width=20
        )
        table.add_column(
            "téléphone",
            justify="center",
            style=TEXT_STYLE,
            max_width=15)
        table.add_column(
            "compagnie",
            justify="center",
            style=TEXT_STYLE,
            max_width=15)
        table.add_column(
            "Date de création",
            justify="center",
            style=TEXT_STYLE,
            max_width=12)
        table.add_column(
            "Dernier contact",
            justify="center",
            style=TEXT_STYLE,
            max_width=12)
        table.add_column(
            "Commercial",
            justify="center",
            style=TEXT_STYLE,
            max_width=15)

        if self.SESSION["show_archived"]:
            table.add_column(
                "archivé",
                justify="center",
                style=TEXT_STYLE,
                max_width=12)

        for client in clients:
            if self.SESSION["show_archived"]:
                table.add_row(
                    str(client.id),
                    client.full_name,
                    client.email,
                    client.phone,
                    client.company_name,
                    str(client.formatted_created_date),
                    str(client.formatted_last_contact_date),
                    client.commercial.full_name,
                    client.formatted_archived
                )
            else:
                table.add_row(
                    str(client.id),
                    client.full_name,
                    client.email,
                    client.phone,
                    client.company_name,
                    str(client.formatted_created_date),
                    str(client.formatted_last_contact_date),
                    client.commercial.full_name
                )
        self.console.print(table)

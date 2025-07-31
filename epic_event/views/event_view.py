from rich.console import Console
from rich.table import Table

from epic_event.settings import TITLE_STYLE, REQUEST_STYLE, TEXT_STYLE
from epic_event.views.utils_view import UtilsView


class EventView:

    def __init__(self, SESSION):
        self.SESSION = SESSION
        self.console = Console()
        self.utils_view = UtilsView()
        self.mapping = {
            "1": ["id", "Id"],
            "2": ["title","titre"],
            "3": ["start_date", "date de début"],
            "4": ["end_date", "date de fin"],
            "5": ["location", "lieu"],
            "6": ["participants", "nombre de participants"],
            "7": ["notes", "Notes"],
            "8": ["contract.id", "N° Contrat"],
            "9": ["support.full_name", "Organisateur"],
        }

    def display_entity_list(self, events):
        """
        Displays a list of events in a styled table.

        The table includes columns for ID,event.contract.client.company_name,
        contract_id, event.title, formatted_start_date, formatted_end_date,
         location, participants, notes, support.full_name,
        If support doesn't exist, "à définir" is displayed.
        If the session indicates to show archived events, an
        additional column is shown: formatted_archived.

        Args:
            events (list): List of objects Event.
        """

        if len(events) == 1:
            title = "Détails de l'événement"
        else:
            title = "Liste des événements"

        table = Table(title=title,
                      title_style=TITLE_STYLE,
                      header_style=REQUEST_STYLE
                      )
        table.add_column(
            "ID Événement",
            justify="center",
            style=TEXT_STYLE,
            max_width=9
        )
        table.add_column(
            "Client",
            justify="center",
            style=TEXT_STYLE,
            max_width=15
        )
        table.add_column(
            "ID contrat",
            justify="center",
            style=TEXT_STYLE,
            max_width=7
        )
        table.add_column(
            "Titre",
            justify="center",
            style=TEXT_STYLE,
            max_width=25
        )
        table.add_column(
            "Date début",
            justify="center",
            style=TEXT_STYLE,
            max_width=12
        )
        table.add_column(
            "Date fin",
            justify="center",
            style=TEXT_STYLE,
            max_width=12
        )
        table.add_column(
            "lieu",
            justify="center",
            style=TEXT_STYLE,
            max_width=25
        )
        table.add_column(
            "participants",
            justify="center",
            style=TEXT_STYLE,
            max_width=16
        )
        table.add_column(
            "Notes",
            justify="center",
            style=TEXT_STYLE,
            max_width=70
        )
        table.add_column(
            "Organisateur",
            justify="center",
            style=TEXT_STYLE,
            max_width=12
        )
        if self.SESSION["show_archived"]:
            table.add_column(
                "archivé",
                justify="center",
                style=TEXT_STYLE,
                max_width=12)

        for event in events:

            if event.support:
                support_full_name = event.support.full_name
            else:
                support_full_name = " A définir"

            if self.SESSION["show_archived"]:
                table.add_row(
                    str(event.id),
                    event.contract.client.company_name,
                    str(event.contract_id),
                    event.title,
                    str(event.formatted_start_date),
                    str(event.formatted_end_date),
                    event.location,
                    str(event.participants),
                    event.notes,
                    support_full_name,
                    event.formatted_archived
                )
            else:
                table.add_row(
                    str(event.id),
                    event.contract.client.company_name,
                    str(event.contract_id),
                    event.title,
                    str(event.formatted_start_date),
                    str(event.formatted_end_date),
                    event.location,
                    str(event.participants),
                    event.notes,
                    support_full_name
                )

        self.console.print(table)

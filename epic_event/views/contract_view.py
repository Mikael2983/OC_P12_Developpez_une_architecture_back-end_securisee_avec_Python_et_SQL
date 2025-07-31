"""
Module client_view

Provides the ClientView class responsible for displaying client
information in a styled table format using the Rich library.
"""
from rich.console import Console
from rich.table import Table

from epic_event.settings import TITLE_STYLE, REQUEST_STYLE, TEXT_STYLE, SUCCESS_STYLE
from epic_event.views.utils_view import UtilsView


class ContractView:
    """
    View class to handle the presentation of contract data in the console.

    Attributes:
        console (Console): Rich Console instance for styled output.
        utils_view (UtilsView): Instance of utility view class for styled
            messages.
        SESSION (dict): Session dictionary controlling display options.
        mapping (dict): Mapping of user input keys to contract attributes and
            labels.
    """

    def __init__(self, SESSION):
        """
        Initializes a ContractView instance.

        Args:
            SESSION (dict): Session state dict controlling options like
                            whether to show archived clients.
        """
        self.SESSION = SESSION
        self.utils_view = UtilsView()
        self.console = Console()
        self.mapping = {
            "1": ["id", "ID"],
            "2": ["client.company_name", "client"],
            "3": ["total_amount", "Somme Totale"],
            "4": ["amount_due", "Somme Dûe"],
            "5": ["signed", "Signé"]
        }

    def display_entity_list(self, contracts):

        if len(contracts) == 1:
            title = "Détails du contrat"
        else:
            title = "Liste des contrats"

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
            "Client",
            justify="center",
            style=TEXT_STYLE,
            max_width=20
        )
        table.add_column(
            "total amount",
            justify="center",
            style=SUCCESS_STYLE,
            max_width=15
        )
        table.add_column(
            "amount_due",
            justify="center",
            style=SUCCESS_STYLE,
            max_width=15
        )
        table.add_column(
            "date de création",
            justify="center",
            style=TEXT_STYLE,
            max_width=12)
        table.add_column(
            "Signé",
            justify="center",
            style=TEXT_STYLE,
            max_width=12)

        if self.SESSION["show_archived"]:
            table.add_column(
                "archivé",
                justify="center",
                style=TEXT_STYLE,
                max_width=12)

        for contract in contracts:
            if self.SESSION["show_archived"]:
                table.add_row(
                    str(contract.id),
                    contract.client.company_name,
                    contract.total_amount,
                    contract.amount_due,
                    str(contract.formatted_created_date),
                    contract.formatted_signed,
                    contract.formatted_archived
                )
            else:
                table.add_row(
                    str(contract.id),
                    contract.client.company_name,
                    contract.total_amount,
                    contract.amount_due,
                    str(contract.formatted_created_date),
                    contract.formatted_signed
                )
        self.console.print(table)

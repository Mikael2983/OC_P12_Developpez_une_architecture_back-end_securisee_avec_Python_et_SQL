"""
Module collaborator_view

Provides the CollaboratorView class responsible for displaying collaborator
information in a styled table format using the Rich library.
"""
from rich.console import Console
from rich.table import Table

from epic_event.settings import (TITLE_STYLE, REQUEST_STYLE,
                                 TEXT_STYLE, SUCCESS_STYLE)


class CollaboratorView:
    """
    View class to handle the presentation of collaborator data in the console.

    Attributes:
        console (Console): Rich Console instance for styled output.
        SESSION (dict): Session dictionary controlling display options.
    """
    def __init__(self, SESSION):
        """
        Initializes a CollaboratorView instance.

        Args:
            SESSION (dict): Session state dict controlling options like
                            whether to show archived collaborators.
        """
        self.console = Console()
        self.SESSION = SESSION

    def display_entity_list(self, collaborators: list):
        """
        Displays a list of collaborators in a styled table.

        The table includes columns for ID, name, email, and service/role.
        If the session indicates to show archived collaborators, an
        additional column is shown.

        Args:
            collaborators (list): List of objects Collaborator.
        """

        if len(collaborators) == 1:
            title = "Détails du collaborateur"
        else:
            title = "Liste des collaborateurs"

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
            "Nom",
            justify="center",
            style=TEXT_STYLE,
            max_width=25
        )
        table.add_column(
            "email",
            justify="center",
            style=TEXT_STYLE,
            max_width=30
        )
        table.add_column(
            "Service",
            justify="center",
            style=TEXT_STYLE,
            max_width=12)

        if self.SESSION["show_archived"]:
            table.add_column(
                "archivé",
                justify="center",
                style=TEXT_STYLE,
                max_width=12)

        for collaborator in collaborators:

            if self.SESSION["show_archived"]:
                table.add_row(
                    str(collaborator.id),
                    collaborator.full_name,
                    collaborator.email,
                    collaborator.role,
                    collaborator.formatted_archived,
                )
            else:
                table.add_row(
                    str(collaborator.id),
                    collaborator.full_name,
                    collaborator.email,
                    collaborator.role,
                )
        self.console.print(table)



"""
Module utils_view

This module contains the class UtilsView which provides methods
to apply Rich styles to messages and display stylish menus
in the console.
"""
from rich import print

from epic_event.settings import (TITLE_STYLE, LINE_STYLE, REQUEST_STYLE,
                                 TEXT_STYLE)


class UtilsView:
    """
    Utility class for stylized display with rich library.

    Provides static and instance methods to apply styles
    Rich to text messages and display formatted menus in the console.
    """

    @staticmethod
    def apply_rich_style(message: str, style: str) -> str:
        """
        Apply a given rich style to a text message.

        Args:
            message (str): The text to be styled.
            style (str): The name of the Rich style to apply.

        Returns:
            str: The stylized message with Rich tags.
        """
        return f"[{style}]{message}[/{style}]"

    def display_styled_menu(self, header, request, text):
        """
        Displays a stylized menu in the console with a header, a message
        of request and a list of texts.

        Args:
            header (str or None): The title or header of the menu.
                If None or empty, it will not be displayed.
            request (str or None): The request or prompt message to the user.
                                  If None or empty, it will not be displayed.
            text (list[str]): List of channels to be displayed in the menu
                body, each prefixed with an indentation.

        """
        if header:
            print(self.apply_rich_style(header, TITLE_STYLE))
            print(self.apply_rich_style("-" * len(header), LINE_STYLE))
        if request:
            print(self.apply_rich_style(request, REQUEST_STYLE))
        for string in text:
            print(self.apply_rich_style(f"    {string}", TEXT_STYLE))

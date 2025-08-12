from epic_event.models import Client, Collaborator, Contract, Event

from epic_event.models.entity import Entity


# for each entity, determines the list of CRUD actions allowed according to the
# user’s role
# it is used to generate the menus in MainController.
permissions = {
    "collaborator": {
        "admin": [
            "details", "create", "modify", "delete"
        ],
        "gestion": [
            "details", "create", "modify", "delete"
        ],
        "commercial": [
            "details", "modify",
                ],
        "support": [
            "details", "modify",
                ]
        },
    "client": {
        "admin": [
            "details", "create", "modify", "delete"
        ],
        "gestion": [
            "details"
                ],
        "commercial": [
            "details", "create", "modify", "delete"
                ],
        "support": [
            "details",
                ]
        },
    "contract": {
        "admin": [
            "details", "create", "modify", "delete"
        ],
        "gestion": [
            "details", "create", "modify", "delete"
                ],
        "commercial": [
            "details"
                ],
        "support": [
            "details",
                ]
        },
    "event": {
        "admin": [
            "details", "create", "modify", "delete"
        ],
        "gestion": [
            "details", "modify"
                ],
        "commercial": [
            "details", "create"
                ],
        "support": [
            "details", "modify", "delete"
                ]
        },
    }


def has_object_permission(user: Collaborator,
                          action: str,
                          item: Entity) -> bool:
    """
    Checks if the user has permission to act on the given object according to
    business rules.
    Args:
        user: The user.
        action: The requested action ('create', 'update', 'delete').
        item: Object (optional) to which the action relates.

    Returns:
        bool: True if user has permission, False otherwise.
    """

    if user.role == "admin":
        return True

    if isinstance(item, Collaborator):
        return (getattr(item, "id", None) == getattr(user, "id", None)
                or user.role == "gestion" and action != "password"
                or action == "password" and item == user)

    if isinstance(item, Client):
        return getattr(item, "commercial", None) == user

    if isinstance(item, Contract):
        return user.role == "gestion"

    if isinstance(item, Event):
        return (getattr(item, "support", None) == user
                or (user.role == "gestion" and action == "update"))

    return False

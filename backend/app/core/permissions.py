from fastapi import HTTPException
from app.core.store import documents, permissions


EDIT_ROLES = {"owner", "editor"}


def get_user_role(document_id: str, user_id: str) -> str | None:
    if document_id not in documents:
        return None
    return permissions.get(document_id, {}).get(user_id)


def require_document_exists(document_id: str):
    if document_id not in documents:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": 404,
                    "message": "Resource not found",
                    "detail": "Document not found",
                }
            },
        )


def require_access(document_id: str, user_id: str) -> str:
    require_document_exists(document_id)
    role = get_user_role(document_id, user_id)
    if not role:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": 403,
                    "message": "You do not have permission to perform this action.",
                    "detail": "No access to this document.",
                }
            },
        )
    return role


def require_edit_access(document_id: str, user_id: str) -> str:
    role = require_access(document_id, user_id)
    if role not in EDIT_ROLES:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": 403,
                    "message": "You do not have permission to perform this action.",
                    "detail": "Required role: editor or above.",
                }
            },
        )
    return role


def require_owner(document_id: str, user_id: str):
    role = require_access(document_id, user_id)
    if role != "owner":
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": 403,
                    "message": "You do not have permission to perform this action.",
                    "detail": "Only the owner can perform this action.",
                }
            },
        )
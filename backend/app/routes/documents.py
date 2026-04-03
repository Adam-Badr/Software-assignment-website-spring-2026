from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    CreateDocumentRequest,
    CreateDocumentResponse,
    GetDocumentResponse,
    UpdateDocumentRequest,
    UpdateDocumentResponse,
    DeleteDocumentResponse,
    ListDocumentsResponse,
    DocumentListItem,
    CollaboratorEntry,
    SessionResponse,
    SessionResponseCollaborator,
)
from app.core.auth import get_current_user_id
from app.core.permissions import require_access, require_edit_access, require_owner
from app.core.store import documents, permissions, users, sessions, make_id, now_iso

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("", response_model=CreateDocumentResponse, status_code=201)
def create_document(payload: CreateDocumentRequest, user_id: str = Depends(get_current_user_id)):
    now = now_iso()
    document_id = make_id("doc")
    documents[document_id] = {
        "document_id": document_id,
        "title": payload.title,
        "content": "",
        "owner_id": user_id,
        "created_at": now,
        "updated_at": now,
        "version": 1,
    }
    permissions[document_id] = {user_id: "owner"}

    return CreateDocumentResponse(
        document_id=document_id,
        title=payload.title,
        owner_id=user_id,
        created_at=now,
        updated_at=now,
        version=1,
    )


@router.get("", response_model=ListDocumentsResponse)
def list_documents(user_id: str = Depends(get_current_user_id)):
    items = []
    for document_id, role_map in permissions.items():
        role = role_map.get(user_id)
        if not role:
            continue
        doc = documents[document_id]
        items.append(
            DocumentListItem(
                document_id=document_id,
                title=doc["title"],
                role=role,
                updated_at=doc["updated_at"],
            )
        )
    return ListDocumentsResponse(documents=items)


@router.get("/{document_id}", response_model=GetDocumentResponse)
def get_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    require_access(document_id, user_id)
    doc = documents[document_id]

    collaborators = [
        CollaboratorEntry(user_id=uid, role=role)
        for uid, role in permissions.get(document_id, {}).items()
        if role != "owner"
    ]

    return GetDocumentResponse(
        document_id=doc["document_id"],
        title=doc["title"],
        content=doc["content"],
        owner_id=doc["owner_id"],
        version=doc["version"],
        updated_at=doc["updated_at"],
        collaborators=collaborators,
    )
@router.patch("/{document_id}", response_model=UpdateDocumentResponse)
def update_document(document_id: str, payload: UpdateDocumentRequest, user_id: str = Depends(get_current_user_id)):
    require_edit_access(document_id, user_id)
    doc = documents[document_id]
    changed = False
    if payload.title is not None:
        doc["title"] = payload.title
        changed = True
    if payload.content is not None:
        doc["content"] = payload.content
        changed = True

    if changed:
        doc["version"] += 1
        doc["updated_at"] = now_iso()

    return UpdateDocumentResponse(
        document_id=doc["document_id"],
        title=doc["title"],
        version=doc["version"],
        updated_at=doc["updated_at"],
    )


@router.delete("/{document_id}", response_model=DeleteDocumentResponse)
def delete_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    require_owner(document_id, user_id)
    documents.pop(document_id, None)
    permissions.pop(document_id, None)

    return DeleteDocumentResponse(message="Document deleted successfully.")

@router.post("/{document_id}/session", response_model=SessionResponse)
def create_session(document_id: str, user_id: str = Depends(get_current_user_id)):
    require_access(document_id, user_id)
    session_id = make_id("sess")
    sessions[session_id] = {
        "session_id": session_id,
        "document_id": document_id,
        "user_id": user_id,
        "created_at": now_iso(),
    }

    current_collaborators = []
    for sess in sessions.values():
        if sess["document_id"] != document_id or sess["user_id"] == user_id:
            continue
        collaborator = users[sess["user_id"]]
        current_collaborators.append(
            SessionResponseCollaborator(
                user_id=collaborator["user_id"],
                name=collaborator["name"],
                cursor_position=0,
            )
        )

    return SessionResponse(
        document_id=document_id,
        session_id=session_id,
        websocket_url=f"ws://localhost:8000/ws/{document_id}",
        current_collaborators=current_collaborators,
    )
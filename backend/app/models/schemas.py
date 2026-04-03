from typing import Literal, Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field


Role = Literal["owner", "editor", "commenter", "viewer"]
AIAction = Literal["rewrite", "summarize", "translate", "restructure"]


class ErrorBody(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    created_at: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str


class CreateDocumentRequest(BaseModel):
    title: str = Field(min_length=1)


class CreateDocumentResponse(BaseModel):
    document_id: str
    title: str
    owner_id: str
    created_at: str
    updated_at: str
    version: int


class CollaboratorEntry(BaseModel):
    user_id: str
    role: Role


class GetDocumentResponse(BaseModel):
    document_id: str
    title: str
    content: str
    owner_id: str
    version: int
    updated_at: str
    collaborators: List[CollaboratorEntry]


class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class UpdateDocumentResponse(BaseModel):
    document_id: str
    title: str
    version: int
    updated_at: str


class DeleteDocumentResponse(BaseModel):
    message: str


class DocumentListItem(BaseModel):
    document_id: str
    title: str
    role: Role
    updated_at: str


class ListDocumentsResponse(BaseModel):
    documents: List[DocumentListItem]


class SessionResponseCollaborator(BaseModel):
    user_id: str
    name: str
    cursor_position: int


class SessionResponse(BaseModel):
    document_id: str
    session_id: str
    websocket_url: str
    current_collaborators: List[SessionResponseCollaborator]


class ShareDocumentRequest(BaseModel):
    user_email: EmailStr
    role: Role


class ShareDocumentResponse(BaseModel):
    document_id: str
    user_id: str
    role: Role
    granted_at: str


class UpdatePermissionRequest(BaseModel):
    role: Role


class UpdatePermissionResponse(BaseModel):
    user_id: str
    role: Role
    updated_at: str


class RevokePermissionResponse(BaseModel):
    message: str


class AIInvokeOptions(BaseModel):
    tone: Optional[str] = None
    target_language: Optional[str] = None


class AIInvokeRequest(BaseModel):
    selected_text: str = Field(min_length=1)
    action: AIAction
    options: AIInvokeOptions


class AIInvokeResponse(BaseModel):
    job_id: str
    status: str
    document_id: str
    estimated_seconds: int


class AIJobProcessingResponse(BaseModel):
    job_id: str
    status: str


class AIJobCompletedResponse(BaseModel):
    job_id: str
    status: str
    original_text: str
    suggestion: str
    action: AIAction
    created_at: str
    completed_at: str


class AIJobFailedResponse(BaseModel):
    job_id: str
    status: str
    error: str


class AIAcceptRequest(BaseModel):
    accepted: bool
    partial_text: Optional[str] = None


class AIAcceptResponse(BaseModel):
    job_id: str
    outcome: str
    recorded_at: str
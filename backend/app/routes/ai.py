from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.models.schemas import (
    AIInvokeRequest,
    AIInvokeResponse,
    AIJobProcessingResponse,
    AIJobCompletedResponse,
    AIJobFailedResponse,
    AIAcceptRequest,
    AIAcceptResponse,
)
from app.core.auth import get_current_user_id
from app.core.permissions import require_access, require_edit_access
from app.core.store import ai_jobs, documents, make_id, now_iso


router = APIRouter(prefix="/api/v1", tags=["ai"])


def generate_mock_suggestion(action: str, selected_text: str, options: dict) -> str:
    text = selected_text.strip()

    if action == "rewrite":
        return f"Improved version: {text}"

    if action == "summarize":
        shortened = text[: max(20, min(len(text), 80))]
        return f"Summary: {shortened}"

    if action == "translate":
        target = options.get("target_language") or "target language"
        return f"[Translated to {target}] {text}"

    if action == "restructure":
        return f"Restructured content:\n- {text}"

    return text


def process_ai_job(job_id: str):
    import time

    job = ai_jobs.get(job_id)
    if not job:
        return

    job["status"] = "processing"

    time.sleep(2)

    try:
        suggestion = generate_mock_suggestion(
            action=job["action"],
            selected_text=job["selected_text"],
            options=job["options"],
        )
        job["status"] = "completed"
        job["suggestion"] = suggestion
        job["completed_at"] = now_iso()
    except Exception:
        job["status"] = "failed"
        job["error"] = "AI provider timeout. Please try again."


@router.post("/documents/{document_id}/ai/invoke", response_model=AIInvokeResponse, status_code=202)
def invoke_ai(
    document_id: str,
    payload: AIInvokeRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    require_edit_access(document_id, user_id)

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

    job_id = make_id("job_ai")
    ai_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "document_id": document_id,
        "user_id": user_id,
        "action": payload.action,
        "selected_text": payload.selected_text,
        "options": payload.options.model_dump(),
        "created_at": now_iso(),
        "completed_at": None,
        "suggestion": None,
        "error": None,
        "outcome": "pending",
    }

    background_tasks.add_task(process_ai_job, job_id)

    return AIInvokeResponse(
        job_id=job_id,
        status="pending",
        document_id=document_id,
        estimated_seconds=10,
    )


@router.get("/ai/jobs/{job_id}")
def get_ai_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    job = ai_jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": 404,
                    "message": "Resource not found",
                    "detail": "AI job not found",
                }
            },
        )

    if job["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": 403,
                    "message": "You do not have permission to perform this action.",
                    "detail": "No access to this AI job.",
                }
            },
        )

    if job["status"] in {"pending", "processing"}:
        return AIJobProcessingResponse(
            job_id=job_id,
            status=job["status"],
        )

    if job["status"] == "completed":
        return AIJobCompletedResponse(
            job_id=job_id,
            status="completed",
            original_text=job["selected_text"],
            suggestion=job["suggestion"],
            action=job["action"],
            created_at=job["created_at"],
            completed_at=job["completed_at"],
        )

    return AIJobFailedResponse(
        job_id=job_id,
        status="failed",
        error=job["error"] or "AI provider timeout. Please try again.",
    )


@router.post("/ai/jobs/{job_id}/accept", response_model=AIAcceptResponse)
def accept_ai_job(
    job_id: str,
    payload: AIAcceptRequest,
    user_id: str = Depends(get_current_user_id),
):
    job = ai_jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": 404,
                    "message": "Resource not found",
                    "detail": "AI job not found",
                }
            },
        )

    if job["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": 403,
                    "message": "You do not have permission to perform this action.",
                    "detail": "No access to this AI job.",
                }
            },
        )

    if payload.accepted:
        job["outcome"] = "accepted" if not payload.partial_text else "modified"
    else:
        job["outcome"] = "rejected"

    return AIAcceptResponse(
        job_id=job_id,
        outcome=job["outcome"],
        recorded_at=now_iso(),
    )
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router
from app.routes.ai import router as ai_router

app = FastAPI(title="CollabDocs PoC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if hasattr(exc, "status_code") and hasattr(exc, "detail"):
        detail = exc.detail
        if isinstance(detail, dict) and "error" in detail:
            return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=500,
        content={ "error": {"code": 500,"message": "Internal server error","detail": "Unexpected server error",} },)


@app.get("/health")
def health():
    return {"status": "ok"}
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(ai_router)
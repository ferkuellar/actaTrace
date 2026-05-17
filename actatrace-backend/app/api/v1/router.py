from fastapi import APIRouter

from app.api.v1 import actas, alerts, auth, blockchain, custody_events, documents, prep_results, traceability, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(actas.router, prefix="/actas", tags=["actas"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(custody_events.router, prefix="/custody-events", tags=["custody-events"])
api_router.include_router(prep_results.router, prefix="/prep-results", tags=["prep-results"])
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(traceability.router, prefix="/traceability", tags=["traceability"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])

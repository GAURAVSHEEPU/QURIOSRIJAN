"""
Health and System Readiness Diagnostic Endpoints.
"""

from fastapi import APIRouter, Depends
from src.api.schemas import HealthResponse
from src.api.dependencies import get_artifact_store, ArtifactStore

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
@router.get("/api/health", response_model=HealthResponse)
def health_check(store: ArtifactStore = Depends(get_artifact_store)):
    """
    Health check endpoint to verify backend service operational status and model readiness.
    
    Returns:
        HealthResponse object containing status, service name, models_loaded boolean, and tutor availability.
    """
    return HealthResponse(
        status="ok",
        service="quantum-learning-platform",
        models_loaded=store.models_loaded,
        tutor_available=True
    )


from fastapi import APIRouter

router = APIRouter()

@router.get(
    "/health",
    description="""
    Health check endpoint.

    Returns a simple status message indicating that the service is running and healthy.
    Useful for monitoring and readiness/liveness probes.
    """,
    tags=["Health"],
)
async def health_check():
    return {"status": "ok"}

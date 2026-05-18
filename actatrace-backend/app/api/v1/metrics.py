from fastapi import APIRouter, Response

from app.observability.metrics import render_metrics

router = APIRouter()


@router.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    body, content_type = render_metrics()
    return Response(content=body, media_type=content_type)

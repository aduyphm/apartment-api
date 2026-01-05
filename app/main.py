import time
from pathlib import Path
from fastapi import FastAPI, APIRouter, Request
from starlette_exporter import PrometheusMiddleware, handle_metrics

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.utils.logs import logger

BASE_PATH = Path(__file__).resolve().parent

root_router = APIRouter()
app = FastAPI()
app.add_middleware(PrometheusMiddleware,
                   app_name="price-prediction",
                   prefix="metric",
                   group_paths=True)
app.add_route("/actuator/prometheus", handle_metrics)


@app.middleware("http")
async def log(req: Request, call_next):
    if "clientMessageId" in req.headers:
        client_message_id = req.headers["clientMessageId"]
    else:
        client_message_id = ""
    start_time = time.time()
    response = await call_next(req)
    process_time = time.time() - start_time
    if not (str(req.url.path) in ["/actuator/health", "/actuator/info", "/actuator/prometheus", "/probe"]):
        message = '"{} {}" {}'.format(req.method, str(req.url.path), response.status_code)
        logger.info(message, extra={"clientMessageId": client_message_id, "status_code": response.status_code,
                                    "duration": str(round(process_time, 1))})
    return response


@root_router.get("/actuator/health", status_code=200)
def health_check():
    return "ok"


@root_router.get("/actuator/info", status_code=200)
def health_check_info():
    return "ok"


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")

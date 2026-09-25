from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from controller import admin_controller, auth_and_user_controller
from utils.db_connection import DbConnection
from utils.log_utils import LogMiddleware, get_logger, initialize_logs
from utils.settings import get_settings

logger = get_logger(__name__)

initialize_logs()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.db = DbConnection(settings)
    yield
    app.state.db.close()


app = FastAPI(title="VeloScope webservice", lifespan=lifespan)

app.add_middleware(LogMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic 422 errors to log them.
    """
    body = await request.body()
    body_str = body.decode() if body else "empty body"

    logger.error(f"Validation Error\nErrors: {exc.errors()}\nBody: {body_str}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body_str},
    )


app.include_router(admin_controller.router)
app.include_router(auth_and_user_controller.router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation (Swagger UI)"""
    return RedirectResponse(url="/docs")


@app.get("/hello/{name}", tags=["Misc"])
async def hello_name(name: str):
    """Display Hello"""
    logger.info("Display Hello")
    return {"message": f"Hello {name}"}


# Run the FastAPI application
if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "5000")),
    )

    logger.info("VeloScope webservice stopped")

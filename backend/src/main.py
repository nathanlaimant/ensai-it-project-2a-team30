"""
Module: main.py

Point d'entrée de l'application FastAPI VeloScope : initialisation des
logs, gestion du cycle de vie de la connexion à la base de données,
gestion globale des erreurs de validation, enregistrement des routeurs
et lancement du serveur Uvicorn.
"""

from contextlib import asynccontextmanager

import uvicorn
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
    """
    Gère le cycle de vie de l'application FastAPI.

    Ouvre la connexion à la base de données au démarrage de l'application
    et la ferme proprement à son arrêt.

    Parameters
    ----------
    app : FastAPI
        Instance de l'application FastAPI.

    Yields
    ------
    None
        Contrôle rendu à l'application pendant toute sa durée de vie.
    """
    app.state.db = DbConnection(get_settings())
    yield
    app.state.db.close()


app = FastAPI(title="VeloScope webservice", lifespan=lifespan)

app.add_middleware(LogMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepte les erreurs de validation Pydantic (422) pour les journaliser.

    Parameters
    ----------
    request : Request
        Requête HTTP à l'origine de l'erreur de validation.
    exc : RequestValidationError
        Exception de validation levée par FastAPI/Pydantic.

    Returns
    -------
    JSONResponse
        Réponse HTTP 422 contenant le détail des erreurs de validation
        et le corps de la requête reçue.
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
    """
    Redirige vers la documentation de l'API (Swagger UI).

    Returns
    -------
    RedirectResponse
        Réponse de redirection HTTP vers `/docs`.
    """
    return RedirectResponse(url="/docs")


@app.get("/hello/{name}", tags=["Misc"])
async def hello_name(name: str):
    """
    Affiche un message de salutation personnalisé.

    Parameters
    ----------
    name : str
        Nom à inclure dans le message de salutation.

    Returns
    -------
    dict
        Dictionnaire contenant le message de salutation.
    """
    logger.info("Display Hello")
    return {"message": f"Hello {name}"}


# Run the FastAPI application
if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        app,
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
    )

    logger.info("VeloScope webservice stopped")


import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def load_environment_variables():
    """
    Charge les variables d'environnement depuis un fichier .env
    situé à la racine du frontend ou dans un dossier parent.

    Les variables déjà définies dans l'environnement sont conservées.
    """
    current_dir = Path(__file__).resolve().parent

    env_file = None

    for directory in [current_dir, *current_dir.parents]:
        candidate = directory / ".env"
        if candidate.is_file():
            env_file = candidate
            break

    if env_file is None:
        logger.info("Aucun fichier .env trouvé.")
        return

    with open(env_file, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Ignore les lignes vides et les commentaires
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip()

            # Retire les guillemets éventuels
            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in ("'", '"')
            ):
                value = value[1:-1]

            # Ne remplace pas une variable déjà définie
            os.environ.setdefault(key, value)

    logger.info("Variables d'environnement chargées depuis %s", env_file)


def display_values(include_prefix: str = ""):
    """
    Affiche dans les logs les variables d'environnement
    correspondant au préfixe demandé.

    Les valeurs sensibles sont masquées.
    """
    logger.info("Variables d'environnement (%s) :", include_prefix)

    for key, value in sorted(os.environ.items()):
        if key.startswith(include_prefix):
            if any(
                sensitive in key.upper()
                for sensitive in ("PASSWORD", "SECRET", "TOKEN", "KEY")
            ):
                value = "********"

            logger.info("%s = %s", key, value)

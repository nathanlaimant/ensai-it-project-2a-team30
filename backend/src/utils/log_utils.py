import logging
import logging.config
import numbers
from functools import wraps
from pathlib import Path

import yaml
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

"""Utilitaires de journalisation (logging)."""


def initialize_logs(name: str):
    """
    Initialise la journalisation à partir d'un fichier de configuration.
 
    Crée le dossier `logs` à la racine du projet s'il n'existe pas,
    charge la configuration de logging depuis `logging_config.yml`,
    puis écrit un bandeau de démarrage dans les logs.
 
    Parameters
    ----------
    name : str
        Nom de l'application ou du module démarré, affiché dans le
        bandeau de démarrage des logs.
 
    Returns
    -------
    None
    """

    # Create the logs folder at project root if it doesn't exist
    logs_dir = Path(__file__).resolve().parents[2] / "logs"
    logs_dir.mkdir(exist_ok=True)

    config_file = Path(__file__).resolve().parents[2] / "logging_config.yml"

    with open(config_file, encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
        logging.config.dictConfig(config)

        logging.info("-" * 50)
        logging.info(f"Starting {name}                           ")
        logging.info("-" * 50)


def get_logger(module_name: str, max_size: int = 25):
    """
    Retourne un logger dont le nom est raccourci si nécessaire.
 
    Si le chemin du module dépasse `max_size` caractères, les parties
    du chemin (sauf la dernière) sont réduites à leur initiale.
 
    Parameters
    ----------
    module_name : str
        Nom complet du module (ex: `__name__` du module appelant).
    max_size : int, optional
        Longueur maximale du nom avant raccourcissement. Par défaut 25.
 
    Returns
    -------
    logging.Logger
        Logger associé au nom (raccourci ou non).
    """
    if len(module_name) <= max_size:
        return logging.getLogger(module_name)

    parts = module_name.split(".")
    short_prefix = [p[0] for p in parts[:-1]]
    short_name = ".".join(short_prefix + [parts[-1]])

    return logging.getLogger(short_name)


class LogIndentation:
    """
    Gère l'indentation des logs lors de l'entrée dans une nouvelle méthode.
 
    Parameters
    ----------
    current_indentation : int
        Niveau d'indentation courant (nombre de niveaux imbriqués).
    indentation_size : int
        Nombre d'espaces représentant un niveau d'indentation.
    """

    current_indentation = 0
    indentation_size = 2

    @classmethod
    def increase_indentation(cls):
        """
        Augmente le niveau d'indentation courant d'un cran.
 
        Returns
        -------
        None
        """
        cls.current_indentation += 1

    @classmethod
    def decrease_indentation(cls):
        """
        Diminue le niveau d'indentation courant d'un cran.
 
        Returns
        -------
        None
        """
        cls.current_indentation -= 1

    @classmethod
    def get_indentation(cls):
        """
        Retourne la chaîne d'espaces correspondant à l'indentation courante.
 
        Returns
        -------
        str
            Chaîne composée d'espaces, dont la longueur dépend du niveau
            d'indentation courant.
        """
        return " " * cls.indentation_size * cls.current_indentation


def log(func):
    """
    Décorateur journalisant les appels de méthode et leurs résultats.
 
    Appliqué à une méthode, ce décorateur journalise :
    - l'appel de la méthode avec la valeur de ses paramètres (les
      paramètres sensibles comme les mots de passe ou jetons sont masqués) ;
    - la valeur de retour de la méthode (tronquée si elle est trop longue).
 
    Parameters
    ----------
    func : callable
        Méthode ou fonction à décorer.
 
    Returns
    -------
    callable
        La fonction `wrapper` encapsulant `func` avec la journalisation.
    """

    SENSITIVE_KEYWORDS = {
        "password",
        "passwd",
        "pwd",
        "pass",
        "token",
        "secret",
        "key",
    }

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Exécute `func` en journalisant son appel et son résultat.
 
        Parameters
        ----------
        *args
            Arguments positionnels transmis à `func`.
        **kwargs
            Arguments nommés transmis à `func`.
 
        Returns
        -------
        Any
            Le résultat retourné par `func`.
        """
        if args and hasattr(args[0], "__class__"):
            logger = get_logger(f"{args[0].__class__.__module__}")
        else:
            logger = logging.getLogger(__name__)

        LogIndentation.increase_indentation()
        indentation = LogIndentation.get_indentation()

        # Retrieve method parameters
        method_name = func.__name__
        param_names = func.__code__.co_varnames[1 : func.__code__.co_argcount]
        args_list = []

        for i, arg in enumerate(args[1:]):
            if i >= len(param_names):
                break
            param_name = param_names[i].lower()
            if any(keyword in param_name for keyword in SENSITIVE_KEYWORDS):
                args_list.append("*****")
            else:
                args_list.append(
                    str(arg) if not isinstance(arg, numbers.Number) else arg
                )

        for k, v in kwargs.items():
            if any(keyword in k.lower() for keyword in SENSITIVE_KEYWORDS):
                args_list.append("*****")
            else:
                args_list.append(str(v) if not isinstance(v, numbers.Number) else v)

        args_tuple = tuple(args_list)

        # Log method entry
        logger.info(f"{indentation}{method_name}{args_tuple} - START")
        result = func(*args, **kwargs)
        logger.info(f"{indentation}{method_name}{args_tuple} - END")

        # Shorten long output for readability
        if isinstance(result, list):
            result_str = str([str(item) for item in result[:3]])
            result_str += f" ... ({len(result)} elements)"
        elif isinstance(result, dict):
            result_str = [(str(k), str(v)) for k, v in list(result.items())[:3]]
            result_str += f" ... ({len(result)} elements)"
        elif isinstance(result, str) and len(result) > 50:
            result_str = result[:50] + f" ... ({len(result)} characters)"
        else:
            result_str = str(result)

        logger.info(f"{indentation}  └─> Output: {result_str}")

        LogIndentation.decrease_indentation()

        return result

    return wrapper


class LogMiddleware(BaseHTTPMiddleware):
    """Middleware FastAPI journalisant les requêtes et réponses HTTP."""
    async def dispatch(self, request: Request, call_next):
        """
        Journalise une requête HTTP entrante et sa réponse.
 
        Capture la méthode, le chemin, le code de statut et les détails
        d'erreur éventuels de la requête traitée.
 
        Parameters
        ----------
        request : Request
            Requête HTTP entrante.
        call_next : callable
            Fonction permettant de transmettre la requête au gestionnaire
            suivant dans la chaîne de middlewares.
 
        Returns
        -------
        Response
            Réponse HTTP renvoyée par le gestionnaire suivant.
 
        Raises
        ------
        Exception
            Toute exception levée pendant le traitement de la requête,
            journalisée puis propagée.
        """

        method = request.method
        path = str(request.url.path)

        logging.info(f"{method} {path} - START")

        try:
            response = await call_next(request)
            logging.info(f"{method} {path} - END [Status: {response.status_code}]")
            return response

        except Exception as e:
            logging.error(f"{method} {path} - FAILED [Status: 500] Error: {str(e)}")
            raise e

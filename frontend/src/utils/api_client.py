import os
from typing import Any, Optional
import requests

class APIClient:
    """
    Client HTTP générique pour consommer une API REST.
 
    Parameters
    ----------
    base_url : str, optional
        URL de base de l'API. Si non fournie, utilise la variable
        d'environnement `API_BASE_URL`, ou `http://localhost:5000` par défaut.
    timeout : int, optional
        Délai maximal, en secondes, avant qu'une requête n'échoue par
        timeout. Par défaut 10.
    """
    def __init__(self, base_url: str = None, timeout: int = 10):
        default_url = os.getenv("API_BASE_URL", "http://localhost:5000")
        self.base_url = (base_url or default_url).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        """
        Construit l'URL complète d'un endpoint à partir de l'URL de base.
 
        Parameters
        ----------
        endpoint : str
            Chemin de l'endpoint à appeler (avec ou sans `/` initial).
 
        Returns
        -------
        str
            URL complète résultant de la jointure de l'URL de base et
            de l'endpoint.
        """
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        """
        Envoie une requête HTTP GET à l'API.
 
        Parameters
        ----------
        endpoint : str
            Chemin de l'endpoint à appeler.
        params : dict, optional
            Paramètres de requête (query string) à transmettre.
        headers : dict, optional
            En-têtes HTTP à transmettre.
 
        Returns
        -------
        Any
            Contenu JSON de la réponse, ou un dictionnaire vide si la
            réponse ne contient pas de corps.
        """
        url = self._build_url(endpoint)
        response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else {}

    def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        """
        Envoie une requête HTTP POST à l'API.
 
        Parameters
        ----------
        endpoint : str
            Chemin de l'endpoint à appeler.
        data : dict, optional
            Corps de la requête, envoyé au format JSON.
        headers : dict, optional
            En-têtes HTTP à transmettre.
 
        Returns
        -------
        Any
            Contenu JSON de la réponse, ou un dictionnaire vide si la
            réponse ne contient pas de corps.
        """
        url = self._build_url(endpoint)
        response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else {}

    def put(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        """
        Envoie une requête HTTP PUT à l'API.
 
        Parameters
        ----------
        endpoint : str
            Chemin de l'endpoint à appeler.
        data : dict, optional
            Corps de la requête, envoyé au format JSON.
        headers : dict, optional
            En-têtes HTTP à transmettre.
 
        Returns
        -------
        Any
            Contenu JSON de la réponse, ou un dictionnaire vide si la
            réponse ne contient pas de corps.
        """
        url = self._build_url(endpoint)
        response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else {}

    def delete(
        self,
        endpoint: str,
        headers: Optional[dict[str, str]] = None,
    ) -> int:
        """
        Envoie une requête HTTP DELETE à l'API.
 
        Parameters
        ----------
        endpoint : str
            Chemin de l'endpoint à appeler.
        headers : dict, optional
            En-têtes HTTP à transmettre.
 
        Returns
        -------
        int
            Code de statut HTTP de la réponse.
        """
        url = self._build_url(endpoint)
        response = self.session.delete(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.status_code
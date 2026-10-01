"""HTTP client abstraction used by feed ingestion."""


class HttpClient:
    """Représente la dépendance HTTP client de l'application."""

    def get(self, url: str) -> dict:
        """
        Récupère un contenu JSON à partir d'une URL.

        Parameters
        ----------
        url : str
            URL à interroger.

        Returns
        -------
        dict
            Contenu JSON de la réponse.
        """
        raise NotImplementedError

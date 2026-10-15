from __future__ import annotations

from datetime import date


class SystemInformation:
    """
    Décrit le système.

    Parameters
    ----------
    system_id : str | None
        Identifiant unique du système. Non-nullable, mais peut être None si l'objet n'a pas été persistée.
    language : str
        Langue par défaut des données du système (ex: "fr").
    name : str
        Nom public du système de vélos partagés.
    url : str | None
        URL du site web officiel du système. Nullable.
    start_date : date | None
        Date de mise en service du système. Nullable.
    phone_number : str | None
        Numéro de téléphone de contact du système. Nullable.
    email : str | None
        Adresse email de contact du système. Nullable.
    timezone : str
        Fuseau horaire du système (ex: "Europe/Paris").
    """

    def __init__(
        self,
        language: str,
        name: str,
        url: str | None,
        start_date: date | None,
        phone_number: str | None,
        email: str | None,
        timezone: str,
        system_id: str | None = None,
    ):
        self.system_id = system_id
        self.language = language
        self.name = name
        self.url = url
        self.start_date = start_date
        self.phone_number = phone_number
        self.email = email
        self.timezone = timezone

    @classmethod
    def from_dict(cls, data: dict) -> SystemInformation:
        """Crée une instance de SystemInformation à partir d'un dictionnaire."""
        return cls(
            language=data["language"],
            name=data["name"],
            url=data.get("url"),
            start_date=(
                date.fromisoformat(data["start_date"])
                if data.get("start_date")
                else None
            ),
            phone_number=data.get("phone_number"),
            email=data.get("email"),
            timezone=data["timezone"],
            system_id=data["system_id"],
        )

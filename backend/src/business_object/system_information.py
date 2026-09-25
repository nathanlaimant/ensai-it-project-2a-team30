from datetime import date

from pydantic import BaseModel


class SystemInformation(BaseModel):
    """
    Décrit le système.
 
    Parameters
    ----------
    system_id : str
        Identifiant unique du système.
    language : str
        Langue par défaut des données du système (ex: "fr").
    name : str
        Nom public du système de vélos partagés.
    url : str
        URL du site web officiel du système.
    start_date : date
        Date de mise en service du système.
    phone_number : str
        Numéro de téléphone de contact du système.
    email : str
        Adresse email de contact du système.
    timezone : str
        Fuseau horaire du système (ex: "Europe/Paris").
 
    Returns
    -------
    SystemInformation
        Instance représentant les métadonnées du système.
    """

    system_id: str
    language: str
    name: str
    url: str
    start_date: date
    phone_number: str
    email: str
    timezone: str

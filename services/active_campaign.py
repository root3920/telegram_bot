import os
import requests

ACTIVE_CAMPAIGN_API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
ACTIVE_CAMPAIGN_API_TOKEN = os.getenv("ACTIVE_CAMPAIGN_API_TOKEN")

def sync_contact(email: str, codigo: str):
    """
    Sincroniza un contacto en ActiveCampaign con un código personalizado.
    """
    url = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contact/sync"
    headers = {
        "Api-Token": ACTIVE_CAMPAIGN_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "contact": {
            "email": email,
            "fieldValues": [
                {"field": os.getenv("CODIGO_CAMPO_ID"), "value": codigo}
            ]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code

def asignar_etiqueta(contact_id: int, tag_id: int):
    """
    Asigna una etiqueta (tag) a un contacto en ActiveCampaign.
    """
    url = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contactTags"
    headers = {
        "Api-Token": ACTIVE_CAMPAIGN_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "contactTag": {
            "contact": contact_id,
            "tag": tag_id
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code

def agregar_a_automatizacion(contact_id: int, automation_id: int):
    """
    Agrega un contacto a una automatización específica en ActiveCampaign.
    """
    url = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contactAutomations"
    headers = {
        "Api-Token": ACTIVE_CAMPAIGN_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "contactAutomation": {
            "contact": str(contact_id),
            "automation": str(automation_id)
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code
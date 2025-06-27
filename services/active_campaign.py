import os, requests
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
API_TOKEN = os.getenv("ACTIVE_CAMPAIGN_API_TOKEN")
TAG_ID = os.getenv("TAG_ID")
AUTOMATION_ID = os.getenv("AUTOMATION_ID")
CODIGO_CAMPO_ID = os.getenv("CODIGO_CAMPO_ID")

def sync_contact(email, code):
    url = f"{API_URL}/api/3/contact/sync"
    headers = {"Api-Token": API_TOKEN, "Content-Type": "application/json"}
    payload = {
        "contact": {
            "email": email,
            "fieldValues": [{"field": CODIGO_CAMPO_ID, "value": code}]
        }
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code in (200, 201):
        contact_id = res.json().get("contact", {}).get("id")
        if contact_id:
            add_tag(contact_id)
            add_to_automation(contact_id)
    return res.status_code

def add_tag(contact_id):
    url = f"{API_URL}/api/3/contactTags"
    headers = {"Api-Token": API_TOKEN, "Content-Type": "application/json"}
    requests.post(url, headers=headers, json={"contactTag": {"contact": contact_id, "tag": TAG_ID}})

def add_to_automation(contact_id):
    url = f"{API_URL}/api/3/contactAutomations"
    headers = {"Api-Token": API_TOKEN, "Content-Type": "application/json"}
    requests.post(url, headers=headers, json={"contactAutomation": {"contact": contact_id, "automation": AUTOMATION_ID}})

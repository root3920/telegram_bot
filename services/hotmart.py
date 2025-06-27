import os, requests, base64
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("HOTMART_CLIENT_ID")
CLIENT_SECRET = os.getenv("HOTMART_CLIENT_SECRET")

def verificar_compra_hotmart(email: str) -> bool:
    try:
        basic_token = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_url = (
            f"https://api-sec-vlc.hotmart.com/security/oauth/token"
            f"?grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {basic_token}"
        }
        auth = requests.post(token_url, headers=headers)
        auth.raise_for_status()
        access_token = auth.json().get("access_token")
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        params = {"transaction_status": "APPROVED"}
        url = "https://developers.hotmart.com/payments/api/v1/sales/history"

        while True:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()
            for venta in data.get("items", []):
                if venta.get("buyer", {}).get("email", "").lower() == email.lower():
                    return True
            next_page = data.get("page_info", {}).get("next_page_token")
            if not next_page:
                break
            params["page_token"] = next_page
    except Exception as e:
        print("❌ Error verificando compra:", e)
    return False
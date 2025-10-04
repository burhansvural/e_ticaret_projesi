# frontend/src/api.py
import requests
from threading import Thread
import time
from websockets.sync.client import connect

API_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/products_updates"


def fetch_products_from_api():
    """Backend'den tüm ürünleri çeker."""
    try:
        response = requests.get(f"{API_URL}/products/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Hatası (fetch_products): {e}")
        return None  # Hata durumunda None döndür


def logout_user_api(access_token, refresh_token=None):
    """Backend'e logout isteği gönderir."""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        data = {}
        if refresh_token:
            data["refresh_token"] = refresh_token
        
        response = requests.post(f"{API_URL}/users/logout", headers=headers, json=data)
        response.raise_for_status()
        return {"success": True, "message": response.json().get("message", "Başarıyla çıkış yapıldı")}
    except requests.exceptions.RequestException as e:
        print(f"API Hatası (logout): {e}")
        return {"success": False, "message": "Çıkış işlemi sırasında bir hata oluştu"}


def listen_for_updates_in_thread(page):
    """WebSocket dinleyicisini ayrı bir thread'de başlatır."""

    def ws_listener():
        while True:
            try:
                with connect(WS_URL) as websocket:
                    print("WebSocket bağlantısı kuruldu.")
                    for message in websocket:
                        if message == "products_updated":
                            page.pubsub.send_all("products_update")
            except Exception as e:
                print(f"WebSocket hatası: {e}. 5sn sonra tekrar denenecek.")
                time.sleep(5)

    thread = Thread(target=ws_listener, daemon=True)
    thread.start()
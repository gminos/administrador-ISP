import requests
import logging
import os

logger = logging.getLogger(__name__)

class WireguardManager:
    def __init__(self, host=None, port=51821, password=None):
        self.host = host or os.environ.get('WG_EASY_API_HOST', 'wg-easy')
        self.password = password or os.environ.get('WG_EASY_API_PASSWORD', 'secret_dev_password')
        self.base_url = f"http://{self.host}:{port}"
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        try:
            url = f"{self.base_url}/api/session"
            response = self.session.post(url, json={"password": self.password}, timeout=10)
            response.raise_for_status()
            logger.info("Autenticado exitosamente con el servidor WireGuard")
        except Exception as e:
            logger.error(f"Fallo al autenticar con WireGuard: {e}")
            raise

    def get_clients(self):
        try:
            url = f"{self.base_url}/api/wireguard/client"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo la lista de clientes: {e}")
            return []

    def create_client(self, name: str):
        try:
            url = f"{self.base_url}/api/wireguard/client"
            response = self.session.post(url, json={"name": name}, timeout=10)
            response.raise_for_status()

            clients = self.get_clients()
            for client in clients:
                if client.get('name') == name:
                    return client
            return None
        except Exception as e:
            logger.error(f"Error creando el cliente {name}: {e}")
            raise

    def get_client_config(self, client_id: str):
        try:
            url = f"{self.base_url}/api/wireguard/client/{client_id}/configuration"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error obteniendo la configuración para el cliente {client_id}: {e}")
            raise

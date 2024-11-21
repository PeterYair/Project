import requests

def verificar_estado(servicio_id, url):
    """
    Verifica si un servicio está online o offline haciendo una solicitud HTTP.
    :param servicio_id: ID del servicio (opcional, no se utiliza aquí directamente).
    :param url: URL del servicio a verificar.
    :return: "online" si el servicio responde correctamente, "offline" en caso contrario.
    """
    # Encabezados personalizados para simular una solicitud legítima
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://google.com",  # Simula venir desde Google
    }

    try:
        print(f"Verificando estado de {url}...")  # Mensaje de depuración
        # Hacer una solicitud HTTP con los encabezados personalizados
        response = requests.get(url, headers=headers, timeout=10)

        # Evaluar el estado HTTP de la respuesta
        if response.status_code == 200:
            print(f"Servicio {url} está online.")
            return "online"
        else:
            print(f"Servicio {url} está offline con código {response.status_code}.")
            return "offline"
    except requests.exceptions.RequestException as e:
        print(f"Error al verificar el servicio {url}: {str(e)}")
        return "offline"

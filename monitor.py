import requests

def verificar_estado(servicio_id, url):
    """
    Verifica si un servicio está online o offline haciendo una solicitud HTTP.
    :param servicio_id: ID del servicio (opcional, no se utiliza aquí directamente).
    :param url: URL del servicio a verificar.
    :return: "online" si el servicio responde correctamente, "offline" en caso contrario.
    """
    try:
        response = requests.get(url, timeout=5)  # Tiempo de espera de 10 segundos
        if response.status_code == 200:
            return "online"
        else:
            return "offline"
    except requests.exceptions.RequestException:
        return "offline"

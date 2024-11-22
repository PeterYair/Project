from concurrent.futures import ThreadPoolExecutor
import requests
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Verificar un solo servicio
def verificar_estado(servicio_id, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://google.com",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return {
            "id": servicio_id,
            "url": url,
            "status": "online" if response.status_code == 200 else "offline",
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds()
        }
    except requests.exceptions.Timeout:
        return {"id": servicio_id, "url": url, "status": "offline", "error": "timeout"}
    except requests.exceptions.ConnectionError:
        return {"id": servicio_id, "url": url, "status": "offline", "error": "connection_error"}
    except requests.exceptions.RequestException as e:
        return {"id": servicio_id, "url": url, "status": "offline", "error": str(e)}

# Verificar múltiples servicios usando un pool de hilos
def verificar_servicios_concurrente(servicios, max_workers=10):
    resultados = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {executor.submit(verificar_estado, s["id"], s["url"]): s for s in servicios}
        for futuro in futuros:
            try:
                resultados.append(futuro.result())
            except Exception as e:
                logging.error(f"Error al verificar servicio: {e}")
    return resultados

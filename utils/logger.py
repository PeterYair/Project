from datetime import datetime

LOG_FILE = "data/logs.txt"

def log_event(servicio, estado):
    """Registra eventos en el archivo de logs."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as file:
        file.write(f"[{timestamp}] {servicio} - {estado}\n")

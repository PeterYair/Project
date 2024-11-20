# Monitor de Aula Virtual

Este proyecto monitorea el estado de la página web `aulavirtual.autonomadeica.edu.pe` y muestra su estado (Online/Offline) en una interfaz gráfica de escritorio. Además, registra eventos en un archivo de logs.

## Estructura
- **app.py**: Interfaz gráfica con Tkinter.
- **monitor.py**: Lógica para verificar el estado de la página web.
- **config.py**: Configuración del proyecto.
- **utils/logger.py**: Registro de eventos.

## Requisitos
1. Python 3.7 o superior.
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt

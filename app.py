import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk  # Usar Pillow para manejar la imagen y escalarla
import mysql.connector  # Asegúrate de tener este módulo instalado si usas MySQL
from config import DB_CONFIG
import datetime
import threading
import winsound  # Para reproducir sonido en Windows
import csv  # Para generar el reporte en CSV
import requests  # Necesario para hacer la verificación HTTP


class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard de Monitoreo - Universidad Autónoma de Ica")
        self.root.configure(bg="#F5F5F5")  # Fondo principal suave
        self.root.state('zoomed')

        # Crear encabezado principal
        self.header_frame = tk.Frame(self.root, bg="#003366")  # Azul institucional
        self.header_frame.pack(fill=tk.X, pady=10)

        # Crear área de servicios con scrollbar
        self.main_frame = tk.Frame(self.root, bg="#F5F5F5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(self.main_frame, bg="#F5F5F5", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#F5F5F5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"),
                width=self.scrollable_frame.winfo_reqwidth()
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.root.winfo_screenwidth())
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.build_ui()
        self.load_services()  # Cargar los servicios al iniciar la aplicación
        self.actualizar_estado_servicios()  # Actualizar los servicios periódicamente

    def build_ui(self):
        # Encabezado principal
        tk.Label(
            self.header_frame,
            text="Universidad Autónoma de Ica - Dashboard de Monitoreo",
            bg="#003366",
            fg="white",
            font=("Helvetica", 24, "bold")
        ).pack(fill=tk.X, pady=20)

        # Botones principales
        button_frame = tk.Frame(self.header_frame, bg="#003366")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Registrar Nuevo Servicio",
            font=("Arial", 14),
            bg="#0072C6",
            fg="white",
            command=self.registrar_servicio
        ).grid(row=0, column=0, padx=10)

        # Botón para generar reporte
        tk.Button(
            button_frame,
            text="Generar Reporte",
            font=("Arial", 14),
            bg="#0072C6",
            fg="white",
            command=self.generar_reporte
        ).grid(row=0, column=1, padx=10)

    def load_services(self):
        """
        Carga los servicios desde la base de datos y los agrega al dashboard.
        """
        # Limpiar el frame de servicios antes de cargar los nuevos
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        servicios = self.obtener_servicios()  # Obtener servicios de la base de datos
        print(f"Servicios cargados: {servicios}")  # Depuración

        # Ajustamos el número de columnas y centramos los servicios
        for idx, servicio in enumerate(servicios):
            self.agregar_servicio_dashboard(servicio["id"], servicio["nombre"], servicio["url"], servicio["estado"], idx)

    def agregar_servicio_dashboard(self, servicio_id, nombre, url, estado, idx):
        """
        Agrega un servicio al dashboard y lo coloca centrado.
        """
        servicio_frame = tk.Frame(self.scrollable_frame, bg="white", borderwidth=1, relief="solid")
        servicio_frame.grid(row=idx, column=0, pady=5, padx=10, sticky="ew")  # Aseguramos que el widget ocupe toda la fila

        # Configuración de la columna
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Nombre del servicio
        tk.Label(
            servicio_frame,
            text=nombre,
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#003366",
            anchor="center"  # Alinear al centro
        ).grid(row=0, column=0, padx=10, pady=5, sticky="ew")  # Centrado

        # Indicador de estado con imágenes
        if estado == "online":
            color = "#28A745"  # Verde para online
            estado_text = "Online"
            estado_img = "static/images/comprobado.png"
        else:
            color = "#DC3545"  # Rojo para offline
            estado_text = "Offline"
            estado_img = "static/images/alerta.png"

        # Cargar la imagen de estado y redimensionarla (tamaño igual que delete.png)
        estado_image = Image.open(estado_img)
        estado_image = estado_image.resize((56, 56), Image.Resampling.LANCZOS)  # Duplicar tamaño
        estado_photo = ImageTk.PhotoImage(estado_image)

        estado_label = tk.Label(
            servicio_frame,
            text=estado_text,
            font=("Arial", 14, "bold"),
            bg=color,
            fg="white",
            width=10
        )
        estado_label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Mostrar la imagen de estado (comprobado o alerta)
        estado_image_label = tk.Label(servicio_frame, image=estado_photo)
        estado_image_label.image = estado_photo  # Mantener la referencia
        estado_image_label.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # Cargar la imagen delete.png y redimensionarla (duplicar el tamaño)
        try:
            delete_image = Image.open("static/images/delete.png")  # Abrir la imagen delete.png
            delete_image = delete_image.resize((56, 56), Image.Resampling.LANCZOS)  # Duplicar tamaño
            delete_photo = ImageTk.PhotoImage(delete_image)  # Convertir a un formato adecuado para Tkinter
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            delete_photo = None

        # Botón para eliminar el servicio con la imagen escalada y texto
        eliminar_button = tk.Button(
            servicio_frame,
            text="Borrar",
            image=delete_photo,  # Usar la imagen escalada
            compound="left",  # El texto y la imagen estarán a la izquierda
            bg="white",
            relief="flat",
            command=lambda: self.eliminar_servicio(servicio_id, servicio_frame)
        )
        eliminar_button.image = delete_photo  # Referencia para evitar que se elimine
        eliminar_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

    def obtener_servicios(self):
        """
        Obtiene los servicios de la base de datos.
        """
        try:
            # Conexión a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM servicios;"
            cursor.execute(query)
            servicios = cursor.fetchall()
            return servicios

        except mysql.connector.Error as err:
            print(f"Error de conexión a MySQL: {err}")
            return []

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def verificar_estado(self, servicio_id, url):
        """
        Verifica si un servicio está online mediante una solicitud HTTP.
        
        :param servicio_id: El ID del servicio
        :param url: La URL del servicio
        :return: 'online' si el servicio responde, 'offline' si no responde.
        """
        try:
            response = requests.get(url, timeout=5)  # Timeout de 5 segundos
            if response.status_code == 200:
                return 'online'
            else:
                return 'offline'
        except requests.exceptions.RequestException:
            return 'offline'  # Si ocurre un error en la solicitud, lo marcamos como offline

    def actualizar_estado_servicios(self):
        """
        Actualiza el estado de los servicios y reproduce una alerta si algún servicio está offline.
        """
        servicios = self.obtener_servicios()
        hora_actual = datetime.datetime.now()

        for servicio in servicios:
            estado = self.verificar_estado(servicio["id"], servicio["url"])

            # Solo actualiza el estado sin pasar parámetros incorrectos
            for widget in self.scrollable_frame.winfo_children():
                if isinstance(widget, tk.Frame) and widget.winfo_children():
                    label = widget.grid_slaves(row=0, column=0)[0]
                    if label.cget("text") == servicio["nombre"]:
                        estado_label = widget.grid_slaves(row=0, column=1)[0]
                        estado_label.config(
                            text="Online" if estado == "online" else "Offline",
                            bg="#28A745" if estado == "online" else "#DC3545"
                        )

                        if estado == "offline":
                            threading.Thread(target=self.reproducir_alerta).start()
                        break

        self.root.after(60000, self.actualizar_estado_servicios)  # Llama a la función cada 60 segundos

    def reproducir_alerta(self):
        """
        Reproduce un sonido de alerta durante 5 segundos.
        """
        for _ in range(5):  # Reproducir sonido repetidamente durante 5 segundos
            winsound.Beep(1000, 1000)  # Frecuencia: 1000 Hz, Duración: 1 segundo

    def generar_reporte(self):
        """
        Genera un reporte completo con el estado actual de los servicios, historial de cambios,
        alertas y estadísticas.
        """
        servicios = self.obtener_servicios()
        
        reporte_filename = "static/reports/reporte_completo_servicios.csv"
        
        with open(reporte_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Escribir encabezados
            writer.writerow(["ID", "Nombre", "Estado", "URL", "Fecha de Actualización"])
            
            # Escribir datos actuales de los servicios
            for servicio in servicios:
                writer.writerow([servicio["id"], servicio["nombre"], servicio["estado"], servicio["url"], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            
            # Escribir el historial de cambios de estado
            writer.writerow([])  # Dejar una línea en blanco entre secciones
            writer.writerow(["ID", "Nombre", "Fecha de Cambio", "Estado Anterior", "Estado Actual", "Duración (Horas)"])

            for servicio in servicios:
                historial = self.obtener_historial_de_estado(servicio["id"])  # Obtener historial
                for cambio in historial:
                    writer.writerow([servicio["id"], servicio["nombre"], cambio["hora"], cambio["estado"], cambio["estado"], 0])  # Ajustar duración según sea necesario
        
            # Escribir las estadísticas
            writer.writerow([])  # Línea en blanco
            writer.writerow(["Estadísticas del Sistema"])
            writer.writerow(["Total de Servicios", len(servicios)])
            servicios_online = sum(1 for servicio in servicios if servicio["estado"] == "online")
            writer.writerow(["Servicios Online", servicios_online])
            servicios_offline = len(servicios) - servicios_online
            writer.writerow(["Servicios Offline", servicios_offline])
            
            # Escribir las alertas generadas
            writer.writerow([])  # Línea en blanco
            writer.writerow(["Alertas Generadas"])
            writer.writerow(["ID", "Nombre del Servicio", "Tipo de Alerta", "Fecha de Alerta", "Descripción"])
            
            alertas = self.obtener_alertas()  # Obtener alertas
            for alerta in alertas:
                writer.writerow([alerta["id"], alerta["nombre"], alerta["tipo"], alerta["fecha"], alerta["descripcion"]])
        
        messagebox.showinfo("Generar Reporte", f"El reporte ha sido generado correctamente: {reporte_filename}")

    def obtener_historial_de_estado(self, servicio_id):
        """
        Obtiene el historial de cambios de estado de un servicio.
        """
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM historial WHERE servicio_id = %s ORDER BY hora ASC"
            cursor.execute(query, (servicio_id,))
            historial = cursor.fetchall()
            return historial
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_alertas(self):
        """
        Obtiene las alertas generadas por los servicios.
        """
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM alertas;"
            cursor.execute(query)
            alertas = cursor.fetchall()
            return alertas
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def registrar_servicio(self):
        """
        Permite al usuario registrar un nuevo servicio en la base de datos.
        """
        nombre = simpledialog.askstring("Registrar Servicio", "Ingrese el nombre del servicio:")
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre para el servicio.")
            return

        url = simpledialog.askstring("Registrar Servicio", "Ingrese la URL del servicio:")
        if not url:
            messagebox.showwarning("Advertencia", "Debe ingresar una URL válida.")
            return

        try:
            # Conexión a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Insertar el servicio en la base de datos
            query = "INSERT INTO servicios (nombre, url, estado) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, url, "online"))
            connection.commit()

            messagebox.showinfo("Éxito", f"El servicio '{nombre}' ha sido registrado correctamente.")
            self.load_services()  # Recargar la lista de servicios
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al registrar el servicio: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def eliminar_servicio(self, servicio_id, servicio_frame):
        """
        Elimina un servicio de la base de datos y actualiza la interfaz.
        """
        try:
            # Conexión a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Eliminar el servicio de la base de datos
            query = "DELETE FROM servicios WHERE id = %s"
            cursor.execute(query, (servicio_id,))
            connection.commit()

            messagebox.showinfo("Éxito", "El servicio ha sido eliminado correctamente.")
            servicio_frame.destroy()  # Eliminar visualmente el servicio del dashboard
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar el servicio: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()

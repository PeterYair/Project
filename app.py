import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk  # Usar Pillow para manejar imágenes
from utils.db_manager import obtener_servicios, actualizar_estado_servicio, registrar_estado, agregar_servicio, eliminar_servicio
from monitor import verificar_servicios_concurrente
import datetime
import csv  # Para generar el reporte en CSV
import winsound  # Para emitir alertas sonoras en Windows
import threading  # Para manejar tareas en segundo plano


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
        self.cargar_servicios()  # Cargar los servicios al iniciar la aplicación
        self.iniciar_verificacion_automatica()  # Comenzar la verificación periódica en segundo plano

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

        tk.Button(
            button_frame,
            text="Generar Reporte",
            font=("Arial", 14),
            bg="#0072C6",
            fg="white",
            command=self.generar_reporte
        ).grid(row=0, column=1, padx=10)

    def cargar_servicios(self):
        """
        Carga los servicios desde la base de datos y los agrega al dashboard.
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        servicios = obtener_servicios()
        for idx, servicio in enumerate(servicios):
            self.mostrar_servicio_dashboard(servicio, idx)

    def mostrar_servicio_dashboard(self, servicio, idx):
        """
        Muestra un servicio en el dashboard.
        """
        servicio_frame = tk.Frame(self.scrollable_frame, bg="white", borderwidth=1, relief="solid")
        servicio_frame.grid(row=idx, column=0, pady=5, padx=10, sticky="ew")

        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        tk.Label(
            servicio_frame,
            text=servicio["nombre"],
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#003366"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        estado_color = "#28A745" if servicio["estado"] == "online" else "#DC3545"
        tk.Label(
            servicio_frame,
            text=servicio["estado"].capitalize(),
            font=("Arial", 14),
            bg=estado_color,
            fg="white",
            width=15
        ).grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        eliminar_button = tk.Button(
            servicio_frame,
            text="Eliminar",
            bg="white",
            command=lambda: self.eliminar_servicio(servicio["id"], servicio_frame)
        )
        eliminar_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

    def iniciar_verificacion_automatica(self):
        """
        Inicia la verificación de servicios en un hilo separado para evitar bloquear la interfaz.
        """
        threading.Thread(target=self.actualizar_estado_servicios, daemon=True).start()

    def actualizar_estado_servicios(self):
        """
        Actualiza el estado de los servicios periódicamente y reproduce alerta si un servicio está offline.
        """
        while True:
            servicios = obtener_servicios()
            resultados = verificar_servicios_concurrente(servicios)

            hora_actual = datetime.datetime.now()
            alerta_sonora = False

            for resultado in resultados:
                actualizar_estado_servicio(resultado["id"], resultado["status"])
                registrar_estado(resultado["id"], resultado["status"], hora_actual)

                if resultado["status"] == "offline":
                    alerta_sonora = True

            # Actualizar la interfaz gráfica desde el hilo principal
            self.root.after(0, self.cargar_servicios)

            if alerta_sonora:
                self.reproducir_alerta()

            # Esperar 60 segundos antes de la próxima verificación
            threading.Event().wait(60)

    def reproducir_alerta(self):
        """
        Reproduce una alerta sonora si un servicio está offline.
        """
        for _ in range(5):  # Reproducir 5 tonos de 1 segundo cada uno
            winsound.Beep(1000, 1000)

    def registrar_servicio(self):
        nombre = simpledialog.askstring("Registrar Servicio", "Ingrese el nombre del servicio:")
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre.")
            return

        url = simpledialog.askstring("Registrar Servicio", "Ingrese la URL del servicio:")
        if not url:
            messagebox.showwarning("Advertencia", "Debe ingresar una URL.")
            return

        if agregar_servicio(nombre, url):
            messagebox.showinfo("Éxito", f"Servicio '{nombre}' registrado correctamente.")
            self.cargar_servicios()
        else:
            messagebox.showerror("Error", "No se pudo registrar el servicio.")

    def generar_reporte(self):
        servicios = obtener_servicios()
        archivo = "static/reports/reporte_servicios.csv"

        with open(archivo, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Nombre", "Estado", "URL", "Fecha de Actualización"])
            for servicio in servicios:
                writer.writerow([servicio["id"], servicio["nombre"], servicio["estado"], servicio["url"], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        messagebox.showinfo("Reporte Generado", f"Reporte guardado en {archivo}")

    def eliminar_servicio(self, servicio_id, frame):
        if eliminar_servicio(servicio_id):
            messagebox.showinfo("Éxito", "Servicio eliminado correctamente.")
            frame.destroy()
        else:
            messagebox.showerror("Error", "No se pudo eliminar el servicio.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()

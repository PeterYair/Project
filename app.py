import tkinter as tk
from tkinter import simpledialog, messagebox
from utils.db_manager import obtener_servicios, agregar_servicio, registrar_estado, actualizar_estado_servicio, eliminar_servicio
from monitor import verificar_estado
import datetime
import threading
import winsound  # Para reproducir sonido en Windows


class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard de Monitoreo - Universidad Autónoma de Ica")
        self.root.configure(bg="#F5F5F5")  # Fondo principal suave
        self.root.state('zoomed')

        # Crear encabezado principal
        self.header_frame = tk.Frame(self.root, bg="#003366")  # Azul institucional
        self.header_frame.pack(fill=tk.X)

        # Crear área para los servicios
        self.services_frame = tk.Frame(self.root, bg="#F5F5F5")  # Fondo suave
        self.services_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        button_frame.pack()

        tk.Button(
            button_frame,
            text="Registrar Nuevo Servicio",
            font=("Arial", 14),
            bg="#0072C6",
            fg="white",
            command=self.registrar_servicio
        ).pack(side=tk.LEFT, padx=10, pady=10)

    def load_services(self):
        """
        Carga los servicios desde la base de datos y los agrega al dashboard.
        """
        # Limpiar el frame de servicios antes de cargar los nuevos
        for widget in self.services_frame.winfo_children():
            widget.destroy()

        servicios = obtener_servicios()  # Obtener servicios de la base de datos
        print(f"Servicios cargados: {servicios}")  # Depuración

        for servicio in servicios:
            self.agregar_servicio_dashboard(servicio["id"], servicio["nombre"], servicio["url"], servicio["estado"])

    def agregar_servicio_dashboard(self, servicio_id, nombre, url, estado):
        """
        Agrega un servicio al dashboard.
        """
        servicio_frame = tk.Frame(self.services_frame, bg="white", borderwidth=1, relief="solid")
        servicio_frame.pack(fill=tk.X, pady=5, padx=10)

        # Nombre del servicio
        tk.Label(
            servicio_frame,
            text=nombre,
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#003366"
        ).pack(side=tk.LEFT, padx=10)

        # Indicador de estado
        color = "#28A745" if estado == "online" else "#DC3545"  # Verde para online, rojo para offline
        estado_label = tk.Label(
            servicio_frame,
            text="Online" if estado == "online" else "Offline",
            font=("Arial", 14, "bold"),
            bg=color,
            fg="white",
            width=10,
            anchor="center"
        )
        estado_label.pack(side=tk.LEFT, padx=10)

        # Botón para eliminar el servicio
        tk.Button(
            servicio_frame,
            text="Eliminar",
            font=("Arial", 12),
            bg="#DC3545",
            fg="white",
            command=lambda: self.eliminar_servicio(servicio_id, servicio_frame)
        ).pack(side=tk.RIGHT, padx=10, pady=5)

    def reproducir_alerta(self):
        """
        Reproduce un sonido de alerta durante 5 segundos.
        """
        for _ in range(5):  # Reproducir sonido repetidamente durante 5 segundos
            winsound.Beep(1000, 1000)  # Frecuencia: 1000 Hz, Duración: 1 segundo

    def actualizar_estado_servicios(self):
        """
        Actualiza el estado de los servicios y reproduce una alerta si algún servicio está offline.
        """
        servicios = obtener_servicios()
        hora_actual = datetime.datetime.now()

        for servicio in servicios:
            estado = verificar_estado(servicio["id"], servicio["url"])

            if actualizar_estado_servicio(servicio["id"], estado):
                for widget in self.services_frame.winfo_children():
                    if isinstance(widget, tk.Frame) and widget.winfo_children():
                        label = widget.winfo_children()[0]
                        if label.cget("text") == servicio["nombre"]:
                            estado_label = widget.winfo_children()[1]
                            estado_label.config(
                                text="Online" if estado == "online" else "Offline",
                                bg="#28A745" if estado == "online" else "#DC3545"
                            )

                            # Reproducir alerta si está offline
                            if estado == "offline":
                                threading.Thread(target=self.reproducir_alerta).start()
                            break

        self.root.after(60000, self.actualizar_estado_servicios)

    def registrar_servicio(self):
        """
        Permite al usuario registrar un nuevo servicio.
        """
        nombre = simpledialog.askstring("Registrar Servicio", "Ingrese el nombre del servicio:")
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre para el servicio.")
            return

        url = simpledialog.askstring("Registrar Servicio", "Ingrese la URL del servicio:")
        if not url:
            messagebox.showwarning("Advertencia", "Debe ingresar una URL válida.")
            return

        if agregar_servicio(nombre, url):
            messagebox.showinfo("Éxito", f"El servicio '{nombre}' ha sido registrado correctamente.")
            self.load_services()  # Recargar el dashboard
        else:
            messagebox.showerror("Error", "No se pudo registrar el servicio. Inténtelo nuevamente.")

    def eliminar_servicio(self, servicio_id, servicio_frame):
        """
        Elimina un servicio del dashboard y la base de datos.
        """
        if eliminar_servicio(servicio_id):
            messagebox.showinfo("Éxito", "El servicio ha sido eliminado correctamente.")
            servicio_frame.destroy()  # Eliminar visualmente el servicio del dashboard
        else:
            messagebox.showerror("Error", "No se pudo eliminar el servicio.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()

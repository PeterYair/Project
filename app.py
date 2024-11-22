import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
from PIL import Image, ImageTk  # Usar Pillow para manejar imágenes
from utils.db_manager import obtener_servicios, actualizar_servicio, eliminar_servicio, agregar_servicio, registrar_estado, actualizar_estado_servicio
from monitor import verificar_servicios_concurrente
import threading
import datetime
import csv  # Para generar el reporte en CSV
import winsound  # Para emitir alertas sonoras en Windows


class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard de Monitoreo - Universidad Autónoma de Ica")
        self.root.configure(bg="#F5F5F5")  # Fondo suave
        self.root.geometry("1024x768")  # Tamaño predeterminado
        self.root.state('zoomed')  # Pantalla completa

        # Paleta de colores institucionales
        self.color_primario = "#003366"  # Azul oscuro
        self.color_secundario = "#0072C6"  # Azul claro
        self.color_acento = "#F5F5F5"  # Fondo claro
        self.color_eliminar = "#D32F2F"  # Rojo oscuro
        self.color_texto_botones = "white"  # Texto blanco para botones

        # Crear encabezado principal
        self.header_frame = tk.Frame(self.root, bg=self.color_primario, height=80)
        self.header_frame.pack(fill=tk.X)

        # Crear área de servicios
        self.main_frame = tk.Frame(self.root, bg=self.color_acento)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.scroll_canvas = tk.Canvas(self.main_frame, bg=self.color_acento, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.scroll_canvas.yview)
        self.scrollable_frame = tk.Frame(self.scroll_canvas, bg=self.color_acento)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )

        self.scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n", width=self.root.winfo_width() - 40)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.build_ui()
        self.cargar_servicios()
        self.iniciar_verificacion_automatica()

    def build_ui(self):
        # Título principal
        tk.Label(
            self.header_frame,
            text="Universidad Autónoma de Ica - Dashboard de Monitoreo",
            bg=self.color_primario,
            fg="white",
            font=("Helvetica", 24, "bold")
        ).pack(fill=tk.X, pady=20)

        # Botones principales
        button_frame = tk.Frame(self.header_frame, bg=self.color_primario)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Administrar Servicios",
            font=("Helvetica", 14),
            bg=self.color_secundario,
            fg=self.color_texto_botones,
            command=self.abrir_modal_servicios,
            relief="groove",
            borderwidth=1
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame,
            text="Generar Reporte",
            font=("Helvetica", 14),
            bg=self.color_secundario,
            fg=self.color_texto_botones,
            command=self.generar_reporte,
            relief="groove",
            borderwidth=1
        ).grid(row=0, column=1, padx=10)

    def cargar_servicios(self):
        """
        Carga los servicios desde la base de datos y los muestra en el dashboard.
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        servicios = obtener_servicios()
        for idx, servicio in enumerate(servicios):
            self.mostrar_servicio_dashboard(servicio, idx)

    def mostrar_servicio_dashboard(self, servicio, idx):
        """
        Muestra un servicio en el dashboard y lo centra horizontalmente.
        """
        # Crear un marco para el servicio
        servicio_frame = tk.Frame(self.scrollable_frame, bg="white", borderwidth=1, relief="solid")
        servicio_frame.grid(row=idx, column=0, pady=10, sticky="nsew")  # Expandir y centrar en la fila

        # Configurar el ancho del grid para centrar los elementos
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Nombre del servicio
        tk.Label(
            servicio_frame,
            text=servicio["nombre"],
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg=self.color_primario
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Estado del servicio
        estado_color = "#28A745" if servicio["estado"] == "online" else "#DC3545"
        tk.Label(
            servicio_frame,
            text=servicio["estado"].capitalize(),
            font=("Helvetica", 14),
            bg=estado_color,
            fg="white",
            width=10
        ).grid(row=0, column=1, padx=10, pady=10, sticky="e")

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

    def generar_reporte(self):
        """
        Genera un reporte CSV con el estado de los servicios.
        """
        servicios = obtener_servicios()
        archivo = "static/reports/reporte_servicios.csv"

        with open(archivo, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Nombre", "Estado", "URL", "Fecha de Actualización"])
            for servicio in servicios:
                writer.writerow([servicio["id"], servicio["nombre"], servicio["estado"], servicio["url"], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        messagebox.showinfo("Reporte Generado", f"Reporte guardado en {archivo}")

    def abrir_modal_servicios(self):
        """
        Abre una ventana modal para administrar servicios.
        """
        modal = Toplevel(self.root)
        modal.title("Administrar Servicios")
        modal.geometry("600x400")
        modal.configure(bg=self.color_acento)

        tk.Label(
            modal,
            text="Administrar Servicios",
            font=("Helvetica", 16, "bold"),
            bg=self.color_primario,
            fg="white"
        ).pack(fill=tk.X, pady=10)

        servicios = obtener_servicios()

        frame_servicios = tk.Frame(modal, bg=self.color_acento)
        frame_servicios.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for servicio in servicios:
            servicio_frame = tk.Frame(frame_servicios, bg="white", borderwidth=1, relief="solid")
            servicio_frame.pack(fill=tk.X, pady=5)

            tk.Label(
                servicio_frame,
                text=f"Nombre: {servicio['nombre']} | URL: {servicio['url']}",
                font=("Helvetica", 12),
                bg="white",
                fg=self.color_primario,
                anchor="w"
            ).pack(side=tk.LEFT, padx=10, pady=5)

            # Botón de eliminar
            tk.Button(
                servicio_frame,
                text="Eliminar",
                bg=self.color_eliminar,
                fg=self.color_texto_botones,
                command=lambda s=servicio: self.eliminar_servicio(s, servicio_frame),
                font=("Helvetica", 12),
                relief="groove",
                borderwidth=1
            ).pack(side=tk.RIGHT, padx=10)

            # Botón de editar
            tk.Button(
                servicio_frame,
                text="Editar",
                bg=self.color_secundario,
                fg=self.color_texto_botones,
                command=lambda s=servicio: self.editar_servicio(s, modal),
                font=("Helvetica", 12),
                relief="groove",
                borderwidth=1
            ).pack(side=tk.RIGHT)

        tk.Button(
            modal,
            text="Agregar Servicio",
            font=("Helvetica", 14),
            bg=self.color_secundario,
            fg=self.color_texto_botones,
            command=lambda: self.registrar_servicio(modal)
        ).pack(side=tk.BOTTOM, pady=10)

    def editar_servicio(self, servicio, modal):
        """
        Edita un servicio existente.
        """
        nuevo_nombre = simpledialog.askstring("Editar Servicio", f"Nuevo nombre para '{servicio['nombre']}':", parent=modal)
        if not nuevo_nombre:
            return

        nueva_url = simpledialog.askstring("Editar Servicio", f"Nueva URL para '{servicio['nombre']}':", parent=modal)
        if not nueva_url:
            return

        if actualizar_servicio(servicio["id"], nuevo_nombre, nueva_url):
            messagebox.showinfo("Éxito", "El servicio se actualizó correctamente.", parent=modal)
            self.cargar_servicios()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el servicio.", parent=modal)

    def eliminar_servicio(self, servicio, frame):
        """
        Elimina un servicio desde la ventana modal.
        """
        if eliminar_servicio(servicio["id"]):
            messagebox.showinfo("Éxito", "El servicio se eliminó correctamente.")
            frame.destroy()
            self.cargar_servicios()
        else:
            messagebox.showerror("Error", "No se pudo eliminar el servicio.")

    def registrar_servicio(self, modal=None):
        """
        Permite agregar un nuevo servicio.
        """
        nombre = simpledialog.askstring("Registrar Servicio", "Ingrese el nombre del servicio:", parent=modal)
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre.", parent=modal)
            return

        url = simpledialog.askstring("Registrar Servicio", "Ingrese la URL del servicio:", parent=modal)
        if not url:
            messagebox.showwarning("Advertencia", "Debe ingresar una URL.", parent=modal)
            return

        if agregar_servicio(nombre, url):
            messagebox.showinfo("Éxito", f"Servicio '{nombre}' registrado correctamente.", parent=modal)
            self.cargar_servicios()
        else:
            messagebox.showerror("Error", "No se pudo registrar el servicio.", parent=modal)


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()

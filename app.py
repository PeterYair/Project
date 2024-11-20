import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
from utils.db_manager import obtener_servicios, agregar_servicio, registrar_estado, obtener_historial_estado, actualizar_estado_servicio
from monitor import verificar_estado
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import datetime


class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Servicios")
        self.root.configure(bg="#1e1e1e")
        self.root.state('zoomed')

        self.header_frame = tk.Frame(self.root, bg="#333333")
        self.header_frame.pack(fill=tk.X)

        self.graph_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.services_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.services_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.build_ui()

    def build_ui(self):
        tk.Label(self.header_frame, text="Dashboard de Monitoreo", bg="#333333", fg="white",
                 font=("Arial", 20)).pack(fill=tk.X, pady=10)

        tk.Button(self.header_frame, text="Registrar Nuevo Servicio", font=("Arial", 14), bg="#4CAF50", fg="white",
                  command=self.registrar_servicio).pack(pady=5)

        self.load_services()
        self.create_graphs()

    def load_services(self):
        servicios = obtener_servicios()
        for servicio in servicios:
            self.agregar_servicio_dashboard(servicio["id"], servicio["nombre"], servicio["url"], servicio["estado"])

    def agregar_servicio_dashboard(self, servicio_id, nombre, url, estado):
        servicio_frame = tk.Frame(self.services_frame, bg="#2e2e2e", borderwidth=1, relief="solid")
        servicio_frame.pack(fill=tk.X, pady=5, padx=5)

        tk.Label(servicio_frame, text=nombre, font=("Arial", 14), bg="#2e2e2e", fg="white").pack(side=tk.LEFT, padx=10)

        tk.Button(servicio_frame, text="Verificar", font=("Arial", 12), bg="#4CAF50", fg="white",
                  command=lambda: self.verificar_servicio(servicio_id, url, nombre)).pack(side=tk.LEFT)

        color = "green" if estado == "online" else "red"
        canvas = tk.Canvas(servicio_frame, width=20, height=20, bg=color, highlightthickness=0)
        canvas.pack(side=tk.RIGHT, padx=10)

    def verificar_servicio(self, servicio_id, url, nombre):
        """
        Verifica el estado de un servicio y actualiza el dashboard.
        También registra el cambio de estado en la base de datos.
        """
        estado = verificar_estado(servicio_id, url)
        hora_actual = datetime.datetime.now()

        # Actualiza el estado en la base de datos
        if actualizar_estado_servicio(servicio_id, estado):
            registrar_estado(servicio_id, estado, hora_actual)
            messagebox.showinfo("Estado Actualizado", f"El servicio '{nombre}' está ahora: {estado.upper()}")

            # Encuentra el frame del servicio y actualiza su color
            for widget in self.services_frame.winfo_children():
                # Busca el frame correspondiente por el nombre del servicio
                if isinstance(widget, tk.Frame) and widget.winfo_children():
                    label = widget.winfo_children()[0]  # El primer hijo es el label con el nombre
                    if label.cget("text") == nombre:
                        # Cambia el color del indicador basado en el estado
                        canvas = widget.winfo_children()[-1]  # El último hijo es el canvas del indicador
                        canvas.config(bg="green" if estado == "online" else "red")
                        break
        else:
            messagebox.showerror("Error", f"No se pudo actualizar el estado del servicio '{nombre}'.")

        self.refresh_dashboard()  # Actualiza los gráficos

    def registrar_servicio(self):
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
            self.refresh_dashboard()
        else:
            messagebox.showerror("Error", "No se pudo registrar el servicio. Inténtelo nuevamente.")

    def refresh_dashboard(self):
        for widget in self.services_frame.winfo_children():
            widget.destroy()
        self.load_services()
        self.create_graphs()

    def create_graphs(self):
        servicios = obtener_servicios()
        data = pd.DataFrame(servicios)

        if not data.empty:
            estado_counts = data['estado'].value_counts()

            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(estado_counts.index, estado_counts.values, color=['green', 'red'])
            ax.set_facecolor("#2e2e2e")
            ax.tick_params(colors='white')
            ax.set_title("Estado de los Servicios", color="white")
            ax.set_xlabel("Estado", color="white")
            ax.set_ylabel("Cantidad", color="white")

            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_service_graph(self, servicio_id, nombre):
        graph_window = Toplevel(self.root)
        graph_window.title(f"Historial del Servicio: {nombre}")
        graph_window.geometry("800x600")
        graph_window.configure(bg="#1e1e1e")

        historial = obtener_historial_estado(servicio_id)
        data = pd.DataFrame(historial)

        if not data.empty:
            fig = Figure(figsize=(10, 5), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(data['hora'], data['estado'], marker='o', color='blue')
            ax.set_facecolor("#2e2e2e")
            ax.tick_params(colors='white')
            ax.set_title("Historial de Cambios de Estado", color="white")
            ax.set_xlabel("Hora", color="white")
            ax.set_ylabel("Estado", color="white")

            canvas = FigureCanvasTkAgg(fig, graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(graph_window, text="No hay historial disponible.", bg="#1e1e1e", fg="white",
                     font=("Arial", 14)).pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()

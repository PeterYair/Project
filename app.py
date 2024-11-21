import tkinter as tk
from tkinter import simpledialog, messagebox
from utils.db_manager import obtener_servicios, agregar_servicio, registrar_estado, actualizar_estado_servicio, eliminar_servicio
from monitor import verificar_estado
import datetime



class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Servicios")
        self.root.configure(bg="#1e1e1e")
        self.root.state('zoomed')

        self.header_frame = tk.Frame(self.root, bg="#333333")
        self.header_frame.pack(fill=tk.X)

        self.services_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.services_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.build_ui()
        self.actualizar_estado_servicios()

    def build_ui(self):
        tk.Label(self.header_frame, text="Dashboard de Monitoreo", bg="#333333", fg="white",
                 font=("Arial", 20)).pack(fill=tk.X, pady=10)

        button_frame = tk.Frame(self.header_frame, bg="#333333")
        button_frame.pack()

        tk.Button(button_frame, text="Registrar Nuevo Servicio", font=("Arial", 14), bg="#4CAF50", fg="white",
                  command=self.registrar_servicio).pack(side=tk.LEFT, padx=5, pady=5)

        self.load_services()

    def load_services(self):
        servicios = obtener_servicios()
        for servicio in servicios:
            self.agregar_servicio_dashboard(servicio["id"], servicio["nombre"], servicio["url"], servicio["estado"])

    def agregar_servicio_dashboard(self, servicio_id, nombre, url, estado):
        servicio_frame = tk.Frame(self.services_frame, bg="#2e2e2e", borderwidth=1, relief="solid")
        servicio_frame.pack(fill=tk.X, pady=5, padx=5)

        tk.Label(servicio_frame, text=nombre, font=("Arial", 14), bg="#2e2e2e", fg="white").pack(side=tk.LEFT, padx=10)

        color = "green" if estado == "online" else "red"
        canvas = tk.Canvas(servicio_frame, width=20, height=20, bg=color, highlightthickness=0)
        canvas.pack(side=tk.RIGHT, padx=10)

        delete_button = tk.Button(servicio_frame, text="Eliminar", font=("Arial", 10), bg="#f44336", fg="white",
                                  command=lambda: self.eliminar_servicio(servicio_id, servicio_frame))
        delete_button.pack(side=tk.RIGHT, padx=10)

        servicio_frame.canvas = canvas  # Guardar el canvas para actualizarlo más tarde

    def actualizar_estado_servicios(self):
        servicios = obtener_servicios()
        hora_actual = datetime.datetime.now()

        for servicio in servicios:
            estado = verificar_estado(servicio["id"], servicio["url"])

            if actualizar_estado_servicio(servicio["id"], estado):
                for widget in self.services_frame.winfo_children():
                    if isinstance(widget, tk.Frame) and widget.winfo_children():
                        label = widget.winfo_children()[0]
                        if label.cget("text") == servicio["nombre"]:
                            canvas = widget.canvas
                            canvas.config(bg="green" if estado == "online" else "red")
                            break

        self.root.after(60000, self.actualizar_estado_servicios)

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

    def eliminar_servicio(self, servicio_id, servicio_frame):
        if eliminar_servicio(servicio_id):
            messagebox.showinfo("Éxito", "El servicio ha sido eliminado correctamente.")
            servicio_frame.destroy()  # Elimina el frame del servicio de la interfaz
        else:
            messagebox.showerror("Error", "No se pudo eliminar el servicio. Verifique que exista.")

    def refresh_dashboard(self):
        for widget in self.services_frame.winfo_children():
            widget.destroy()
        self.load_services()


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()

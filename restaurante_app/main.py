# main.py
# Punto de entrada de la aplicacion grafica del restaurante.
# Crea una unica ventana principal de Tkinter, prepara los servicios
# (ArchivoServicio y Restaurante), entrega esas dependencias a las
# vistas y controla el cambio entre la pantalla de acceso (LoginView)
# y la interfaz principal (MainView) dentro de la misma ventana.

import tkinter as tk
from pathlib import Path

from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante import Restaurante
from ui.login_view import LoginView
from ui.main_view import MainView


class AplicacionRestaurante:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Restaurante - Tkinter")
        self.root.geometry("920x560")
        self.root.minsize(780, 500)
        self.icono_app = None

        # Prepara los servicios que usaran las vistas.
        ruta_base = Path(__file__).resolve().parent
        self.configurar_icono_ventana(ruta_base)
        archivo_servicio = ArchivoServicio(ruta_base / "datos")
        self.restaurante = Restaurante(archivo_servicio)

        self.vista_actual = None
        self.mostrar_login()

    def configurar_icono_ventana(self, ruta_base) -> None:
        # Usa un PNG pequeno como icono de la ventana. Si no existe,
        # la ventana simplemente usa el icono por defecto del sistema.
        ruta_icono = ruta_base / "assets" / "logo" / "icono.png"
        if not ruta_icono.exists():
            return

        try:
            self.icono_app = tk.PhotoImage(file=str(ruta_icono))
            self.root.iconphoto(True, self.icono_app)
        except tk.TclError:
            pass

    def cambiar_vista(self, nueva_vista) -> None:
        # Reemplaza la vista actual dentro de la misma ventana.
        if self.vista_actual is not None:
            self.vista_actual.destroy()

        self.vista_actual = nueva_vista
        self.vista_actual.pack(fill="both", expand=True)

    def mostrar_login(self) -> None:
        # Muestra la primera pantalla de la aplicacion.
        vista = LoginView(
            self.root,
            self.restaurante,
            self.mostrar_interfaz_principal,
        )
        self.cambiar_vista(vista)

    def mostrar_interfaz_principal(self, usuario_actual) -> None:
        # Abre la interfaz principal despues de un acceso correcto.
        vista = MainView(
            self.root,
            self.restaurante,
            usuario_actual,
            self.mostrar_login,
        )
        self.cambiar_vista(vista)

    def ejecutar(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = AplicacionRestaurante()
    app.ejecutar()
# ui/login_view.py
# Pantalla de acceso simulada. Solo pide usuario y contrasena, delega
# la validacion a Restaurante y nunca lee JSON directamente. El logo
# es opcional: si no existe assets/logo/logo.png, la vista funciona
# igual sin mostrarlo.

import tkinter as tk
from pathlib import Path
from tkinter import ttk


class LoginView(tk.Frame):
    def __init__(self, master, restaurante_servicio, al_iniciar_sesion):
        super().__init__(master, bg="#fff5f9")
        self.restaurante_servicio = restaurante_servicio
        self.al_iniciar_sesion = al_iniciar_sesion

        self.usuario_entry = None
        self.contrasena_entry = None
        self.mensaje_error = None
        self.logo = None

        self.definir_estilos()
        self.construir_interfaz()

    def definir_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Login.TButton",
            background="#EF007E",
            foreground="#ffffff",
            font=("Arial", 11, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        estilo.map("Login.TButton", background=[("active", "#c2005f")])

    def cargar_logo(self):
        # Carga el logo desde assets/logo/logo.png usando una ruta
        # relativa al proyecto. Si no existe, se continua sin logo.
        ruta_base = Path(__file__).resolve().parent.parent
        ruta_logo = ruta_base / "assets" / "logo" / "logo.png"

        if not ruta_logo.exists():
            return None

        try:
            self.logo = tk.PhotoImage(file=str(ruta_logo))
        except tk.TclError:
            return None

        return self.logo

    def construir_interfaz(self):
        contenedor = tk.Frame(self, bg="#ffffff", padx=32, pady=28)
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        logo = self.cargar_logo()
        if logo is not None:
            tk.Label(contenedor, image=logo, bg="#ffffff").pack(pady=(0, 12))

        tk.Label(
            contenedor, text="Restaurante", bg="#ffffff", fg="#000000",
            font=("Arial", 22, "bold"),
        ).pack(pady=(0, 6))

        tk.Label(
            contenedor, text="Inicio de sesión", bg="#ffffff", fg="#4a4a4a",
            font=("Arial", 11),
        ).pack(pady=(0, 22))

        tk.Label(
            contenedor, text="Usuario", bg="#ffffff", fg="#1a1a1a",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")

        self.usuario_entry = tk.Entry(contenedor, width=30, font=("Arial", 11))
        self.usuario_entry.pack(pady=(4, 14), ipady=4)
        self.usuario_entry.focus()

        tk.Label(
            contenedor, text="Contraseña", bg="#ffffff", fg="#1a1a1a",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")

        self.contrasena_entry = tk.Entry(contenedor, width=30, font=("Arial", 11), show="*")
        self.contrasena_entry.pack(pady=(4, 14), ipady=4)
        self.contrasena_entry.bind("<Return>", lambda evento: self.iniciar_sesion())

        self.mensaje_error = tk.Label(
            contenedor, text="", bg="#ffffff", fg="#c2005f", font=("Arial", 10),
        )
        self.mensaje_error.pack(pady=(0, 14))

        ttk.Button(
            contenedor, text="Iniciar sesión", command=self.iniciar_sesion, style="Login.TButton",
        ).pack(fill="x")

    def iniciar_sesion(self):
        assert self.usuario_entry is not None
        assert self.contrasena_entry is not None
        assert self.mensaje_error is not None

        usuario = self.usuario_entry.get().strip()
        contrasena = self.contrasena_entry.get().strip()

        if not usuario or not contrasena:
            self.mensaje_error.config(text="Ingrese usuario y contraseña.")
            return

        usuario_validado = self.restaurante_servicio.validar_acceso(usuario, contrasena)

        if usuario_validado is None:
            self.mensaje_error.config(text="Credenciales incorrectas.")
            return

        self.mensaje_error.config(text="")
        self.al_iniciar_sesion(usuario_validado)
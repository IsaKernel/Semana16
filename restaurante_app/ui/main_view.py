# ui/main_view.py
# Panel principal con navegacion lateral (sidebar) y area de contenido.
# Las vistas nunca leen ni escriben productos.json/usuarios.json
# directamente: siempre piden la operacion a self.restaurante_servicio.
# Semana 16: la seccion Usuarios aplica manejo de eventos
# (<<TreeviewSelect>>, <Return>, <Escape>, <<ComboboxSelected>>).

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


class MainView(tk.Frame):
    ROLES_FORMULARIO = ("Empleado", "Cliente")

    def __init__(self, master, restaurante_servicio, usuario_actual, al_cerrar_sesion):
        super().__init__(master, bg="#fff5f9")
        self.restaurante_servicio = restaurante_servicio
        self.usuario_actual = usuario_actual
        self.al_cerrar_sesion = al_cerrar_sesion

        self.contenido = None
        self.etiqueta_estado = None
        self.botones_menu = {}
        self.iconos = {}

        # Formulario de productos.
        self.producto_codigo_entry = None
        self.producto_nombre_entry = None
        self.producto_categoria_entry = None
        self.producto_precio_entry = None
        self.producto_stock_entry = None
        self.tabla_productos = None

        # Formulario de usuarios (Semana 16).
        self.usuario_identificacion_entry = None
        self.usuario_nombre_entry = None
        self.usuario_correo_entry = None
        self.usuario_celular_entry = None
        self.usuario_login_entry = None
        self.usuario_contrasena_entry = None
        self.usuario_rol_combo = None
        self.usuario_rol_estado = None
        self.usuario_seleccionado = None  # identificacion del usuario cargado
        self.tabla_usuarios = None

        # Ventas.
        self.venta_usuario_combo = None
        self.venta_producto_combo = None
        self.tabla_ventas = None

        self.definir_estilos()
        self.construir_interfaz()

    # -------------------------------------------------------------------------
    # Configuracion general: colores, estilos e iconos.
    # -------------------------------------------------------------------------
    def definir_estilos(self):
        self.color_fondo = "#fff5f9"
        self.color_panel = "#ffffff"
        self.color_encabezado = "#000000"
        self.color_texto = "#1a1a1a"
        self.color_secundario = "#ffd9e8"
        self.color_resaltado = "#EF007E"

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "MenuApp.TButton", background="#1a1a1a", foreground="#ffffff",
            font=("Arial", 10, "bold"), padding=(12, 10), borderwidth=0, anchor="w",
        )
        estilo.map("MenuApp.TButton", background=[("active", "#333333")])
        estilo.configure(
            "MenuActivo.TButton", background=self.color_resaltado, foreground="#ffffff",
            font=("Arial", 10, "bold"), padding=(12, 10), borderwidth=0, anchor="w",
        )
        estilo.map("MenuActivo.TButton", background=[("active", "#c2005f")])
        estilo.configure(
            "Secundario.TButton", background="#1a1a1a", foreground="#ffffff",
            font=("Arial", 10, "bold"), padding=(10, 7), borderwidth=0,
        )
        estilo.map("Secundario.TButton", background=[("active", "#333333")])
        estilo.configure(
            "Accion.TButton", background=self.color_resaltado, foreground="#ffffff",
            font=("Arial", 10, "bold"), padding=(10, 7), borderwidth=0,
        )
        estilo.map("Accion.TButton", background=[("active", "#c2005f")])
        estilo.configure(
            "Eliminar.TButton", background="#8f0047", foreground="#ffffff",
            font=("Arial", 10, "bold"), padding=(10, 7), borderwidth=0,
        )
        estilo.map("Eliminar.TButton", background=[("active", "#6e0037")])
        estilo.configure(
            "Treeview.Heading", background=self.color_secundario,
            foreground=self.color_encabezado, font=("Arial", 10, "bold"),
        )

    def cargar_icono(self, nombre_archivo):
        ruta_base = Path(__file__).resolve().parent.parent
        ruta_icono = ruta_base / "assets" / "icons" / nombre_archivo

        if not ruta_icono.exists():
            return None

        icono = tk.PhotoImage(file=str(ruta_icono))
        self.iconos[nombre_archivo] = icono
        return icono

    def crear_boton(self, contenedor, texto, comando, estilo, icono=None):
        imagen = self.cargar_icono(icono) if icono else None

        if imagen is not None:
            boton = ttk.Button(
                contenedor, text=texto, command=comando, style=estilo,
                image=imagen, compound="left",
            )
        else:
            boton = ttk.Button(contenedor, text=texto, command=comando, style=estilo)

        return boton

    # -------------------------------------------------------------------------
    # Estructura principal: sidebar (navegacion) + area de contenido.
    # -------------------------------------------------------------------------
    def construir_interfaz(self):
        frame_sidebar = tk.Frame(self, bg=self.color_encabezado, width=190, padx=16, pady=18)
        frame_sidebar.pack(side="left", fill="y")
        frame_sidebar.pack_propagate(False)

        tk.Label(
            frame_sidebar, text="RESTAURANTE", bg=self.color_encabezado,
            fg="#ffffff", font=("Arial", 16, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            frame_sidebar, text=f"{self.usuario_actual.nombre}\n({self.usuario_actual.rol})",
            bg=self.color_encabezado, fg="#f2b8d4", font=("Arial", 10),
            wraplength=150, justify="left",
        ).pack(anchor="w", pady=(0, 24))

        self.crear_boton_menu(frame_sidebar, "Inicio", self.mostrar_inicio, "home.png")
        # Semana 16: solo el Administrador ve la gestion de usuarios.
        if self.usuario_actual.rol == "Administrador":
            self.crear_boton_menu(frame_sidebar, "Usuarios", self.mostrar_usuarios, "users.png")
        self.crear_boton_menu(frame_sidebar, "Productos", self.mostrar_productos, "productos.png")
        self.crear_boton_menu(frame_sidebar, "Ventas", self.mostrar_ventas, "sales.png")

        tk.Frame(frame_sidebar, bg=self.color_encabezado).pack(fill="both", expand=True)

        self.crear_boton(
            frame_sidebar, "Cerrar sesión", self.cerrar_sesion, "Eliminar.TButton", "logout.png",
        ).pack(fill="x", pady=(16, 0))

        frame_principal = tk.Frame(self, bg=self.color_fondo)
        frame_principal.pack(side="left", fill="both", expand=True)

        self.contenido = tk.Frame(frame_principal, bg=self.color_fondo, padx=28, pady=24)
        self.contenido.pack(fill="both", expand=True)

        barra_estado = tk.Frame(frame_principal, bg=self.color_secundario, padx=18, pady=8)
        barra_estado.pack(fill="x", side="bottom")

        self.etiqueta_estado = tk.Label(
            barra_estado, bg=self.color_secundario, fg=self.color_texto, font=("Arial", 10),
        )
        self.etiqueta_estado.pack(side="left")

        self.mostrar_inicio()

    def crear_boton_menu(self, contenedor, texto, comando, icono):
        boton = self.crear_boton(contenedor, texto, comando, "MenuApp.TButton", icono)
        boton.pack(fill="x", pady=(0, 8))
        self.botones_menu[texto] = boton

    def marcar_seccion(self, seccion):
        for texto, boton in self.botones_menu.items():
            estilo = "MenuActivo.TButton" if texto == seccion else "MenuApp.TButton"
            boton.configure(style=estilo)

    def limpiar_contenido(self):
        assert self.contenido is not None
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def actualizar_barra_estado(self):
        assert self.etiqueta_estado is not None
        self.etiqueta_estado.config(
            text=(
                f"Productos: {self.restaurante_servicio.cantidad_productos()} | "
                f"Usuarios: {self.restaurante_servicio.cantidad_usuarios()} | "
                f"Ventas: {self.restaurante_servicio.cantidad_ventas()} | "
                "Datos JSON locales"
            )
        )

    # -------------------------------------------------------------------------
    # Inicio.
    # -------------------------------------------------------------------------
    def mostrar_inicio(self):
        self.marcar_seccion("Inicio")
        self.limpiar_contenido()
        self.actualizar_barra_estado()

        assert self.contenido is not None

        tk.Label(
            self.contenido, text="Panel principal", bg=self.color_fondo,
            fg=self.color_encabezado, font=("Arial", 20, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            self.contenido,
            text="Gestione usuarios y productos y registre ventas desde el menú lateral.",
            bg=self.color_fondo, fg=self.color_texto, font=("Arial", 12),
        ).pack(anchor="w", pady=(0, 22))

        resumen = tk.Frame(self.contenido, bg=self.color_fondo)
        resumen.pack(fill="x")
        self.crear_tarjeta_resumen(resumen, "Usuarios registrados", self.restaurante_servicio.cantidad_usuarios())
        self.crear_tarjeta_resumen(resumen, "Productos registrados", self.restaurante_servicio.cantidad_productos())
        self.crear_tarjeta_resumen(resumen, "Ventas registradas", self.restaurante_servicio.cantidad_ventas())

    def crear_tarjeta_resumen(self, contenedor, titulo, valor):
        tarjeta = tk.Frame(contenedor, bg=self.color_panel, padx=18, pady=16)
        tarjeta.pack(side="left", fill="x", expand=True, padx=(0, 14))

        tk.Label(
            tarjeta, text=titulo, bg=self.color_panel, fg=self.color_texto,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")
        tk.Label(
            tarjeta, text=str(valor), bg=self.color_panel, fg=self.color_resaltado,
            font=("Arial", 24, "bold"),
        ).pack(anchor="w", pady=(8, 0))

    # -------------------------------------------------------------------------
    # Usuarios (Semana 16): CRUD + manejo de eventos.
    #   command= -> botones (accion directa de un clic)
    #   bind()   -> eventos de tabla, teclado y combobox
    # -------------------------------------------------------------------------
    def mostrar_usuarios(self):
        # Doble control: el menu ya oculta el boton, pero se valida el rol igual.
        if self.usuario_actual.rol != "Administrador":
            messagebox.showerror("Usuarios", "Solo el administrador puede acceder a esta sección.")
            return

        self.marcar_seccion("Usuarios")
        self.limpiar_contenido()
        self.usuario_seleccionado = None

        assert self.contenido is not None

        self.crear_titulo_seccion("Gestión de usuarios")

        cuerpo = tk.Frame(self.contenido, bg=self.color_fondo)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        formulario = tk.LabelFrame(
            cuerpo, text="Datos del usuario", bg=self.color_panel, fg=self.color_encabezado,
            font=("Arial", 10, "bold"), padx=14, pady=10,
        )
        formulario.grid(row=0, column=0, sticky="n", padx=(0, 18))

        self.usuario_identificacion_entry = self.crear_campo(formulario, "Identificación", 0)
        self.usuario_nombre_entry = self.crear_campo(formulario, "Nombre", 1)
        self.usuario_correo_entry = self.crear_campo(formulario, "Correo", 2)
        self.usuario_celular_entry = self.crear_campo(formulario, "Celular", 3)
        self.usuario_login_entry = self.crear_campo(formulario, "Usuario", 4)
        self.usuario_contrasena_entry = self.crear_campo(formulario, "Contraseña", 5, show="*")

        tk.Label(
            formulario, text="Rol", bg=self.color_panel, fg=self.color_texto,
            font=("Arial", 10, "bold"),
        ).grid(row=6, column=0, sticky="w", pady=(0, 8), padx=(0, 10))

        self.usuario_rol_combo = ttk.Combobox(
            formulario, values=self.ROLES_FORMULARIO, state="readonly", width=24,
            font=("Arial", 10),
        )
        self.usuario_rol_combo.grid(row=6, column=1, sticky="ew", pady=(0, 8))
        self.usuario_rol_combo.set("Cliente")

        self.usuario_rol_estado = tk.Label(
            formulario, text="Rol seleccionado: Cliente", bg=self.color_panel,
            fg=self.color_texto, font=("Arial", 9),
        )
        self.usuario_rol_estado.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 4))

        tk.Label(
            formulario, text="Al actualizar, deje la contraseña vacía para conservar la actual.",
            bg=self.color_panel, fg="#666666", font=("Arial", 8), wraplength=290, justify="left",
        ).grid(row=8, column=0, columnspan=2, sticky="w")

        acciones = tk.Frame(formulario, bg=self.color_panel)
        acciones.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        acciones.grid_columnconfigure(0, weight=1)
        acciones.grid_columnconfigure(1, weight=1)

        # command=: cada boton ejecuta su callback directamente al hacer clic.
        botones = (
            ("Registrar", self.registrar_usuario, "Accion.TButton", "add.png", 0, 0),
            ("Actualizar", self.actualizar_usuario, "Accion.TButton", "edit.png", 0, 1),
            ("Eliminar", self.eliminar_usuario, "Eliminar.TButton", "delete.png", 1, 0),
            ("Limpiar", self.limpiar_formulario_usuario, "Secundario.TButton", "clean.png", 1, 1),
        )
        for texto, comando, estilo, icono, fila, columna in botones:
            self.crear_boton(acciones, texto, comando, estilo, icono).grid(
                row=fila, column=columna, sticky="ew", padx=3, pady=3,
            )

        listado = self.crear_listado(cuerpo, "Usuarios registrados", usar_grid=True)
        # La tabla NO muestra contrasena ni datos sensibles.
        self.tabla_usuarios = self.crear_tabla(
            listado,
            ("identificacion", "nombre", "usuario", "rol"),
            ("Identificación", "Nombre", "Usuario", "Rol"),
        )

        # bind(): conecta eventos con callbacks que reciben el objeto 'event'.
        # Seleccionar una fila de la tabla carga el usuario en el formulario.
        self.tabla_usuarios.bind("<<TreeviewSelect>>", self.al_seleccionar_usuario)
        # Cambiar la opcion del Combobox actualiza el texto del rol.
        self.usuario_rol_combo.bind("<<ComboboxSelected>>", self.al_seleccionar_rol)

        # Enter en cualquier campo del formulario confirma el registro.
        # Escape en el formulario o en la tabla limpia todo.
        campos_formulario = (
            self.usuario_identificacion_entry,
            self.usuario_nombre_entry,
            self.usuario_correo_entry,
            self.usuario_celular_entry,
            self.usuario_login_entry,
            self.usuario_contrasena_entry,
            self.usuario_rol_combo,
        )
        for widget in campos_formulario:
            widget.bind("<Return>", self.al_presionar_enter)
            widget.bind("<Escape>", self.al_presionar_escape)
        self.tabla_usuarios.bind("<Escape>", self.al_presionar_escape)

        self.refrescar_usuarios()
        self.usuario_identificacion_entry.focus()

    def obtener_datos_usuario(self):
        assert self.usuario_identificacion_entry is not None
        assert self.usuario_nombre_entry is not None
        assert self.usuario_correo_entry is not None
        assert self.usuario_celular_entry is not None
        assert self.usuario_login_entry is not None
        assert self.usuario_contrasena_entry is not None
        assert self.usuario_rol_combo is not None

        return (
            self.usuario_identificacion_entry.get(),
            self.usuario_nombre_entry.get(),
            self.usuario_correo_entry.get(),
            self.usuario_celular_entry.get(),
            self.usuario_login_entry.get(),
            self.usuario_contrasena_entry.get(),
            self.usuario_rol_combo.get(),
        )

    # ---- Callbacks de botones (command=) ----
    def registrar_usuario(self):
        try:
            self.restaurante_servicio.registrar_usuario(*self.obtener_datos_usuario())
            self.limpiar_formulario_usuario()
            self.refrescar_usuarios()
            messagebox.showinfo("Usuarios", "Usuario registrado correctamente.")
        except ValueError as error:
            messagebox.showerror("Usuarios", str(error))

    def actualizar_usuario(self):
        if self.usuario_seleccionado is None:
            messagebox.showerror("Usuarios", "Seleccione un usuario de la tabla.")
            return

        datos = self.obtener_datos_usuario()
        if datos[0].strip() != self.usuario_seleccionado:
            messagebox.showerror("Usuarios", "No cambie la identificación del usuario seleccionado.")
            return

        try:
            self.restaurante_servicio.actualizar_usuario(*datos)
            self.limpiar_formulario_usuario()
            self.refrescar_usuarios()
            messagebox.showinfo("Usuarios", "Usuario actualizado correctamente.")
        except ValueError as error:
            messagebox.showerror("Usuarios", str(error))

    def eliminar_usuario(self):
        if self.usuario_seleccionado is None:
            messagebox.showerror("Usuarios", "Seleccione un usuario de la tabla.")
            return

        if not messagebox.askyesno("Usuarios", "¿Desea eliminar el usuario seleccionado?"):
            return

        try:
            self.restaurante_servicio.eliminar_usuario(
                self.usuario_seleccionado,
                self.usuario_actual.identificacion,
            )
            self.limpiar_formulario_usuario()
            self.refrescar_usuarios()
            messagebox.showinfo("Usuarios", "Usuario eliminado correctamente.")
        except ValueError as error:
            messagebox.showerror("Usuarios", str(error))

    # ---- Callbacks de eventos (bind()) ----
    def al_seleccionar_usuario(self, event):
        # <<TreeviewSelect>>: toma el identificador de la fila, consulta el
        # objeto en el servicio y lo carga en el formulario.
        assert self.tabla_usuarios is not None

        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            return

        valores = self.tabla_usuarios.item(seleccion[0], "values")
        if not valores:
            return

        usuario = self.restaurante_servicio.buscar_usuario_por_identificacion(str(valores[0]))
        if usuario is None:
            return

        self.cargar_usuario_en_formulario(usuario)

    def al_presionar_enter(self, event):
        # <Return>: reutiliza el mismo metodo del boton Registrar.
        self.registrar_usuario()

    def al_presionar_escape(self, event):
        # <Escape>: reutiliza el mismo metodo del boton Limpiar.
        self.limpiar_formulario_usuario()

    def al_seleccionar_rol(self, event):
        # <<ComboboxSelected>>: responde al cambio de rol.
        assert self.usuario_rol_combo is not None
        self.actualizar_texto_rol(self.usuario_rol_combo.get())

    # ---- Apoyo del formulario ----
    def cargar_usuario_en_formulario(self, usuario):
        assert self.usuario_identificacion_entry is not None
        assert self.usuario_nombre_entry is not None
        assert self.usuario_correo_entry is not None
        assert self.usuario_celular_entry is not None
        assert self.usuario_login_entry is not None
        assert self.usuario_rol_combo is not None

        self.limpiar_campos_usuario()
        self.usuario_seleccionado = usuario.identificacion
        self.usuario_identificacion_entry.insert(0, usuario.identificacion)
        self.usuario_nombre_entry.insert(0, usuario.nombre)
        self.usuario_correo_entry.insert(0, usuario.correo)
        self.usuario_celular_entry.insert(0, usuario.celular)
        self.usuario_login_entry.insert(0, usuario.usuario)
        # La contraseña no se carga: vacia significa "conservar la actual".

        if usuario.rol == "Administrador":
            # El rol de un administrador no se modifica desde esta pantalla.
            self.usuario_rol_combo.configure(values=("Administrador",), state="disabled")
        else:
            self.usuario_rol_combo.configure(values=self.ROLES_FORMULARIO, state="readonly")
        self.usuario_rol_combo.set(usuario.rol)
        self.actualizar_texto_rol(usuario.rol)

    def limpiar_campos_usuario(self):
        for entrada in (
            self.usuario_identificacion_entry,
            self.usuario_nombre_entry,
            self.usuario_correo_entry,
            self.usuario_celular_entry,
            self.usuario_login_entry,
            self.usuario_contrasena_entry,
        ):
            assert entrada is not None
            entrada.delete(0, tk.END)

    def limpiar_formulario_usuario(self):
        assert self.usuario_identificacion_entry is not None
        assert self.usuario_rol_combo is not None

        self.limpiar_campos_usuario()
        self.usuario_seleccionado = None
        self.usuario_rol_combo.configure(values=self.ROLES_FORMULARIO, state="readonly")
        self.usuario_rol_combo.set("Cliente")
        self.actualizar_texto_rol("Cliente")

        if self.tabla_usuarios is not None:
            self.tabla_usuarios.selection_remove(self.tabla_usuarios.selection())

        self.usuario_identificacion_entry.focus()

    def actualizar_texto_rol(self, rol):
        if self.usuario_rol_estado is not None:
            self.usuario_rol_estado.config(text=f"Rol seleccionado: {rol}")

    def refrescar_usuarios(self):
        assert self.tabla_usuarios is not None

        self.limpiar_tabla(self.tabla_usuarios)
        for usuario in self.restaurante_servicio.listar_usuarios():
            self.tabla_usuarios.insert(
                "", tk.END,
                values=(usuario.identificacion, usuario.nombre, usuario.usuario, usuario.rol),
            )
        self.actualizar_barra_estado()

    # -------------------------------------------------------------------------
    # Productos.
    # -------------------------------------------------------------------------
    def mostrar_productos(self):
        self.marcar_seccion("Productos")
        self.limpiar_contenido()

        assert self.contenido is not None

        self.crear_titulo_seccion("Gestión de productos")

        cuerpo = tk.Frame(self.contenido, bg=self.color_fondo)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        formulario = tk.LabelFrame(
            cuerpo, text="Datos del producto", bg=self.color_panel, fg=self.color_encabezado,
            font=("Arial", 10, "bold"), padx=14, pady=14,
        )
        formulario.grid(row=0, column=0, sticky="n", padx=(0, 18))

        self.producto_codigo_entry = self.crear_campo(formulario, "Código", 0)
        self.producto_nombre_entry = self.crear_campo(formulario, "Nombre", 1)
        self.producto_categoria_entry = self.crear_campo(formulario, "Categoría", 2)
        self.producto_precio_entry = self.crear_campo(formulario, "Precio", 3)
        self.producto_stock_entry = self.crear_campo(formulario, "Stock", 4)

        acciones = tk.Frame(formulario, bg=self.color_panel)
        acciones.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        botones = (
            ("Registrar", self.registrar_producto, "Accion.TButton", "add.png"),
            ("Cargar por código", self.cargar_producto_en_formulario, "Secundario.TButton", "search.png"),
            ("Actualizar", self.actualizar_producto, "Accion.TButton", "edit.png"),
            ("Eliminar", self.eliminar_producto, "Eliminar.TButton", "delete.png"),
            ("Limpiar", self.limpiar_formulario_producto, "Secundario.TButton", "clean.png"),
        )

        for texto, comando, estilo, icono in botones:
            self.crear_boton(acciones, texto, comando, estilo, icono).pack(fill="x", pady=(0, 7))

        listado = self.crear_listado(cuerpo, "Productos registrados", usar_grid=True)
        self.tabla_productos = self.crear_tabla(
            listado,
            ("codigo", "nombre", "categoria", "precio", "stock"),
            ("Código", "Nombre", "Categoría", "Precio", "Stock"),
        )
        self.refrescar_productos()

    def obtener_datos_producto(self):
        assert self.producto_codigo_entry is not None
        assert self.producto_nombre_entry is not None
        assert self.producto_categoria_entry is not None
        assert self.producto_precio_entry is not None
        assert self.producto_stock_entry is not None

        return (
            self.producto_codigo_entry.get(),
            self.producto_nombre_entry.get(),
            self.producto_categoria_entry.get(),
            self.producto_precio_entry.get(),
            self.producto_stock_entry.get(),
        )

    def registrar_producto(self):
        try:
            self.restaurante_servicio.registrar_producto(*self.obtener_datos_producto())
            self.limpiar_formulario_producto()
            self.refrescar_productos()
            messagebox.showinfo("Productos", "Producto registrado correctamente.")
        except ValueError as error:
            messagebox.showerror("Productos", str(error))

    def cargar_producto_en_formulario(self):
        assert self.producto_codigo_entry is not None
        assert self.producto_nombre_entry is not None
        assert self.producto_categoria_entry is not None
        assert self.producto_precio_entry is not None
        assert self.producto_stock_entry is not None

        producto = self.restaurante_servicio.buscar_producto_por_codigo(self.producto_codigo_entry.get())
        if producto is None:
            messagebox.showerror("Productos", "No existe un producto con ese código.")
            return

        codigo_buscado = self.producto_codigo_entry.get()
        self.limpiar_formulario_producto()
        self.producto_codigo_entry.insert(0, codigo_buscado.strip())
        self.producto_nombre_entry.insert(0, producto.nombre)
        self.producto_categoria_entry.insert(0, producto.categoria)
        self.producto_precio_entry.insert(0, str(producto.precio))
        self.producto_stock_entry.insert(0, str(producto.stock))

    def actualizar_producto(self):
        try:
            codigo, nombre, categoria, precio, stock = self.obtener_datos_producto()
            self.restaurante_servicio.actualizar_producto(codigo, nombre, categoria, precio, stock)
            self.refrescar_productos()
            messagebox.showinfo("Productos", "Producto actualizado correctamente.")
        except ValueError as error:
            messagebox.showerror("Productos", str(error))

    def eliminar_producto(self):
        assert self.producto_codigo_entry is not None

        try:
            self.restaurante_servicio.eliminar_producto(self.producto_codigo_entry.get())
            self.limpiar_formulario_producto()
            self.refrescar_productos()
            messagebox.showinfo("Productos", "Producto eliminado correctamente.")
        except ValueError as error:
            messagebox.showerror("Productos", str(error))

    def limpiar_formulario_producto(self):
        entradas = (
            self.producto_codigo_entry, self.producto_nombre_entry,
            self.producto_categoria_entry, self.producto_precio_entry,
            self.producto_stock_entry,
        )
        for entrada in entradas:
            assert entrada is not None
            entrada.delete(0, tk.END)

    def refrescar_productos(self):
        assert self.tabla_productos is not None

        self.limpiar_tabla(self.tabla_productos)
        for producto in self.restaurante_servicio.listar_productos():
            self.tabla_productos.insert(
                "", tk.END,
                values=(
                    producto.codigo, producto.nombre, producto.categoria,
                    f"{producto.precio:.2f}", producto.stock,
                ),
            )
        self.actualizar_barra_estado()

    # -------------------------------------------------------------------------
    # Ventas (command= + callback).
    # -------------------------------------------------------------------------
    def mostrar_ventas(self):
        self.marcar_seccion("Ventas")
        self.limpiar_contenido()

        assert self.contenido is not None

        self.crear_titulo_seccion("Registro de ventas")

        cuerpo = tk.Frame(self.contenido, bg=self.color_fondo)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        formulario = tk.LabelFrame(
            cuerpo, text="Nueva venta", bg=self.color_panel, fg=self.color_encabezado,
            font=("Arial", 10, "bold"), padx=14, pady=14,
        )
        formulario.grid(row=0, column=0, sticky="n", padx=(0, 18))

        self.venta_usuario_combo = self.crear_combo(
            formulario, "Usuario", 0, self.obtener_opciones_usuarios(),
        )
        self.venta_producto_combo = self.crear_combo(
            formulario, "Producto", 1, self.obtener_opciones_productos(),
        )

        acciones = tk.Frame(formulario, bg=self.color_panel)
        acciones.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.crear_boton(
            acciones, "Registrar venta", self.registrar_venta, "Accion.TButton", "add.png",
        ).pack(fill="x", pady=(0, 7))

        listado = self.crear_listado(cuerpo, "Ventas registradas", usar_grid=True)
        self.tabla_ventas = self.crear_tabla(
            listado,
            ("identificador", "usuario", "producto", "fecha"),
            ("N°", "Usuario", "Producto", "Fecha"),
        )
        self.refrescar_ventas()

    def obtener_opciones_usuarios(self):
        return [
            f"{usuario.identificacion} - {usuario.nombre}"
            for usuario in self.restaurante_servicio.listar_usuarios()
        ]

    def obtener_opciones_productos(self):
        return [
            f"{producto.codigo} - {producto.nombre}"
            for producto in self.restaurante_servicio.listar_productos()
        ]

    def registrar_venta(self):
        assert self.venta_usuario_combo is not None
        assert self.venta_producto_combo is not None

        seleccion_usuario = self.venta_usuario_combo.get()
        seleccion_producto = self.venta_producto_combo.get()

        if not seleccion_usuario or not seleccion_producto:
            messagebox.showerror("Ventas", "Seleccione un usuario y un producto.")
            return

        usuario_identificacion = seleccion_usuario.split(" - ")[0]
        producto_codigo = seleccion_producto.split(" - ")[0]

        try:
            self.restaurante_servicio.registrar_venta(usuario_identificacion, producto_codigo)
            self.refrescar_ventas()
            messagebox.showinfo("Ventas", "Venta registrada correctamente.")
        except ValueError as error:
            messagebox.showerror("Ventas", str(error))

    def refrescar_ventas(self):
        assert self.tabla_ventas is not None

        self.limpiar_tabla(self.tabla_ventas)
        for venta in self.restaurante_servicio.listar_ventas():
            self.tabla_ventas.insert(
                "", tk.END,
                values=(venta.identificador, venta.usuario_identificacion, venta.producto_codigo, venta.fecha),
            )
        self.actualizar_barra_estado()

    # -------------------------------------------------------------------------
    # Utilidades de interfaz compartidas por las vistas.
    # -------------------------------------------------------------------------
    def crear_titulo_seccion(self, texto):
        assert self.contenido is not None
        tk.Label(
            self.contenido, text=texto, bg=self.color_fondo, fg=self.color_encabezado,
            font=("Arial", 20, "bold"),
        ).pack(anchor="w", pady=(0, 16))

    def crear_campo(self, contenedor, etiqueta, fila, show=None):
        tk.Label(
            contenedor, text=etiqueta, bg=self.color_panel, fg=self.color_texto,
            font=("Arial", 10, "bold"),
        ).grid(row=fila, column=0, sticky="w", pady=(0, 8), padx=(0, 10))

        entrada = tk.Entry(contenedor, width=26, font=("Arial", 10), show=show)
        entrada.grid(row=fila, column=1, sticky="ew", pady=(0, 8))
        return entrada

    def crear_combo(self, contenedor, etiqueta, fila, opciones):
        tk.Label(
            contenedor, text=etiqueta, bg=self.color_panel, fg=self.color_texto,
            font=("Arial", 10, "bold"),
        ).grid(row=fila, column=0, sticky="w", pady=(0, 8), padx=(0, 10))

        combo = ttk.Combobox(
            contenedor, width=24, font=("Arial", 10), state="readonly", values=opciones,
        )
        if opciones:
            combo.current(0)
        combo.grid(row=fila, column=1, sticky="ew", pady=(0, 8))
        return combo

    def crear_listado(self, contenedor, titulo, usar_grid=False):
        listado = tk.LabelFrame(
            contenedor, text=titulo, bg=self.color_panel, fg=self.color_encabezado,
            font=("Arial", 10, "bold"), padx=12, pady=12,
        )

        if usar_grid:
            listado.grid(row=0, column=1, sticky="nsew")
        else:
            listado.pack(fill="both", expand=True)

        return listado

    def crear_tabla(self, contenedor, columnas, encabezados):
        frame_tabla = tk.Frame(contenedor, bg=self.color_panel)
        frame_tabla.pack(fill="both", expand=True)

        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)
        barra = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)

        for columna, encabezado in zip(columnas, encabezados):
            tabla.heading(columna, text=encabezado)
            tabla.column(columna, width=110, anchor="w")

        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    def limpiar_tabla(self, tabla):
        for item in tabla.get_children():
            tabla.delete(item)

    def cerrar_sesion(self):
        self.al_cerrar_sesion()
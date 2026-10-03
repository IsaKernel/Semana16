# restaurante_app — Semana 16: Manejo de eventos aplicado a la gestión de usuarios

**Estudiante:** Cueva Ochoa Sabrina Isabel
**Asignatura:** Programación Orientada a Objetos
**Actividad:** Semana 16 — Manejo de eventos aplicado a la gestión de usuarios

Continuación del proyecto `restaurante_app` a partir de la base construida en la Semana 15 (navegación lateral, gestión completa de productos, consulta de usuarios y registro de ventas con `command=`). Esta semana se evoluciona la sección **Usuarios**, que pasa de ser solo consulta a un CRUD completo con formulario y tabla, usada como contexto práctico para trabajar el fundamento de la semana: **una interacción del usuario → un evento → `bind()` → un callback → el servicio → persistencia → respuesta visual**.

## Evolución respecto a la Semana 15

Se conservó todo el trabajo previo (login, sidebar, gestión de productos, ventas) y se modificó únicamente lo necesario:

- Atributo `rol` en el modelo `Usuario` (Administrador, Empleado, Cliente), validado en su setter.
- Persistencia del rol en `datos/usuarios.json`.
- Nuevos métodos en `Restaurante`: `registrar_usuario()`, `actualizar_usuario()`, `eliminar_usuario()`, `guardar_usuarios()` y `buscar_usuario_por_nombre_usuario()`.
- Sección **Usuarios** en `main_view.py` con formulario, `Treeview`, `Combobox` de rol y los eventos de la semana.
- El botón "Usuarios" del menú lateral solo aparece para el rol Administrador.

## Estructura del proyecto

```
restaurante_app/
├── datos/
│   ├── productos.json
│   ├── usuarios.json
│   └── ventas.json
├── modelos/
│   ├── __init__.py
│   ├── producto.py
│   ├── usuario.py
│   └── venta.py
├── servicios/
│   ├── __init__.py
│   ├── archivo_servicio.py
│   └── restaurante.py
├── ui/
│   ├── __init__.py
│   ├── login_view.py
│   └── main_view.py
├── assets/
│   ├── icons/          (add.png, clean.png, delete.png, edit.png, home.png,
│   │                     logout.png, productos.png, sales.png, search.png, users.png)
│   └── logo/            (icono.png, logo.png)
├── main.py
└── README.md
```

## Responsabilidad de cada archivo

- **`modelos/usuario.py`** — representa a la persona y valida sus propios campos mediante `@property`. Esta semana incorpora `rol`, que solo acepta los valores de `ROLES_PERMITIDOS`. No conoce JSON ni reglas de negocio.
- **`servicios/archivo_servicio.py`** — genérico: solo `leer_json()` y `escribir_json()`. No cambió esta semana.
- **`servicios/restaurante.py`** — concentra las reglas de negocio de usuarios: duplicados de identificación y de nombre de usuario, qué roles se pueden registrar, protección de la cuenta autenticada y persistencia en `usuarios.json`. Las vistas nunca validan ni escriben JSON.
- **`ui/main_view.py`** — captura los eventos, lee el formulario, llama al servicio y actualiza la tabla. No decide si un usuario es válido ni toca `usuarios.json`.
- **`main.py`, `login_view.py`, `producto.py`, `venta.py`** — sin cambios.

## Roles

| Rol | Acceso a la gestión de usuarios |
|-----|---------------------------------|
| Administrador | Sí. Registra, consulta, actualiza y elimina Empleados y Clientes |
| Empleado | No. El botón "Usuarios" no aparece |
| Cliente | No. El botón "Usuarios" no aparece |

Además del menú, `mostrar_usuarios()` vuelve a comprobar el rol antes de construir la pantalla. No se implementó un sistema de permisos complejo: el rol solo decide si se accede a esta sección.

Reglas aplicadas en `Restaurante`:

- Desde la interfaz solo se registran Empleados y Clientes.
- No se cambia el rol de un administrador ni se asigna el rol Administrador a otro usuario.
- No se puede eliminar la cuenta con la que se inició sesión, ni cuentas de administrador.

## Modelo `Usuario` con rol

```python
class Usuario:
    ROLES_PERMITIDOS = ("Administrador", "Empleado", "Cliente")
    ROLES_GESTIONABLES = ("Empleado", "Cliente")

    @rol.setter
    def rol(self, valor):
        rol_limpio = (valor or "").strip()
        if not rol_limpio:
            raise ValueError("El rol no puede estar vacío.")
        if rol_limpio not in self.ROLES_PERMITIDOS:
            raise ValueError("El rol seleccionado no es válido.")
        self._rol = rol_limpio
```

Si un registro antiguo de `usuarios.json` no trae el campo `rol`, `Restaurante.cargar_datos()` lo carga como Cliente.

## Eventos implementados

| Origen | Evento | Mecanismo | Callback | Resultado |
|--------|--------|-----------|----------|-----------|
| Treeview | `<<TreeviewSelect>>` | `bind()` | `al_seleccionar_usuario` | Carga el usuario seleccionado en el formulario |
| Campos del formulario | `<Return>` | `bind()` | `al_presionar_enter` | Registra el usuario |
| Formulario y tabla | `<Escape>` | `bind()` | `al_presionar_escape` | Limpia el formulario y la selección |
| Combobox de rol | `<<ComboboxSelected>>` | `bind()` | `al_seleccionar_rol` | Actualiza el texto "Rol seleccionado" |
| Botones | clic | `command=` | `registrar_usuario`, `actualizar_usuario`, `eliminar_usuario`, `limpiar_formulario_usuario` | Acciones principales |

```python
# En mostrar_usuarios(): los eventos se conectan con bind()
self.tabla_usuarios.bind("<<TreeviewSelect>>", self.al_seleccionar_usuario)
self.usuario_rol_combo.bind("<<ComboboxSelected>>", self.al_seleccionar_rol)

for widget in campos_formulario:
    widget.bind("<Return>", self.al_presionar_enter)
    widget.bind("<Escape>", self.al_presionar_escape)
self.tabla_usuarios.bind("<Escape>", self.al_presionar_escape)
```

### `<<TreeviewSelect>>`: de la fila al formulario

```python
def al_seleccionar_usuario(self, event):
    seleccion = self.tabla_usuarios.selection()
    if not seleccion:
        return

    valores = self.tabla_usuarios.item(seleccion[0], "values")
    usuario = self.restaurante_servicio.buscar_usuario_por_identificacion(str(valores[0]))
    if usuario is None:
        return

    self.cargar_usuario_en_formulario(usuario)
```

La tabla solo guarda identificación, nombre, usuario y rol. El callback toma la identificación de la fila y le pide el objeto completo a `Restaurante`, de modo que ningún dato sensible (como la contraseña) viaja en el `Treeview`.

### `<Return>` y `<Escape>`

```python
def al_presionar_enter(self, event):
    self.registrar_usuario()           # el mismo método del botón Registrar

def al_presionar_escape(self, event):
    self.limpiar_formulario_usuario()  # el mismo método del botón Limpiar
```

Los callbacks de teclado no repiten la lógica: llaman a los métodos que ya usan los botones. La diferencia es que reciben el parámetro `event`, que `command=` no entrega.

### `<<ComboboxSelected>>`: responder al cambio de rol

```python
def al_seleccionar_rol(self, event):
    self.actualizar_texto_rol(self.usuario_rol_combo.get())
```

El Combobox es de solo lectura y ofrece Empleado y Cliente. Si se selecciona un administrador en la tabla, el combo se muestra deshabilitado con el valor Administrador, porque su rol no se modifica desde esta pantalla.

## `command=` frente a `bind()`

- **`command=`** se usa en los botones. Ejecuta un callback cuando se hace clic y no recibe información del evento.
- **`bind()`** asocia un evento concreto (una selección en la tabla, una tecla, un cambio en el combo) a un callback que recibe el objeto `event`.
- En ambos casos se pasa la **referencia** al método, sin paréntesis; Tkinter lo ejecuta cuando ocurre el evento.
- Un callback coordina: lee la interfaz, llama a `Restaurante` y actualiza la vista. No reemplaza al servicio.

## Gestión de usuarios en `Restaurante`

```python
def registrar_usuario(self, identificacion, nombre, correo, celular, usuario, contrasena, rol):
    if not (contrasena or "").strip():
        raise ValueError("La contraseña no puede estar vacía.")

    nuevo_usuario = Usuario(identificacion, nombre, correo, celular, usuario, contrasena, rol)

    if nuevo_usuario.rol not in Usuario.ROLES_GESTIONABLES:
        raise ValueError("Desde esta pantalla solo se registran Empleados y Clientes.")
    if self.buscar_usuario_por_identificacion(nuevo_usuario.identificacion) is not None:
        raise ValueError("Ya existe un usuario con esa identificación.")
    if self.buscar_usuario_por_nombre_usuario(nuevo_usuario.usuario) is not None:
        raise ValueError("Ya existe un usuario con ese nombre de usuario.")

    self.usuarios.append(nuevo_usuario)
    self.guardar_usuarios()
    return nuevo_usuario
```

- `actualizar_usuario()` conserva la contraseña actual si el campo llega vacío, y rechaza nombres de usuario repetidos y cambios de rol no permitidos.
- `eliminar_usuario()` recibe además la identificación de la cuenta autenticada para impedir que se elimine a sí misma.
- `guardar_usuarios()` reescribe `usuarios.json` completo, con el mismo patrón que `guardar_productos()`.
- Todos los errores se comunican con `ValueError`, y la interfaz los muestra con `messagebox`.

## Flujo de la aplicación

```
Inicio de la aplicación
        ↓
LoginView → Restaurante.validar_acceso()
        ↓
MainView (sidebar: Inicio, Usuarios*, Productos, Ventas)
        ↓
* Solo el Administrador accede a "Usuarios"
        ↓
Formulario + Treeview de usuarios
        ↓
Selecciona una fila → <<TreeviewSelect>>
        ↓
bind() → al_seleccionar_usuario(event)
        ↓
Restaurante.buscar_usuario_por_identificacion()
        ↓
Se cargan los datos en el formulario
        ↓
Actualizar / Eliminar / Limpiar (command=)
        ↓
Restaurante valida y guarda → usuarios.json
        ↓
Se refresca el Treeview y se muestra un mensaje al usuario
```

## Persistencia

Los usuarios se guardan en `datos/usuarios.json` con los campos `identificacion`, `nombre`, `correo`, `celular`, `usuario`, `contrasena` y `rol`. Al volver a ejecutar la aplicación, `Restaurante` los recupera desde ese archivo.

## Ejecución

Desde la carpeta que contiene `restaurante_app/`:

```bash
python -m restaurante_app.main
```

## Credenciales de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| isa     | hope2     | Administrador |
| sebas   | hope1     | Empleado |

> El acceso es una simulación pedagógica; no representa un mecanismo de autenticación seguro (sin cifrado).

## Pruebas realizadas

- **Continuidad**: login, navegación, productos y ventas siguen funcionando.
- **Acceso por rol**: con `isa` (Administrador) aparece "Usuarios" en el menú; con `sebas` (Empleado) no aparece.
- **Registro**: se registró un usuario Cliente y un Empleado, y ambos aparecieron en el Treeview.
- **`<<TreeviewSelect>>`**: al seleccionar una fila, sus datos se cargaron en el formulario.
- **Actualizar**: se modificó un dato, se presionó Actualizar y el cambio se conservó.
- **Eliminar**: se pidió confirmación previa y el usuario desapareció de la tabla.
- **Cuenta autenticada**: al intentar eliminar la cuenta administrativa en uso se mostró un mensaje de error y no se eliminó.
- **`<Return>`**: Enter en un campo del formulario ejecutó el registro.
- **`<Escape>`**: Escape limpió el formulario y la selección.
- **`<<ComboboxSelected>>`**: al cambiar el rol se actualizó el texto "Rol seleccionado".
- **Persistencia real**: se cerró la aplicación, se volvió a ejecutar y los usuarios se recuperaron desde `usuarios.json`.
- **Sin datos sensibles**: el Treeview no muestra la contraseña.

## Reflexión

Esta semana dejó clara la diferencia entre `command=` y `bind()`ya que el primero conecta un botón con una acción, y el segundo permite reaccionar a cualquier evento, como una selección en la tabla o una tecla. Lo más útil fue ver que Enter y Escape no necesitan lógica propia: reutilizan `registrar_usuario()` y `limpiar_formulario_usuario()`, los mismos métodos de los botones. Y como las reglas viven en `Restaurante`, si mañana cambia una regla (por ejemplo, qué roles se pueden registrar), se modifica en un solo lugar sin tocar los eventos ni la tabla.
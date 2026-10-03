    # modelos/usuario.py
# Representa a una persona registrada en el sistema del restaurante.
# Semana 16: se agrega el atributo 'rol' (Administrador, Empleado o Cliente)
# para diferenciar de forma sencilla lo que cada persona puede hacer.
# Es una simulación pedagógica: no es un mecanismo de autenticación seguro
# (sin hash, sin sal).


class Usuario:
    ROLES_PERMITIDOS = ("Administrador", "Empleado", "Cliente")
    # Roles que el administrador puede crear y gestionar desde la interfaz.
    ROLES_GESTIONABLES = ("Empleado", "Cliente")

    def __init__(
        self,
        identificacion: str,
        nombre: str,
        correo: str,
        celular: str = "",
        usuario: str = "",
        contrasena: str = "",
        rol: str = "Cliente",
    ) -> None:
        self.identificacion = identificacion
        self.nombre = nombre
        self.correo = correo
        self.celular = celular
        self.usuario = usuario
        self.contrasena = contrasena
        self.rol = rol

    @property
    def identificacion(self) -> str:
        return self._identificacion

    @identificacion.setter
    def identificacion(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("La identificación no puede estar vacía.")
        self._identificacion = valor.strip()

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        valor_limpio = (valor or "").strip()
        if not valor_limpio:
            raise ValueError("El correo no puede estar vacío.")
        posicion_arroba = valor_limpio.find("@")
        if posicion_arroba == -1 or "." not in valor_limpio[posicion_arroba + 1:]:
            raise ValueError("El correo debe contener @ y un punto después del @.")
        self._correo = valor_limpio

    @property
    def celular(self) -> str:
        return self._celular

    @celular.setter
    def celular(self, valor: str) -> None:
        self._celular = (valor or "").strip()

    @property
    def usuario(self) -> str:
        return self._usuario

    @usuario.setter
    def usuario(self, valor: str) -> None:
        # Si no se define un nombre de usuario, se usa la identificación.
        valor_limpio = (valor or "").strip()
        self._usuario = valor_limpio if valor_limpio else self.identificacion

    @property
    def contrasena(self) -> str:
        return self._contrasena

    @contrasena.setter
    def contrasena(self, valor: str) -> None:
        self._contrasena = (valor or "").strip()

    @property
    def rol(self) -> str:
        return self._rol

    @rol.setter
    def rol(self, valor: str) -> None:
        rol_limpio = (valor or "").strip()
        if not rol_limpio:
            raise ValueError("El rol no puede estar vacío.")
        if rol_limpio not in self.ROLES_PERMITIDOS:
            raise ValueError("El rol seleccionado no es válido.")
        self._rol = rol_limpio
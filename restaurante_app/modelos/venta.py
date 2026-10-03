# modelos/venta.py
# Representa una venta simple: relaciona un usuario existente con un
# producto existente en una fecha determinada. Sigue el mismo estilo
# de validacion con @property que producto.py y usuario.py: el objeto
# nunca puede quedar en un estado invalido porque el setter no lo permite.


class Venta:
    def __init__(
        self,
        identificador: str,
        usuario_identificacion: str,
        producto_codigo: str,
        fecha: str,
    ) -> None:
        self.identificador = identificador
        self.usuario_identificacion = usuario_identificacion
        self.producto_codigo = producto_codigo
        self.fecha = fecha

    @staticmethod
    def validar_texto(valor: str, campo: str) -> str:
        if not valor or not valor.strip():
            raise ValueError(f"El campo {campo} no puede estar vacío.")
        return valor.strip()

    @property
    def identificador(self) -> str:
        return self._identificador

    @identificador.setter
    def identificador(self, valor: str) -> None:
        self._identificador = self.validar_texto(valor, "identificador")

    @property
    def usuario_identificacion(self) -> str:
        return self._usuario_identificacion

    @usuario_identificacion.setter
    def usuario_identificacion(self, valor: str) -> None:
        self._usuario_identificacion = self.validar_texto(valor, "usuario")

    @property
    def producto_codigo(self) -> str:
        return self._producto_codigo

    @producto_codigo.setter
    def producto_codigo(self, valor: str) -> None:
        self._producto_codigo = self.validar_texto(valor, "producto")

    @property
    def fecha(self) -> str:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: str) -> None:
        self._fecha = self.validar_texto(valor, "fecha")
# servicios/archivo_servicio.py
# Servicio generico de persistencia: no conoce Producto ni Usuario,
# solo sabe leer y escribir archivos JSON dentro de una carpeta de
# datos. Es identico en responsabilidad al ArchivoServicio del
# proyecto docente (Biblioteca App).
# servicios/archivo_servicio.py
import json
from pathlib import Path

class ArchivoServicio:
    def __init__(self, carpeta_datos):
        self.carpeta_datos = Path(carpeta_datos)

    def leer_json(self, nombre_archivo):
        ruta = self.carpeta_datos / nombre_archivo

        if not ruta.exists():
            return []

        with ruta.open("r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def escribir_json(self, nombre_archivo, datos):
        ruta = self.carpeta_datos / nombre_archivo
        ruta.parent.mkdir(parents=True, exist_ok=True)

        with ruta.open("w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
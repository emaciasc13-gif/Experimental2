"""ÚNICO módulo autorizado para leer y escribir archivos JSON."""
import json
from pathlib import Path


class GestorJSON:
    """Guarda una lista de diccionarios en un archivo JSON."""

    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)

    def leer(self):
        if not self.ruta.exists():
            return []
        try:
            with self.ruta.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def guardar(self, datos):
        try:
            with self.ruta.open("w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
                archivo.write("\n")
            return True
        except (OSError, TypeError, ValueError):
            return False

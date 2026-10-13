"""Herramientas de consola y validación reutilizables."""
import os

COLORES = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AZUL": "\033[94m",
    "AMARILLO": "\033[93m",
    "CYAN": "\033[96m",
    "RESET": "\033[0m",
}
RESPUESTAS_SI = ("si", "sí", "s", "yes", "y")  # Tupla inmutable.


def limpiar_pantalla():
    if os.isatty(1):
        os.system("cls" if os.name == "nt" else "clear")


def imprimir_color(texto, color):
    codigo = COLORES.get(color, "")
    final = COLORES["RESET"] if codigo else ""
    print(f"{codigo}{texto}{final}")


def imprimir_titulo(texto):
    limpiar_pantalla()
    imprimir_color("=" * 58, "AZUL")
    print(texto.center(58))
    imprimir_color("=" * 58, "AZUL")
    print()


def imprimir_exito(mensaje):
    imprimir_color(f"✓ {mensaje}", "VERDE")


def imprimir_error(mensaje):
    imprimir_color(f"✗ {mensaje}", "ROJO")


def imprimir_info(mensaje):
    imprimir_color(f"ℹ {mensaje}", "CYAN")


def confirmar(pregunta):
    return input(f"{pregunta} (si/no): ").strip().casefold() in RESPUESTAS_SI


def es_email_valido(texto):
    """Validación básica de correo suficiente para esta práctica."""
    texto = str(texto).strip()
    if texto.count("@") != 1:
        return False
    usuario, dominio = texto.split("@")
    return bool(usuario and "." in dominio and not dominio.startswith(".")
                and not dominio.endswith(".") and " " not in texto)

"""VISTA: menús, input() y print(). Las reglas están en views.py."""
import views
from shared.herramientas import (
    confirmar, imprimir_error, imprimir_exito, imprimir_info, imprimir_titulo,
)


def pausa():
    try:
        input("\nPresione Enter para continuar...")
    except EOFError:
        pass


def pedir_entero(etiqueta):
    try:
        return int(input(etiqueta).strip())
    except (ValueError, EOFError):
        imprimir_error("Debe ingresar un número entero")
        return None


def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    """Polimorfismo: los tres modelos se muestran con la misma función."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")  # __str__ llama a etiqueta() según el modelo.
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    """Muestra cualquier modelo recorriendo su diccionario de campos."""
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {clave.replace('_', ' ').capitalize():<18}: {valor}")


# ----------------------------------------------------------------------
# MENÚ DE ESTUDIANTES
# ----------------------------------------------------------------------
def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Correo electrónico: "),
        "carnet": input("Carnet: "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*views.crear_estudiante(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES REGISTRADOS")
    mostrar_lista(views.obtener_estudiantes())
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    mostrar_lista(views.buscar_estudiantes(termino), "No hay coincidencias.")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = views.obtener_estudiante(pedir_entero("ID del estudiante: "))
    if estudiante is None:
        imprimir_error("Estudiante no encontrado")
    else:
        mostrar_detalle(estudiante)
        promedio = views.promedio_de_estudiante(estudiante.id)
        imprimir_info(f"Promedio de notas: {promedio if promedio is not None else 'sin notas'}")
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    estudiante = views.obtener_estudiante(pedir_entero("ID: "))
    if estudiante is None:
        imprimir_error("Estudiante no encontrado")
        return pausa()
    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco los campos que no desea cambiar.\n")
    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        nuevo = input(f"{campo.capitalize()} [{getattr(estudiante, campo)}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*views.actualizar_estudiante(estudiante.id, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    estudiante = views.obtener_estudiante(pedir_entero("ID: "))
    if estudiante is None:
        imprimir_error("Estudiante no encontrado")
    elif confirmar(f"¿Desea eliminar a {estudiante.nombre_completo()}?"):
        mostrar_resultado(*views.eliminar_estudiante(estudiante.id))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# ----------------------------------------------------------------------
# MENÚ DE MATERIAS
# ----------------------------------------------------------------------
def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre de la materia: "),
        "codigo": input("Código (p. ej. MAT101): "),
        "creditos": input("Créditos (1 a 10): "),
        "cupos": input("Cupos disponibles (0 a 30): "),
    }
    mostrar_resultado(*views.crear_materia(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS REGISTRADAS")
    mostrar_lista(views.obtener_materias())
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(views.buscar_materias(termino), "No hay coincidencias.")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = views.obtener_materia(pedir_entero("ID: "))
    if materia is None:
        imprimir_error("Materia no encontrada")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    materia = views.obtener_materia(pedir_entero("ID: "))
    if materia is None:
        imprimir_error("Materia no encontrada")
        return pausa()
    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco los campos que no desea cambiar.\n")
    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        nuevo = input(f"{campo.capitalize()} [{getattr(materia, campo)}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*views.actualizar_materia(materia.id, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    materia = views.obtener_materia(pedir_entero("ID: "))
    if materia is None:
        imprimir_error("Materia no encontrada")
    elif confirmar(f"¿Desea eliminar la materia {materia.nombre}?"):
        mostrar_resultado(*views.eliminar_materia(materia.id))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# ----------------------------------------------------------------------
# MENÚ DE MATRÍCULAS
# ----------------------------------------------------------------------
def matricular_estudiante():
    imprimir_titulo("REGISTRAR MATRÍCULA")
    imprimir_info("Estudiantes disponibles:")
    mostrar_lista(views.obtener_estudiantes())
    imprimir_info("Materias disponibles:")
    mostrar_lista(views.obtener_materias())
    datos = {
        "estudiante_id": pedir_entero("ID del estudiante: "),
        "materia_id": pedir_entero("ID de la materia: "),
        "periodo": input("Periodo (p. ej. 2026-1): "),
    }
    mostrar_resultado(*views.crear_matricula(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRÍCULAS REGISTRADAS")
    mostrar_lista(views.obtener_matriculas())
    pausa()


def registrar_nota():
    imprimir_titulo("REGISTRAR NOTA")
    id_matricula = pedir_entero("ID de la matrícula: ")
    nota = input("Nota (de 0 a 20): ")
    mostrar_resultado(*views.registrar_nota(id_matricula, nota))
    pausa()


def ver_certificado():
    imprimir_titulo("CERTIFICADO ACADÉMICO")
    texto = views.certificado(pedir_entero("ID de la matrícula: "))
    if texto is None:
        imprimir_error("No se encontró la matrícula o sus datos relacionados")
    else:
        print(texto)
    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    matricula = views.obtener_matricula(pedir_entero("ID de la matrícula: "))
    if matricula is None:
        imprimir_error("Matrícula no encontrada")
    elif confirmar(f"¿Retirar la matrícula #{matricula.id} y devolver el cupo?"):
        mostrar_resultado(*views.retirar_matricula(matricula.id))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN ACADÉMICO")
    datos = views.resumen_academico()
    print(f"  Estudiantes registrados : {datos['total_estudiantes']}")
    print(f"  Carreras distintas      : {', '.join(datos['carreras']) or 'ninguna'}")
    print(f"  Materias registradas    : {datos['total_materias']}")
    sin_cupo = datos["materias_sin_cupo"]
    print(f"  Materias sin cupo       : {', '.join(m.nombre for m in sin_cupo) or 'ninguna'}")
    print(f"  Matrículas registradas  : {datos['total_matriculas']}")
    print(f"  Matrículas aprobadas    : {datos['matriculas_aprobadas']}")
    pausa()


# Los diccionarios conectan cada tecla con una TUPLA (texto, función).
MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por ID", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por ID", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Matricular", matricular_estudiante),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Registrar nota", registrar_nota),
    "4": ("Ver certificado", ver_certificado),
    "5": ("Retirar matrícula", retirar_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    """Bucle reutilizable para los tres submenús y el menú principal."""
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _accion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()
        try:
            opcion = input("Seleccione una opción: ").strip()
        except EOFError:
            return
        if opcion not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue
        _texto, accion = opciones[opcion]
        if accion is None:
            return
        accion()


def ir_estudiantes():
    ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)


def ir_materias():
    ejecutar_menu("MATERIAS", MENU_MATERIAS)


def ir_matriculas():
    ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)


MENU_PRINCIPAL = {
    "1": ("Estudiantes", ir_estudiantes),
    "2": ("Materias", ir_materias),
    "3": ("Matrículas", ir_matriculas),
    "4": ("Resumen", resumen),
    "0": ("Salir", None),
}


if __name__ == "__main__":
    try:
        ejecutar_menu("SISTEMA ACADÉMICO", MENU_PRINCIPAL)
        imprimir_exito("Gracias por utilizar el Sistema Académico")
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado.")

"""CONTROLADOR: funciones de CRUD, búsquedas y reglas del sistema académico.

No contiene input() ni print(). La única lectura/escritura de JSON se realiza
mediante shared/json_manager.py. Los nombres de las funciones siguen la sección
16 de la guía y usan list, tuple, set y dict con comentarios explicativos.
"""
from pathlib import Path

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

CARPETA_DATOS = Path(__file__).resolve().parent / "data"


def configurar_archivos(carpeta=None):
    """Configura la carpeta de datos; también permite aislar las pruebas."""
    global gestor_estudiantes, gestor_materias, gestor_matriculas
    ruta = Path(carpeta) if carpeta is not None else CARPETA_DATOS
    gestor_estudiantes = GestorJSON(ruta / "estudiantes.json")
    gestor_materias = GestorJSON(ruta / "materias.json")
    gestor_matriculas = GestorJSON(ruta / "matriculas.json")


configurar_archivos()


# ----------------------------------------------------------------------
# FUNCIONES GENÉRICAS: sirven para cualquier modelo y cualquier JSON.
# ----------------------------------------------------------------------
# TUPLA: las operaciones de escritura devuelven (exito, mensaje) para que la Vista
# pueda mostrar el resultado sin tener que conocer las reglas del negocio.
def _id_entero(valor):
    """Convierte un ID positivo a int; devuelve None si no es válido."""
    if isinstance(valor, bool) or valor is None:
        return None
    texto = str(valor).strip()
    if not texto.isdecimal():
        return None
    numero = int(texto)
    return numero if numero > 0 else None


def _entero_entre(valor, minimo, maximo):
    """Valida un entero sin truncar decimales."""
    if isinstance(valor, bool) or valor is None:
        return None
    texto = str(valor).strip()
    if not texto.isdecimal():
        return None
    numero = int(texto)
    return numero if minimo <= numero <= maximo else None


def leer_objetos(gestor, modelo):
    """Lee la LISTA JSON y convierte cada diccionario al modelo solicitado."""
    objetos = []
    for datos in gestor.leer():
        objetos.append(modelo.desde_diccionario(datos))
    return objetos


def ids_registrados(gestor):
    """SET de IDs existentes: evita buscar un identificador duplicado a mano."""
    return {int(registro["id"]) for registro in gestor.leer() if "id" in registro}


def obtener_por_id(gestor, modelo, id_registro):
    """Busca un objeto por ID y devuelve None cuando no existe."""
    id_registro = _id_entero(id_registro)
    if id_registro is None or id_registro not in ids_registrados(gestor):
        return None
    for registro in gestor.leer():
        if int(registro.get("id", -1)) == id_registro:
            return modelo.desde_diccionario(registro)
    return None


def buscar(gestor, modelo, termino, campos):
    """Búsqueda lineal; campos es una TUPLA fija de atributos buscables."""
    termino = str(termino or "").strip().casefold()
    if not termino:
        return []
    encontrados = []  # LISTA de objetos que coinciden con el término.
    for objeto in leer_objetos(gestor, modelo):
        for campo in campos:
            valor = str(getattr(objeto, campo, "")).casefold()
            if termino in valor:
                encontrados.append(objeto)
                break
    return encontrados


def siguiente_id(gestor):
    """Calcula el próximo ID sin depender del número de registros actuales."""
    ids = ids_registrados(gestor)
    return max(ids, default=0) + 1


def guardar_nuevo(gestor, objeto, nombre="Registro"):
    """Añade un objeto a la LISTA persistida y devuelve (éxito, mensaje)."""
    datos = gestor.leer()
    if objeto.id in {int(registro.get("id", -1)) for registro in datos}:
        return False, f"El ID {objeto.id} ya existe"
    datos.append(objeto.a_diccionario())
    if not gestor.guardar(datos):
        return False, f"No se pudo guardar el {nombre.lower()}"
    return True, f"{nombre} creado correctamente"


def reemplazar(gestor, objeto, nombre="Registro"):
    """Reemplaza un diccionario por ID sin modificar la lista durante el recorrido."""
    datos = gestor.leer()
    for posicion, registro in enumerate(datos):
        if int(registro.get("id", -1)) == objeto.id:
            datos[posicion] = objeto.a_diccionario()
            if not gestor.guardar(datos):
                return False, f"No se pudo actualizar el {nombre.lower()}"
            return True, f"{nombre} actualizado correctamente"
    return False, f"No existe el {nombre.lower()} con ID {objeto.id}"


def eliminar(gestor, id_registro, nombre="Registro"):
    """Filtra la LISTA para eliminar un ID y guarda el resultado."""
    id_registro = _id_entero(id_registro)
    if id_registro is None:
        return False, "El ID debe ser un entero positivo"
    datos = gestor.leer()
    nuevos = [registro for registro in datos
              if int(registro.get("id", -1)) != id_registro]
    if len(nuevos) == len(datos):
        return False, f"No existe el {nombre.lower()} con ID {id_registro}"
    if not gestor.guardar(nuevos):
        return False, f"No se pudo eliminar el {nombre.lower()}"
    return True, f"{nombre} eliminado correctamente"


def indice_por_id(gestor, modelo):
    """DICT {id: objeto}: permite cruzar relaciones sin buscar cada ID uno a uno."""
    return {objeto.id: objeto for objeto in leer_objetos(gestor, modelo)}


# ----------------------------------------------------------------------
# ESTUDIANTES
# ----------------------------------------------------------------------
CAMPOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet", "carrera")
CAMPOS_OBLIGATORIOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet")


def carnets_registrados(excepto_id=None):
    """SET de carnets normalizados: la comprobación de duplicados es directa."""
    return {str(registro.get("carnet", "")).strip().upper()
            for registro in gestor_estudiantes.leer()
            if int(registro.get("id", -1)) != excepto_id}


def emails_registrados(excepto_id=None):
    """SET de correos normalizados para evitar duplicados."""
    return {str(registro.get("email", "")).strip().casefold()
            for registro in gestor_estudiantes.leer()
            if int(registro.get("id", -1)) != excepto_id}


def validar_estudiante(datos, id_actual=None):
    """Devuelve un mensaje de error o None cuando los datos son válidos."""
    if id_actual is None:
        for campo in CAMPOS_OBLIGATORIOS_ESTUDIANTE:
            if str(datos.get(campo, "")).strip() == "":
                return f"El campo {campo} es obligatorio"

    if "email" in datos:
        email = str(datos.get("email", "")).strip().casefold()
        if not es_email_valido(email):
            return f"El email '{email}' no es válido"
        if email in emails_registrados(id_actual):
            return "Ese email ya está registrado"

    if "carnet" in datos:
        carnet = str(datos.get("carnet", "")).strip().upper()
        if not carnet and id_actual is None:
            return "El carnet es obligatorio"
        if carnet and carnet in carnets_registrados(id_actual):
            return "Ese carnet ya está registrado"

    return None


def crear_estudiante(datos):
    datos = {campo: str(datos.get(campo, "")).strip() for campo in CAMPOS_ESTUDIANTE}
    datos["email"] = datos["email"].casefold()
    datos["carnet"] = datos["carnet"].upper()
    datos["nombre"] = datos["nombre"].title()
    datos["apellido"] = datos["apellido"].title()
    error = validar_estudiante(datos)
    if error:
        return False, error
    estudiante = Estudiante(siguiente_id(gestor_estudiantes), **datos)
    return guardar_nuevo(gestor_estudiantes, estudiante, "Estudiante")


def obtener_estudiantes():
    return leer_objetos(gestor_estudiantes, Estudiante)


def obtener_estudiante(id_registro):
    return obtener_por_id(gestor_estudiantes, Estudiante, id_registro)


def buscar_estudiantes(termino):
    return buscar(gestor_estudiantes, Estudiante, termino, CAMPOS_ESTUDIANTE)


def actualizar_estudiante(id_registro, cambios):
    estudiante = obtener_estudiante(id_registro)
    if estudiante is None:
        return False, "No existe ese estudiante"
    if any(campo not in CAMPOS_ESTUDIANTE for campo in cambios):
        return False, "Se recibió un campo que no pertenece al estudiante"
    datos = {campo: getattr(estudiante, campo) for campo in CAMPOS_ESTUDIANTE}
    for campo, valor in cambios.items():
        if str(valor).strip() != "":
            datos[campo] = str(valor).strip()
    datos["email"] = datos["email"].casefold()
    datos["carnet"] = datos["carnet"].upper()
    datos["nombre"] = datos["nombre"].title()
    datos["apellido"] = datos["apellido"].title()
    error = validar_estudiante(datos, estudiante.id)
    if error:
        return False, error
    actualizado = Estudiante(estudiante.id, **datos)
    return reemplazar(gestor_estudiantes, actualizado, "Estudiante")


def eliminar_estudiante(id_registro):
    id_registro = _id_entero(id_registro)
    if id_registro is None or obtener_estudiante(id_registro) is None:
        return False, "No existe ese estudiante"
    # Evitamos dejar matrículas apuntando a un estudiante eliminado.
    if any(m.estudiante_id == id_registro for m in obtener_matriculas()):
        return False, "Retire primero las matrículas de este estudiante"
    return eliminar(gestor_estudiantes, id_registro, "Estudiante")


# ----------------------------------------------------------------------
# MATERIAS
# ----------------------------------------------------------------------
CAMPOS_MATERIA = ("nombre", "codigo")
CAMPOS_EDITABLES_MATERIA = ("nombre", "codigo", "creditos", "cupos")


def codigos_registrados(excepto_id=None):
    """SET de códigos normalizados: no permite registrar una materia duplicada."""
    return {str(registro.get("codigo", "")).strip().upper()
            for registro in gestor_materias.leer()
            if int(registro.get("id", -1)) != excepto_id}


def validar_materia(datos, id_actual=None):
    if id_actual is None and str(datos.get("nombre", "")).strip() == "":
        return "El nombre de la materia es obligatorio"
    if id_actual is None and str(datos.get("codigo", "")).strip() == "":
        return "El código de la materia es obligatorio"

    if "codigo" in datos:
        codigo = str(datos.get("codigo", "")).strip().upper()
        if not codigo:
            return "El código de la materia es obligatorio"
        if codigo in codigos_registrados(id_actual):
            return "Ese código ya está registrado"

    if "creditos" in datos:
        creditos = _entero_entre(datos["creditos"], 1, 10)
        if creditos is None:
            return "Los créditos deben ser un entero entre 1 y 10"
    elif id_actual is None:
        return "Los créditos son obligatorios"

    if "cupos" in datos:
        cupos = _entero_entre(datos["cupos"], 0, Materia.CUPOS_MAXIMOS)
        if cupos is None:
            return f"Los cupos deben ser un entero entre 0 y {Materia.CUPOS_MAXIMOS}"
    elif id_actual is None:
        return "Los cupos son obligatorios"

    return None


def crear_materia(datos):
    datos = {
        "nombre": str(datos.get("nombre", "")).strip().title(),
        "codigo": str(datos.get("codigo", "")).strip().upper(),
        "creditos": datos.get("creditos", ""),
        "cupos": datos.get("cupos", ""),
    }
    error = validar_materia(datos)
    if error:
        return False, error
    datos["creditos"] = _entero_entre(datos["creditos"], 1, 10)
    datos["cupos"] = _entero_entre(datos["cupos"], 0, Materia.CUPOS_MAXIMOS)
    materia = Materia(siguiente_id(gestor_materias), **datos)
    return guardar_nuevo(gestor_materias, materia, "Materia")


def obtener_materias():
    return leer_objetos(gestor_materias, Materia)


def obtener_materia(id_registro):
    return obtener_por_id(gestor_materias, Materia, id_registro)


def buscar_materias(termino):
    return buscar(gestor_materias, Materia, termino, CAMPOS_MATERIA)


def actualizar_materia(id_registro, cambios):
    materia = obtener_materia(id_registro)
    if materia is None:
        return False, "No existe esa materia"
    if any(campo not in CAMPOS_EDITABLES_MATERIA for campo in cambios):
        return False, "Se recibió un campo que no pertenece a la materia"
    datos = {
        "nombre": materia.nombre,
        "codigo": materia.codigo,
        "creditos": materia.creditos,
        "cupos": materia.cupos,
    }
    for campo, valor in cambios.items():
        if str(valor).strip() != "":
            datos[campo] = valor
    datos["nombre"] = str(datos["nombre"]).strip().title()
    datos["codigo"] = str(datos["codigo"]).strip().upper()
    error = validar_materia(datos, materia.id)
    if error:
        return False, error
    datos["creditos"] = _entero_entre(datos["creditos"], 1, 10)
    datos["cupos"] = _entero_entre(datos["cupos"], 0, Materia.CUPOS_MAXIMOS)
    actualizada = Materia(materia.id, **datos)
    return reemplazar(gestor_materias, actualizada, "Materia")


def eliminar_materia(id_registro):
    id_registro = _id_entero(id_registro)
    if id_registro is None or obtener_materia(id_registro) is None:
        return False, "No existe esa materia"
    # Evitamos dejar matrículas apuntando a una materia eliminada.
    if any(m.materia_id == id_registro for m in obtener_matriculas()):
        return False, "Retire primero las matrículas de esta materia"
    return eliminar(gestor_materias, id_registro, "Materia")


def materias_sin_cupo():
    return [materia for materia in obtener_materias() if not materia.hay_cupo()]


# ----------------------------------------------------------------------
# MATRÍCULAS
# ----------------------------------------------------------------------
def crear_matricula(datos):
    estudiante_id = _id_entero(datos.get("estudiante_id"))
    materia_id = _id_entero(datos.get("materia_id"))
    periodo = str(datos.get("periodo", "")).strip()
    if estudiante_id is None or materia_id is None:
        return False, "El ID del estudiante y el ID de la materia son obligatorios"
    if not periodo:
        return False, "El periodo es obligatorio"

    estudiante = obtener_estudiante(estudiante_id)
    if estudiante is None:
        return False, "El estudiante indicado no existe"
    materia = obtener_materia(materia_id)
    if materia is None:
        return False, "La materia indicada no existe"
    if not materia.hay_cupo():
        return False, "La materia no tiene cupos disponibles"

    # La clave lógica de una matrícula es estudiante + materia + periodo.
    for existente in obtener_matriculas():
        if (existente.estudiante_id == estudiante_id
                and existente.materia_id == materia_id
                and existente.periodo.casefold() == periodo.casefold()):
            return False, "El estudiante ya está matriculado en esa materia durante ese periodo"

    matricula = Matricula(siguiente_id(gestor_matriculas), estudiante_id,
                          materia_id, periodo, None)
    exito, mensaje = guardar_nuevo(gestor_matriculas, matricula, "Matrícula")
    if not exito:
        return exito, mensaje

    materia.ocupar_cupo()
    exito_cupo, _mensaje_cupo = reemplazar(gestor_materias, materia, "Materia")
    if not exito_cupo:
        eliminar(gestor_matriculas, matricula.id, "Matrícula")
        return False, "No se pudo guardar el cupo; se canceló la matrícula"
    return True, "Matrícula creada y cupo actualizado"


def obtener_matriculas():
    return leer_objetos(gestor_matriculas, Matricula)


def obtener_matricula(id_registro):
    return obtener_por_id(gestor_matriculas, Matricula, id_registro)


def registrar_nota(id_registro, nota):
    matricula = obtener_matricula(id_registro)
    if matricula is None:
        return False, "No existe esa matrícula"
    if not Materia.es_nota_valida(nota):
        return False, "La nota debe ser un número entre 0 y 20"
    matricula.nota = float(nota)
    return reemplazar(gestor_matriculas, matricula, "Matrícula")


def retirar_matricula(id_registro):
    matricula = obtener_matricula(id_registro)
    if matricula is None:
        return False, "No existe esa matrícula"
    materia = obtener_materia(matricula.materia_id)
    if materia is None:
        return False, "No se encontró la materia asociada; no se retiró la matrícula"

    cupos_originales = materia.cupos
    materia.liberar_cupo()
    exito, _mensaje = reemplazar(gestor_materias, materia, "Materia")
    if not exito:
        return False, "No se pudo devolver el cupo"

    exito, mensaje = eliminar(gestor_matriculas, matricula.id, "Matrícula")
    if not exito:
        materia.cupos = cupos_originales
        reemplazar(gestor_materias, materia, "Materia")
        return False, mensaje
    return True, "Matrícula retirada y cupo devuelto"


def certificado(id_registro):
    matricula = obtener_matricula(id_registro)
    if matricula is None:
        return None

    # Estos diccionarios índice cruzan las tres entidades por ID.
    estudiantes = indice_por_id(gestor_estudiantes, Estudiante)
    materias = indice_por_id(gestor_materias, Materia)
    estudiante = estudiantes.get(matricula.estudiante_id)
    materia = materias.get(matricula.materia_id)
    if estudiante is None or materia is None:
        return None

    nota_texto = "Pendiente" if matricula.nota is None else f"{matricula.nota:g}"
    return (
        f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        f"Estudiante: {estudiante.nombre_completo()}   ({estudiante.carnet})\n"
        f"Materia   : {materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos\n"
        f"------------------------------------------\n"
        f"Nota      : {nota_texto}\n"
        f"Estado    : {matricula.estado()}"
    )


def matriculas_por_estudiante():
    """DICT de LISTAS: setdefault agrupa las matrículas por estudiante."""
    agrupadas = {}
    for matricula in obtener_matriculas():
        agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
    return agrupadas


def promedio_de_estudiante(id_registro):
    """Promedio de las notas registradas; devuelve None si todavía no hay notas."""
    id_registro = _id_entero(id_registro)
    if id_registro is None or obtener_estudiante(id_registro) is None:
        return None
    agrupadas = matriculas_por_estudiante()
    notas = [matricula.nota for matricula in agrupadas.get(id_registro, [])
             if matricula.nota is not None]
    if not notas:
        return None
    return round(sum(notas) / len(notas), 2)


def matriculas_aprobadas():
    return [matricula for matricula in obtener_matriculas() if matricula.esta_aprobada()]


def resumen_academico():
    """Prepara los valores del resumen para que main.py solo los presente."""
    estudiantes = obtener_estudiantes()
    # SET: elimina carreras repetidas; sorted() las presenta en orden.
    carreras = sorted({estudiante.carrera.strip() for estudiante in estudiantes
                       if estudiante.carrera.strip()})
    return {
        "total_estudiantes": len(estudiantes),
        "carreras": carreras,
        "total_materias": len(obtener_materias()),
        "materias_sin_cupo": materias_sin_cupo(),
        "total_matriculas": len(obtener_matriculas()),
        "matriculas_aprobadas": len(matriculas_aprobadas()),
    }

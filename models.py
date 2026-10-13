"""Modelos del sistema académico: herencia, polimorfismo y serialización."""
from datetime import date
import math


class ModeloBase:
    """Clase padre: conserva el ID y define las conversiones comunes."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        """Convierte un registro JSON en una instancia del modelo correspondiente."""
        datos = dict(datos)                 # Copiamos el diccionario original.
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)    # Único método de clase del proyecto.

    def a_diccionario(self):
        return {"id": self.id}

    def etiqueta(self):
        return f"registro {self.id}"

    def __str__(self):
        # Polimorfismo: cada hijo proporciona su propia etiqueta().
        return f"[{self.id}] {self.etiqueta()}"


class Persona(ModeloBase):
    """Datos comunes de una persona."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona y agrega carnet y carrera."""

    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera or 'sin carrera'}"


class Materia(ModeloBase):
    """Materia y reglas estáticas solicitadas en la guía."""

    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14

    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        """True si valor es un número finito entre 0 y 20."""
        if isinstance(valor, bool) or valor is None or str(valor).strip() == "":
            return False
        try:
            numero = float(valor)
        except (TypeError, ValueError, OverflowError):
            return False
        return math.isfinite(numero) and 0 <= numero <= 20

    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if not self.hay_cupo():
            return False
        self.cupos -= 1
        return True

    def liberar_cupo(self):
        if self.cupos >= Materia.CUPOS_MAXIMOS:
            return False
        self.cupos += 1
        return True

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self):
        aviso = " · SIN CUPO" if not self.hay_cupo() else ""
        return (f"{self.nombre} · {self.codigo} · {self.creditos} créditos · "
                f"{self.cupos} cupos{aviso}")


class Matricula(ModeloBase):
    """Relaciona a un estudiante con una materia durante un periodo."""

    def __init__(self, id_registro, estudiante_id, materia_id, periodo, nota=None, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = str(periodo)
        self.nota = float(nota) if nota is not None and str(nota).strip() != "" else None
        self.fecha = str(fecha) if fecha else date.today().isoformat()

    def esta_aprobada(self):
        return self.nota is not None and self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        if self.nota is None:
            return "Pendiente"
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        # El estado no se guarda: se calcula con estado() al mostrarlo.
        return datos

    def etiqueta(self):
        nota_texto = "Pendiente" if self.nota is None else f"{self.nota:g}/20"
        return (f"Estudiante #{self.estudiante_id} · Materia #{self.materia_id} · "
                f"{self.periodo} · {nota_texto} · {self.estado()}")

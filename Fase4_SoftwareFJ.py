# -*- coding: utf-8 -*-
# Fase 4 - Programación UNAD | Software FJ
# Autor: Moisés Felipe Chávez De la Hoz
# Fuente equivalente al notebook; ejecutar: python Fase4_SoftwareFJ.py

# 1. Fase 4 – Componente práctico
#
# Sistema Integral de Gestión de Clientes, Servicios y Reservas
# Software FJ
#
# Estudiante: Moisés Felipe Chávez De la Hoz
# Universidad: Universidad Nacional Abierta y a Distancia – UNAD
# Programa: Ingeniería de Sistemas · Curso: Programación · Código: 213023
# Actividad: Fase 4 – Componente práctico – Prácticas simuladas
# Curso metodológico · Práctica simulada · Noviembre de 2026
#
# Objetivo: gestionar clientes, servicios y reservas mediante POO y demostrar el manejo de
# excepciones sin detener el sistema ante entradas inválidas. Desarrollo individual según
# autorización del tutor indicada por el estudiante; la actividad original es colaborativa. Los
# datos viven en listas y objetos; únicamente los logs se escriben en archivo.
#
# Ejecutar el archivo completo con python Fase4_SoftwareFJ.py. Las tarifas son simuladas en COP;
# no se gestionan horarios, pagos ni inventario real.

# ============================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN DE LOGGING
# ============================================================
# Se usa exclusivamente la biblioteca estándar. Un logger propio evita duplicar mensajes al
# ejecutar de nuevo la configuración. El archivo conserva ejecuciones anteriores.

from abc import ABC, abstractmethod
from pathlib import Path
import logging
import math
import re

logger = logging.getLogger("software_fj")
logger.setLevel(logging.INFO)
logger.propagate = False
for manejador in logger.handlers[:]:
    manejador.close()
    logger.removeHandler(manejador)
ruta_log = Path.cwd() / "sistema.log"
manejador = logging.FileHandler(ruta_log, mode="a", encoding="utf-8")
manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(manejador)
logger.info("Inicio del programa Software FJ")
print(f"Log activo: {ruta_log}")

# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================
# Las excepciones específicas heredan de una excepción común. Los validadores registran el
# rechazo y conservan la causa original cuando falla una conversión.

class ErrorSistemaFJ(Exception):
    """Base de los errores de negocio de Software FJ."""

class ClienteInvalidoError(ErrorSistemaFJ):
    """Datos personales inválidos."""

class ServicioInvalidoError(ErrorSistemaFJ):
    """Tarifa o parámetros del servicio inválidos."""

class ServicioNoDisponibleError(ErrorSistemaFJ):
    """El servicio está deshabilitado para nuevas operaciones."""

class ReservaInvalidaError(ErrorSistemaFJ):
    """Cliente, servicio, identificación o duración de reserva inválidos."""

class OperacionNoPermitidaError(ErrorSistemaFJ):
    """Transición de estado no permitida."""

def rechazar(tipo_error, mensaje):
    logger.warning("%s: %s", tipo_error.__name__, mensaje)
    raise tipo_error(mensaje)

def texto_valido(valor, campo, tipo_error):
    if not isinstance(valor, str) or not valor.strip():
        rechazar(tipo_error, f"{campo} debe ser un texto no vacío.")
    return valor.strip()

def numero_valido(valor, campo, tipo_error, minimo=0, incluir_minimo=False):
    """Acepta números o cadenas numéricas finitas, pero nunca booleanos."""
    try:
        if isinstance(valor, bool) or not isinstance(valor, (int, float, str)):
            raise ValueError("Tipo numérico no admitido")
        numero = float(valor)
    except (ValueError, TypeError, OverflowError) as error_original:
        logger.warning("Conversión inválida en %s", campo)
        # Encadenamiento real: conserva la causa técnica de la conversión.
        raise tipo_error(f"{campo} debe ser numérico.") from error_original
    if not math.isfinite(numero):
        rechazar(tipo_error, f"{campo} debe ser finito.")
    if numero < minimo or (numero == minimo and not incluir_minimo):
        relacion = "mayor o igual que" if incluir_minimo else "mayor que"
        rechazar(tipo_error, f"{campo} debe ser {relacion} {minimo}.")
    return numero

def entero_positivo(valor, campo, tipo_error):
    numero = numero_valido(valor, campo, tipo_error)
    if not numero.is_integer():
        rechazar(tipo_error, f"{campo} debe ser entero.")
    return int(numero)

# ============================================================
# 3. CLASE ABSTRACTA ENTIDAD
# ============================================================
# Define el contrato general de las entidades. La identificación es de solo lectura. Cliente,
# Servicio y Reserva implementan su propia descripción.

class Entidad(ABC):
    """Abstracción común; no permite instanciar entidades incompletas."""
    def __init__(self, identificacion):
        self.__identificacion = identificacion

    @property
    def identificacion(self):
        return self.__identificacion

    @abstractmethod
    def describir(self):
        """Retorna una descripción de la entidad."""

# ============================================================
# 4. CLASE CLIENTE
# ============================================================
# Los atributos personales son privados. Las propiedades validan antes de modificar el valor;
# una asignación inválida conserva el dato anterior. La encapsulación en Python no equivale a
# una barrera de seguridad.

class Cliente(Entidad):
    """Cliente con datos sencillos y acceso validado."""
    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(texto_valido(identificacion, "Identificación", ClienteInvalidoError))
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        logger.info("Cliente creado: %s", self.identificacion)

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        self.__nombre = texto_valido(valor, "Nombre", ClienteInvalidoError)

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        correo = texto_valido(valor, "Correo", ClienteInvalidoError)
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo):
            rechazar(ClienteInvalidoError, "El correo no tiene un formato básico válido.")
        self.__correo = correo

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        telefono = texto_valido(valor, "Teléfono", ClienteInvalidoError)
        if not re.fullmatch(r"\+?[0-9]{7,15}", telefono):
            rechazar(ClienteInvalidoError, "El teléfono debe tener de 7 a 15 dígitos, con + opcional.")
        self.__telefono = telefono

    def describir(self):
        return f"Cliente {self.identificacion}: {self.nombre}"

# ============================================================
# 5. CLASE ABSTRACTA SERVICIO
# ============================================================
# Establece tres métodos abstractos. Las tarifas son de solo lectura y la disponibilidad se
# cambia con una propiedad booleana. Duración predeterminada: una unidad; se puede indicar otra
# al cotizar.

class Servicio(Entidad):
    """Contrato común de los servicios; concentra validaciones compartidas."""
    def __init__(self, identificacion, precio, disponible=True):
        super().__init__(texto_valido(identificacion, "Código de servicio", ServicioInvalidoError))
        self.__precio = numero_valido(precio, "Precio", ServicioInvalidoError)
        self.disponible = disponible

    @property
    def precio(self):
        return self.__precio

    @property
    def disponible(self):
        return self.__disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            rechazar(ServicioInvalidoError, "La disponibilidad debe ser True o False.")
        self.__disponible = valor

    def comprobar_disponibilidad(self):
        if not self.disponible:
            rechazar(ServicioNoDisponibleError, f"Servicio {self.identificacion} no disponible.")

    @staticmethod
    def ajustar_costo(base, descuento, impuesto):
        """Descuento e impuesto son porcentajes entre 0 y 100."""
        descuento = numero_valido(descuento, "Descuento", ServicioInvalidoError, incluir_minimo=True)
        impuesto = numero_valido(impuesto, "Impuesto", ServicioInvalidoError, incluir_minimo=True)
        if descuento > 100 or impuesto > 100:
            rechazar(ServicioInvalidoError, "Los porcentajes no pueden superar 100.")
        total = base * (1 - descuento / 100) * (1 + impuesto / 100)
        if not math.isfinite(total):
            rechazar(ServicioInvalidoError, "El costo calculado excede el rango permitido.")
        return round(total, 2)

    def describir(self):
        return self.describir_servicio()

    @abstractmethod
    def calcular_costo(self, descuento=0, impuesto=0, *, duracion=1):
        """Sobrecarga simulada mediante parámetros opcionales, no firmas múltiples."""

    @abstractmethod
    def describir_servicio(self):
        """Descripción propia del tipo de servicio."""

    @abstractmethod
    def validar_parametros(self, duracion=1):
        """Valida parámetros propios y devuelve la duración normalizada."""

# ============================================================
# 6. CLASE RESERVASALA
# ============================================================
# Sobrescribe los métodos de Servicio: costo por hora, capacidad entera positiva y duración
# positiva en horas.

class ReservaSala(Servicio):
    def __init__(self, identificacion, precio, capacidad, disponible=True):
        super().__init__(identificacion, precio, disponible)
        self.__capacidad = entero_positivo(capacidad, "Capacidad", ServicioInvalidoError)
        logger.info("Servicio creado: sala %s", self.identificacion)

    @property
    def capacidad(self):
        return self.__capacidad

    def validar_parametros(self, duracion=1):
        self.comprobar_disponibilidad()
        return numero_valido(duracion, "Horas de sala", ServicioInvalidoError)

    def calcular_costo(self, descuento=0, impuesto=0, *, duracion=1):
        horas = self.validar_parametros(duracion)
        return self.ajustar_costo(self.precio * horas, descuento, impuesto)

    def describir_servicio(self):
        return f"Sala {self.identificacion}: {self.capacidad} personas, COP {self.precio:,.0f}/hora"

# ============================================================
# 7. CLASE ALQUILEREQUIPO
# ============================================================
# El alquiler usa días enteros y multiplica la tarifa diaria por la cantidad de equipos. No
# admite fracciones de día.

class AlquilerEquipo(Servicio):
    def __init__(self, identificacion, precio, cantidad, disponible=True):
        super().__init__(identificacion, precio, disponible)
        self.__cantidad = entero_positivo(cantidad, "Cantidad de equipos", ServicioInvalidoError)
        # La disponibilidad puede ser False al registrar el catálogo.
        logger.info("Servicio creado: equipo %s", self.identificacion)

    @property
    def cantidad(self):
        return self.__cantidad

    def validar_parametros(self, duracion=1):
        self.comprobar_disponibilidad()
        return entero_positivo(duracion, "Días de alquiler", ServicioInvalidoError)

    def calcular_costo(self, descuento=0, impuesto=0, *, duracion=1):
        dias = self.validar_parametros(duracion)
        return self.ajustar_costo(self.precio * self.cantidad * dias, descuento, impuesto)

    def describir_servicio(self):
        return f"Equipo {self.identificacion}: {self.cantidad} unidades, COP {self.precio:,.0f}/equipo/día"

# ============================================================
# 8. CLASE ASESORIAESPECIALIZADA
# ============================================================
# La asesoría exige una especialidad y una duración mínima de una hora; admite fracciones
# posteriores, por ejemplo 1,5 horas.

class AsesoriaEspecializada(Servicio):
    def __init__(self, identificacion, precio, especialidad, disponible=True):
        super().__init__(identificacion, precio, disponible)
        self.__especialidad = texto_valido(especialidad, "Especialidad", ServicioInvalidoError)
        logger.info("Servicio creado: asesoría %s", self.identificacion)

    @property
    def especialidad(self):
        return self.__especialidad

    def validar_parametros(self, duracion=1):
        self.comprobar_disponibilidad()
        return numero_valido(duracion, "Horas de asesoría", ServicioInvalidoError,
                             minimo=1, incluir_minimo=True)

    def calcular_costo(self, descuento=0, impuesto=0, *, duracion=1):
        horas = self.validar_parametros(duracion)
        return self.ajustar_costo(self.precio * horas, descuento, impuesto)

    def describir_servicio(self):
        return f"Asesoría {self.identificacion}: {self.especialidad}, COP {self.precio:,.0f}/hora (mínimo 1)"

# ============================================================
# 9. CLASE RESERVA
# ============================================================
# Integra objetos Cliente y Servicio. La creación valida y fija el costo base; procesar,
# confirmar y cancelar comprueban el estado. Una reserva cancelada no puede reabrirse. El costo
# consultado corresponde al importe original, incluso tras cancelar; no representa un cobro.

class Reserva(Entidad):
    """Reserva con duración, costo y estado protegidos mediante propiedades."""
    def __init__(self, identificacion, cliente, servicio, duracion):
        super().__init__(texto_valido(identificacion, "Código de reserva", ReservaInvalidaError))
        if not isinstance(cliente, Cliente):
            rechazar(ReservaInvalidaError, "La reserva requiere un objeto Cliente.")
        if not isinstance(servicio, Servicio):
            rechazar(ReservaInvalidaError, "La reserva requiere un objeto Servicio.")
        tiempo = numero_valido(duracion, "Duración de reserva", ReservaInvalidaError)
        try:
            tiempo = servicio.validar_parametros(tiempo)
            costo = servicio.calcular_costo(duracion=tiempo)
        except ServicioInvalidoError as error_original:
            logger.warning("Parámetros incompatibles con la reserva")
            raise ReservaInvalidaError("La duración no cumple las reglas del servicio.") from error_original
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = tiempo
        self.__costo_base = costo
        self.__estado = "pendiente"
        logger.info("Reserva realizada: %s; servicio %s", self.identificacion, servicio.identificacion)

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def estado(self):
        return self.__estado

    def __exigir_estado(self, permitidos, operacion):
        if self.estado not in permitidos:
            rechazar(OperacionNoPermitidaError,
                     f"No se puede {operacion} una reserva en estado {self.estado}.")

    def procesar(self):
        self.__exigir_estado(("pendiente",), "procesar")
        self.servicio.comprobar_disponibilidad()
        self.__estado = "procesada"
        logger.info("Reserva procesada: %s", self.identificacion)

    def confirmar(self):
        self.__exigir_estado(("procesada",), "confirmar")
        self.servicio.comprobar_disponibilidad()
        self.__estado = "confirmada"
        logger.info("Reserva confirmada: %s", self.identificacion)

    def cancelar(self):
        self.__exigir_estado(("pendiente", "procesada", "confirmada"), "cancelar")
        self.__estado = "cancelada"
        logger.info("Reserva cancelada: %s", self.identificacion)

    def calcular_costo(self, descuento=0, impuesto=0):
        # Sobrecarga simulada: misma función con cero, uno o dos argumentos.
        return Servicio.ajustar_costo(self.__costo_base, descuento, impuesto)

    def describir(self):
        return f"Reserva {self.identificacion}: {self.estado}, costo COP {self.calcular_costo():,.2f}"

# ============================================================
# 10. LISTAS INTERNAS Y PREPARACIÓN
# ============================================================
# Las tres listas almacenan objetos de demostración sin persistencia. Los datos personales son
# ficticios. Las operaciones de prueba usan listas independientes para comprobar sus efectos.

clientes = []
servicios = []
reservas = []
clientes.append(Cliente("DEMO-1", "Ana Pérez", "ana@example.com", "3001234567"))
servicios.extend([
    ReservaSala("S-1", 50000, 10),
    AlquilerEquipo("E-1", 30000, 2),
    AsesoriaEspecializada("A-1", 80000, "Programación"),
])
reservas.append(Reserva("R-DEMO", clientes[0], servicios[0], 2))
print(f"En memoria: {len(clientes)} cliente, {len(servicios)} servicios, {len(reservas)} reserva.")

# ============================================================
# 11. DEMOSTRACIÓN DE POLIMORFISMO
# ============================================================
# Una lista de Servicio contiene tres clases concretas. Las mismas llamadas ejecutan los métodos
# sobrescritos; se cotiza una hora de sala, un día de dos equipos y una hora de asesoría.

costos_polimorficos = []
for servicio in servicios:
    costo = servicio.calcular_costo()
    costos_polimorficos.append(costo)
    print(f"{servicio.describir_servicio()} → COP {costo:,.2f}")
assert costos_polimorficos == [50000, 60000, 80000]
assert all(isinstance(servicio, Servicio) for servicio in servicios)

# ============================================================
# 12. DEMOSTRACIÓN DE SOBRECARGA SIMULADA
# ============================================================
# Python utiliza una sola firma con parámetros opcionales. Se comprueban tres formas de llamar
# calcular_costo: sin argumentos, con descuento y con descuento e impuesto.

sala = servicios[0]
cotizaciones = [sala.calcular_costo(), sala.calcular_costo(10), sala.calcular_costo(10, 19)]
assert cotizaciones == [50000, 45000, 53550]
for forma, valor in zip(("Sin ajustes", "Descuento 10%", "Descuento 10% e impuesto 19%"), cotizaciones):
    print(f"{forma}: COP {valor:,.2f}")

# ============================================================
# 13. DEMOSTRACIÓN DE TRY/EXCEPT
# ============================================================
# Se intenta cambiar un correo por uno inválido. Se controla la excepción y se verifica que el
# dato anterior permanezca intacto.

correo_anterior = clientes[0].correo
try:
    clientes[0].correo = "correo-incorrecto"
except ClienteInvalidoError as error:
    logger.error("Error controlado al actualizar correo: %s", error)
    print(f"ERROR CONTROLADO: {error}")
assert clientes[0].correo == correo_anterior
print("El cliente mantiene su correo válido; la ejecución continúa.")

# ============================================================
# 14. DEMOSTRACIÓN DE TRY/EXCEPT/ELSE
# ============================================================
# else se ejecuta únicamente cuando el procesamiento de la reserva termina sin excepciones.

procesamiento_exitoso = False
try:
    reservas[0].procesar()
except ErrorSistemaFJ as error:
    logger.error("No se procesó la reserva: %s", error)
    print(f"ERROR CONTROLADO: {error}")
else:
    procesamiento_exitoso = True
    print("ELSE: reserva procesada correctamente.")
assert procesamiento_exitoso and reservas[0].estado == "procesada"

# ============================================================
# 15. DEMOSTRACIÓN DE TRY/EXCEPT/FINALLY
# ============================================================
# Se prueban un caso exitoso y otro inválido. finally registra el fin de cada intento y aumenta
# un contador, independientemente del resultado.

intentos_finalizados = 0
for duracion in (1, -2):
    try:
        temporal = Reserva("R-FINALLY", clientes[0], servicios[0], duracion)
        print(f"Creación correcta: duración {temporal.duracion}.")
    except ErrorSistemaFJ as error:
        logger.error("Error controlado en demostración finally: %s", error)
        print(f"ERROR CONTROLADO: {error}")
    finally:
        intentos_finalizados += 1
        logger.info("FINALLY: intento de reserva finalizado")
        print("FINALLY: intento finalizado.")
assert intentos_finalizados == 2

# ============================================================
# 16. DEMOSTRACIÓN DE ENCADENAMIENTO
# ============================================================
# La conversión de una duración textual inválida produce ValueError. Se transforma en
# ReservaInvalidaError conservando el error original en __cause__; el log guarda la traza de
# ambas excepciones.

causa_comprobada = False
try:
    Reserva("R-CAUSA", clientes[0], servicios[0], "dos horas")
except ReservaInvalidaError as error:
    logger.exception("Excepción encadenada controlada en demostración")
    causa_comprobada = isinstance(error.__cause__, ValueError)
    print(f"ERROR CONTROLADO: {type(error).__name__}: {error}")
    print(f"CAUSA ORIGINAL: {type(error.__cause__).__name__}: {error.__cause__}")
assert causa_comprobada
print("La causa se verificó y el programa continúa.")

# ============================================================
# 17. OPERACIONES DE PRUEBA
# ============================================================
# Cada operación incluye su resultado esperado. Las pruebas positivas comprueban valores o
# efectos; las negativas exigen la excepción concreta. Los fallos inesperados se contabilizan
# sin interrumpir las siguientes pruebas. El resumen final impide declarar éxito si falla
# alguna.

clientes_prueba, servicios_prueba, reservas_prueba = [], [], []
resultados = []

def ejecutar_prueba(numero, titulo, operacion, error_esperado=None):
    print(f"\nPRUEBA {numero} - {titulo}")
    print(f"ESPERADO: {error_esperado.__name__ if error_esperado else 'éxito con comprobación'}")
    correcto = False
    try:
        operacion()
    except Exception as error:
        # La captura general se limita al ejecutor de pruebas para seguir con el resto.
        if error_esperado is not None and type(error) is error_esperado:
            correcto = True
            logger.exception("Prueba %s: excepción esperada controlada", numero)
            print(f"ERROR CONTROLADO: {error}")
            print("RESULTADO: CORRECTO")
        else:
            logger.exception("Prueba %s: fallo inesperado", numero)
            print(f"RESULTADO: FALLO ({type(error).__name__}: {error})")
    else:
        correcto = error_esperado is None
        print("RESULTADO: CORRECTO" if correcto else "RESULTADO: FALLO (no ocurrió la excepción esperada)")
    finally:
        resultados.append((numero, titulo, correcto))
        logger.info("Prueba %s finalizada; aprobada=%s", numero, correcto)

def cliente_correcto():
    cliente = Cliente("1001", "Laura Gómez", "laura@example.com", "+573001234567")
    clientes_prueba.append(cliente)
    assert cliente.nombre == "Laura Gómez" and len(clientes_prueba) == 1

def sala_correcta():
    servicio = ReservaSala("S-T", 50000, 12)
    servicios_prueba.append(servicio)
    assert servicio.calcular_costo(duracion=2) == 100000

def equipo_correcto():
    servicio = AlquilerEquipo("E-T", 30000, 2)
    servicios_prueba.append(servicio)
    assert servicio.calcular_costo(duracion=3) == 180000

def asesoria_correcta():
    servicio = AsesoriaEspecializada("A-T", 80000, "Python")
    servicios_prueba.append(servicio)
    assert servicio.calcular_costo(duracion=1.5) == 120000

def reserva_correcta():
    reserva = Reserva("R-T", clientes_prueba[0], servicios_prueba[0], 2)
    reservas_prueba.append(reserva)
    assert reserva.estado == "pendiente" and reserva.calcular_costo() == 100000

def confirmar_correctamente():
    reserva = reservas_prueba[0]
    reserva.procesar()
    reserva.confirmar()
    assert reserva.estado == "confirmada"

def cancelar_correctamente():
    reservas_prueba[0].cancelar()
    assert reservas_prueba[0].estado == "cancelada"

def servicio_no_disponible():
    servicio = AlquilerEquipo("E-NO", 30000, 1, disponible=False)
    Reserva("R-NO", clientes_prueba[0], servicio, 1)

def actualizacion_invalida():
    cliente = clientes_prueba[0]
    anterior = cliente.correo
    try:
        cliente.correo = "sin-arroba"
    finally:
        assert cliente.correo == anterior

def comprobar_causa():
    try:
        Reserva("R-TEXTO", clientes_prueba[0], servicios_prueba[0], "abc")
    except ReservaInvalidaError as error:
        assert isinstance(error.__cause__, ValueError)
        raise

def comprobar_listas_y_polimorfismo():
    assert len(clientes_prueba) == 1
    assert len(servicios_prueba) == 3
    assert len(reservas_prueba) == 1
    assert [s.calcular_costo() for s in servicios_prueba] == [50000, 60000, 80000]
    assert len({type(s) for s in servicios_prueba}) == 3
    assert all(s.describir_servicio() for s in servicios_prueba)

def comprobar_sobrecarga():
    r = reservas_prueba[0]
    assert (r.calcular_costo(), r.calcular_costo(10), r.calcular_costo(10, 19)) == (100000, 90000, 107100)

def disponibilidad_al_confirmar():
    servicio = ReservaSala("S-DISP", 50000, 4)
    reserva = Reserva("R-DISP", clientes_prueba[0], servicio, 1)
    reserva.procesar()
    servicio.disponible = False
    try:
        reserva.confirmar()
    finally:
        assert reserva.estado == "procesada"

def estado_solo_lectura():
    reservas_prueba[0].estado = "confirmada"

def cliente_actualizado():
    cliente = clientes_prueba[0]
    cliente.nombre = "Laura Gómez Ruiz"
    cliente.correo = "laura.gomez@example.com"
    cliente.telefono = "3109876543"
    assert cliente.nombre == "Laura Gómez Ruiz"
    assert cliente.correo == "laura.gomez@example.com"
    assert cliente.telefono == "3109876543"
    assert not hasattr(cliente, "__correo")

def reanudar_operacion_valida():
    reserva = Reserva("R-CONTINUA", clientes_prueba[0], servicios_prueba[2], 1)
    reserva.procesar()
    reserva.confirmar()
    reservas_prueba.append(reserva)
    assert reserva.estado == "confirmada" and len(reservas_prueba) == 2

print("=" * 60)
print("SOFTWARE FJ - PRUEBAS DEL SISTEMA")
print("=" * 60)
casos = [
    ("Cliente válido y almacenamiento", cliente_correcto, None),
    ("Cliente con nombre vacío", lambda: Cliente("2", " ", "a@example.com", "3001234567"), ClienteInvalidoError),
    ("ReservaSala y costo de dos horas", sala_correcta, None),
    ("Servicio con precio negativo", lambda: ReservaSala("S-X", -1, 2), ServicioInvalidoError),
    ("AlquilerEquipo y costo de tres días", equipo_correcto, None),
    ("Asesoría y costo de hora y media", asesoria_correcta, None),
    ("Reserva válida y costo", reserva_correcta, None),
    ("Reserva con duración negativa", lambda: Reserva("R-X", clientes_prueba[0], servicios_prueba[0], -2), ReservaInvalidaError),
    ("Procesar y confirmar reserva", confirmar_correctamente, None),
    ("Cancelar reserva confirmada", cancelar_correctamente, None),
    ("Cancelar dos veces", lambda: reservas_prueba[0].cancelar(), OperacionNoPermitidaError),
    ("Servicio no disponible", servicio_no_disponible, ServicioNoDisponibleError),
    ("Confirmar una reserva cancelada", lambda: reservas_prueba[0].confirmar(), OperacionNoPermitidaError),
    ("Encapsulación: correo inválido conserva dato", actualizacion_invalida, ClienteInvalidoError),
    ("Duración textual y causa ValueError", comprobar_causa, ReservaInvalidaError),
    ("Alquiler con fracción de día", lambda: Reserva("R-FRAC", clientes_prueba[0], servicios_prueba[1], 1.5), ReservaInvalidaError),
    ("Asesoría menor de una hora", lambda: Reserva("R-CORTA", clientes_prueba[0], servicios_prueba[2], 0.5), ReservaInvalidaError),
    ("Listas y métodos polimórficos", comprobar_listas_y_polimorfismo, None),
    ("Sobrecarga simulada sobre reserva", comprobar_sobrecarga, None),
    ("Porcentaje fuera de rango", lambda: servicios_prueba[0].calcular_costo(101), ServicioInvalidoError),
    ("Precio infinito", lambda: ReservaSala("S-INF", float("inf"), 2), ServicioInvalidoError),
    ("Duración NaN", lambda: Reserva("R-NAN", clientes_prueba[0], servicios_prueba[0], float("nan")), ReservaInvalidaError),
    ("Booleano como duración", lambda: Reserva("R-BOOL", clientes_prueba[0], servicios_prueba[0], True), ReservaInvalidaError),
    ("Cliente de tipo incorrecto", lambda: Reserva("R-CLI", "Laura", servicios_prueba[0], 1), ReservaInvalidaError),
    ("Servicio de tipo incorrecto", lambda: Reserva("R-SRV", clientes_prueba[0], "sala", 1), ReservaInvalidaError),
    ("Disponibilidad al confirmar y estado conservado", disponibilidad_al_confirmar, ServicioNoDisponibleError),
    ("Estado de reserva de solo lectura", estado_solo_lectura, AttributeError),
    ("Actualización válida del cliente", cliente_actualizado, None),
    ("Teléfono inválido", lambda: Cliente("3", "Luis", "luis@example.com", "abc"), ClienteInvalidoError),
    ("Identificación vacía", lambda: Cliente("", "Luis", "luis@example.com", "3001234567"), ClienteInvalidoError),
    ("Capacidad no entera", lambda: ReservaSala("S-CAP", 50000, 2.5), ServicioInvalidoError),
    ("Cantidad de equipos cero", lambda: AlquilerEquipo("E-CERO", 30000, 0), ServicioInvalidoError),
    ("Especialidad vacía", lambda: AsesoriaEspecializada("A-VAC", 80000, ""), ServicioInvalidoError),
    ("Entidad abstracta", lambda: Entidad("X"), TypeError),
    ("Servicio abstracto", lambda: Servicio("X", 1000), TypeError),
    ("Confirmar antes de procesar", lambda: Reserva("R-PEND", clientes_prueba[0], servicios_prueba[0], 1).confirmar(), OperacionNoPermitidaError),
    ("Operación válida después de errores", reanudar_operacion_valida, None),
]
for numero, (titulo, operacion, esperado) in enumerate(casos, 1):
    ejecutar_prueba(numero, titulo, operacion, esperado)

# ============================================================
# 18. RESULTADOS Y CONCLUSIÓN DE EJECUCIÓN
# ============================================================
# El resumen se calcula a partir de las pruebas reales. Se exige que todas aprueben y se
# comprueba que el log contenga eventos, advertencias y errores. Los datos finales permanecen en
# listas en memoria; al terminar el programa se pierden.

aprobadas = sum(correcto for _, _, correcto in resultados)
fallidas = len(resultados) - aprobadas
print("\n" + "=" * 60)
print(f"PRUEBAS FINALIZADAS: {aprobadas}/{len(resultados)} correctas; {fallidas} fallidas.")
print(f"Listas de prueba: {len(clientes_prueba)} cliente, {len(servicios_prueba)} servicios, {len(reservas_prueba)} reservas.")
assert len(resultados) >= 10 and fallidas == 0, "Revisar las pruebas fallidas antes de entregar."
assert procesamiento_exitoso and intentos_finalizados == 2 and causa_comprobada
assert reservas_prueba[0].estado == "cancelada"
assert reservas_prueba[1].estado == "confirmada"
logger.info("Pruebas finalizadas: %s/%s correctas", aprobadas, len(resultados))
for handler in logger.handlers:
    handler.flush()
assert ruta_log.is_file()
contenido_log = ruta_log.read_text(encoding="utf-8")
assert all(nivel in contenido_log for nivel in ("| INFO |", "| WARNING |", "| ERROR |"))
assert "Reserva confirmada" in contenido_log and "Reserva cancelada" in contenido_log
assert "ValueError" in contenido_log and "ReservaInvalidaError" in contenido_log
print("Log verificado: eventos INFO, validaciones WARNING y excepciones ERROR.")
print("El sistema finalizó las pruebas y continuó funcionando correctamente después del manejo de excepciones.")
print("=" * 60)

# Conclusión: se representaron las entidades mediante abstracción, herencia y encapsulación. La
# misma interfaz permitió cotizar tres servicios diferentes; los parámetros opcionales simularon
# sobrecarga. Las excepciones controlaron entradas y transiciones inválidas, mientras el log
# conservó evidencia. El resumen anterior constituye la evidencia de la ejecución, no una
# afirmación previa a las pruebas.

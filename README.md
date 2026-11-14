# Fase 4 - Programación UNAD

## Sistema Integral de Gestión de Clientes, Servicios y Reservas

### Descripción

Software FJ es una empresa ficticia que ofrece reserva de salas, alquiler de equipos y asesorías especializadas. Este proyecto gestiona clientes, servicios y reservas con objetos y listas en memoria. Los datos se reinician al ejecutar todo el notebook; únicamente los eventos y errores se guardan en `sistema.log`.

### Objetivo

Aplicar programación orientada a objetos y manejo avanzado de excepciones en la Fase 4 – Componente práctico – Prácticas simuladas del curso Programación (213023), Ingeniería de Sistemas, UNAD. Versión individual según la autorización del tutor indicada por el estudiante.

### Tecnologías

- Python 3 (validación en Python 3.12).
- Jupyter Notebook.
- Programación Orientada a Objetos.
- `logging`, `abc`, `math`, `re` y `pathlib`, de la biblioteca estándar.

### Conceptos implementados

- Abstracción: `Entidad` y `Servicio` no pueden instanciarse.
- Herencia: `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`; tres servicios concretos heredan de `Servicio`.
- Polimorfismo y métodos sobrescritos: se recorren servicios diferentes con la misma interfaz.
- Encapsulación: datos privados y propiedades validadas en `Cliente`; identidad y estado de reserva de solo lectura.
- Sobrecarga simulada: parámetros opcionales `descuento` e `impuesto` en `calcular_costo` (porcentajes entre 0 y 100).
- Excepciones personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento con `raise ... from ...`.
- Logs de nivel INFO, WARNING y ERROR; las trazas de errores intencionales son evidencia del manejo de excepciones.

### Servicios

- `ReservaSala`: tarifa por hora; capacidad entera positiva.
- `AlquilerEquipo`: tarifa por equipo y día; cantidad y días enteros positivos.
- `AsesoriaEspecializada`: tarifa por hora, mínimo una hora; especialidad no vacía.

Los precios están expresados en pesos colombianos (COP). El descuento se aplica primero y luego el impuesto: `base * (1 - descuento/100) * (1 + impuesto/100)`. Los valores finales se redondean a dos decimales. Es un ejercicio simulado: la disponibilidad se controla con un indicador; no hay calendario, inventario compartido, pagos ni base de datos.

### Ejecución

1. Abrir esta carpeta en VS Code con las extensiones Python y Jupyter, o en Jupyter Notebook/JupyterLab.
2. Seleccionar un kernel Python 3. Si no está disponible: `python -m pip install ipykernel`.
3. Abrir `Fase4_SoftwareFJ.ipynb` y elegir **Reiniciar kernel y ejecutar todas las celdas**.
4. Leer las demostraciones y el resumen de pruebas de las secciones 18 y 19.

Para ejecutar automáticamente desde esta carpeta:

```powershell
python -m pip install nbformat nbclient ipykernel
python -c "import nbformat; from nbclient import NotebookClient; p='Fase4_SoftwareFJ.ipynb'; n=nbformat.read(p, as_version=4); NotebookClient(n, timeout=120, kernel_name='python3', resources={'metadata': {'path': '.'}}).execute(); nbformat.write(n,p)"
```

Estas herramientas son necesarias para ejecutar notebooks; el sistema Software FJ no importa dependencias externas. El log se crea en el directorio de trabajo del kernel (normalmente esta carpeta). Su ruta absoluta se imprime al iniciar. Cada ejecución agrega eventos; no borra evidencias anteriores. No se registran correos ni teléfonos.

### Pruebas

La sección 18 ejecuta operaciones numeradas válidas e inválidas y comprueba resultados con `assert`. Una prueba negativa solo aprueba si ocurre exactamente la excepción prevista; una excepción inesperada o una ausencia de error se reporta como FALLO. Las pruebas continúan y el resumen final exige que todas aprueben. Se verifican costos, estados, listas, encapsulación, disponibilidad y causas de excepciones, además de entradas vacías, booleanos y números no finitos.

El flujo permitido es `pendiente → procesada → confirmada`. Se puede cancelar desde cualquiera de esos tres estados. `cancelada` es terminal. La disponibilidad se comprueba al crear, procesar y confirmar; cancelar sigue permitido si el servicio se deshabilita. La reserva conserva su duración y costo base de creación.

### Autor

Moisés Felipe Chávez De la Hoz  
Programa: Ingeniería de Sistemas  
Universidad Nacional Abierta y a Distancia – UNAD  
Noviembre de 2026

### Repositorio

[Fase4-Programacion-UNAD](https://github.com/moydlahoz/Fase4-Programacion-UNAD)

### Validación realizada y lista de comprobación

Notebook validado con `nbformat` y ejecutado íntegramente con `nbclient` en dos kernels nuevos: **37/37 operaciones correctas en ambas ejecuciones**, sin salidas de error inesperado. Se conservan los resultados en las celdas. La última prueba crea y confirma una reserva después de las pruebas negativas. El log evidencia ambas ejecuciones y las trazas de las excepciones esperadas.

- [x] Clase abstracta general: `Entidad`, sección 4; prueba 34.
- [x] Cliente: sección 5; pruebas 1, 2, 14, 28, 29 y 30.
- [x] Encapsulación: propiedades de Cliente y estado de Reserva; pruebas 14, 27 y 28.
- [x] Clase abstracta Servicio: sección 6; prueba 35.
- [x] ReservaSala: sección 7; prueba 3.
- [x] AlquilerEquipo: sección 8; prueba 5.
- [x] AsesoriaEspecializada: sección 9; prueba 6.
- [x] Herencia: entidades derivadas de Entidad y servicios concretos derivados de Servicio.
- [x] Polimorfismo: sección 12 y prueba 18.
- [x] Métodos sobrescritos: costo, descripción y validación en cada servicio.
- [x] Sobrecarga simulada: sección 13 y prueba 19.
- [x] Clase Reserva: sección 10; pruebas 7 a 13, 16, 17 y 26.
- [x] Listas internas: sección 11; prueba 18 y comprobación final.
- [x] Validaciones: texto, correo, teléfono, tarifa, duración, porcentajes, tipos y finitud.
- [x] Excepciones personalizadas: seis clases en sección 3, todas utilizadas directamente o como base de captura.
- [x] try/except: sección 14.
- [x] try/except/else: sección 15; se comprueba la rama else.
- [x] try/except/finally: sección 16; se comprueba finally con éxito y error.
- [x] Encadenamiento de excepciones: sección 17 y prueba 15, con causa comprobada.
- [x] Sistema de logs: sección 2, niveles INFO/WARNING/ERROR y trazas.
- [x] Archivo sistema.log: generado por el notebook y verificado en sección 19.
- [x] Mínimo 10 operaciones: 37 pruebas numeradas en sección 18.
- [x] Casos válidos: costos, actualización de datos y transiciones permitidas.
- [x] Casos inválidos: errores específicos esperados y comprobados.
- [x] Continuidad después de errores: prueba 37 y resumen de sección 19.
- [x] Sin base de datos: objetos y listas en memoria; solo logs en archivo.
- [x] Código documentado: Markdown, docstrings y comentarios de decisiones relevantes.
- [x] Notebook ejecutable: 38 celdas, 18 de código, ejecución completa validada.
- [x] README: descripción, conceptos, servicios, instrucciones y comprobaciones.
- [x] .gitignore: exclusiones de Python/Jupyter; conserva sistema.log.
- [x] Proyecto publicado en GitHub: enlace real anterior, rama main, commits separados sin alterar fechas ni usar force push.

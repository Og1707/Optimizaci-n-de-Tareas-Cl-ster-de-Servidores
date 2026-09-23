# Optimización de Tareas — Clúster de Servidores

Proyecto académico de Técnicas de Programación que implementa tres enfoques algorítmicos
para resolver el problema de **selección de tareas con máxima ganancia** en un servidor
que solo puede ejecutar una tarea a la vez.

---

## Problema que resuelve

Un clúster de servidores recibe miles de peticiones de procesamiento al día.
Como el servidor solo puede ejecutar **una tarea a la vez**, es necesario elegir
qué tareas ejecutar para **maximizar la ganancia total**, sin que los intervalos
de las tareas seleccionadas se solapen.

Cada tarea tiene:
- `start_time`: tiempo de inicio
- `end_time`: tiempo de finalización
- `profit`: ganancia o prioridad

Este es el problema clásico de **Weighted Interval Scheduling**.

---

## Tres enfoques implementados

| Enfoque | Algoritmo | Complejidad | Óptimo |
|---------|-----------|-------------|--------|
| A | Greedy (voraz) | O(n log n) | ❌ No garantizado |
| B | DP + búsqueda lineal | O(n²) | ✅ Garantizado |
| C | DP + búsqueda binaria | O(n log n) | ✅ Garantizado |

---

## Requisitos

- Python 3.11 o superior
- No se requieren dependencias externas para ejecutar la aplicación
- `pytest` es opcional para ejecutar los tests (también funciona con `unittest`)

---

## Instalación

```bash
# Clonar o descargar el proyecto
cd task_optimizer

# (Opcional) Instalar pytest para una mejor salida de tests
pip install pytest
```

No se requiere ningún paso adicional de instalación.

---

## Estructura del proyecto

```
task_optimizer/
│
├── src/
│   ├── models/
│   │   ├── task.py                         # Modelo Task (dataclass frozen)
│   │   └── result.py                       # Modelo AlgorithmResult
│   │
│   ├── algorithms/
│   │   ├── greedy.py                       # Enfoque A: Greedy O(n log n)
│   │   ├── dynamic_programming_linear.py   # Enfoque B: DP + lineal O(n²)
│   │   └── dynamic_programming_binary.py   # Enfoque C: DP + binaria O(n log n)
│   │
│   ├── generators/
│   │   └── task_generator.py               # Generador de tareas aleatorias
│   │
│   ├── benchmarking/
│   │   └── benchmark.py                    # Sistema de benchmarking real
│   │
│   ├── demonstrations/
│   │   └── demonstrations.py               # Demostraciones para los 4 retos
│   │
│   └── utils/
│       └── formatting.py                   # Formateo de consola
│
├── tests/
│   ├── test_greedy.py                      # 20 tests del Greedy
│   ├── test_dynamic_programming.py         # 30 tests de los algoritmos DP
│   └── test_task_generator.py              # 9 tests del generador y modelo
│
├── docs/
│   ├── arquitectura.md                     # Decisiones de arquitectura
│   ├── algoritmos.md                       # Descripción de algoritmos
│   ├── complejidad.md                      # Análisis de complejidad
│   ├── sustentacion.md                     # Guía para la sustentación
│   └── benchmarking.md                     # Metodología de benchmarking
│
├── main.py                                 # Punto de entrada (menú de consola)
├── requirements.txt                        # Dependencias
└── README.md                               # Este archivo
```

---

## Cómo ejecutar el programa

```bash
cd task_optimizer
python main.py
```

El programa muestra un menú interactivo:

```
=======================================================
   OPTIMIZACIÓN DE TAREAS — CLÚSTER DE SERVIDORES
=======================================================
   Tareas en memoria: ninguna (semilla=42)
───────────────────────────────────────────────────────
  ALGORITMOS
  1. Generar tareas aleatorias
  2. Ejecutar Greedy (Enfoque A)
  3. Ejecutar DP Lineal — O(n²) (Enfoque B)
  4. Ejecutar DP Binaria — O(n log n) (Enfoque C)
  5. Comparar los tres algoritmos
───────────────────────────────────────────────────────
  DEMOSTRACIONES DE SUSTENTACIÓN
  6. Demo Reto 1: Greedy falla vs DP
  7. Demo Reto 2: Impacto del ordenamiento
  8. Demo Reto 3: La recurrencia dp[i] = max(...)
  9. Demo Reto 4: Benchmark de rendimiento
───────────────────────────────────────────────────────
  PRUEBAS
 10. Ejecutar pruebas automatizadas
───────────────────────────────────────────────────────
  0. Salir
```

---

## Cómo ejecutar las pruebas

```bash
cd task_optimizer

# Con unittest (incluido en Python, sin instalar nada):
python -m unittest discover tests -v

# Con pytest (mejor salida):
pytest tests/ -v
```

Resultado esperado: **59 tests, 0 fallos, 0 errores.**

---

## Cómo ejecutar la demostración del Reto 1 (Greedy vs DP)

### Opción A — Desde el menú interactivo:
```bash
python main.py
# Seleccionar opción 6
```

### Opción B — Directamente desde Python:
```python
from src.demonstrations.demonstrations import demo_reto1_greedy_vs_dp
demo_reto1_greedy_vs_dp()
```

Salida esperada:
```
============================================================
   RETO 1: LA TRAMPA DE LA AVARICIA
   Greedy vs Programación Dinámica
============================================================

Tareas del caso de prueba:
  ...
  T1: [0→10], profit=10   <- Greedy la elige
  T2: [0→5],  profit=6
  T3: [5→10], profit=6

RESULTADOS:
  Greedy:     ganancia = 10  (subóptimo)
  DP Lineal:  ganancia = 12  (óptimo)
  DP Binaria: ganancia = 12  (óptimo)

ANÁLISIS:
  Greedy subóptimo: pierde 2 unidades de ganancia.
  DP obtiene la solución óptima: 12
```

---

## Cómo ejecutar el benchmark

```bash
python main.py
# Seleccionar opción 9, luego opción 2 (benchmark completo con N=100,000)
```

O directamente:
```python
from src.benchmarking.benchmark import run_benchmark, print_benchmark_results
results = run_benchmark(sizes=[1000, 5000, 10000, 20000, 50000, 100000], seed=42)
print_benchmark_results(results)
```

Los tiempos son **reales**, medidos con `time.perf_counter()`.

---

## Explicación de los tres algoritmos

### Enfoque A — Greedy

Ordena las tareas de mayor a menor ganancia y selecciona secuencialmente las que
no se solapan con la última seleccionada.

**Por qué puede fallar:** Al elegir la tarea más rentable individualmente, puede
bloquear combinaciones de tareas más pequeñas que juntas producen mayor ganancia.

### Enfoque B — DP + búsqueda lineal

Implementa Weighted Interval Scheduling mediante la recurrencia:

```
dp[i] = max(profit[i] + dp[p(i)], dp[i-1])
```

Donde `p(i)` es el índice de la última tarea compatible con `i`, encontrado
mediante búsqueda lineal (O(n) por tarea).

### Enfoque C — DP + búsqueda binaria

Idéntica recurrencia que el Enfoque B, pero `p(i)` se calcula en O(log n)
usando `bisect.bisect_right()` sobre el array de `end_times` (que está
ordenado porque las tareas están ordenadas por `end_time`).

---

## Complejidades temporales

| Enfoque | Ordenamiento | Búsqueda | DP | Total |
|---------|-------------|----------|----|-------|
| A — Greedy | O(n log n) | — | O(n) | **O(n log n)** |
| B — DP Lineal | O(n log n) | O(n²) | O(n) | **O(n²)** |
| C — DP Binaria | O(n log n) | O(n log n) | O(n) | **O(n log n)** |

## Complejidades espaciales

Todos los algoritmos: **O(n)** — se almacena la lista de tareas y el array dp.

---

## Ejemplo de ejecución

Entrada: 5 tareas aleatorias (seed=42)

```
Ganancia máxima:  850

Tareas seleccionadas (DP Binaria):
  T1: [1200 → 3400], profit=150
  T4: [3400 → 7800], profit=420
  T7: [7900 → 9500], profit=280
```

---

## Limitaciones

1. **DP Lineal con N > 20,000**: La complejidad O(n²) hace que sea impráctica
   para N muy grande. El benchmark omite DP Lineal para N > 20,000.

2. **Interfaz de consola únicamente**: No hay interfaz gráfica (por diseño).

3. **Tiempos enteros**: El modelo usa `int` para tiempos y ganancias.
   No soporta tiempos decimales (no requerido por el enunciado).

---

## Decisiones técnicas relevantes

- **`@dataclass(frozen=True)`**: Las tareas son inmutables. Previene bugs por
  modificación accidental de datos y permite usarlas en sets/dicts.

- **`bisect` de la stdlib**: No se usa ninguna librería externa. `bisect` es
  el módulo estándar de Python para búsqueda binaria en listas ordenadas.

- **`time.perf_counter()`**: El reloj de mayor resolución del sistema.
  Diseñado específicamente para benchmarking de código.

- **Separación modelo/algoritmo/presentación**: Los algoritmos retornan
  `AlgorithmResult`, no imprimen nada. La presentación está en `formatting.py`.

- **Semilla reproducible**: El generador usa `random.Random(seed)` para
  garantizar que el benchmark pueda repetirse bajo las mismas condiciones.

---

## Convención de compatibilidad

Dos tareas A y B son **compatibles** si no se solapan.

La convención adoptada (estándar en Weighted Interval Scheduling):

```
A.end_time <= B.start_time  →  compatibles (el igual está permitido)
```

Una tarea que **termina** en `t=5` es compatible con una que **empieza** en `t=5`.

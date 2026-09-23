# Arquitectura del Proyecto

## Visión general

El proyecto sigue una arquitectura modular con separación de responsabilidades.
Cada componente tiene una única razón para cambiar (principio SOLID: responsabilidad única).

```
task_optimizer/
│
├── src/                        ← Código fuente principal
│   ├── models/                 ← Modelos de datos (qué son los datos)
│   ├── algorithms/             ← Lógica algorítmica pura (qué hacen)
│   ├── generators/             ← Generación de datos de prueba
│   ├── benchmarking/           ← Medición de rendimiento
│   ├── demonstrations/         ← Escenarios de demostración
│   └── utils/                  ← Presentación en consola
│
├── tests/                      ← Pruebas automatizadas
├── docs/                       ← Documentación técnica
└── main.py                     ← Punto de entrada
```

---

## Decisiones de arquitectura

### 1. Modelos de datos inmutables (`frozen=True`)

```python
@dataclass(frozen=True)
class Task:
    id: int
    start_time: int
    end_time: int
    profit: int
```

**Por qué:**
- Una tarea del servidor es un dato fijo: no cambia después de recibirse.
- `frozen=True` previene modificaciones accidentales (bug frecuente en algoritmos).
- Genera `__hash__` automáticamente → permite usar tareas en sets y dicts.
- Facilita el razonamiento: una función que recibe una Task sabe que no puede cambiarla.

**Alternativa descartada:** Usar diccionarios `{"id": 1, "start": 0}`.
Desventaja: no hay validación, no hay type hints, el código es menos legible.

---

### 2. Resultado tipado (`AlgorithmResult`)

Todos los algoritmos retornan el mismo tipo `AlgorithmResult`:

```python
@dataclass
class AlgorithmResult:
    selected_tasks: List[Task]
    total_profit: int
    algorithm_name: str
```

**Por qué:**
- Permite comparar resultados de diferentes algoritmos de forma uniforme.
- Facilita los tests (mismo tipo de dato para comparar).
- El benchmarking puede procesar resultados sin saber qué algoritmo los generó.
- Evita que los algoritmos mezclen lógica de cálculo con lógica de presentación.

**Alternativa descartada:** Retornar solo `int` (la ganancia máxima).
Desventaja: no permite verificar qué tareas fueron seleccionadas (necesario para el Reto 3).

---

### 3. Algoritmos como funciones puras

Los tres algoritmos son funciones (no clases):

```python
def greedy_task_selection(tasks: List[Task]) -> AlgorithmResult: ...
def dp_linear_task_selection(tasks: List[Task]) -> AlgorithmResult: ...
def dp_binary_task_selection(tasks: List[Task]) -> AlgorithmResult: ...
```

**Por qué:**
- El algoritmo no tiene estado. Misma entrada → misma salida siempre.
- Más fácil de testear: basta con llamar la función y verificar el resultado.
- No hay efectos secundarios ocultos.
- La firma es autodocumentada: recibe tareas, retorna resultado.

**Alternativa descartada:** Clases `GreedySolver`, `DPLinearSolver`, etc.
Desventaja: agrega complejidad innecesaria sin beneficio real para este problema.

---

### 4. Separación algoritmo/presentación

Los algoritmos **no imprimen nada**. Solo calculan y retornan.

La presentación está en `src/utils/formatting.py`.

**Por qué:**
- Un algoritmo debe ser reutilizable en diferentes contextos (tests, benchmarks, GUI).
- Si los algoritmos imprimieran, los tests capturarían salida no relevante.
- Facilita el benchmarking: se mide solo el tiempo del algoritmo, no el de imprimir.

---

### 5. Generador como módulo independiente

El generador de tareas está en `src/generators/`, separado de los algoritmos.

**Por qué:**
- Los algoritmos no deben depender de cómo se generan los datos.
- El generador puede cambiarse sin afectar los algoritmos.
- Permite usar el generador en tests, benchmarks y demostraciones por separado.

---

### 6. Demostraciones como módulo independiente

Las demostraciones están en `src/demonstrations/`, separadas de los algoritmos.

**Por qué:**
- Las demostraciones son escenarios pedagógicos, no lógica de producción.
- Pueden modificarse sin afectar el comportamiento de los algoritmos.
- El estudiante puede abrir `demonstrations.py` y leer inmediatamente
  qué hace cada demostración para la sustentación.

---

## Flujo de dependencias

```
main.py
  ├── src/generators/task_generator.py
  ├── src/algorithms/greedy.py
  │     └── src/models/ (Task, AlgorithmResult)
  ├── src/algorithms/dynamic_programming_linear.py
  │     └── src/models/ (Task, AlgorithmResult)
  ├── src/algorithms/dynamic_programming_binary.py
  │     └── src/models/ (Task, AlgorithmResult)
  ├── src/benchmarking/benchmark.py
  │     ├── src/generators/task_generator.py
  │     └── src/algorithms/ (lineal y binaria)
  ├── src/demonstrations/demonstrations.py
  │     ├── src/algorithms/ (los tres)
  │     ├── src/generators/task_generator.py
  │     └── src/utils/formatting.py
  └── src/utils/formatting.py
        └── src/models/ (Task, AlgorithmResult)
```

Las dependencias fluyen en una sola dirección: desde el nivel superior hacia abajo.
No hay dependencias circulares.

---

## Qué no se hizo y por qué

- **No se usaron clases abstractas ni interfaces**: El problema no lo requiere.
  Las tres funciones tienen la misma firma, lo cual es suficiente polimorfismo.

- **No se usó herencia**: No existe una relación "es-un" entre los algoritmos.

- **No se usó un framework web o CLI**: El problema es académico y la interfaz
  de consola es suficiente. Agregar frameworks añadiría dependencias sin valor.

- **No se usó numpy u otras librerías de datos**: El módulo `bisect` de la
  stdlib es suficiente para la búsqueda binaria. Numpy añadiría instalación
  innecesaria.

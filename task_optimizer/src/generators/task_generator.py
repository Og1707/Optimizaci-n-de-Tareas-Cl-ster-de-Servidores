"""
Generador de tareas aleatorias para el clúster de servidores.

Propósito:
    Producir conjuntos de tareas controlados y reproducibles para:
    - Pruebas unitarias (semilla fija → mismo resultado siempre).
    - Benchmarking (misma entrada para todos los algoritmos).
    - Demostraciones (casos predefinidos con comportamiento conocido).

Decisión de diseño:
    Se usa el módulo estándar `random` con una semilla explícita para garantizar
    reproducibilidad. No se usan dependencias externas (numpy, etc.) para mantener
    el proyecto liviano y fácil de ejecutar en cualquier entorno.
"""

import random
from typing import List

from src.models.task import Task


def generate_tasks(
    n: int,
    seed: int = 42,
    max_time: int = 100_000,
    max_profit: int = 1_000,
    min_duration: int = 1,
) -> List[Task]:
    """
    Genera una lista de n tareas aleatorias con tiempos y ganancias válidos.

    Garantías de los datos generados:
        - start_time < end_time  (la tarea tiene duración positiva)
        - profit > 0             (toda tarea tiene valor)
        - Los tiempos están dentro del rango [0, max_time]

    Diseño del generador:
        1. Se elige un start_time aleatorio en [0, max_time - min_duration].
        2. Se elige un end_time aleatorio en [start_time + min_duration, max_time].
        3. Se elige un profit aleatorio en [1, max_profit].

        Este diseño produce una distribución de tareas que superpone muchas entre sí,
        lo cual es necesario para que los algoritmos de optimización tengan sentido
        y para que las diferencias de complejidad sean observables.

    Args:
        n:            Número de tareas a generar.
        seed:         Semilla para el generador aleatorio. Garantiza reproducibilidad.
        max_time:     Límite superior del horizonte temporal.
        max_profit:   Ganancia máxima posible por tarea.
        min_duration: Duración mínima de cada tarea (evita tareas de duración 0).

    Returns:
        Lista de n objetos Task con datos válidos, ordenados por id.

    Raises:
        ValueError: Si n < 0 o los parámetros son incoherentes.

    Ejemplos:
        >>> tasks = generate_tasks(n=5, seed=42)
        >>> len(tasks)
        5
        >>> all(t.start_time < t.end_time for t in tasks)
        True
        >>> all(t.profit > 0 for t in tasks)
        True
    """
    if n < 0:
        raise ValueError(f"n debe ser >= 0, se recibió: {n}")
    if max_time < min_duration:
        raise ValueError(
            f"max_time ({max_time}) debe ser >= min_duration ({min_duration})."
        )
    if n == 0:
        return []

    rng = random.Random(seed)
    tasks: List[Task] = []

    for task_id in range(1, n + 1):
        # start_time: cualquier punto que deje espacio para al menos min_duration
        start_time = rng.randint(0, max_time - min_duration)
        # end_time: al menos min_duration después del inicio
        end_time = rng.randint(start_time + min_duration, max_time)
        # profit: entero positivo
        profit = rng.randint(1, max_profit)

        tasks.append(Task(id=task_id, start_time=start_time, end_time=end_time, profit=profit))

    return tasks


def generate_greedy_failure_case() -> List[Task]:
    """
    Genera un caso determinista donde el algoritmo Greedy falla.

    Este caso existe para el Reto 1 de la sustentación.

    Construcción del caso:
        - T1: [0 → 10], profit=10  ← Greedy la elige primero (mayor ganancia)
        - T2: [0 →  5], profit=6
        - T3: [5 → 10], profit=6
        - T4: [2 →  8], profit=9   ← Greedy intenta elegirla pero solapa con T1

        Resultado Greedy:    T1          → ganancia = 10
        Resultado Óptimo:    T2 + T3     → ganancia = 12

        El Greedy elige T1 porque tiene la mayor ganancia individual.
        Sin embargo, la combinación T2 + T3 produce mayor ganancia total.
        Este es el error fundamental del Greedy: optimizar localmente no
        garantiza la solución óptima global.

    Returns:
        Lista de 4 tareas que demuestran el fallo del Greedy.
    """
    return [
        Task(id=1, start_time=0, end_time=10, profit=10),  # Greedy la elige
        Task(id=2, start_time=0, end_time=5,  profit=6),   # Compatible con T3
        Task(id=3, start_time=5, end_time=10, profit=6),   # Compatible con T2
        Task(id=4, start_time=2, end_time=8,  profit=9),   # Alternativa media
    ]


def generate_all_compatible_tasks(n: int = 5) -> List[Task]:
    """
    Genera n tareas que no se solapan entre sí.
    Útil para verificar que los algoritmos seleccionan todas las tareas.

    Returns:
        Lista de n tareas consecutivas sin solapamiento.
    """
    tasks = []
    for i in range(1, n + 1):
        start = (i - 1) * 10
        end = i * 10
        tasks.append(Task(id=i, start_time=start, end_time=end, profit=i * 10))
    return tasks


def generate_all_overlapping_tasks(n: int = 5) -> List[Task]:
    """
    Genera n tareas que todas se solapan entre sí.
    Solo una puede ser seleccionada. La óptima es la de mayor ganancia.

    Returns:
        Lista de n tareas que comparten el mismo intervalo [0, 100].
    """
    tasks = []
    for i in range(1, n + 1):
        tasks.append(Task(id=i, start_time=0, end_time=100, profit=i * 10))
    return tasks

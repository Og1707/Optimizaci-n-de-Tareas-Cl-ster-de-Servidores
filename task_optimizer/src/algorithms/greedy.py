"""
Enfoque A — Algoritmo Greedy (Voraz) para selección de tareas.

IDEA DEL ALGORITMO:
    Ordenar las tareas de mayor a menor ganancia y seleccionar secuencialmente
    aquellas que no se solapen con la última tarea ya seleccionada.

ADVERTENCIA IMPORTANTE:
    Este algoritmo NO garantiza la solución óptima.
    Toma decisiones localmente óptimas (la tarea de mayor ganancia disponible)
    sin considerar el impacto global de esa decisión.

    Ejemplo de fallo:
        T1: [0→10], profit=10  ← Greedy la elige (máxima ganancia individual)
        T2: [0→5],  profit=6
        T3: [5→10], profit=6

        Greedy:  T1          → ganancia = 10
        Óptimo:  T2 + T3     → ganancia = 12

    El Greedy cae en una "trampa": al elegir T1 (la más rentable individualmente),
    bloquea la posibilidad de combinar T2 + T3, que juntas generan más ganancia.

COMPLEJIDAD TEMPORAL:
    - Ordenamiento: O(n log n)
    - Recorrido de selección: O(n)
    - Total: O(n log n)

COMPLEJIDAD ESPACIAL:
    - O(n) para almacenar las tareas y el resultado.
"""

from typing import List

from src.models.task import Task
from src.models.result import AlgorithmResult


def greedy_task_selection(tasks: List[Task]) -> AlgorithmResult:
    """
    Selecciona tareas usando el enfoque Greedy (voraz).

    Estrategia:
        1. Ordenar tareas de MAYOR a MENOR ganancia.
        2. Recorrer la lista ordenada.
        3. Seleccionar una tarea si no se solapa con la última seleccionada.

    La condición de compatibilidad es:
        tarea_candidata.start_time >= ultima_seleccionada.end_time

    Esto significa que la nueva tarea puede comenzar exactamente cuando
    termina la última (end_time <= start_time, el igual está permitido).

    Args:
        tasks: Lista de tareas a evaluar. No se modifica (copia interna).

    Returns:
        AlgorithmResult con las tareas seleccionadas y la ganancia total.
    """
    if not tasks:
        return AlgorithmResult(
            selected_tasks=[],
            total_profit=0,
            algorithm_name="Greedy"
        )

    # PASO 1: Ordenar de mayor a menor ganancia.
    # Esta es la decisión "voraz": priorizar siempre la tarea más rentable.
    sorted_tasks = sorted(tasks, key=lambda task: task.profit, reverse=True)

    selected: List[Task] = []
    last_end_time: int = -1  # Marca el fin de la última tarea seleccionada

    # PASO 2: Recorrer en orden de ganancia decreciente
    for task in sorted_tasks:
        # PASO 3: Seleccionar si no hay solapamiento con la última seleccionada
        # Convención: end_time <= start_time → compatible (el igual es válido)
        if task.start_time >= last_end_time:
            selected.append(task)
            last_end_time = task.end_time

    total_profit = sum(t.profit for t in selected)

    return AlgorithmResult(
        selected_tasks=selected,
        total_profit=total_profit,
        algorithm_name="Greedy"
    )

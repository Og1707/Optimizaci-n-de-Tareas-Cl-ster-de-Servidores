"""
Enfoque C — Programación Dinámica con búsqueda binaria del compatible (Weighted Interval Scheduling).

RELACIÓN CON EL ENFOQUE B:
    Este algoritmo implementa exactamente la misma recurrencia que el Enfoque B:

        dp[i] = max(profit[i] + dp[p(i)], dp[i-1])

    La ÚNICA diferencia es cómo se encuentra p(i): el índice de la última
    tarea compatible con la tarea i.

    - Enfoque B: búsqueda LINEAL  → O(n)  por cada tarea → O(n²) total
    - Enfoque C: búsqueda BINARIA → O(log n) por cada tarea → O(n log n) total

    Ambos producen exactamente la misma ganancia máxima.
    La diferencia es únicamente de rendimiento.

POR QUÉ FUNCIONA LA BÚSQUEDA BINARIA AQUÍ:
    La búsqueda binaria requiere que los datos estén ordenados.
    Como las tareas están ordenadas por end_time ascendente, el array
    de end_times forma una secuencia ordenada.

    Para buscar p(i) (última tarea j tal que tasks[j].end_time <= tasks[i].start_time),
    podemos hacer una búsqueda binaria sobre el array de end_times.

    Usamos bisect_right del módulo estándar `bisect`:
        bisect_right(end_times, tasks[i].start_time)
    Retorna el índice de inserción para tasks[i].start_time en end_times,
    que equivale al número de tareas que terminan <= tasks[i].start_time.

POR QUÉ SOLO FUNCIONA CON end_time ORDENADO:
    Si las tareas NO estuvieran ordenadas por end_time:
    - El array de end_times no estaría ordenado.
    - bisect_right daría resultados incorrectos.
    - p(i) sería incorrecto → la recurrencia fallaría.

    La búsqueda binaria es una optimización que DEPENDE del ordenamiento previo.

DESGLOSE DE LA COMPLEJIDAD TEMPORAL:
    1. Ordenamiento por end_time:         O(n log n)  ← algoritmo de sorting estándar
    2. Construcción del array end_times:  O(n)
    3. Construcción del DP:
       - Para cada tarea i (n tareas):    O(n)
       - Búsqueda binaria de p(i):        O(log n)
       - Total:                           O(n log n)
    4. Reconstrucción de la solución:     O(n log n)  ← n tareas × O(log n) por búsqueda
    ────────────────────────────────────────────────────
    TOTAL:                                O(n log n)  ← dominado por sorting + búsquedas

    Comparación con Enfoque B:            O(n²)
    Mejora para n=100.000:                ~100.000/17 ≈ 5.882x más rápido teóricamente.

COMPLEJIDAD ESPACIAL:
    - dp[]:            O(n)
    - end_times[]:     O(n)
    - sorted_tasks[]:  O(n)
    - TOTAL:           O(n)
"""

import bisect
from typing import List

from src.models.task import Task
from src.models.result import AlgorithmResult


def _find_last_compatible_binary(end_times: List[int], start_time: int) -> int:
    """
    Encuentra el índice (base 1) de la última tarea compatible mediante
    búsqueda BINARIA.

    Precondición:
        end_times debe ser un array ORDENADO ASCENDENTEMENTE de tiempos de
        finalización. Esto se garantiza porque las tareas están ordenadas
        por end_time antes de llamar a esta función.

    Lógica:
        Buscamos cuántas tareas terminan en un tiempo <= start_time.
        bisect_right(end_times, start_time) retorna el índice de inserción
        correcto en la lista ordenada, que equivale al conteo de elementos
        <= start_time.

        Este valor es directamente el índice base-1 del último compatible,
        ya que dp usa base 1 (dp[0] = caso vacío).

    Complejidad: O(log n)  ← ventaja clave sobre la búsqueda lineal O(n)

    Args:
        end_times:  Lista ordenada de tiempos de finalización (base 0).
        start_time: Tiempo de inicio de la tarea actual.

    Returns:
        Número de tareas compatibles anteriores (índice base-1 del dp).
        Retorna 0 si ninguna tarea es compatible.
    """
    # bisect_right devuelve el índice donde se insertaría start_time
    # en la lista ordenada end_times, manteniendo el orden.
    # Equivale a: ¿cuántas tareas tienen end_time <= start_time?
    return bisect.bisect_right(end_times, start_time)


def dp_binary_task_selection(tasks: List[Task]) -> AlgorithmResult:
    """
    Selecciona tareas con ganancia máxima usando Programación Dinámica
    y búsqueda BINARIA para encontrar la última tarea compatible.

    Misma recurrencia que el Enfoque B, mejor complejidad temporal.
    Garantiza la SOLUCIÓN ÓPTIMA.

    Pasos:
        1. Ordenar las tareas por end_time ascendente. (O(n log n))
        2. Construir el array de end_times para búsqueda binaria. (O(n))
        3. Construir el array dp[] con la recurrencia. (O(n log n))
        4. Reconstruir la solución óptima recorriendo dp[] hacia atrás. (O(n log n))

    Args:
        tasks: Lista de tareas a evaluar. No se modifica.

    Returns:
        AlgorithmResult con las tareas óptimas y la ganancia máxima.
    """
    if not tasks:
        return AlgorithmResult(
            selected_tasks=[],
            total_profit=0,
            algorithm_name="DP Binaria"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 1: Ordenar por end_time ASCENDENTE.
    #
    # RETO 2 — LÍNEA CLAVE (idéntica al Enfoque B):
    #   Esta línea es el fundamento de ambos algoritmos DP.
    #   Cambiarla rompe la recurrencia (ver doc del Enfoque B para la
    #   explicación matemática completa).
    #
    # ADICIONALMENTE en el Enfoque C:
    #   El ordenamiento es también prerequisito para que bisect_right funcione.
    #   Si end_times no está ordenado, bisect_right devuelve resultados incorrectos.
    # ─────────────────────────────────────────────────────────────────────────
    sorted_tasks = sorted(tasks, key=lambda task: task.end_time)  # ← RETO 2: esta línea

    n = len(sorted_tasks)

    # Precomputar el array de end_times ordenados para usar con bisect.
    # Este array permite búsqueda binaria en O(log n) en lugar de O(n).
    end_times: List[int] = [task.end_time for task in sorted_tasks]

    # dp[i] = máxima ganancia considerando las primeras i tareas (base 1)
    # dp[0] = 0 → caso base: sin tareas, ganancia = 0
    dp: List[int] = [0] * (n + 1)

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 2: Construcción de la tabla DP.
    # ─────────────────────────────────────────────────────────────────────────
    for i in range(1, n + 1):
        current_task = sorted_tasks[i - 1]

        # p(i): índice del último compatible (base 1). O(log n) por búsqueda binaria.
        # Esta es la única diferencia con el Enfoque B.
        p_i = _find_last_compatible_binary(end_times[:i - 1], current_task.start_time)
        # Nota: usamos end_times[:i-1] para buscar solo entre las tareas anteriores,
        # excluyendo la tarea actual.

        # ─────────────────────────────────────────────────────────────────────
        # RETO 3 — LA RECURRENCIA (idéntica al Enfoque B):
        #
        #   dp[i] = max(
        #       current_task.profit + dp[p_i],   # Opción 1: TOMAR la tarea i
        #       dp[i - 1]                          # Opción 2: RECHAZAR la tarea i
        #   )
        #
        # Esta recurrencia es exactamente igual al Enfoque B.
        # Solo cambió cómo calculamos p_i: O(log n) en vez de O(n).
        # ─────────────────────────────────────────────────────────────────────
        take_task = current_task.profit + dp[p_i]   # Opción 1: tomar
        skip_task = dp[i - 1]                        # Opción 2: rechazar

        dp[i] = max(take_task, skip_task)            # ← RETO 3: recurrencia

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 3: Reconstrucción de la solución óptima.
    #
    # Mismo procedimiento que el Enfoque B, pero usando búsqueda binaria
    # para calcular p_i durante la reconstrucción.
    # ─────────────────────────────────────────────────────────────────────────
    selected: List[Task] = []
    i = n
    while i >= 1:
        current_task = sorted_tasks[i - 1]
        p_i = _find_last_compatible_binary(end_times[:i - 1], current_task.start_time)

        if current_task.profit + dp[p_i] >= dp[i - 1]:
            selected.append(current_task)
            i = p_i
        else:
            i -= 1

    selected.reverse()  # Ordenar por tiempo de inicio para presentación

    return AlgorithmResult(
        selected_tasks=selected,
        total_profit=dp[n],
        algorithm_name="DP Binaria"
    )

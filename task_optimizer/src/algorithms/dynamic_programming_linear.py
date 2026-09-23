"""
Enfoque B — Programación Dinámica con búsqueda lineal del compatible (Weighted Interval Scheduling).

PROBLEMA QUE RESUELVE:
    Dado un conjunto de tareas con intervalos [start, end] y ganancias,
    encontrar el subconjunto de tareas compatibles (sin solapamiento) que
    maximiza la ganancia total.

    Este es el problema clásico de "Weighted Interval Scheduling".

POR QUÉ EL GREEDY FALLA Y LA DP ES NECESARIA:
    El Greedy toma decisiones locales sin ver el futuro.
    La Programación Dinámica evalúa sistemáticamente TODAS las posibilidades
    mediante una recurrencia que garantiza la optimalidad global.

FUNDAMENTO MATEMÁTICO — LA RECURRENCIA:

    Sea dp[i] = la máxima ganancia obtenible considerando las primeras i tareas
                (ordenadas por end_time ascendente).

    Sea p(i) = índice de la última tarea compatible con la tarea i.
               Una tarea j es compatible con i si j.end_time <= i.start_time.
               p(i) = índice más alto j tal que j.end_time <= i.start_time.
               Si no existe tal j, p(i) = 0.

    RECURRENCIA:
        dp[0] = 0  (caso base: sin tareas, ganancia = 0)

        dp[i] = max(
            tasks[i-1].profit + dp[p(i)],   # OPCIÓN 1: Tomar la tarea i
            dp[i-1]                           # OPCIÓN 2: Rechazar la tarea i
        )

    INTERPRETACIÓN EN TÉRMINOS DEL SERVIDOR:
        - "Tomar la tarea i":
            Ejecutar la tarea i y sumar la mejor ganancia posible con las
            tareas que terminaron ANTES de que i empiece (dp[p(i)]).
            → El servidor ejecuta esta tarea ahora.

        - "Rechazar la tarea i":
            No ejecutar la tarea i y conservar la mejor solución encontrada
            hasta el momento con las i-1 tareas anteriores (dp[i-1]).
            → El servidor prefiere una combinación anterior de tareas.

POR QUÉ ORDENAR POR end_time ES FUNDAMENTAL:
    La recurrencia dp[i] depende de dp[p(i)] y dp[i-1].
    Para que dp[i-1] represente "la mejor solución con las tareas anteriores",
    es necesario que las tareas estén ordenadas de forma consistente.

    Si ordenamos por end_time:
        - dp[i-1] representa la mejor solución con tareas que terminan antes.
        - p(i) puede encontrarse mirando hacia atrás: buscamos la tarea j
          con mayor índice tal que j.end_time <= i.start_time.
        - Esto es correcto porque las tareas con índice menor terminan antes
          (o al mismo tiempo).

    Si ordenamos por start_time o profit:
        - dp[i-1] ya no representa "las tareas que podrían ser compatibles".
        - La búsqueda de p(i) puede devolver índices incorrectos.
        - La recurrencia se rompe → resultados incorrectos.

COMPLEJIDAD TEMPORAL:
    - Ordenamiento:                O(n log n)
    - Construcción del DP:
        - Para cada tarea i (n tareas):           O(n)
        - Se busca p(i) con búsqueda lineal:      O(n)
        - Total búsquedas:                        O(n²)
    - Reconstrucción de la solución:              O(n)
    - TOTAL:                                      O(n²)  ← dominado por la búsqueda lineal

COMPLEJIDAD ESPACIAL:
    - dp[]:  O(n)
    - Lista de tareas ordenadas: O(n)
    - TOTAL: O(n)
"""

from typing import List

from src.models.task import Task
from src.models.result import AlgorithmResult


def _find_last_compatible_linear(tasks: List[Task], index: int) -> int:
    """
    Encuentra el índice de la última tarea compatible con tasks[index]
    mediante búsqueda LINEAL (de derecha a izquierda).

    Una tarea j es compatible con la tarea i si:
        tasks[j].end_time <= tasks[index].start_time

    Precondición:
        Las tareas deben estar ordenadas por end_time ascendente.
        Bajo esta condición, buscar de derecha a izquierda desde index-1
        garantiza encontrar el índice MÁS ALTO posible.

    Complejidad: O(n) en el peor caso (cuando no hay compatibles o el
                 compatible está al inicio de la lista).

    Args:
        tasks: Lista de tareas ordenadas por end_time ascendente (índice base 0).
        index: Índice de la tarea actual (base 0).

    Returns:
        Índice base-1 de la última tarea compatible.
        Retorna 0 si no existe ninguna tarea compatible (equivale a dp[0] = 0).
    """
    task_start = tasks[index].start_time

    # Búsqueda lineal: recorremos desde index-1 hacia 0
    # Buscamos la primera (más a la derecha) que termina a tiempo
    # Complejidad: O(n) en el peor caso
    for j in range(index - 1, -1, -1):
        if tasks[j].end_time <= task_start:
            # +1 porque dp usa índice base 1 (dp[0] es el caso base vacío)
            return j + 1

    # Ninguna tarea es compatible: retornamos 0 (dp[0] = 0)
    return 0


def dp_linear_task_selection(tasks: List[Task]) -> AlgorithmResult:
    """
    Selecciona tareas con ganancia máxima usando Programación Dinámica
    y búsqueda lineal para encontrar la última tarea compatible.

    Garantiza la SOLUCIÓN ÓPTIMA (a diferencia del Greedy).

    Pasos:
        1. Ordenar las tareas por end_time ascendente.
           → CRÍTICO: sin este orden, la recurrencia es incorrecta.
        2. Construir el array dp[] con la recurrencia.
        3. Reconstruir la solución óptima recorriendo dp[] hacia atrás.

    Args:
        tasks: Lista de tareas a evaluar. No se modifica (se crea copia).

    Returns:
        AlgorithmResult con las tareas óptimas y la ganancia máxima.
    """
    if not tasks:
        return AlgorithmResult(
            selected_tasks=[],
            total_profit=0,
            algorithm_name="DP Lineal"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 1: Ordenar por end_time ASCENDENTE.
    #
    # RETO 2 — LÍNEA CLAVE: Esta línea define el orden que hace funcionar la DP.
    #
    # Fundamento matemático:
    #   La recurrencia dp[i] = max(profit[i] + dp[p(i)], dp[i-1]) requiere que
    #   dp[i-1] represente "la mejor solución con tareas de índice anterior".
    #   Si las tareas están ordenadas por end_time, entonces las tareas con
    #   índice menor SIEMPRE terminan antes (o al mismo tiempo) que la tarea i.
    #   Esto garantiza que p(i) pueda encontrarse mirando hacia la izquierda.
    #
    # Cambiar este orden por start_time o profit ROMPE la recurrencia porque:
    #   - dp[i-1] ya no representa "tareas que terminaron antes".
    #   - La búsqueda de p(i) puede encontrar tareas que en realidad no son
    #     compatibles con la tarea i bajo el nuevo orden.
    # ─────────────────────────────────────────────────────────────────────────
    sorted_tasks = sorted(tasks, key=lambda task: task.end_time)  # ← RETO 2: esta línea

    n = len(sorted_tasks)

    # dp[i] = máxima ganancia considerando las primeras i tareas (base 1)
    # dp[0] = 0 → caso base: sin tareas, ganancia = 0
    dp: List[int] = [0] * (n + 1)

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 2: Construcción de la tabla DP.
    #
    # Para cada tarea i (1-indexed), decidimos:
    #   ¿Conviene ejecutar esta tarea o es mejor ignorarla?
    # ─────────────────────────────────────────────────────────────────────────
    for i in range(1, n + 1):
        current_task = sorted_tasks[i - 1]  # La tarea actual (0-indexed en la lista)

        # p(i): índice del último compatible (base 1). O(n) por búsqueda lineal.
        p_i = _find_last_compatible_linear(sorted_tasks, i - 1)

        # ─────────────────────────────────────────────────────────────────────
        # RETO 3 — LA RECURRENCIA (línea más importante del algoritmo):
        #
        #   dp[i] = max(
        #       current_task.profit + dp[p_i],   # Opción 1: TOMAR la tarea i
        #       dp[i - 1]                          # Opción 2: RECHAZAR la tarea i
        #   )
        #
        # Opción 1 — Tomar la tarea i:
        #   Ejecutamos la tarea actual y acumulamos la mejor ganancia posible
        #   con las tareas compatibles anteriores (dp[p_i]).
        #   → El servidor ejecuta esta tarea.
        #
        # Opción 2 — Rechazar la tarea i:
        #   No ejecutamos la tarea actual y conservamos la mejor solución
        #   encontrada hasta ahora con las i-1 tareas anteriores (dp[i-1]).
        #   → El servidor prefiere una combinación de tareas anteriores.
        #
        # El max() garantiza que siempre elegimos la decisión más rentable.
        # ─────────────────────────────────────────────────────────────────────
        take_task = current_task.profit + dp[p_i]   # Opción 1: tomar
        skip_task = dp[i - 1]                        # Opción 2: rechazar

        dp[i] = max(take_task, skip_task)            # ← RETO 3: recurrencia

    # ─────────────────────────────────────────────────────────────────────────
    # PASO 3: Reconstrucción de la solución óptima.
    #
    # Recorremos dp[] hacia atrás para determinar qué tareas fueron seleccionadas.
    # Una tarea i fue seleccionada si dp[i] != dp[i-1].
    # (Si dp[i] == dp[i-1], fue más rentable rechazar la tarea.)
    # ─────────────────────────────────────────────────────────────────────────
    selected: List[Task] = []
    i = n
    while i >= 1:
        current_task = sorted_tasks[i - 1]
        p_i = _find_last_compatible_linear(sorted_tasks, i - 1)

        if current_task.profit + dp[p_i] >= dp[i - 1]:
            # Se eligió tomar la tarea i
            selected.append(current_task)
            i = p_i  # Saltamos al último compatible
        else:
            # Se eligió rechazar la tarea i
            i -= 1

    selected.reverse()  # Ordenar por tiempo de inicio para presentación

    return AlgorithmResult(
        selected_tasks=selected,
        total_profit=dp[n],
        algorithm_name="DP Lineal"
    )

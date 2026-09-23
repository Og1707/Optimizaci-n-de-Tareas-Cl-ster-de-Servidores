"""
Módulo de demostraciones para la sustentación del proyecto.

Cada demostración es independiente, directa y autodescriptiva.
El estudiante puede abrir este archivo y entender inmediatamente
qué hace cada demostración y por qué es importante.

DEMOSTRACIONES DISPONIBLES:
    - demo_reto1_greedy_vs_dp(): Muestra el caso donde Greedy falla.
    - demo_reto2_ordering_impact(): Muestra por qué el orden importa en DP.
    - demo_reto3_recurrence(): Traza paso a paso la recurrencia dp[i] = max(...)
    - demo_reto4_benchmark(): Ejecuta el benchmark de rendimiento.
"""

from src.models.task import Task
from src.generators.task_generator import (
    generate_greedy_failure_case,
    generate_tasks,
)
from src.algorithms.greedy import greedy_task_selection
from src.algorithms.dynamic_programming_linear import dp_linear_task_selection
from src.algorithms.dynamic_programming_binary import dp_binary_task_selection
from src.benchmarking.benchmark import run_benchmark, print_benchmark_results
from src.utils.formatting import print_tasks_table, print_result_summary


def demo_reto1_greedy_vs_dp() -> None:
    """
    RETO 1: Demuestra que el Greedy puede producir una solución inferior a la óptima.

    Muestra el caso clásico donde la avaricia local no conduce al óptimo global.
    """
    print("\n" + "=" * 60)
    print("   RETO 1: LA TRAMPA DE LA AVARICIA")
    print("   Greedy vs Programación Dinámica")
    print("=" * 60)

    tasks = generate_greedy_failure_case()

    print("\nTareas del caso de prueba:")
    print_tasks_table(tasks)

    print("\nOrden de evaluación Greedy (mayor a menor ganancia):")
    sorted_by_profit = sorted(tasks, key=lambda t: t.profit, reverse=True)
    for i, t in enumerate(sorted_by_profit, 1):
        print(f"  {i}. {t}")

    # Ejecutar los tres algoritmos
    greedy_result = greedy_task_selection(tasks)
    dp_linear_result = dp_linear_task_selection(tasks)
    dp_binary_result = dp_binary_task_selection(tasks)

    print("\n" + "-" * 60)
    print("RESULTADOS:")
    print("-" * 60)

    print_result_summary(greedy_result)
    print_result_summary(dp_linear_result)
    print_result_summary(dp_binary_result)

    print("\n" + "-" * 60)
    print("ANÁLISIS:")
    print("-" * 60)

    if greedy_result.total_profit < dp_linear_result.total_profit:
        diff = dp_linear_result.total_profit - greedy_result.total_profit
        print(f"  ✗ Greedy subóptimo: pierde {diff} unidades de ganancia.")
        print(f"  ✓ DP obtiene la solución óptima: {dp_linear_result.total_profit}")
        print()
        print("  Explicación:")
        print("  El Greedy eligió la tarea más rentable individualmente (T1, profit=10).")
        print("  Al hacerlo, bloqueó la combinación T2+T3 (profit=6+6=12).")
        print()
        print("  Óptimo local  ≠  Óptimo global.")
        print()
        print("  El Greedy no evalúa si existen combinaciones de tareas más pequeñas")
        print("  que juntas superen a la tarea más rentable.")
        print()
        print("  La DP evalúa TODAS las posibilidades mediante la recurrencia:")
        print("  dp[i] = max(profit[i] + dp[compatible_anterior], dp[i-1])")
    else:
        print("  Greedy y DP coinciden en este caso (no es un caso de fallo).")

    print("=" * 60 + "\n")


def demo_reto2_ordering_impact() -> None:
    """
    RETO 2: Demuestra por qué el ordenamiento por end_time es fundamental.

    Muestra qué sucede cuando se usa un orden incorrecto (start_time o profit)
    y por qué la DP produce resultados incorrectos.
    """
    print("\n" + "=" * 60)
    print("   RETO 2: EL ORDEN DEL CAOS")
    print("   Por qué end_time es el único orden válido para DP")
    print("=" * 60)

    # Caso donde el orden importa claramente
    tasks = [
        Task(id=1, start_time=0, end_time=5,  profit=3),
        Task(id=2, start_time=3, end_time=10, profit=5),
        Task(id=3, start_time=5, end_time=8,  profit=4),
        Task(id=4, start_time=6, end_time=12, profit=6),
        Task(id=5, start_time=8, end_time=11, profit=3),
    ]

    print("\nTareas del caso de demostración:")
    print_tasks_table(tasks)

    # ── Orden correcto: por end_time ─────────────────────────────────────────
    print("\n" + "-" * 60)
    print("ORDEN CORRECTO: sorted by end_time (ascendente)")
    print("-" * 60)
    sorted_by_end = sorted(tasks, key=lambda t: t.end_time)
    print("Secuencia de evaluación:")
    for i, t in enumerate(sorted_by_end, 1):
        print(f"  {i}. {t}")

    dp_result = dp_linear_task_selection(tasks)
    print(f"\n  DP Lineal (orden correcto): ganancia = {dp_result.total_profit}")
    print(f"  Tareas: {[t.id for t in dp_result.selected_tasks]}")

    # ── Orden incorrecto: por start_time ────────────────────────────────────
    print("\n" + "-" * 60)
    print("ORDEN INCORRECTO: sorted by start_time")
    print("(simulación de lo que ocurriría si se cambia el orden)")
    print("-" * 60)

    # Aplicamos la lógica DP manualmente con orden incorrecto
    sorted_by_start = sorted(tasks, key=lambda t: t.start_time)
    print("Secuencia de evaluación con orden incorrecto:")
    for i, t in enumerate(sorted_by_start, 1):
        print(f"  {i}. {t}")

    print()
    print("  Problema: con este orden, dp[i-1] ya no representa 'la mejor")
    print("  solución con tareas anteriores que terminaron antes'.")
    print()
    print("  Ejemplo concreto:")
    print("  Si la tarea 3 termina en t=12 pero está antes de una que termina")
    print("  en t=8, la búsqueda de 'última compatible' puede devolver un índice")
    print("  incorrecto, porque busca hacia atrás pero las tareas NO están")
    print("  ordenadas por tiempo de finalización.")
    print()
    print("  FUNDAMENTO MATEMÁTICO:")
    print("  La recurrencia dp[i] = max(profit[i] + dp[p(i)], dp[i-1]) requiere:")
    print()
    print("  1. dp[i-1] = mejor solución con {tarea_1, ..., tarea_{i-1}}")
    print("     → Solo es correcto si la tarea i-1 TERMINA antes que la tarea i.")
    print("     → Solo es correcto si ordenamos por end_time.")
    print()
    print("  2. p(i) = índice de la última tarea j tal que j.end_time <= i.start_time")
    print("     → Solo podemos encontrar este índice correctamente si las tareas")
    print("       están ordenadas por end_time (mirando hacia la izquierda).")
    print()
    print("  Si el orden cambia, dp[i-1] puede incluir tareas que terminen DESPUÉS")
    print("  de que empiece la tarea i, haciendo que la recurrencia sea incorrecta.")

    print("=" * 60 + "\n")


def demo_reto3_recurrence() -> None:
    """
    RETO 3: Traza la recurrencia dp[i] = max(...) paso a paso.

    Muestra exactamente qué decisión toma el algoritmo en cada paso
    y cómo eso se traduce a la lógica del servidor.
    """
    print("\n" + "=" * 60)
    print("   RETO 3: LA DECISIÓN DEL ALGORITMO")
    print("   Traza paso a paso de dp[i] = max(...)")
    print("=" * 60)

    # Caso pequeño para poder trazar manualmente
    tasks = [
        Task(id=1, start_time=0,  end_time=3,  profit=3),
        Task(id=2, start_time=1,  end_time=4,  profit=5),
        Task(id=3, start_time=3,  end_time=6,  profit=4),
        Task(id=4, start_time=5,  end_time=9,  profit=6),
        Task(id=5, start_time=6,  end_time=10, profit=2),
    ]

    print("\nTareas (ordenadas por end_time — orden correcto para DP):")
    sorted_tasks = sorted(tasks, key=lambda t: t.end_time)
    print_tasks_table(sorted_tasks)

    print("\nTabla dp[] construida paso a paso:")
    print(f"  {'i':>3} | {'Tarea':>6} | {'[start→end]':>12} | {'profit':>6} | {'p(i)':>5} | {'Tomar':>8} | {'Rechazar':>8} | {'dp[i]':>7} | Decisión")
    print("  " + "-" * 100)

    n = len(sorted_tasks)
    dp = [0] * (n + 1)

    for i in range(1, n + 1):
        task = sorted_tasks[i - 1]

        # Búsqueda lineal de p(i) para la traza
        p_i = 0
        for j in range(i - 2, -1, -1):
            if sorted_tasks[j].end_time <= task.start_time:
                p_i = j + 1
                break

        take = task.profit + dp[p_i]
        skip = dp[i - 1]
        dp[i] = max(take, skip)
        decision = "TOMAR" if take >= skip else "RECHAZAR"

        print(f"  {i:>3} | T{task.id:>4} | [{task.start_time:>4}→{task.end_time:>4}] | {task.profit:>6} | {p_i:>5} | {take:>8} | {skip:>8} | {dp[i]:>7} | {decision}")

    print(f"\n  dp final: {dp}")
    print(f"  Ganancia óptima: dp[{n}] = {dp[n]}")

    print("\n" + "-" * 60)
    print("INTERPRETACIÓN EN TÉRMINOS DEL SERVIDOR:")
    print("-" * 60)
    print()
    print("  dp[i] = ¿Cuál es la MÁXIMA ganancia posible usando las primeras i tareas?")
    print()
    print("  En cada paso i, el servidor pregunta:")
    print()
    print("  → OPCIÓN 1 - Ejecutar la tarea i:")
    print("      Ganancia = profit[i] + dp[p(i)]")
    print("      = ganancia de esta tarea")
    print("        + mejor ganancia posible con tareas que NO se solapan con esta")
    print()
    print("  → OPCIÓN 2 - Rechazar la tarea i:")
    print("      Ganancia = dp[i-1]")
    print("      = la mejor solución que ya teníamos sin esta tarea")
    print()
    print("  El servidor elige la opción más rentable en cada decisión.")
    print("  Como evalúa TODAS las posibilidades mediante la tabla dp,")
    print("  la solución final garantizadamente es la ÓPTIMA GLOBAL.")

    print("=" * 60 + "\n")


def demo_reto4_benchmark() -> None:
    """
    RETO 4: Benchmark de rendimiento con N = 100.000 tareas.

    Demuestra empíricamente la diferencia entre O(n²) y O(n log n).
    """
    print("\n" + "=" * 60)
    print("   RETO 4: PRUEBA DE ESTRÉS - BENCHMARKING")
    print("   DP Lineal O(n²) vs DP Binaria O(n log n)")
    print("=" * 60)

    # Tamaños progresivos para observar la tendencia de complejidad
    sizes = [1_000, 5_000, 10_000, 20_000, 50_000, 100_000]

    print(f"\n  Ejecutando benchmark con semilla fija = 42...")
    print(f"  El DP Lineal se omite para N > 20,000 (O(n²) demasiado lento)")
    print()

    results = run_benchmark(sizes=sizes, seed=42, skip_linear_above=20_000)
    print_benchmark_results(results, skip_linear_above=20_000)

"""
Utilidades de formateo para presentación en consola.

Propósito:
    Centralizar toda la lógica de presentación para que los módulos
    de negocio (algoritmos, benchmarking) no mezclen lógica de consola
    con lógica algorítmica.

    Principio de responsabilidad única: los algoritmos calculan,
    este módulo presenta.
"""

from typing import List

from src.models.task import Task
from src.models.result import AlgorithmResult


def print_tasks_table(tasks: List[Task], title: str = "") -> None:
    """
    Imprime una lista de tareas en formato tabular.

    Args:
        tasks: Lista de tareas a mostrar.
        title: Título opcional para la tabla.
    """
    if title:
        print(f"\n  {title}")

    if not tasks:
        print("  (sin tareas)")
        return

    header = f"  {'ID':>4} | {'Inicio':>8} | {'Fin':>8} | {'Ganancia':>8} | {'Duración':>8}"
    separator = "  " + "-" * (len(header) - 2)

    print(separator)
    print(header)
    print(separator)

    for task in tasks:
        print(
            f"  T{task.id:>3} | "
            f"{task.start_time:>8} | "
            f"{task.end_time:>8} | "
            f"{task.profit:>8} | "
            f"{task.duration():>8}"
        )

    print(separator)
    total_profit = sum(t.profit for t in tasks)
    print(f"  {'Total':>4} | {'':>8} | {'':>8} | {total_profit:>8} | {'':>8}")
    print(separator)


def print_result_summary(result: AlgorithmResult) -> None:
    """
    Imprime un resumen del resultado de un algoritmo.

    Args:
        result: Resultado del algoritmo a mostrar.
    """
    print(f"\n  ▶ {result.algorithm_name}")
    print(f"    Ganancia total:   {result.total_profit:>8,}")
    print(f"    Tareas seleccionadas: {result.count}")

    if result.selected_tasks:
        task_ids = ", ".join(f"T{t.id}" for t in result.selected_tasks)
        print(f"    Tareas: {task_ids}")
    else:
        print("    Tareas: (ninguna)")


def print_comparison_table(results: List[AlgorithmResult]) -> None:
    """
    Imprime una tabla comparativa de múltiples resultados de algoritmos.

    Args:
        results: Lista de resultados a comparar.
    """
    print("\n" + "─" * 60)
    print(f"  {'Algoritmo':<22} | {'Ganancia':>10} | {'Tareas':>8}")
    print("  " + "─" * 56)

    for result in results:
        print(
            f"  {result.algorithm_name:<22} | "
            f"{result.total_profit:>10,} | "
            f"{result.count:>8}"
        )

    print("  " + "─" * 56)

    # Determinar si hay diferencias entre los resultados DP
    dp_results = [r for r in results if "DP" in r.algorithm_name]
    if len(dp_results) == 2:
        if dp_results[0].total_profit == dp_results[1].total_profit:
            print(f"  ✓ DP Lineal y DP Binaria coinciden: {dp_results[0].total_profit:,}")
        else:
            print(f"  ✗ ERROR: DP Lineal y DP Binaria difieren!")

    greedy_results = [r for r in results if "Greedy" in r.algorithm_name]
    if greedy_results and dp_results:
        greedy_profit = greedy_results[0].total_profit
        optimal_profit = dp_results[0].total_profit
        if greedy_profit < optimal_profit:
            print(f"  ✗ Greedy subóptimo: pierde {optimal_profit - greedy_profit:,} unidades.")
        else:
            print(f"  ✓ Greedy coincide con el óptimo en este caso.")

    print("─" * 60)


def format_task_list(tasks: List[Task]) -> str:
    """
    Devuelve una representación en string de una lista de tareas.
    Útil para debug y logging.
    """
    if not tasks:
        return "[]"
    return "[" + ", ".join(str(t) for t in tasks) + "]"


def print_header(title: str) -> None:
    """Imprime un encabezado decorativo para secciones de la consola."""
    width = 60
    print("\n" + "=" * width)
    # Centrar el título
    padding = (width - len(title) - 2) // 2
    print(" " * padding + title)
    print("=" * width)

"""
main.py — Punto de entrada del programa.

Interfaz de consola para el proyecto de Optimización de Tareas.

CÓMO EJECUTAR:
    cd task_optimizer
    python main.py

REQUISITOS:
    Python 3.11+
    No se requieren dependencias externas.
"""

import sys
import subprocess
import os
from typing import List, Optional

from src.models.task import Task
from src.generators.task_generator import generate_tasks
from src.algorithms.greedy import greedy_task_selection
from src.algorithms.dynamic_programming_linear import dp_linear_task_selection
from src.algorithms.dynamic_programming_binary import dp_binary_task_selection
from src.utils.formatting import (
    print_tasks_table,
    print_result_summary,
    print_comparison_table,
    print_header,
)
from src.demonstrations.demonstrations import (
    demo_reto1_greedy_vs_dp,
    demo_reto2_ordering_impact,
    demo_reto3_recurrence,
    demo_reto4_benchmark,
)
from src.benchmarking.benchmark import run_benchmark, print_benchmark_results


# ─────────────────────────────────────────────────────────────────────────────
# Estado de la sesión (simple, sin base de datos ni persistencia)
# ─────────────────────────────────────────────────────────────────────────────
_current_tasks: List[Task] = []
_current_seed: int = 42
_current_n: int = 10


def _get_tasks_or_warn() -> Optional[List[Task]]:
    """Retorna las tareas actuales o muestra un mensaje de error."""
    if not _current_tasks:
        print("\n  ⚠  No hay tareas generadas. Use la opción 1 para generar tareas.")
        return None
    return _current_tasks


def menu_generate_tasks() -> None:
    """Opción 1: Generar tareas."""
    global _current_tasks, _current_seed, _current_n

    print_header("GENERAR TAREAS")

    try:
        n_input = input("\n  Número de tareas (default=10): ").strip()
        n = int(n_input) if n_input else 10

        seed_input = input("  Semilla aleatoria (default=42): ").strip()
        seed = int(seed_input) if seed_input else 42

        if n <= 0:
            print("  ⚠  El número de tareas debe ser positivo.")
            return

    except ValueError:
        print("  ⚠  Entrada inválida. Usando valores por defecto (n=10, seed=42).")
        n, seed = 10, 42

    _current_tasks = generate_tasks(n=n, seed=seed)
    _current_n = n
    _current_seed = seed

    print(f"\n  ✓ Generadas {len(_current_tasks)} tareas con semilla {seed}")

    if n <= 20:
        print_tasks_table(_current_tasks, title="Tareas generadas:")
    else:
        print(f"\n  (Se muestran las primeras 10 de {n} tareas)")
        print_tasks_table(_current_tasks[:10])
        print(f"  ... ({n - 10} tareas más)")


def menu_run_greedy() -> None:
    """Opción 2: Ejecutar algoritmo Greedy."""
    tasks = _get_tasks_or_warn()
    if tasks is None:
        return

    print_header("ALGORITMO GREEDY (Enfoque A)")
    print("\n  ⚠  RECORDATORIO: El Greedy NO garantiza la solución óptima.")
    print("     Puede producir una solución inferior a la de Programación Dinámica.\n")

    result = greedy_task_selection(tasks)
    print_result_summary(result)

    if result.selected_tasks and len(result.selected_tasks) <= 20:
        print()
        print_tasks_table(result.selected_tasks, title="Tareas seleccionadas:")


def menu_run_dp_linear() -> None:
    """Opción 3: Ejecutar DP con búsqueda lineal."""
    tasks = _get_tasks_or_warn()
    if tasks is None:
        return

    print_header("DP + BÚSQUEDA LINEAL (Enfoque B) — O(n²)")

    if len(tasks) > 10_000:
        confirm = input(
            f"\n  ⚠  N={len(tasks):,} puede ser muy lento con O(n²). "
            f"¿Continuar? (s/N): "
        ).strip().lower()
        if confirm != 's':
            print("  Cancelado.")
            return

    result = dp_linear_task_selection(tasks)
    print_result_summary(result)

    if result.selected_tasks and len(result.selected_tasks) <= 20:
        print()
        print_tasks_table(result.selected_tasks, title="Tareas seleccionadas:")


def menu_run_dp_binary() -> None:
    """Opción 4: Ejecutar DP con búsqueda binaria."""
    tasks = _get_tasks_or_warn()
    if tasks is None:
        return

    print_header("DP + BÚSQUEDA BINARIA (Enfoque C) — O(n log n)")
    result = dp_binary_task_selection(tasks)
    print_result_summary(result)

    if result.selected_tasks and len(result.selected_tasks) <= 20:
        print()
        print_tasks_table(result.selected_tasks, title="Tareas seleccionadas:")


def menu_run_comparison() -> None:
    """Opción 5: Comparar los tres algoritmos."""
    tasks = _get_tasks_or_warn()
    if tasks is None:
        return

    print_header("COMPARACIÓN: Greedy vs DP Lineal vs DP Binaria")

    if len(tasks) > 10_000:
        print(f"\n  ⚠  N={len(tasks):,}: se omite DP Lineal O(n²) por rendimiento.")
        results = [
            greedy_task_selection(tasks),
            dp_binary_task_selection(tasks),
        ]
    else:
        results = [
            greedy_task_selection(tasks),
            dp_linear_task_selection(tasks),
            dp_binary_task_selection(tasks),
        ]

    for result in results:
        print_result_summary(result)

    print()
    print_comparison_table(results)


def menu_demo_reto1() -> None:
    """Opción 6: Demostración Reto 1 — Greedy vs DP."""
    demo_reto1_greedy_vs_dp()


def menu_demo_reto2() -> None:
    """Opción 7: Demostración Reto 2 — Importancia del ordenamiento."""
    demo_reto2_ordering_impact()


def menu_demo_reto3() -> None:
    """Opción 8: Demostración Reto 3 — La recurrencia dp[i] = max(...)."""
    demo_reto3_recurrence()


def menu_run_benchmark() -> None:
    """Opción 9: Ejecutar benchmark de rendimiento."""
    print_header("BENCHMARK: DP Lineal O(n²) vs DP Binaria O(n log n)")
    print("\n  Seleccione el modo:")
    print("  1. Benchmark rápido (hasta N=20,000)")
    print("  2. Benchmark completo con N=100,000 (puede tardar varios minutos)")
    print("  0. Cancelar")

    choice = input("\n  Opción: ").strip()

    if choice == "1":
        sizes = [1_000, 5_000, 10_000, 20_000]
        results = run_benchmark(sizes=sizes, seed=42, skip_linear_above=20_000)
        print_benchmark_results(results, skip_linear_above=20_000)

    elif choice == "2":
        print("\n  ⚠  DP Lineal se omitirá para N > 20,000 (O(n²) extremadamente lento).")
        print("     DP Binaria se ejecutará para todos los tamaños.\n")
        sizes = [1_000, 5_000, 10_000, 20_000, 50_000, 100_000]
        results = run_benchmark(sizes=sizes, seed=42, skip_linear_above=20_000)
        print_benchmark_results(results, skip_linear_above=20_000)

    elif choice == "0":
        print("  Cancelado.")
    else:
        print("  Opción inválida.")


def menu_run_tests() -> None:
    """Opción 10: Ejecutar las pruebas automatizadas."""
    print_header("EJECUTAR PRUEBAS AUTOMATIZADAS")
    print()

    # Ejecutamos pytest o unittest según disponibilidad
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Intentar con pytest primero
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            cwd=test_dir,
            capture_output=False,
        )
        if result.returncode != 0:
            print("\n  (Si pytest no está disponible, use: python -m unittest discover tests)")
    except Exception:
        # Fallback a unittest
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "tests", "-v"],
            cwd=test_dir,
            capture_output=False,
        )


def _print_main_menu() -> None:
    """Imprime el menú principal."""
    task_count = f"{len(_current_tasks):,}" if _current_tasks else "ninguna"
    print("\n" + "=" * 55)
    print("   OPTIMIZACIÓN DE TAREAS — CLÚSTER DE SERVIDORES")
    print("=" * 55)
    print(f"   Tareas en memoria: {task_count} (semilla={_current_seed})")
    print("─" * 55)
    print("  ALGORITMOS")
    print("  1. Generar tareas aleatorias")
    print("  2. Ejecutar Greedy (Enfoque A)")
    print("  3. Ejecutar DP Lineal — O(n²) (Enfoque B)")
    print("  4. Ejecutar DP Binaria — O(n log n) (Enfoque C)")
    print("  5. Comparar los tres algoritmos")
    print("─" * 55)
    print("  DEMOSTRACIONES DE SUSTENTACIÓN")
    print("  6. Demo Reto 1: Greedy falla vs DP")
    print("  7. Demo Reto 2: Impacto del ordenamiento")
    print("  8. Demo Reto 3: La recurrencia dp[i] = max(...)")
    print("  9. Demo Reto 4: Benchmark de rendimiento")
    print("─" * 55)
    print("  PRUEBAS")
    print(" 10. Ejecutar pruebas automatizadas")
    print("─" * 55)
    print("  0. Salir")
    print("=" * 55)


def main() -> None:
    """Bucle principal del programa."""
    handlers = {
        "1":  menu_generate_tasks,
        "2":  menu_run_greedy,
        "3":  menu_run_dp_linear,
        "4":  menu_run_dp_binary,
        "5":  menu_run_comparison,
        "6":  menu_demo_reto1,
        "7":  menu_demo_reto2,
        "8":  menu_demo_reto3,
        "9":  menu_run_benchmark,
        "10": menu_run_tests,
    }

    while True:
        _print_main_menu()
        choice = input("\n  Seleccione una opción: ").strip()

        if choice == "0":
            print("\n  ¡Hasta luego!\n")
            break
        elif choice in handlers:
            try:
                handlers[choice]()
            except KeyboardInterrupt:
                print("\n  (Interrumpido por el usuario)")
            except Exception as e:
                print(f"\n  ✗ Error inesperado: {e}")
                print("    Verifique que las tareas hayan sido generadas correctamente.")
        else:
            print(f"\n  ⚠  Opción '{choice}' no válida. Elija entre 0 y 10.")

        input("\n  Presione Enter para continuar...")


if __name__ == "__main__":
    main()

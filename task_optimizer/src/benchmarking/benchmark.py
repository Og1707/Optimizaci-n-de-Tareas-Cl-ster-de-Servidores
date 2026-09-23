"""
Sistema de benchmarking para comparar los algoritmos de optimización de tareas.

PROPÓSITO:
    Medir y comparar el tiempo de ejecución real de los algoritmos DP Lineal y
    DP Binaria con diferentes tamaños de entrada para demostrar empíricamente
    la diferencia de complejidad O(n²) vs O(n log n).

    IMPORTANTE: Este módulo mide tiempos REALES, no inventados.
    Los resultados varían según el hardware donde se ejecuten.

POR QUÉ time.perf_counter():
    - perf_counter() usa el reloj de mayor resolución disponible en el sistema.
    - Es específicamente diseñado para medir duraciones cortas (benchmarking).
    - A diferencia de time.time(), no se ve afectado por ajustes del reloj del sistema.
    - A diferencia de time.process_time(), incluye tiempo de espera de I/O,
      lo cual es apropiado aquí porque queremos el tiempo total de pared.
    - Es el estándar recomendado por Python para medir rendimiento de código.

NOTA SOBRE EL ENFOQUE B CON N GRANDE:
    La búsqueda lineal O(n²) puede ser extremadamente lenta para N=100.000.
    Por eso el benchmark permite configurar tamaños máximos para cada algoritmo.
    No se falsifican resultados: simplemente se advierte cuando el tiempo
    estimado es demasiado largo.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional

from src.models.task import Task
from src.generators.task_generator import generate_tasks
from src.algorithms.dynamic_programming_linear import dp_linear_task_selection
from src.algorithms.dynamic_programming_binary import dp_binary_task_selection


@dataclass
class BenchmarkRun:
    """Resultado de una ejecución de benchmark para un algoritmo y tamaño N."""

    algorithm_name: str
    n: int
    elapsed_ms: float
    total_profit: int
    tasks_selected: int

    def __str__(self) -> str:
        return (
            f"  {self.algorithm_name:<20} | "
            f"N={self.n:>7,} | "
            f"Tiempo: {self.elapsed_ms:>10.2f} ms | "
            f"Ganancia: {self.total_profit:>10,} | "
            f"Tareas: {self.tasks_selected:>6}"
        )


@dataclass
class BenchmarkResult:
    """Resultado completo del benchmark para un tamaño N."""

    n: int
    seed: int
    linear_run: Optional[BenchmarkRun] = None
    binary_run: Optional[BenchmarkRun] = None

    @property
    def profits_match(self) -> bool:
        """Verifica que ambos algoritmos obtienen la misma ganancia óptima."""
        if self.linear_run is None or self.binary_run is None:
            return False
        return self.linear_run.total_profit == self.binary_run.total_profit

    @property
    def speedup(self) -> Optional[float]:
        """Factor de aceleración del algoritmo binario vs lineal."""
        if (
            self.linear_run is None
            or self.binary_run is None
            or self.binary_run.elapsed_ms == 0
        ):
            return None
        return self.linear_run.elapsed_ms / self.binary_run.elapsed_ms


def _run_timed(algorithm_func, tasks: List[Task]) -> tuple:
    """
    Ejecuta un algoritmo y mide su tiempo de ejecución.

    Medimos SOLO el tiempo del algoritmo, no la generación de tareas.
    Las tareas ya fueron generadas antes de llamar a esta función.

    Returns:
        (elapsed_ms, result) donde elapsed_ms es el tiempo en milisegundos.
    """
    start = time.perf_counter()
    result = algorithm_func(tasks)
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000.0
    return elapsed_ms, result


def run_benchmark(
    sizes: List[int],
    seed: int = 42,
    skip_linear_above: int = 20_000,
) -> List[BenchmarkResult]:
    """
    Ejecuta el benchmark comparativo para todos los tamaños dados.

    DISEÑO DEL BENCHMARK:
        - Se genera UNA SOLA vez el conjunto de tareas para cada N con la misma semilla.
        - Ambos algoritmos reciben exactamente la misma entrada.
        - Se mide SOLO el tiempo del algoritmo (no la generación).
        - Los resultados son reproducibles bajo las mismas condiciones de hardware.

    Args:
        sizes:             Lista de tamaños N a probar.
        seed:              Semilla para reproducibilidad.
        skip_linear_above: Si N > este valor, se omite el algoritmo lineal
                           (demasiado lento para esperar). Se informa claramente.

    Returns:
        Lista de BenchmarkResult, uno por cada tamaño N.
    """
    results: List[BenchmarkResult] = []

    for n in sizes:
        # Generar las mismas tareas para ambos algoritmos
        tasks = generate_tasks(n=n, seed=seed)

        benchmark_result = BenchmarkResult(n=n, seed=seed)

        # ── Algoritmo DP Lineal ──────────────────────────────────────────────
        if n <= skip_linear_above:
            elapsed_ms, result = _run_timed(dp_linear_task_selection, tasks)
            benchmark_result.linear_run = BenchmarkRun(
                algorithm_name="DP Lineal",
                n=n,
                elapsed_ms=elapsed_ms,
                total_profit=result.total_profit,
                tasks_selected=result.count,
            )
        else:
            # No ejecutamos el O(n²) para N muy grande para no bloquear el benchmark
            benchmark_result.linear_run = None

        # ── Algoritmo DP Binaria ─────────────────────────────────────────────
        elapsed_ms, result = _run_timed(dp_binary_task_selection, tasks)
        benchmark_result.binary_run = BenchmarkRun(
            algorithm_name="DP Binaria",
            n=n,
            elapsed_ms=elapsed_ms,
            total_profit=result.total_profit,
            tasks_selected=result.count,
        )

        results.append(benchmark_result)

    return results


def print_benchmark_results(results: List[BenchmarkResult], skip_linear_above: int = 20_000) -> None:
    """
    Imprime los resultados del benchmark en un formato claro y tabular.
    """
    separator = "─" * 80

    print("\n" + "=" * 80)
    print("   BENCHMARK: DP Lineal O(n²)  vs  DP Binaria O(n log n)")
    print("=" * 80)
    print(f"  Semilla utilizada: 42 (resultados reproducibles)")
    print(f"  Tiempo medido con: time.perf_counter() (mayor resolución disponible)")
    print(f"  Nota: DP Lineal se omite para N > {skip_linear_above:,} (demasiado lento)")
    print(separator)

    for br in results:
        print(f"\n  N = {br.n:,}")
        print(separator)

        if br.linear_run:
            print(br.linear_run)
        else:
            print(f"  {'DP Lineal':<20} | N={br.n:>7,} | Omitido (N > {skip_linear_above:,}, O(n²) muy lento)")

        if br.binary_run:
            print(br.binary_run)

        # Verificación de corrección: ambos deben dar la misma ganancia
        if br.linear_run and br.binary_run:
            if br.profits_match:
                print(f"\n  ✓ Ganancia coincide: {br.linear_run.total_profit:,}  (ambos algoritmos son correctos)")
            else:
                print(f"\n  ✗ ERROR: Ganancias no coinciden! "
                      f"Lineal={br.linear_run.total_profit}, "
                      f"Binaria={br.binary_run.total_profit}")

            if br.speedup is not None:
                print(f"  → Aceleración: DP Binaria es {br.speedup:.1f}x más rápida")

    print("\n" + "=" * 80)
    print("  ANÁLISIS DE COMPLEJIDAD")
    print(separator)
    print("  DP Lineal  O(n²):      Al duplicar N, el tiempo se multiplica ~4x")
    print("  DP Binaria O(n log n): Al duplicar N, el tiempo se multiplica ~2x")
    print("  Diferencia en N=100k:  ~100000/17 ≈ 5882x teóricamente más operaciones")
    print("=" * 80 + "\n")

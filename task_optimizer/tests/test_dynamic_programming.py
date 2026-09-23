"""
Tests para los algoritmos de Programación Dinámica (Enfoques B y C).

Verifica:
    - Casos límite (vacío, una tarea).
    - Correctitud para todos los casos del enunciado.
    - Igualdad de resultados entre DP Lineal y DP Binaria.
    - Reconstrucción correcta de la solución (las tareas devueltas son correctas).
    - Compatibilidad de las tareas seleccionadas.
    - Caso donde Greedy falla y ambas DP encuentran el óptimo.
    - Validación cruzada con semillas aleatorias.

NOTA SOBRE LA VALIDACIÓN CRUZADA:
    El test más importante de este módulo es test_linear_equals_binary_random,
    que verifica con múltiples semillas que ambos algoritmos producen
    exactamente la misma ganancia óptima.
"""

import unittest
from typing import List

from src.models.task import Task
from src.algorithms.dynamic_programming_linear import dp_linear_task_selection
from src.algorithms.dynamic_programming_binary import dp_binary_task_selection
from src.algorithms.greedy import greedy_task_selection
from src.generators.task_generator import (
    generate_tasks,
    generate_greedy_failure_case,
    generate_all_compatible_tasks,
    generate_all_overlapping_tasks,
)


class TestDPEmptyCases(unittest.TestCase):
    """Tests de casos límite: entrada vacía y una sola tarea."""

    def test_linear_empty_list_returns_zero(self):
        result = dp_linear_task_selection([])
        self.assertEqual(result.total_profit, 0)
        self.assertEqual(result.count, 0)

    def test_binary_empty_list_returns_zero(self):
        result = dp_binary_task_selection([])
        self.assertEqual(result.total_profit, 0)
        self.assertEqual(result.count, 0)

    def test_linear_single_task_selected(self):
        task = Task(id=1, start_time=0, end_time=5, profit=42)
        result = dp_linear_task_selection([task])
        self.assertEqual(result.total_profit, 42)
        self.assertEqual(result.count, 1)

    def test_binary_single_task_selected(self):
        task = Task(id=1, start_time=0, end_time=5, profit=42)
        result = dp_binary_task_selection([task])
        self.assertEqual(result.total_profit, 42)
        self.assertEqual(result.count, 1)


class TestDPAllCompatible(unittest.TestCase):
    """Tests donde todas las tareas son compatibles entre sí."""

    def test_linear_selects_all_compatible(self):
        """DP debe seleccionar todas las tareas cuando no hay solapamiento."""
        tasks = generate_all_compatible_tasks(n=5)
        result = dp_linear_task_selection(tasks)
        expected_profit = sum(t.profit for t in tasks)
        self.assertEqual(result.total_profit, expected_profit)
        self.assertEqual(result.count, 5)

    def test_binary_selects_all_compatible(self):
        tasks = generate_all_compatible_tasks(n=5)
        result = dp_binary_task_selection(tasks)
        expected_profit = sum(t.profit for t in tasks)
        self.assertEqual(result.total_profit, expected_profit)
        self.assertEqual(result.count, 5)

    def test_adjacent_tasks_both_selected(self):
        """
        Tareas adyacentes (end_time == start_time) deben ser compatibles.
        Convención: end_time <= start_time → compatible.
        """
        tasks = [
            Task(id=1, start_time=0, end_time=5,  profit=10),
            Task(id=2, start_time=5, end_time=10, profit=20),
        ]
        linear_result = dp_linear_task_selection(tasks)
        binary_result = dp_binary_task_selection(tasks)
        self.assertEqual(linear_result.total_profit, 30)
        self.assertEqual(binary_result.total_profit, 30)
        self.assertEqual(linear_result.count, 2)
        self.assertEqual(binary_result.count, 2)


class TestDPAllOverlapping(unittest.TestCase):
    """Tests donde todas las tareas se solapan."""

    def test_linear_selects_best_when_all_overlap(self):
        """Cuando todas se solapan, DP debe seleccionar la de mayor ganancia."""
        tasks = generate_all_overlapping_tasks(n=5)
        result = dp_linear_task_selection(tasks)
        max_profit = max(t.profit for t in tasks)
        self.assertEqual(result.total_profit, max_profit)
        self.assertEqual(result.count, 1)

    def test_binary_selects_best_when_all_overlap(self):
        tasks = generate_all_overlapping_tasks(n=5)
        result = dp_binary_task_selection(tasks)
        max_profit = max(t.profit for t in tasks)
        self.assertEqual(result.total_profit, max_profit)
        self.assertEqual(result.count, 1)


class TestDPGreedyFailureCase(unittest.TestCase):
    """Test del caso donde Greedy falla y DP encuentra el óptimo."""

    def test_dp_linear_finds_optimal_when_greedy_fails(self):
        """
        Caso: T1[0→10]=10, T2[0→5]=6, T3[5→10]=6, T4[2→8]=9
        Greedy: 10 (elige T1)
        Óptimo: 12 (elige T2+T3)
        """
        tasks = generate_greedy_failure_case()
        result = dp_linear_task_selection(tasks)
        self.assertEqual(result.total_profit, 12)

    def test_dp_binary_finds_optimal_when_greedy_fails(self):
        tasks = generate_greedy_failure_case()
        result = dp_binary_task_selection(tasks)
        self.assertEqual(result.total_profit, 12)

    def test_dp_beats_greedy_in_failure_case(self):
        """Verificación explícita: DP > Greedy en el caso de fallo."""
        tasks = generate_greedy_failure_case()
        greedy_result = greedy_task_selection(tasks)
        dp_result = dp_linear_task_selection(tasks)
        self.assertGreater(dp_result.total_profit, greedy_result.total_profit)

    def test_dp_failure_case_tasks_are_t2_and_t3(self):
        """La solución óptima debe incluir T2 y T3 (no T1)."""
        tasks = generate_greedy_failure_case()
        result = dp_linear_task_selection(tasks)
        selected_ids = set(t.id for t in result.selected_tasks)
        self.assertIn(2, selected_ids)
        self.assertIn(3, selected_ids)
        self.assertNotIn(1, selected_ids)


class TestDPLinearEqualsBinary(unittest.TestCase):
    """
    VALIDACIÓN CRUZADA: DP Lineal == DP Binaria.

    Este es el test más importante para verificar que ambas implementaciones
    son correctas y producen el mismo resultado óptimo.
    """

    def _assert_same_profit(self, tasks: List[Task], description: str = "") -> None:
        """Helper: verifica que ambos algoritmos producen la misma ganancia."""
        linear = dp_linear_task_selection(tasks)
        binary = dp_binary_task_selection(tasks)
        self.assertEqual(
            linear.total_profit,
            binary.total_profit,
            msg=f"Ganancias difieren {description}: "
                f"Lineal={linear.total_profit}, Binaria={binary.total_profit}"
        )

    def test_same_profit_failure_case(self):
        self._assert_same_profit(generate_greedy_failure_case(), "caso fallo Greedy")

    def test_same_profit_all_compatible(self):
        self._assert_same_profit(generate_all_compatible_tasks(n=10), "todas compatibles")

    def test_same_profit_all_overlapping(self):
        self._assert_same_profit(generate_all_overlapping_tasks(n=10), "todas solapadas")

    def test_same_profit_random_seed_42(self):
        tasks = generate_tasks(n=100, seed=42)
        self._assert_same_profit(tasks, "aleatorio seed=42")

    def test_same_profit_random_seed_100(self):
        tasks = generate_tasks(n=100, seed=100)
        self._assert_same_profit(tasks, "aleatorio seed=100")

    def test_same_profit_random_seed_999(self):
        tasks = generate_tasks(n=100, seed=999)
        self._assert_same_profit(tasks, "aleatorio seed=999")

    def test_same_profit_multiple_sizes_and_seeds(self):
        """Validación cruzada con múltiples tamaños y semillas."""
        test_cases = [
            (10, 1), (10, 2), (10, 3),
            (50, 10), (50, 20), (50, 30),
            (100, 42), (100, 77), (100, 123),
            (500, 0), (1000, 7),
        ]
        for n, seed in test_cases:
            tasks = generate_tasks(n=n, seed=seed)
            with self.subTest(n=n, seed=seed):
                self._assert_same_profit(tasks, f"n={n}, seed={seed}")


class TestDPSolutionReconstruction(unittest.TestCase):
    """Tests de correctitud en la reconstrucción de la solución."""

    def test_selected_tasks_profit_matches_total(self):
        """La suma de ganancias de las tareas seleccionadas debe igualar total_profit."""
        tasks = generate_tasks(n=50, seed=42)
        for algo in [dp_linear_task_selection, dp_binary_task_selection]:
            with self.subTest(algo=algo.__name__):
                result = algo(tasks)
                computed = sum(t.profit for t in result.selected_tasks)
                self.assertEqual(result.total_profit, computed)

    def test_selected_tasks_are_mutually_compatible(self):
        """Las tareas seleccionadas no deben solaparse entre sí."""
        tasks = generate_tasks(n=100, seed=42)
        for algo in [dp_linear_task_selection, dp_binary_task_selection]:
            with self.subTest(algo=algo.__name__):
                result = algo(tasks)
                selected = sorted(result.selected_tasks, key=lambda t: t.start_time)
                for i in range(len(selected) - 1):
                    self.assertLessEqual(
                        selected[i].end_time,
                        selected[i + 1].start_time,
                        msg=f"{algo.__name__}: solapamiento entre {selected[i]} y {selected[i+1]}"
                    )

    def test_algorithm_names_are_correct(self):
        task = Task(id=1, start_time=0, end_time=1, profit=1)
        self.assertEqual(dp_linear_task_selection([task]).algorithm_name, "DP Lineal")
        self.assertEqual(dp_binary_task_selection([task]).algorithm_name, "DP Binaria")

    def test_known_optimal_solution(self):
        """
        Caso con solución óptima conocida manualmente.

        Tareas ordenadas por end_time:
            T1: [0→3],  profit=3
            T2: [1→4],  profit=5
            T3: [3→6],  profit=4
            T5: [6→10], profit=2
            T4: [5→9],  profit=6

        Solución óptima calculada a mano:
            T2: profit=5
            T3: profit=4 → no compatible con T2 (T2 termina en 4, T3 empieza en 3) → solapan
            T1: [0→3] + T3:[3→6] + T5:[6→10] = 3+4+2 = 9
            T2: [1→4] + ... → T4:[5→9] = 5+6 = 11  ← ÓPTIMO
        """
        tasks = [
            Task(id=1, start_time=0, end_time=3,  profit=3),
            Task(id=2, start_time=1, end_time=4,  profit=5),
            Task(id=3, start_time=3, end_time=6,  profit=4),
            Task(id=4, start_time=5, end_time=9,  profit=6),
            Task(id=5, start_time=6, end_time=10, profit=2),
        ]
        # Calculamos el óptimo: T2[1→4]=5 + T4[5→9]=6 = 11
        # T1[0→3]=3 + T3[3→6]=4 + T5[6→10]=2 = 9
        # T2 no compatible con T3 (T2 end=4 > T3 start=3 → solapan)
        # T2 compatible con T4 (T2 end=4 <= T4 start=5)
        for algo in [dp_linear_task_selection, dp_binary_task_selection]:
            with self.subTest(algo=algo.__name__):
                result = algo(tasks)
                self.assertEqual(result.total_profit, 11)


class TestDPWithEqualTimes(unittest.TestCase):
    """Tests con casos de tiempos iguales."""

    def test_tasks_ending_and_starting_at_same_time(self):
        """
        Verificar que dos tareas donde A.end_time == B.start_time
        son tratadas como compatibles (no hay solapamiento).
        """
        task_a = Task(id=1, start_time=0,  end_time=5,  profit=10)
        task_b = Task(id=2, start_time=5,  end_time=10, profit=15)
        task_c = Task(id=3, start_time=10, end_time=15, profit=5)

        for algo in [dp_linear_task_selection, dp_binary_task_selection]:
            with self.subTest(algo=algo.__name__):
                result = algo([task_a, task_b, task_c])
                self.assertEqual(result.total_profit, 30)
                self.assertEqual(result.count, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""
Tests para el algoritmo Greedy (Enfoque A).

Verifica:
    - Casos límite (vacío, una tarea).
    - Selección correcta cuando todas las tareas son compatibles.
    - Selección correcta cuando todas se solapan.
    - El caso específico donde Greedy es subóptimo.
    - Empate de ganancias.
    - Tareas adyacentes (end_time de una == start_time de la siguiente).
"""

import unittest
from src.models.task import Task
from src.algorithms.greedy import greedy_task_selection
from src.generators.task_generator import generate_greedy_failure_case


class TestGreedyEmptyCases(unittest.TestCase):
    """Tests de casos límite: entrada vacía y una sola tarea."""

    def test_empty_list_returns_zero_profit(self):
        """Sin tareas, la ganancia debe ser 0."""
        result = greedy_task_selection([])
        self.assertEqual(result.total_profit, 0)
        self.assertEqual(result.count, 0)
        self.assertEqual(result.selected_tasks, [])

    def test_single_task_is_always_selected(self):
        """Una sola tarea siempre debe ser seleccionada."""
        task = Task(id=1, start_time=0, end_time=5, profit=10)
        result = greedy_task_selection([task])
        self.assertEqual(result.total_profit, 10)
        self.assertEqual(result.count, 1)
        self.assertIn(task, result.selected_tasks)


class TestGreedyCompatibleTasks(unittest.TestCase):
    """Tests con tareas que no se solapan entre sí."""

    def test_all_compatible_tasks_selected(self):
        """
        Cuando todas las tareas son compatibles, Greedy puede no seleccionarlas
        todas si una de menor ganancia crea conflictos al ordenar por profit.

        En este caso específico, todas son compatibles Y Greedy las selecciona.
        """
        tasks = [
            Task(id=1, start_time=0,  end_time=5,  profit=30),
            Task(id=2, start_time=5,  end_time=10, profit=20),
            Task(id=3, start_time=10, end_time=15, profit=10),
        ]
        result = greedy_task_selection(tasks)
        # Greedy ordena por profit: T1(30), T2(20), T3(10)
        # T1 seleccionada (end=5), T2 compatible (start=5>=5), T3 compatible (start=10>=10)
        self.assertEqual(result.total_profit, 60)
        self.assertEqual(result.count, 3)

    def test_adjacent_tasks_are_compatible(self):
        """
        Tareas adyacentes donde end_time == start_time deben ser compatibles.
        Convención: end_time <= start_time → compatible (el igual está permitido).
        """
        task_a = Task(id=1, start_time=0, end_time=5,  profit=10)
        task_b = Task(id=2, start_time=5, end_time=10, profit=10)
        result = greedy_task_selection([task_a, task_b])
        self.assertEqual(result.total_profit, 20)
        self.assertEqual(result.count, 2)


class TestGreedyOverlappingTasks(unittest.TestCase):
    """Tests con tareas que todas se solapan."""

    def test_all_overlapping_selects_highest_profit(self):
        """
        Cuando todas las tareas se solapan, Greedy correctamente selecciona
        la de mayor ganancia.
        """
        tasks = [
            Task(id=1, start_time=0, end_time=10, profit=10),
            Task(id=2, start_time=0, end_time=10, profit=50),
            Task(id=3, start_time=0, end_time=10, profit=30),
        ]
        result = greedy_task_selection(tasks)
        self.assertEqual(result.total_profit, 50)
        self.assertEqual(result.count, 1)
        self.assertEqual(result.selected_tasks[0].id, 2)


class TestGreedyFailureCase(unittest.TestCase):
    """Test del caso donde Greedy produce una solución subóptima."""

    def test_greedy_suboptimal_vs_dp(self):
        """
        Caso determinista donde Greedy es subóptimo.

        Tareas:
            T1: [0→10], profit=10  ← Greedy la elige
            T2: [0→5],  profit=6
            T3: [5→10], profit=6
            T4: [2→8],  profit=9

        Greedy:  T1          → ganancia = 10
        Óptimo:  T2 + T3     → ganancia = 12
        """
        tasks = generate_greedy_failure_case()
        result = greedy_task_selection(tasks)

        # Greedy elige T1 (mayor ganancia individual = 10)
        # Resultado subóptimo: ganancia 10 < óptimo 12
        self.assertEqual(result.total_profit, 10)
        selected_ids = [t.id for t in result.selected_tasks]
        self.assertIn(1, selected_ids)  # T1 fue elegida

    def test_greedy_failure_case_profit_is_suboptimal(self):
        """
        Verifica explícitamente que la ganancia del Greedy es menor que el óptimo.
        """
        from src.algorithms.dynamic_programming_linear import dp_linear_task_selection
        tasks = generate_greedy_failure_case()
        greedy_result = greedy_task_selection(tasks)
        dp_result = dp_linear_task_selection(tasks)
        self.assertLess(greedy_result.total_profit, dp_result.total_profit)


class TestGreedyTieBreaking(unittest.TestCase):
    """Tests con empates de ganancia."""

    def test_equal_profits_compatible_tasks(self):
        """Tareas con igual ganancia que no se solapan: ambas deben elegirse."""
        tasks = [
            Task(id=1, start_time=0, end_time=5,  profit=10),
            Task(id=2, start_time=5, end_time=10, profit=10),
        ]
        result = greedy_task_selection(tasks)
        self.assertEqual(result.total_profit, 20)
        self.assertEqual(result.count, 2)

    def test_equal_profits_overlapping_tasks(self):
        """Tareas con igual ganancia que se solapan: solo una puede elegirse."""
        tasks = [
            Task(id=1, start_time=0, end_time=10, profit=10),
            Task(id=2, start_time=5, end_time=15, profit=10),
        ]
        result = greedy_task_selection(tasks)
        self.assertEqual(result.total_profit, 10)
        self.assertEqual(result.count, 1)


class TestGreedyResultIntegrity(unittest.TestCase):
    """Tests de integridad del resultado."""

    def test_profit_matches_sum_of_selected(self):
        """La ganancia total debe coincidir con la suma de ganancias de las tareas."""
        tasks = [
            Task(id=1, start_time=0,  end_time=5,  profit=15),
            Task(id=2, start_time=3,  end_time=8,  profit=20),
            Task(id=3, start_time=7,  end_time=12, profit=10),
        ]
        result = greedy_task_selection(tasks)
        expected_sum = sum(t.profit for t in result.selected_tasks)
        self.assertEqual(result.total_profit, expected_sum)

    def test_selected_tasks_are_mutually_compatible(self):
        """Las tareas seleccionadas no deben solaparse entre sí."""
        from src.generators.task_generator import generate_tasks
        tasks = generate_tasks(n=50, seed=42)
        result = greedy_task_selection(tasks)
        selected = sorted(result.selected_tasks, key=lambda t: t.start_time)

        for i in range(len(selected) - 1):
            self.assertLessEqual(
                selected[i].end_time,
                selected[i + 1].start_time,
                msg=f"Tareas solapadas: {selected[i]} y {selected[i + 1]}"
            )

    def test_algorithm_name_is_set(self):
        """El nombre del algoritmo debe estar establecido en el resultado."""
        result = greedy_task_selection([Task(id=1, start_time=0, end_time=1, profit=1)])
        self.assertEqual(result.algorithm_name, "Greedy")


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""
Tests para el generador de tareas.

Verifica:
    - Los datos generados cumplen las invariantes (start < end, profit > 0).
    - La reproducibilidad con semilla fija.
    - El comportamiento con n=0.
    - Los casos especiales predefinidos.
    - Validación de parámetros inválidos.
"""

import unittest

from src.models.task import Task
from src.generators.task_generator import (
    generate_tasks,
    generate_greedy_failure_case,
    generate_all_compatible_tasks,
    generate_all_overlapping_tasks,
)


class TestGenerateTasksBasic(unittest.TestCase):
    """Tests básicos del generador aleatorio."""

    def test_generates_correct_count(self):
        """Debe generar exactamente n tareas."""
        for n in [0, 1, 5, 10, 100]:
            with self.subTest(n=n):
                tasks = generate_tasks(n=n)
                self.assertEqual(len(tasks), n)

    def test_all_tasks_have_valid_start_end(self):
        """Todo start_time debe ser estrictamente menor que end_time."""
        tasks = generate_tasks(n=200, seed=42)
        for task in tasks:
            self.assertLess(
                task.start_time,
                task.end_time,
                msg=f"Task {task.id}: start_time >= end_time"
            )

    def test_all_tasks_have_positive_profit(self):
        """Todo profit debe ser > 0."""
        tasks = generate_tasks(n=200, seed=42)
        for task in tasks:
            self.assertGreater(task.profit, 0, msg=f"Task {task.id}: profit <= 0")

    def test_task_ids_are_sequential(self):
        """Los IDs deben ser 1, 2, 3, ..., n."""
        tasks = generate_tasks(n=10, seed=42)
        for i, task in enumerate(tasks, 1):
            self.assertEqual(task.id, i)


class TestGenerateTasksReproducibility(unittest.TestCase):
    """Tests de reproducibilidad con semilla."""

    def test_same_seed_produces_same_tasks(self):
        """La misma semilla debe producir exactamente las mismas tareas."""
        tasks_a = generate_tasks(n=50, seed=42)
        tasks_b = generate_tasks(n=50, seed=42)
        self.assertEqual(len(tasks_a), len(tasks_b))
        for a, b in zip(tasks_a, tasks_b):
            self.assertEqual(a.id, b.id)
            self.assertEqual(a.start_time, b.start_time)
            self.assertEqual(a.end_time, b.end_time)
            self.assertEqual(a.profit, b.profit)

    def test_different_seeds_produce_different_tasks(self):
        """Semillas diferentes deben producir tareas diferentes."""
        tasks_a = generate_tasks(n=50, seed=42)
        tasks_b = generate_tasks(n=50, seed=99)
        # Es extremadamente improbable que sean idénticas con semillas diferentes
        profits_a = [t.profit for t in tasks_a]
        profits_b = [t.profit for t in tasks_b]
        self.assertNotEqual(profits_a, profits_b)


class TestGenerateTasksEdgeCases(unittest.TestCase):
    """Tests de casos límite."""

    def test_empty_generates_empty_list(self):
        """n=0 debe retornar lista vacía."""
        tasks = generate_tasks(n=0)
        self.assertEqual(tasks, [])

    def test_single_task_generation(self):
        """n=1 debe retornar exactamente 1 tarea válida."""
        tasks = generate_tasks(n=1, seed=1)
        self.assertEqual(len(tasks), 1)
        self.assertLess(tasks[0].start_time, tasks[0].end_time)
        self.assertGreater(tasks[0].profit, 0)

    def test_invalid_n_raises_error(self):
        """n negativo debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            generate_tasks(n=-1)


class TestGreedyFailureCaseGenerator(unittest.TestCase):
    """Tests del caso determinista de fallo del Greedy."""

    def test_returns_four_tasks(self):
        tasks = generate_greedy_failure_case()
        self.assertEqual(len(tasks), 4)

    def test_all_tasks_are_valid(self):
        tasks = generate_greedy_failure_case()
        for task in tasks:
            self.assertLess(task.start_time, task.end_time)
            self.assertGreater(task.profit, 0)

    def test_greedy_profit_is_10(self):
        """El Greedy debe obtener ganancia 10 (subóptimo) en este caso."""
        from src.algorithms.greedy import greedy_task_selection
        tasks = generate_greedy_failure_case()
        result = greedy_task_selection(tasks)
        self.assertEqual(result.total_profit, 10)

    def test_optimal_profit_is_12(self):
        """El óptimo debe ser 12 (T2+T3 = 6+6) en este caso."""
        from src.algorithms.dynamic_programming_linear import dp_linear_task_selection
        tasks = generate_greedy_failure_case()
        result = dp_linear_task_selection(tasks)
        self.assertEqual(result.total_profit, 12)

    def test_deterministic_output(self):
        """El caso de fallo debe ser siempre idéntico (determinista)."""
        tasks_a = generate_greedy_failure_case()
        tasks_b = generate_greedy_failure_case()
        for a, b in zip(tasks_a, tasks_b):
            self.assertEqual(a, b)


class TestSpecialGenerators(unittest.TestCase):
    """Tests de los generadores de casos especiales."""

    def test_all_compatible_tasks_no_overlap(self):
        """Las tareas generadas como compatibles no deben solaparse."""
        tasks = generate_all_compatible_tasks(n=10)
        sorted_tasks = sorted(tasks, key=lambda t: t.start_time)
        for i in range(len(sorted_tasks) - 1):
            self.assertLessEqual(
                sorted_tasks[i].end_time,
                sorted_tasks[i + 1].start_time,
                msg=f"Solapamiento: {sorted_tasks[i]} y {sorted_tasks[i+1]}"
            )

    def test_all_overlapping_tasks_overlap(self):
        """Las tareas generadas como solapantes deben solaparse todas entre sí."""
        tasks = generate_all_overlapping_tasks(n=5)
        # Todas tienen [0, 100], por tanto todas se solapan
        for task in tasks:
            self.assertEqual(task.start_time, 0)
            self.assertEqual(task.end_time, 100)


class TestTaskModel(unittest.TestCase):
    """Tests del modelo Task."""

    def test_task_creation_valid(self):
        """Task válida debe crearse sin errores."""
        task = Task(id=1, start_time=0, end_time=5, profit=10)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.start_time, 0)
        self.assertEqual(task.end_time, 5)
        self.assertEqual(task.profit, 10)

    def test_task_invalid_start_end(self):
        """start_time >= end_time debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            Task(id=1, start_time=5, end_time=5, profit=10)
        with self.assertRaises(ValueError):
            Task(id=1, start_time=10, end_time=5, profit=10)

    def test_task_invalid_profit(self):
        """profit <= 0 debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            Task(id=1, start_time=0, end_time=5, profit=0)
        with self.assertRaises(ValueError):
            Task(id=1, start_time=0, end_time=5, profit=-1)

    def test_task_is_frozen(self):
        """Task debe ser inmutable (frozen=True)."""
        task = Task(id=1, start_time=0, end_time=5, profit=10)
        with self.assertRaises(Exception):
            task.profit = 999  # type: ignore

    def test_task_compatibility(self):
        """Verificar la lógica de compatibilidad entre tareas."""
        t1 = Task(id=1, start_time=0, end_time=5, profit=10)
        t2 = Task(id=2, start_time=5, end_time=10, profit=10)  # adyacente → compatible
        t3 = Task(id=3, start_time=3, end_time=8, profit=10)   # solapante → no compatible

        self.assertTrue(t1.is_compatible_with(t2))
        self.assertTrue(t2.is_compatible_with(t1))
        self.assertFalse(t1.is_compatible_with(t3))
        self.assertFalse(t3.is_compatible_with(t1))

    def test_task_duration(self):
        """La duración debe ser end_time - start_time."""
        task = Task(id=1, start_time=3, end_time=10, profit=5)
        self.assertEqual(task.duration(), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)

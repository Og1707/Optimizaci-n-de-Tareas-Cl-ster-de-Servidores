"""
Resultado común para todos los algoritmos de optimización de tareas.

Decisión de diseño:
    Todos los algoritmos devuelven el mismo tipo AlgorithmResult.
    Esto facilita la comparación, el benchmarking y los tests,
    sin acoplar cada algoritmo al código que lo llama.
"""

from dataclasses import dataclass, field
from typing import List

from src.models.task import Task


@dataclass
class AlgorithmResult:
    """
    Encapsula el resultado de ejecutar cualquiera de los tres algoritmos.

    Atributos:
        selected_tasks: Lista de tareas seleccionadas en la solución.
        total_profit:   Ganancia total de las tareas seleccionadas.
        algorithm_name: Nombre descriptivo del algoritmo que produjo el resultado.

    Invariante:
        total_profit == sum(t.profit for t in selected_tasks)
    """

    selected_tasks: List[Task] = field(default_factory=list)
    total_profit: int = 0
    algorithm_name: str = ""

    def __post_init__(self) -> None:
        # Verificamos que total_profit sea consistente con las tareas seleccionadas.
        # Solo se verifica cuando hay tareas (evita falsos positivos en construcción parcial).
        if self.selected_tasks:
            expected = sum(t.profit for t in self.selected_tasks)
            if self.total_profit != expected:
                raise ValueError(
                    f"total_profit ({self.total_profit}) no coincide con "
                    f"la suma de ganancias de las tareas ({expected})."
                )

    @property
    def count(self) -> int:
        """Número de tareas seleccionadas."""
        return len(self.selected_tasks)

    def __repr__(self) -> str:
        return (
            f"AlgorithmResult(algorithm='{self.algorithm_name}', "
            f"profit={self.total_profit}, "
            f"tasks_selected={self.count})"
        )

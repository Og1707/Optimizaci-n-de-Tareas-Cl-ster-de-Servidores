"""
Modelo de datos para una tarea del clúster de servidores.

Decisión de diseño:
    Se utiliza @dataclass(frozen=True) para hacer las tareas inmutables.
    Esto es importante porque:
    1. Las tareas no deben modificarse después de crearse (integridad del modelo).
    2. Las instancias inmutables pueden usarse como claves de diccionario o en sets.
    3. Facilita el razonamiento sobre el estado del programa (sin efectos secundarios).
    4. Es la representación más cercana al concepto matemático de una "tarea fija".

    frozen=True implica que __hash__ se genera automáticamente, lo que permite
    comparaciones y uso en colecciones hash.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    """
    Representa una tarea a ejecutar en el clúster de servidores.

    Atributos:
        id (int): Identificador único de la tarea. Empieza en 1 por convención.
        start_time (int): Tiempo de inicio de la tarea (unidad arbitraria).
        end_time (int): Tiempo de finalización de la tarea. Debe ser > start_time.
        profit (int): Ganancia o prioridad asociada a ejecutar esta tarea. Debe ser > 0.

    Invariante:
        start_time < end_time
        profit > 0

    Convención de compatibilidad:
        Dos tareas A y B son compatibles si no se solapan.
        Se adopta la convención: A y B son compatibles si A.end_time <= B.start_time.
        Es decir, una tarea que TERMINA en t=5 es compatible con una que EMPIEZA en t=5.
        Esta convención es estándar en el problema de Weighted Interval Scheduling.
    """

    id: int
    start_time: int
    end_time: int
    profit: int

    def __post_init__(self) -> None:
        """Valida que los valores de la tarea sean coherentes."""
        if self.start_time >= self.end_time:
            raise ValueError(
                f"Task {self.id}: start_time ({self.start_time}) "
                f"debe ser menor que end_time ({self.end_time})."
            )
        if self.profit <= 0:
            raise ValueError(
                f"Task {self.id}: profit ({self.profit}) debe ser mayor que 0."
            )
        if self.id < 0:
            raise ValueError(f"Task id ({self.id}) debe ser >= 0.")

    def is_compatible_with(self, other: "Task") -> bool:
        """
        Determina si esta tarea es compatible con 'other'.

        Dos tareas son compatibles si no se solapan.
        Convención: end_time <= start_time (el igual está permitido).

        Args:
            other: La otra tarea a comparar.

        Returns:
            True si las tareas no se solapan, False si se solapan.
        """
        return self.end_time <= other.start_time or other.end_time <= self.start_time

    def duration(self) -> int:
        """Retorna la duración de la tarea."""
        return self.end_time - self.start_time

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id}, "
            f"start={self.start_time}, "
            f"end={self.end_time}, "
            f"profit={self.profit})"
        )

    def __str__(self) -> str:
        return (
            f"T{self.id:>3} | "
            f"[{self.start_time:>6} → {self.end_time:>6}] | "
            f"profit={self.profit:>6}"
        )

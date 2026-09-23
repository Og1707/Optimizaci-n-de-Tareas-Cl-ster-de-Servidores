# Descripción de los Algoritmos

## El problema: Weighted Interval Scheduling

Dado un conjunto de tareas con intervalos `[start_time, end_time]` y ganancias `profit`,
encontrar el subconjunto de tareas no solapadas que maximiza la ganancia total.

**Restricción:** El servidor ejecuta solo una tarea a la vez.

**Convención de compatibilidad:**
```
Tarea A y Tarea B son compatibles si A.end_time <= B.start_time
```
El igual está permitido: una tarea que termina en `t=5` puede coexistir con
una que empieza en `t=5`.

---

## Enfoque A — Greedy (Voraz)

### Idea intuitiva

"Siempre elige la tarea que más ganancia produce ahora."

### Pasos del algoritmo

1. Ordenar las tareas de **mayor a menor ganancia** (`profit` descendente).
2. Recorrer la lista ordenada.
3. Seleccionar una tarea si no se solapa con la última ya seleccionada.

### Pseudocódigo

```
sorted_tasks = sort(tasks, by=profit, descending=True)
selected = []
last_end = -infinito

for task in sorted_tasks:
    if task.start_time >= last_end:
        selected.append(task)
        last_end = task.end_time

return selected
```

### Por qué puede fallar

El Greedy toma decisiones localmente óptimas sin considerar el efecto global.

**Ejemplo de fallo:**
```
T1: [0→10], profit=10   ← Greedy la elige (mayor ganancia)
T2: [0→5],  profit=6
T3: [5→10], profit=6
```

- Greedy elige T1 (mayor ganancia individual: 10).
- Al elegir T1, bloquea a T2 y T3 (se solapan con T1).
- Resultado Greedy: ganancia = **10**
- Resultado óptimo: T2 + T3 = **12**

El Greedy cayó en la "trampa de la avaricia": optimizó el paso actual
sin ver que dos pasos "mediocres" juntos son mejores.

---

## Enfoque B — Programación Dinámica + Búsqueda Lineal

### Idea intuitiva

"Para cada tarea, pregunta: ¿me conviene tomarla, o es mejor ignorarla?"

La respuesta se calcula sistemáticamente para todas las tareas, de la más
temprana a la más tardía (en tiempo de finalización).

### Fundamento matemático

Sea `dp[i]` = la máxima ganancia obtenible considerando las primeras `i` tareas
(ordenadas por `end_time` ascendente).

Sea `p(i)` = el índice más alto `j < i` tal que `tasks[j].end_time <= tasks[i].start_time`.
Si no existe tal `j`, `p(i) = 0`.

**Recurrencia:**
```
dp[0] = 0    (sin tareas, ganancia = 0)

dp[i] = max(
    tasks[i].profit + dp[p(i)],  # Opción 1: tomar la tarea i
    dp[i-1]                       # Opción 2: rechazar la tarea i
)
```

### Interpretación del servidor

- **Opción 1 (tomar):** El servidor ejecuta la tarea `i` y combina su ganancia
  con la mejor solución posible de las tareas que terminaron antes de que `i` empiece.

- **Opción 2 (rechazar):** El servidor no ejecuta la tarea `i` y conserva la
  mejor combinación de tareas anteriores.

El `max()` garantiza que siempre se toma la decisión más rentable.

### Por qué el orden por `end_time` es crítico

La recurrencia depende de que `dp[i-1]` represente "la mejor solución con las
tareas que pueden terminar antes de la tarea `i`".

Si las tareas están ordenadas por `end_time`:
- Las tareas con índice `< i` siempre terminan antes (o al mismo tiempo) que la tarea `i`.
- `p(i)` puede encontrarse mirando hacia la izquierda en la lista.
- La recurrencia es correcta.

Si el orden cambia (por `start_time`, por `profit`, etc.):
- `dp[i-1]` puede incluir tareas que terminan **después** de que empiece la tarea `i`.
- `p(i)` devuelve un índice incorrecto.
- La solución ya no es óptima (puede ser incorrecta o subóptima).

### Búsqueda lineal de `p(i)`

```python
def find_last_compatible_linear(tasks, i):
    for j in range(i - 1, -1, -1):
        if tasks[j].end_time <= tasks[i].start_time:
            return j + 1  # índice base 1
    return 0
```

Recorre desde `i-1` hacia `0`. En el peor caso recorre toda la lista: **O(n)**.

### Reconstrucción de la solución

Después de construir `dp[]`, recorremos hacia atrás:

```
i = n
while i >= 1:
    if tasks[i].profit + dp[p(i)] >= dp[i-1]:
        seleccionar tarea i
        i = p(i)
    else:
        i -= 1
```

---

## Enfoque C — Programación Dinámica + Búsqueda Binaria

### Diferencia con el Enfoque B

Misma recurrencia. Misma lógica. Mismos resultados.

La única diferencia: `p(i)` se calcula en **O(log n)** en lugar de **O(n)**.

### Por qué funciona la búsqueda binaria

Las tareas están ordenadas por `end_time`. Por lo tanto, el array de `end_times`
es una lista ordenada ascendentemente.

Para encontrar el mayor `j` tal que `tasks[j].end_time <= tasks[i].start_time`,
se busca la posición de `tasks[i].start_time` en el array `end_times` usando
`bisect_right`:

```python
p_i = bisect.bisect_right(end_times[:i-1], tasks[i].start_time)
```

`bisect_right(arr, x)` retorna el índice de inserción de `x` en `arr` (lista ordenada).
Esto equivale al número de elementos en `arr` que son `<= x`.
Por lo tanto, retorna directamente el índice `p(i)` en base 1.

**Condición necesaria:** El array `end_times` debe estar ordenado.
Esto se garantiza porque las tareas se ordenaron por `end_time` en el paso 1.
Si el ordenamiento cambia, `bisect_right` da resultados incorrectos.

### Ejemplo de búsqueda binaria

```
end_times = [3, 4, 6, 9, 10]   (ordenado)
task[5].start_time = 5

bisect_right([3, 4, 6, 9, 10], 5) = 2
             ^  ^
             0  1
```

Resultado: `p(5) = 2`, es decir, la última tarea compatible es la tarea de índice 1 (base 0),
que tiene `end_time = 4 <= 5`. Correcto.

---

## Comparación visual

```
N = 1,000 tareas:
  DP Lineal  O(n²):       ~1,000,000 operaciones
  DP Binaria O(n log n):  ~10,000 operaciones  (100x menos)

N = 10,000 tareas:
  DP Lineal  O(n²):       ~100,000,000 operaciones
  DP Binaria O(n log n):  ~130,000 operaciones  (~769x menos)

N = 100,000 tareas:
  DP Lineal  O(n²):       ~10,000,000,000 operaciones
  DP Binaria O(n log n):  ~1,700,000 operaciones  (~5,882x menos)
```

---

## Verificación de correctitud

Tanto el Enfoque B como el C implementan la misma recurrencia.
Por lo tanto, deben producir exactamente la misma ganancia máxima.

Los tests verifican esto con múltiples semillas:

```python
def test_same_profit_multiple_sizes_and_seeds(self):
    for n, seed in [(10,1), (50,10), (100,42), (1000,7), ...]:
        tasks = generate_tasks(n=n, seed=seed)
        linear = dp_linear_task_selection(tasks)
        binary = dp_binary_task_selection(tasks)
        assert linear.total_profit == binary.total_profit
```

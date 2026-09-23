# Análisis de Complejidad

## Resumen

| Algoritmo | Tiempo | Espacio |
|-----------|--------|---------|
| Greedy | O(n log n) | O(n) |
| DP + Búsqueda Lineal | O(n²) | O(n) |
| DP + Búsqueda Binaria | O(n log n) | O(n) |

---

## Complejidad del Greedy

### Temporal

**Paso 1: Ordenamiento**
```
sorted(tasks, key=lambda t: t.profit, reverse=True)
```
- Python usa Timsort, un algoritmo híbrido de merge sort + insertion sort.
- Complejidad: O(n log n) comparaciones.

**Paso 2: Recorrido y selección**
```
for task in sorted_tasks:
    if task.start_time >= last_end:
        ...
```
- Se recorre la lista una vez: O(n) iteraciones.
- Cada iteración hace O(1) trabajo (comparación y posible append).
- Total: O(n).

**Total:**
```
O(n log n) + O(n) = O(n log n)    (dominado por el ordenamiento)
```

### Espacial

- Lista de tareas ordenadas: O(n)
- Lista de tareas seleccionadas: O(n) en el peor caso
- Variable `last_end_time`: O(1)
- **Total: O(n)**

---

## Complejidad de DP + Búsqueda Lineal

### Temporal

**Paso 1: Ordenamiento por end_time**
```
sorted(tasks, key=lambda t: t.end_time)
```
- Timsort: O(n log n)

**Paso 2: Construcción del array dp[]**
```
for i in range(1, n + 1):          ← n iteraciones
    p_i = find_last_compatible_linear(tasks, i - 1)   ← O(n) cada una
    dp[i] = max(profit + dp[p_i], dp[i-1])             ← O(1)
```

La función `find_last_compatible_linear(tasks, i)` recorre desde `i-1` hasta `0`.
- Mejor caso: el compatible está al final de la lista → O(1)
- Peor caso: no hay compatible o está al inicio → O(n)
- Caso promedio: O(n/2) = O(n)

Total del bucle DP:
```
n iteraciones × O(n) por búsqueda = O(n²)
```

**Paso 3: Reconstrucción de la solución**
```
while i >= 1:
    find_last_compatible_linear(...)   ← O(n) cada una
    i -= 1 o i = p_i
```
- El while ejecuta a lo sumo n iteraciones.
- Total: O(n) × O(n) = O(n²).

**Total:**
```
O(n log n) + O(n²) + O(n²) = O(n²)    (dominado por las búsquedas lineales)
```

### Por qué es O(n²) exactamente

La búsqueda lineal tiene que comparar `tasks[j].end_time <= tasks[i].start_time`
para valores de `j` que van desde `i-1` hasta encontrar un compatible.

En el peor caso (todas las tareas se solapan, ningún compatible excepto 0),
la búsqueda para la tarea `i` recorre `i-1` tareas:
```
Tarea 1: 0 comparaciones
Tarea 2: 1 comparación
Tarea 3: 2 comparaciones
...
Tarea n: n-1 comparaciones

Total: 0 + 1 + 2 + ... + (n-1) = n(n-1)/2 = O(n²)
```

### Espacial

- `dp[]` array de n+1 enteros: O(n)
- Lista de tareas ordenadas: O(n)
- Lista de tareas seleccionadas: O(n)
- **Total: O(n)**

---

## Complejidad de DP + Búsqueda Binaria

### Temporal

**Paso 1: Ordenamiento por end_time**
- Timsort: O(n log n)

**Paso 2: Construcción del array `end_times`**
```
end_times = [task.end_time for task in sorted_tasks]
```
- O(n)

**Paso 3: Construcción del array dp[]**
```
for i in range(1, n + 1):                   ← n iteraciones
    p_i = bisect_right(end_times[:i-1], ...) ← O(log n) cada una
    dp[i] = max(...)                          ← O(1)
```

`bisect_right` realiza una búsqueda binaria sobre una lista de `i-1` elementos.
Una búsqueda binaria sobre una lista de tamaño m tiene complejidad O(log m).
Para m ≤ n: O(log n).

Total del bucle DP:
```
n iteraciones × O(log n) por búsqueda = O(n log n)
```

**Paso 4: Reconstrucción de la solución**
- A lo sumo n iteraciones × O(log n) por búsqueda binaria = O(n log n)

**Total:**
```
O(n log n) + O(n) + O(n log n) + O(n log n) = O(n log n)
```

### Por qué la búsqueda binaria es O(log n)

La búsqueda binaria divide el espacio de búsqueda a la mitad en cada paso:

```
Paso 1: n/2  elementos restantes
Paso 2: n/4  elementos restantes
Paso 3: n/8  elementos restantes
...
Paso k: n/2^k = 1  →  k = log2(n)
```

Para encontrar un elemento en una lista de n elementos: O(log n) comparaciones.

Comparación directa con la búsqueda lineal:
```
n=10:      lineal=10,       binaria=4
n=1,000:   lineal=1,000,    binaria=10
n=100,000: lineal=100,000,  binaria=17
```

### Espacial

- `dp[]`: O(n)
- `end_times[]`: O(n)
- Lista de tareas ordenadas: O(n)
- **Total: O(n)**

---

## Comparación empírica

Los tiempos reales varían por hardware, pero la tendencia es predecible:

**Cuando N se duplica:**
- DP Lineal O(n²): el tiempo se multiplica aproximadamente por **4**
  (porque (2n)² = 4n²)
- DP Binaria O(n log n): el tiempo se multiplica aproximadamente por **2**
  (porque 2n log(2n) ≈ 2n log n para n grande)

**Para N = 100,000:**
- Número de operaciones de búsqueda en Lineal: ~5,000,000,000 (5 billones)
- Número de operaciones de búsqueda en Binaria: ~1,700,000 (1.7 millones)
- Diferencia teórica: ~5,882x menos operaciones con búsqueda binaria

---

## Nota sobre Timsort

Python usa **Timsort** para la función `sorted()`:
- Combina merge sort e insertion sort.
- Mejor caso: O(n) cuando los datos ya están ordenados.
- Peor caso: O(n log n).
- Para el benchmark, los datos se generan aleatoriamente, por lo que se espera O(n log n).

---

## Espacio auxiliar

Los tres algoritmos usan O(n) espacio adicional.

Ninguno usa recursión profunda (todos son iterativos), por lo que
el espacio de la pila de llamadas es O(1).

La reconstrucción de la solución también es iterativa.

# Guía de Sustentación

Esta guía prepara al estudiante para defender el código ante el profesor.
Contiene respuestas preparadas para cada reto, con explicaciones técnicas
y conexiones con el código real.

---

## RETO 1: La trampa de la avaricia

### Pregunta: ¿Por qué el Greedy falla?

**Respuesta corta:**
El Greedy optimiza localmente (la mejor decisión ahora) sin considerar el impacto
global. Una elección "óptima" en este paso puede bloquear combinaciones mejores
en pasos futuros.

**Respuesta con el caso concreto:**

El caso de prueba está en `src/generators/task_generator.py`,
función `generate_greedy_failure_case()`:

```
T1: [0→10], profit=10  ← Greedy la elige (máxima ganancia individual)
T2: [0→5],  profit=6
T3: [5→10], profit=6
T4: [2→8],  profit=9   ← Greedy intenta elegirla pero solapa con T1
```

El Greedy ordena por ganancia: T1(10), T4(9), T2(6), T3(6).
Elige T1 (profit=10).
Intenta elegir T4: start=2 < end=10 de T1 → solapan → la rechaza.
Intenta elegir T2: start=0 < end=10 de T1 → solapan → la rechaza.
Intenta elegir T3: start=5 < end=10 de T1 → solapan → la rechaza.

Resultado Greedy: **10**. Solo T1.

La DP evalúa sistemáticamente: la combinación T2+T3 = 6+6 = **12** es mejor.
El Greedy nunca la consideró porque T1 "parecía" mejor individualmente.

### Pregunta: ¿Qué significa "óptimo local" vs "óptimo global"?

**Óptimo local:** La mejor decisión considerando solo el estado actual.
En el Greedy: "T1 tiene profit=10, ninguna tarea individual da más en este momento."

**Óptimo global:** La mejor solución considerando TODAS las posibles combinaciones.
La DP garantiza el óptimo global porque evalúa exhaustivamente todas las opciones
mediante la tabla dp[].

**Analogía:** Es como elegir el camino más rápido en cada intersección sin ver
el mapa completo. Puedes terminar en un camino sin salida.

### Pregunta: ¿Por qué la DP sí encuentra la combinación óptima?

La DP no adivina: evalúa sistemáticamente todas las opciones.

Cuando procesa la tarea T3 (end=10):
```
dp[3] = max(
    profit[T3] + dp[p(T3)],   = 6 + dp[indice de T2] = 6 + 6 = 12
    dp[2]                      = 6 (la mejor solución sin T3)
)
= max(12, 6) = 12
```

La DP descubrió que T2+T3 = 12, algo que el Greedy nunca consideró.

---

## RETO 2: El orden del caos

### Pregunta: ¿Por qué ordenar por `end_time` ascendente?

**La línea clave en el código:**

En `src/algorithms/dynamic_programming_linear.py`, línea marcada con `# ← RETO 2`:
```python
sorted_tasks = sorted(tasks, key=lambda task: task.end_time)
```

**Por qué este orden es el único válido:**

La recurrencia es:
```
dp[i] = max(profit[i] + dp[p(i)], dp[i-1])
```

Esta recurrencia tiene dos dependencias:

1. **`dp[i-1]`** debe representar "la mejor solución con las tareas de índice menor a i".
   Para que esto sea "la mejor solución con tareas que terminaron antes":
   - Las tareas con índice `< i` deben terminar antes (o igual) que la tarea `i`.
   - Esto solo es cierto si están ordenadas por `end_time`.

2. **`dp[p(i)]`** requiere que `p(i)` sea el índice de la última tarea compatible.
   "Última compatible" significa: la de mayor índice `j` tal que `j.end_time <= i.start_time`.
   Para que esto sea buscable mirando hacia la izquierda:
   - Las tareas a la izquierda deben tener `end_time` menor o igual.
   - Solo es cierto si están ordenadas por `end_time`.

### Pregunta: ¿Qué ocurre si ordenamos por `start_time`?

**El problema concreto:**

Suponga este caso:
```
T1: [0→10], profit=5
T2: [2→4],  profit=8
T3: [6→9],  profit=3
```

Ordenado por start_time: T1([0→10]), T2([2→4]), T3([6→9])

Cuando procesamos T3 (índice 3), buscamos la última compatible:
- T2 termina en 4 <= 6 → compatible. p(3) = 2.
- dp[3] = max(3 + dp[2], dp[2]) → correcto hasta aquí.

Pero cuando calculamos dp[2] para T2([2→4]):
- Buscamos la última compatible con T2 (start=2).
- T1 termina en 10 > 2 → NO compatible.
- p(2) = 0.
- dp[2] = max(8 + dp[0], dp[1]) = max(8, 5) = 8.

¿Correcto? Veamos:
- dp[1] = dp de T1([0→10]) = 5.
- dp[2] = max(8, 5) = 8 (T2 sola).

Pero T1 y T2 se solapan (T1 va de 0 a 10, T2 de 2 a 4), eso está bien.

Sin embargo, dp[3]:
- p(3) = índice de última compatible con T3 (start=6) usando orden start_time.
- Buscamos hacia atrás: T2 termina en 4 <= 6 → p(3) = 2.
- dp[3] = max(3 + dp[2], dp[2]) = max(3+8, 8) = max(11, 8) = 11.

¡Pero espera! dp[2] = 8 (incluye T2 [2→4]).
Si tomamos T3 ([6→9]) + T2 ([2→4]), son compatibles. Ganancia = 11.
¿Es eso el óptimo? ¿Qué pasa con T1 ([0→10])? T1 solapa con T2 y T3.
Solo se puede tomar T1 sola (profit=5).
Óptimo real: T2+T3 = 11. ¡El resultado es correcto en este caso!

**Pero el orden por start_time puede fallar en otros casos:**

El problema real ocurre cuando hay tareas cuyo `end_time` no está ordenado
de izquierda a derecha en el array ordenado por `start_time`.

Ejemplo que falla:
```
T1: [0→8],  profit=5    (start=0)
T2: [1→3],  profit=8    (start=1)
T3: [3→6],  profit=4    (start=3)
```

Ordenado por start_time: T1([0→8]), T2([1→3]), T3([3→6])

dp[1] = 5 (T1)
dp[2]: T2 start=1. Búsqueda hacia atrás: T1 end=8 > 1 → no compatible. p=0.
  dp[2] = max(8 + 0, 5) = 8

dp[3]: T3 start=3. Búsqueda hacia atrás: T2 end=3 <= 3 → compatible! p=2.
  dp[3] = max(4 + dp[2], dp[2]) = max(4+8, 8) = 12

Resultado con orden start_time: 12 (T2+T3).

Con orden correcto (end_time): T2([1→3]), T3([3→6]), T1([0→8])
  dp[1]=8 (T2), dp[2]=max(4+8, 8)=12 (T2+T3), dp[3]=max(5+0, 12)=12.

En este caso coincide. Pero el orden por start_time puede dar resultados
incorrectos en casos donde una tarea de inicio temprano termina muy tarde,
haciendo que la búsqueda de compatibles retorne índices incorrectos.

**La respuesta matemática definitiva:**

La recurrencia requiere que para todo `i`, la función `p(i)` retorne el
**mayor índice j < i tal que end_time[j] <= start_time[i]**.

Para que esto funcione buscando hacia la izquierda, se necesita que los
end_times estén en orden no-decreciente en el array. Esto se garantiza
ÚNICAMENTE si las tareas están ordenadas por end_time.

Con cualquier otro orden, los end_times en el array no están ordenados,
y la búsqueda hacia la izquierda puede retornar p(i) incorrecto.

### Pregunta: Modifique el código en vivo y muestre el error.

La modificación es en **una sola línea** en cada archivo DP:

```python
# ANTES (correcto):
sorted_tasks = sorted(tasks, key=lambda task: task.end_time)

# DESPUÉS (incorrecto - cambiar para la demostración):
sorted_tasks = sorted(tasks, key=lambda task: task.start_time)
```

Para verificar, ejecutar el test `test_dp_failure_case_tasks_are_t2_and_t3`:
con el orden incorrecto, este test fallará.

---

## RETO 3: La decisión del algoritmo

### Pregunta: ¿Dónde está la recurrencia dp[i] = max(...)?

En `src/algorithms/dynamic_programming_linear.py`, buscando el comentario
`# ← RETO 3: recurrencia`:

```python
dp[i] = max(take_task, skip_task)   # ← RETO 3: recurrencia
```

La línea completa en contexto:
```python
take_task = current_task.profit + dp[p_i]   # Opción 1: tomar
skip_task = dp[i - 1]                        # Opción 2: rechazar
dp[i] = max(take_task, skip_task)            # ← RETO 3: recurrencia
```

En `dynamic_programming_binary.py` está la misma línea (el Enfoque C usa
la misma recurrencia, solo cambia cómo se calcula `p_i`).

### Pregunta: ¿Qué significa `dp[i]`?

`dp[i]` = la **máxima ganancia posible** considerando las primeras `i` tareas
(donde las tareas están ordenadas por `end_time`).

Es decir: si solo existieran las tareas 1, 2, ..., i, ¿cuánto es lo máximo
que puede ganar el servidor?

### Pregunta: ¿Qué significa tomar la tarea?

```
take_task = current_task.profit + dp[p_i]
```

**Significa:** El servidor decide ejecutar la tarea actual (`i`).
- Gana `current_task.profit` de la tarea actual.
- Más la mejor ganancia posible de las tareas compatibles anteriores (`dp[p_i]`).
- `dp[p_i]` es la mejor ganancia con las tareas que terminaron ANTES de que
  empiece la tarea actual. Son las únicas tareas que el servidor pudo haber
  ejecutado antes sin solapamiento.

**En términos del servidor:** "Ejecuto esta tarea ahora y ya ejecuté la mejor
combinación de tareas que no interfieren con ella."

### Pregunta: ¿Qué significa rechazar la tarea?

```
skip_task = dp[i - 1]
```

**Significa:** El servidor decide NO ejecutar la tarea actual.
- La ganancia es la mejor que se había logrado sin incluir la tarea actual.
- `dp[i-1]` = la mejor solución considerando todas las tareas anteriores.

**En términos del servidor:** "Esta tarea no vale la pena. Prefiero el
tiempo para la combinación de tareas anteriores que ya encontré."

### Pregunta: ¿Qué representa `j` (o `p_i`)?

`j` o `p_i` es el **índice de la última tarea compatible** con la tarea actual.

"Última compatible" significa: la tarea con mayor índice tal que
su tiempo de finalización es menor o igual al tiempo de inicio de la tarea actual.

```
p_i = último j tal que tasks[j].end_time <= tasks[i].start_time
```

Es el "puente" que conecta la tarea actual con las tareas anteriores compatibles.

---

## RETO 4: Prueba de estrés

### Pregunta: ¿Por qué el Enfoque B es O(n²)?

Para cada una de las n tareas, la función `find_last_compatible_linear` recorre
la lista de tareas hacia atrás hasta encontrar un compatible.

En el peor caso (cuando hay que recorrer toda la lista), para la tarea `i` se
hacen `i-1` comparaciones:

```
Tarea 2: 1 comparación
Tarea 3: 2 comparaciones
...
Tarea n: n-1 comparaciones

Total: 1 + 2 + ... + (n-1) = n(n-1)/2 ≈ n²/2 = O(n²)
```

### Pregunta: ¿Por qué el Enfoque C es O(n log n)?

La función `bisect_right` realiza una búsqueda binaria en una lista ordenada.
Una búsqueda binaria divide el espacio a la mitad en cada paso:

```
Paso 1: n/2 elementos
Paso 2: n/4 elementos
...
Paso k: 1 elemento → k = log₂(n)
```

Para cada una de las n tareas: O(log n) → total: O(n log n).

El ordenamiento inicial también es O(n log n), por lo que el total es O(n log n).

### Pregunta: ¿Qué hace exactamente la búsqueda binaria aquí?

```python
p_i = bisect.bisect_right(end_times[:i-1], current_task.start_time)
```

`bisect_right(arr, x)` retorna el índice donde se insertaría `x` en la lista
ordenada `arr` para mantener el orden. Equivale a:
"¿Cuántos elementos de `arr` son menores o iguales a `x`?"

Aquí `arr = end_times[:i-1]` y `x = current_task.start_time`.

Retorna: el número de tareas anteriores cuyo `end_time <= start_time_actual`.
Esto es exactamente `p_i` en base 1 (el índice del último compatible).

### Pregunta: ¿Por qué funciona solo porque las tareas están ordenadas?

La búsqueda binaria **requiere** que la lista esté ordenada.
Si no lo está, la división a la mitad no garantiza que el elemento buscado
esté en la mitad correcta.

En este caso, `end_times` está ordenado ascendentemente porque las tareas
se ordenaron por `end_time` en el paso 1. Por eso la búsqueda binaria es válida.

Si cambiamos el orden a `start_time`:
- `end_times` ya no estaría ordenado.
- `bisect_right` daría resultados incorrectos.
- El algoritmo fallaría.

### Pregunta: ¿Qué sucede cuando N crece?

```
N = 1,000:
  DP Lineal:  ~500,000 operaciones de búsqueda
  DP Binaria: ~10,000 operaciones de búsqueda

N = 10,000:
  DP Lineal:  ~50,000,000 operaciones
  DP Binaria: ~130,000 operaciones  (~385x menos)

N = 100,000:
  DP Lineal:  ~5,000,000,000 operaciones
  DP Binaria: ~1,700,000 operaciones  (~2,941x menos)
```

El tiempo de DP Lineal crece cuadráticamente: al duplicar N, el tiempo se cuadruplica.
El tiempo de DP Binaria crece casi linealmente: al duplicar N, el tiempo se duplica.

Para N=100,000, el Enfoque B puede tardar minutos mientras el Enfoque C tarda segundos
o milisegundos. Esto es observable en el benchmark en vivo.

---

## Líneas clave para señalar durante la sustentación

| Reto | Archivo | Línea a señalar |
|------|---------|-----------------|
| Reto 1 | `src/generators/task_generator.py` | `generate_greedy_failure_case()` |
| Reto 2 | `src/algorithms/dynamic_programming_linear.py` | `sorted(..., key=lambda task: task.end_time)` marcada `# ← RETO 2` |
| Reto 3 | `src/algorithms/dynamic_programming_linear.py` | `dp[i] = max(take_task, skip_task)` marcada `# ← RETO 3` |
| Reto 4 | `src/algorithms/dynamic_programming_linear.py` | `_find_last_compatible_linear()` |
| Reto 4 | `src/algorithms/dynamic_programming_binary.py` | `bisect.bisect_right(end_times[:i-1], ...)` |

---

## Respuestas rápidas para preguntas sorpresa

**¿Qué es Weighted Interval Scheduling?**
El problema de seleccionar intervalos no solapados con máxima ganancia total.
"Weighted" porque cada intervalo tiene un peso (profit), no solo existencia.

**¿Qué garantiza la DP pero no el Greedy?**
La optimalidad de la solución. La DP evalúa todas las posibilidades.

**¿Puede el Greedy a veces dar el resultado óptimo?**
Sí, en algunos casos coincide (por ejemplo, cuando todas las tareas son compatibles
y la de mayor ganancia no bloquea nada). Pero no está garantizado en general.

**¿Por qué p(i) y no simplemente i-1?**
Porque cuando tomamos la tarea `i`, no podemos tomar ninguna tarea que se solape
con ella. El dp[i-1] podría incluir tareas solapantes. dp[p(i)] solo incluye
tareas que definitivamente no se solapan con `i`.

**¿Qué pasaría si profit fuera 0 o negativo?**
El modelo Task valida que profit > 0. Las tareas con profit <= 0 nunca serían
seleccionadas de todas formas (rechazarlas siempre da dp[i] >= 0).

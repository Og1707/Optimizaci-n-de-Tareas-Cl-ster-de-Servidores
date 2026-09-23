## Proyecto Integrador: Optimización de Tareas en un Clúster de Servidores

## 1. El Escenario

Han sido contratados como ingenieros de optimización para un centro de supercomputación. El clúster principal recibe miles de peticiones de procesamiento al día. Dado que el servidor solo puede ejecutar una tarea a la vez, su objetivo es maximizar la ganancia total del servidor eligiendo qué tareas ejecutar y cuáles rechazar, sin que sus horarios se solapen.

Cada petición (tarea) contiene tres datos:

- Tiempo de inicio (Start time)

- Tiempo de finalización (End time)

- Ganancia/Prioridad (Profit/Weight)

## 2. Fase 1: Desarrollo del Código (Entregable)

Deberán escribir un programa (Lenguaje de preferencia) que genere un conjunto de datos de N tareas y resuelva el problema de selección de tareas utilizando tres enfoques distintos.

Nota importante sobre el uso de IA: El uso de herramientas de Inteligencia Artificial (ChatGPT, Claude, Copilot) para generar o estructurar este código está permitido. Sin embargo, el código es solo un requisito previo. La nota de este proyecto se definirá al 100% por su capacidad de analizar, modificar y defender este código en vivo.

- Enfoque A (Algoritmo Voraz/Greedy): Ordena las tareas de mayor a menor ganancia y selecciona secuencialmente las que no se solapen.

- Enfoque B (Programación Dinámica - Búsqueda Lineal): Implementa la solución óptima usando Programación Dinámica (DP), buscando la última tarea compatible iterando una por una (complejidad temporal O(n²)).

- Enfoque C (Programación Dinámica - Búsqueda Binaria): Optimiza el Enfoque B utilizando Búsqueda Binaria para encontrar la última tarea compatible (complejidad temporal O(n log n)).


## 3. Fase 2: La Sustentación (Evaluación)

Deben estar preparados para ejecutar su programa y responder a los siguientes cuatro retos en tiempo real ante el profesor:

## Reto 1: La trampa de la avaricia

Deberán inyectar en su programa un set de datos (creado manualmente por ustedes, de unas 4 o 5 tareas) donde se demuestre en pantalla que el Enfoque A (Greedy) falla y arroja una ganancia menor que los enfoques de Programación Dinámica. Deberán explicar al profesor por qué priorizar la ganancia individual desde el principio no siempre lleva a la solución óptima global.

## Reto 2: El orden del caos

Durante la sustentación, el profesor les pedirá que modifiquen una línea de su código en vivo para ordenar las tareas por tiempo de inicio o por ganancia, en lugar de por tiempo de finalización. Deberán ejecutar el código modificado y defender matemáticamente por qué el algoritmo acaba de colapsar y por qué el tiempo de finalización ascendente es el único orden válido para que la Programación Dinámica funcione.

## Reto 3: La decisión del algoritmo

Deberán proyectar el código de su Enfoque B o C, señalar la línea exacta donde ocurre la relación de recurrencia (usualmente dp[i] = max(...)), y traducir esa línea matemática a la lógica de negocios del servidor. ¿Qué significa exactamente, en términos de negocio y recursos, "tomar" o "no tomar" la tarea actual?

## Reto 4: Prueba de estrés (Benchmarking)

Ejecutarán su programa en vivo con N = 100,000 tareas generadas aleatoriamente. Deberán mostrar en consola la diferencia de tiempo de ejecución (en milisegundos o segundos) entre el Enfoque B y el Enfoque C. Luego, deberán explicar detalladamente cómo la operación de la búsqueda binaria logra esta reducción drástica de tiempo frente a la búsqueda lineal.

## 4. Rúbrica de Evaluación

| Criterio | Porcentaje | Descripción |
| --- | --- | --- |
| Funcionalidad del Código | 10% | Los tres enfoques compilan, |
|   |   | ejecutan sin errores y |
|   |   | generan los conjuntos de |
|   |   | datos de prueba |
|   |   | correctamente. |


| Criterio | Porcentaje | Descripción |
| --- | --- | --- |
| Reto 1 (Greedy vs DP) | 20% | Demuestra con éxito un caso |
|   |   | de falla del algoritmo Greedy |
|   |   | y argumenta claramente el |
|   |   | motivo conceptual. |
| Reto 2 (El Ordenamiento) | 25% | Modifica el código en vivo sin |
|   |   | dudar, predice el error y |
|   |   | argumenta la necesidad |
|   |   | matemática del |
|   |   | ordenamiento por tiempo de |
|   |   | finalización. |
| Reto 3 (La Recurrencia) | 20% | Identifica y explica a la |
|   |   | perfección la relación de |
|   |   | recurrencia dentro de su |
|   |   | propio código, conectándola |
|   |   | con el problema real. |
| Reto 4 (Benchmarking) | 25% | Realiza la prueba de estrés |
|   |   | (100k tareas) exitosamente y |
|   |   | explica la eficiencia |
|   |   | logarítmica de la búsqueda |
|   |   | binaria. |

¡Mucho éxito! Recuerden: la verdadera ingeniería de software no se trata de escribir el código (las máquinas ya hacen eso), sino de entender exactamente qué hace, por qué lo hace y cómo optimizarlo.

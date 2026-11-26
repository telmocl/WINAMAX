# Informe de pruebas funcionales de WINAMAX

Informe de la ejecución del [plan de pruebas funcionales](plan_pruebas.md) antes de la release final (historia #29).

- **Versión probada:** rama `dev`, con todas las historias de la release final fusionadas.
- **Pruebas automatizadas:** antes de la ejecución manual, `uv run pytest` terminó con 115 tests correctos y 1 omitido, sin fallos. Cada corrección se fusionó en `dev` con el flujo de GitHub Actions en verde.
- **Fecha de ejecución:** 26/11/2026.
- **Ejecutado por:** Vilouu (CP-08 a CP-14) y Claude, supervisado por Vilouu (resto de casos). El detalle de cada caso (resultado obtenido, estado, quién lo ejecutó y fecha) está en la sección 4 del plan de pruebas.

## 1. Resumen por ejecución

| Ejecución | Casos ejecutados | Correctos | Fallidos |
|---|---|---|---|
| 1. Primera ejecución de todos los casos del plan | 51 | 41 | 10 |
| 2. Repetición de los casos fallidos y del flujo completo (CP-51), tras las correcciones | 10 | 10 | 0 |

Casos fallidos en la ejecución 1: CP-16, CP-19, CP-20, CP-21, CP-22, CP-25, CP-26, CP-41, CP-46 y CP-51.

Tras la ejecución 2, **los 51 casos del plan son correctos**.

## 2. Errores encontrados

| Nº | Casos que lo detectaron | Descripción | Tarea en Taiga | Rama | Pull request | Estado |
|---|---|---|---|---|---|---|
| 1 | CP-16, CP-20, CP-21 | Al separar los datos no se mostraba el número de filas de entrenamiento y de test. | #126 | `fix/126-filas-train-test` | #13 | Corregido |
| 2 | CP-19, CP-22 | El mensaje del porcentaje de test decía "numero" sin tilde. | #127 | `fix/127-tildes-mensajes-separacion` | #11 | Corregido |
| 3 | CP-25, CP-26 | Con una semilla negativa, o con un porcentaje que deja vacío el conjunto de entrenamiento, se mostraba un error técnico de scikit-learn en inglés. | #128 | `fix/128-mensajes-error-separacion` | #12 | Corregido |
| 4 | CP-41 | Después de guardar el modelo una vez, el botón "Guardar modelo" no hacía nada. | #129 | `fix/129-guardar-modelo-dos-veces` | #14 | Corregido |
| 5 | CP-46, CP-51 | Con un modelo cargado tras reiniciar la aplicación, la predicción se mostraba como "Salida = …" en lugar de con el nombre de la columna de salida. | #130 | `fix/130-etiqueta-prediccion-modelo-cargado` | #15 | Corregido |

**Estado:** `Corregido` si los casos que lo detectaron pasan en la ejecución 2; `Limitación conocida` si el equipo decide no corregirlo antes de la release.

## 3. Limitaciones conocidas

No hay limitaciones conocidas: todos los errores encontrados se han corregido.

### Observaciones de usabilidad (no son fallos según el plan)

Durante la ejecución se anotaron estos detalles. No incumplen ningún resultado esperado, pero el equipo puede tenerlos en cuenta como mejoras:

- **CP-04 y CP-06:** tras el mensaje de error en español se añade el detalle técnico de la librería, en inglés.
- **CP-35 y CP-36:** la tabla de métricas es baja; la fila del MSE solo se ve desplazándose dentro de la tabla, y la columna de entrenamiento corta el valor.
- **CP-48 y CP-49:** si antes se había hecho una predicción, su resultado sigue visible debajo del botón tras un error de validación.

## 4. Conclusión

- [x] Todos los casos de prueba son correctos.
- [x] No hay fallos pendientes, así que no hay limitaciones conocidas que documentar en el `README.md`.
- [x] Se puede crear la release final.

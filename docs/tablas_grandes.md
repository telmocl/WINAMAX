# Visualización de tablas grandes

## Técnica elegida

**Scroll virtual**, con `QTableView` y un modelo propio (`ModeloTabla`, basado en `QAbstractTableModel`) que envuelve el `DataFrame` de pandas.

La tabla no crea un elemento por cada celda. Qt solo pide al modelo (`data()`) los valores de las filas visibles en cada momento y los actualiza al desplazarse. El `DataFrame` se mantiene en memoria y todas las filas siguen siendo accesibles con la barra de desplazamiento.

Esta técnica ya estaba presente en la versión anterior de la interfaz. En esta versión se mantiene y se refuerza con:

- Altura de fila fija (`QHeaderView.Fixed`, 26 px), para que Qt no calcule el tamaño de cada fila.
- Muestreo reducido al ajustar el ancho de columnas (`setResizeContentsPrecision(200)`), para no recorrer miles de filas.
- Carga del archivo en un hilo secundario (`QThread`), con barra de progreso y botones deshabilitados, para que la ventana no se congele con archivos grandes.

## Motivo de la elección

- Con el modelo/vista de Qt el scroll virtual no requiere código adicional de paginación ni de carga por bloques.
- Mantiene el funcionamiento original: el usuario ve una única tabla continua y puede recorrer todas las filas.
- Frente a `QTableWidget`, que crea un item por celda, el coste en memoria y en tiempo de arranque no crece con el número de filas.

## Comportamiento con el dataset de ejemplo (más de 20.000 filas)

Se probó el mismo dataset en la versión anterior y en la nueva.

| Aspecto | Antes del cambio | Después del cambio |
|---|---|---|
| Tiempo de carga | [4] s | [4] s (equivalente) |
| Desplazamiento por la tabla | Fluido | Fluido |
| Ventana durante la carga | [1] | [1] |
| Acceso a todas las filas (última fila) | [SI] | [SI] |

**Conclusión:** con este dataset no hay diferencia apreciable entre ambas versiones. Es el resultado esperado, porque la versión anterior ya usaba `QTableView` con un modelo propio, es decir, scroll virtual. Los cambios añadidos (filas fijas, muestreo reducido y carga en hilo) no alteran el resultado con 20.000 filas; su efecto se aprecia con archivos más grandes.


Capturas:

- [![alt text](<Captura de pantalla 2026-11-19 130512.png>)] `docs/img/antes_tabla.png`
- [![alt text](<Captura de pantalla 2026-11-19 130641.png>)] `docs/img/despues_tabla.png`

## Cómo reproducir la medición

1. Ejecutar la versión anterior (rama `dev`) y la actual con el mismo dataset.
2. Anotar el tiempo de carga con `time.perf_counter()` alrededor de `load_data`.
3. Desplazarse hasta la última fila de la tabla y volver al principio.
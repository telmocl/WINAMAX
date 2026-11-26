# Plan de pruebas funcionales de WINAMAX

## 1. Introducción

Este plan comprueba, desde el punto de vista del usuario y usando solo la interfaz gráfica, que WINAMAX cumple los criterios de aceptación de sus historias de usuario.

- **Versión probada:** rama `dev`, con todas las historias de la release final fusionadas.
- **Requisito previo:** todas las pruebas automatizadas pasan (`uv run pytest`).
- **Cómo se ejecuta:** manualmente, siguiendo solo los pasos escritos. Cada caso lo ejecuta un miembro del equipo que no haya implementado la funcionalidad probada. Si quien ejecuta un caso no puede seguir algún paso sin preguntar, el caso se reescribe antes de continuar.
- **Cómo se arranca la aplicación:** abrir una terminal (PowerShell) en la carpeta raíz del proyecto (la que contiene `pyproject.toml`) y ejecutar `uv run python -m winamax.gui`. Se abre la ventana "WINAMAX - Pipeline de Machine Learning".
- **Cómo se reinicia la aplicación:** cerrar la ventana con la X de la esquina superior derecha y volver a arrancarla como se indica en el punto anterior.

La ventana tiene seis secciones numeradas: **1. Cargar datos (o cargar un modelo guardado)**, **2. Seleccionar columnas**, **3. Separar datos (Train / Test)**, **4. Preprocesar valores inexistentes**, **5. Crear modelo** y **6. Realizar predicción**. Debajo de la sección 1 está la tabla **Datos**. En la parte inferior de la ventana hay una barra de estado con el texto `Dataset: … | Modelo: … | …`.

Los cuadros de mensaje de la aplicación se cierran con el botón **OK**. Los que hacen una pregunta tienen los botones **Yes** y **Cancel** (o **Yes** y **No**).

### 1.1 Historias de usuario probadas

| Funcionalidad | Historias de Taiga | Casos |
|---|---|---|
| Carga de datos (CSV, Excel y SQLite) y visualización en la tabla | #10, #14 | CP-01 a CP-07 |
| Selección de columnas de entrada y salida | #11 | CP-08 a CP-14 |
| Separación en conjuntos de entrenamiento y test | #41 | CP-15 a CP-26 |
| Preprocesado de valores inexistentes | #26 | CP-18, CP-27 a CP-33 |
| Creación del modelo: gráfico, fórmula y métricas | #16 | CP-34 a CP-37 |
| Descripción del modelo | #33 | CP-39 a CP-41, CP-44 |
| Guardado del modelo | #21 | CP-39 a CP-41, CP-44 |
| Recuperación del modelo desde disco | #24 | CP-42 a CP-44, CP-46 |
| Predicciones con un modelo creado y con un modelo cargado | #22 | CP-45 a CP-50 |
| Mejoras de la interfaz: barra de estado y avisos de descarte | #37 | CP-37, CP-38 |

## 2. Datos de prueba

Los archivos de datos **no se guardan en el repositorio**. Quien ejecute las pruebas los coloca en la carpeta local `data/` del proyecto.

### 2.1 Datasets válidos (los mismos datos en tres formatos)

| Archivo | Formato | Filas | Columnas | Valores inexistentes | Columna no numérica |
|---|---|---|---|---|---|
| `housing.csv` | CSV | 20640 | 10 | `total_bedrooms`: 207 | `ocean_proximity` |
| `housing.xlsx` | Excel (una hoja, `housing`) | 20640 | 10 | `total_bedrooms`: 207 | `ocean_proximity` |
| `housing.sqlite` | SQLite (una tabla, `housing`) | 20640 | 10 | `total_bedrooms`: 207 | `ocean_proximity` |

- **Columnas, en este orden:** `longitude`, `latitude`, `housing_median_age`, `total_rooms`, `total_bedrooms`, `population`, `households`, `median_income`, `median_house_value`, `ocean_proximity`.
- **Columnas numéricas:** todas salvo `ocean_proximity`.
- **Columna con valores inexistentes:** solo `total_bedrooms` (207 celdas vacías). La primera fila con un valor inexistente es la **291**.
- **Columna de texto:** `ocean_proximity`, con los valores `<1H OCEAN`, `INLAND`, `ISLAND`, `NEAR BAY` y `NEAR OCEAN`.
- **Primera fila de datos:** `-122.23, 37.88, 41.0, 880.0, 129.0, 322.0, 126.0, 8.3252, 452600.0, NEAR BAY`. En el Excel, las columnas sin decimales se leen como enteros: `-122.23, 37.88, 41, 880, 129.0, 322, 126, 8.3252, 452600, NEAR BAY`.
- `housing.xlsx` y `housing.sqlite` se generan a partir de `housing.csv`, con los mismos datos.

Para comprobar que se dispone de los archivos correctos, ejecutar CP-01, CP-02 y CP-03: la tabla debe mostrar 20640 filas y 10 columnas.

### 2.2 Archivos para los casos de error (se crean durante la prueba)

Estos archivos **no se guardan en el repositorio**. Se crean con PowerShell, desde la carpeta raíz del proyecto, con el comando indicado.

| Archivo | Comando para crearlo | Contenido | Lo usa |
|---|---|---|---|
| `data\vacio.csv` | `New-Item data\vacio.csv -ItemType File` | Ninguno (0 bytes) | CP-04 |
| `data\solo_cabecera.csv` | `Set-Content data\solo_cabecera.csv "a,b"` | Una línea de cabecera sin datos | CP-05 |
| `data\falso.xlsx` | `Set-Content data\falso.xlsx "esto no es un excel"` | Texto plano con extensión de Excel | CP-06 |
| `data\pequeno.csv` | `Set-Content data\pequeno.csv "a,b","1,2","2,4","3,6","4,8"` | Cabecera y 4 filas | CP-15 |
| `data\cinco.csv` | `Set-Content data\cinco.csv "a,b","1,2","2,4","3,6","4,8","5,10"` | Cabecera y 5 filas | CP-26 |
| `data\modelo_invalido.joblib` | `Set-Content data\modelo_invalido.joblib "no soy un modelo"` | Texto plano con la extensión de los modelos | CP-42 |

### 2.3 Preparaciones comunes

Varios casos parten del mismo estado. Cuando un caso indique como precondición una de estas preparaciones, hay que realizar antes sus pasos, en este orden:

**P-1. Dataset cargado**
1. Reiniciar la aplicación (ver 1).
2. En la sección 1, pulsar el botón **Cargar dataset**.
3. En el explorador de archivos, ir a la carpeta `data` del proyecto, seleccionar `housing.csv` y pulsar **Abrir**.
4. Esperar a que la tabla **Datos** muestre los datos.

**P-2. Columnas con valores inexistentes seleccionadas** (P-1 y además):
1. En la lista **Entradas:**, hacer clic en `median_income` y después en `total_bedrooms` (cada clic marca o desmarca una columna; no hace falta pulsar Ctrl).
2. En el desplegable **Salida:**, elegir `median_house_value`.
3. Pulsar **Aceptar** y cerrar el mensaje con **OK**.

**P-3. Columnas sin valores inexistentes seleccionadas** (P-1 y además):
1. En **Entradas:**, hacer clic en `median_income` y después en `housing_median_age`.
2. En **Salida:**, elegir `median_house_value`.
3. Pulsar **Aceptar** y cerrar el mensaje con **OK**.

**P-4. Datos separados con semilla 0** (P-2 y además):
1. En el campo **% Test (1-99):**, borrar el contenido y escribir `20`.
2. En el campo **Semilla (Seed):**, borrar el contenido y escribir `0`.
3. Pulsar **Separar datos** y cerrar el mensaje con **OK**.

**P-5. Modelo de referencia creado** (P-4 y además):
1. En la sección 4, marcar **Rellenar con la media de cada columna (Train)**.
2. Pulsar **Aplicar preprocesado** y cerrar el mensaje con **OK**.
3. En la sección 5, pulsar **Crear Modelo de Regresión Lineal** y cerrar el mensaje con **OK**.

El modelo de P-5 es el **modelo de referencia**: `median_house_value = 42050.2828 * median_income + 13.5916 * total_bedrooms + 36943.0919`.

## 3. Casos de prueba

### 3.1 Carga de datos

#### CP-01. Cargar un CSV válido
- **Historia:** #10, #14
- **Objetivo:** comprobar que `housing.csv` se carga y se muestra completo en la tabla.
- **Precondiciones:** la aplicación está recién arrancada (ver 1) y no hay ningún dataset cargado.
- **Datos de prueba:** `housing.csv` (ver 2.1).
- **Pasos:**
  1. En la sección 1, pulsar el botón **Cargar dataset**.
  2. En el explorador de archivos, ir a la carpeta `data` del proyecto y seleccionar `housing.csv`.
  3. Pulsar **Abrir**.
  4. En la tabla **Datos**, desplazarse con la barra vertical hasta la fila 291 y después hasta la última fila.
- **Resultado esperado:** la tabla **Datos** muestra 10 columnas, de `longitude` a `ocean_proximity`. La fila 1 contiene `-122.23, 37.88, 41.0, 880.0, 129.0, 322.0, 126.0, 8.3252, 452600.0, NEAR BAY`. En la fila 291, la columna `total_bedrooms` muestra `NaN`. La última fila es la **20640**. Junto a los botones de la sección 1 aparece la ruta completa del archivo. La barra de estado muestra `Dataset: housing.csv (20.640 filas)  |  Modelo: ninguno  |  Sin cambios pendientes`. La lista **Entradas:** contiene las 10 columnas y el desplegable **Salida:** muestra `-- Seleccionar Salida --` seguido de las 10 columnas.

#### CP-02. Cargar un Excel válido
- **Historia:** #10, #14
- **Objetivo:** comprobar que `housing.xlsx` se carga y se muestra completo en la tabla.
- **Precondiciones:** la aplicación está recién arrancada y no hay ningún dataset cargado.
- **Datos de prueba:** `housing.xlsx` (ver 2.1).
- **Pasos:**
  1. Pulsar el botón **Cargar dataset**.
  2. Ir a la carpeta `data` del proyecto y seleccionar `housing.xlsx`.
  3. Pulsar **Abrir**.
  4. Desplazarse hasta la última fila de la tabla.
- **Resultado esperado:** la tabla muestra 10 columnas y su última fila es la **20640**. La fila 1 contiene `-122.23, 37.88, 41, 880, 129.0, 322, 126, 8.3252, 452600, NEAR BAY`. La barra de estado muestra `Dataset: housing.xlsx (20.640 filas)`.

#### CP-03. Cargar un SQLite válido
- **Historia:** #10, #14
- **Objetivo:** comprobar que `housing.sqlite` se carga y se muestra completo en la tabla.
- **Precondiciones:** la aplicación está recién arrancada y no hay ningún dataset cargado.
- **Datos de prueba:** `housing.sqlite` (ver 2.1).
- **Pasos:**
  1. Pulsar el botón **Cargar dataset**.
  2. Ir a la carpeta `data` del proyecto y seleccionar `housing.sqlite`.
  3. Pulsar **Abrir**.
  4. Desplazarse hasta la última fila de la tabla.
- **Resultado esperado:** la tabla muestra 10 columnas y su última fila es la **20640**. La fila 1 contiene `-122.23, 37.88, 41.0, 880.0, 129.0, 322.0, 126.0, 8.3252, 452600.0, NEAR BAY`. La barra de estado muestra `Dataset: housing.sqlite (20.640 filas)`.

#### CP-04. Cargar un CSV vacío
- **Historia:** #10, #14
- **Objetivo:** comprobar que un archivo vacío se rechaza con un mensaje claro.
- **Precondiciones:** la aplicación está recién arrancada. Se ha creado `data\vacio.csv` (ver 2.2).
- **Datos de prueba:** `vacio.csv`.
- **Pasos:**
  1. Pulsar el botón **Cargar dataset**.
  2. Ir a la carpeta `data`, seleccionar `vacio.csv` y pulsar **Abrir**.
- **Resultado esperado:** aparece un mensaje de error titulado **No se pudo cargar el archivo** cuyo texto empieza por `El archivo está dañado, vacío o su contenido no corresponde a su extensión`. Al cerrarlo, la tabla **Datos** sigue vacía y la barra de estado muestra `Dataset: ninguno`.

#### CP-05. Cargar un CSV con solo la cabecera
- **Historia:** #10, #14
- **Objetivo:** comprobar que un archivo sin filas de datos se rechaza.
- **Precondiciones:** la aplicación está recién arrancada. Se ha creado `data\solo_cabecera.csv` (ver 2.2).
- **Datos de prueba:** `solo_cabecera.csv`.
- **Pasos:**
  1. Pulsar el botón **Cargar dataset**.
  2. Ir a la carpeta `data`, seleccionar `solo_cabecera.csv` y pulsar **Abrir**.
- **Resultado esperado:** mensaje de error **No se pudo cargar el archivo** cuyo texto empieza por `El archivo no contiene datos.` La tabla sigue vacía y la barra de estado muestra `Dataset: ninguno`.

#### CP-06. Cargar un archivo cuyo contenido no corresponde a su extensión
- **Historia:** #10, #14
- **Objetivo:** comprobar que un archivo con extensión de Excel que no es un Excel se rechaza.
- **Precondiciones:** la aplicación está recién arrancada. Se ha creado `data\falso.xlsx` (ver 2.2).
- **Datos de prueba:** `falso.xlsx`.
- **Pasos:**
  1. Pulsar el botón **Cargar dataset**.
  2. Ir a la carpeta `data`, seleccionar `falso.xlsx` y pulsar **Abrir**.
- **Resultado esperado:** mensaje de error **No se pudo cargar el archivo** cuyo texto empieza por `El archivo está dañado, vacío o su contenido no corresponde a su extensión`. La tabla sigue vacía.

#### CP-07. Cancelar la carga de un dataset
- **Historia:** #10, #14
- **Objetivo:** comprobar que cancelar el explorador de archivos no cambia los datos cargados.
- **Precondiciones:** P-1 (dataset cargado).
- **Datos de prueba:** ninguno.
- **Pasos:**
  1. Pulsar el botón **Cargar dataset**.
  2. En el explorador de archivos, pulsar **Cancelar**.
- **Resultado esperado:** no aparece ningún mensaje. La tabla sigue mostrando `housing.csv` (última fila 20640) y la barra de estado sigue mostrando `Dataset: housing.csv (20.640 filas)`.

### 3.2 Selección de columnas

#### CP-08. Selección válida de entradas y salida
- **Historia:** #11
- **Objetivo:** comprobar que una selección válida se confirma y habilita el paso 3.
- **Precondiciones:** P-1 (dataset cargado).
- **Datos de prueba:** entradas `median_income` y `housing_median_age`; salida `median_house_value`.
- **Pasos:**
  1. En la lista **Entradas:**, hacer clic en `median_income` y después en `housing_median_age`.
  2. En el desplegable **Salida:**, elegir `median_house_value`.
  3. Pulsar **Aceptar**.
- **Resultado esperado:** aparece el mensaje **Selección confirmada** con el texto `Variables confirmadas correctamente.`, `Entradas: median_income, housing_median_age` y `Salida: median_house_value`. Al cerrarlo con **OK**, la sección 3 **Separar datos (Train / Test)** queda habilitada, con `20.0` en **% Test (1-99):** y `42` en **Semilla (Seed):**. Las secciones 4 y 5 siguen deshabilitadas (en gris).

#### CP-09. Confirmar sin elegir la salida
- **Historia:** #11
- **Objetivo:** comprobar que se exige una columna de salida.
- **Precondiciones:** P-1.
- **Datos de prueba:** entrada `median_income`; sin salida.
- **Pasos:**
  1. En **Entradas:**, hacer clic en `median_income`.
  2. Dejar el desplegable **Salida:** en `-- Seleccionar Salida --`.
  3. Pulsar **Aceptar**.
- **Resultado esperado:** mensaje de error **Error de selección** con el texto `Falta seleccionar: una columna de salida (target).` Al cerrarlo, la sección 3 sigue deshabilitada.

#### CP-10. Confirmar sin elegir entradas
- **Historia:** #11
- **Objetivo:** comprobar que se exige al menos una entrada.
- **Precondiciones:** P-1.
- **Datos de prueba:** sin entradas; salida `median_house_value`.
- **Pasos:**
  1. No marcar ninguna columna en **Entradas:**.
  2. En **Salida:**, elegir `median_house_value`.
  3. Pulsar **Aceptar**.
- **Resultado esperado:** mensaje **Error de selección** con el texto `Falta seleccionar: al menos una columna de entrada (features).` La sección 3 sigue deshabilitada.

#### CP-11. Confirmar sin elegir nada
- **Historia:** #11
- **Objetivo:** comprobar el mensaje cuando faltan entradas y salida a la vez.
- **Precondiciones:** P-1.
- **Datos de prueba:** ninguno.
- **Pasos:**
  1. Sin marcar ninguna entrada y con **Salida:** en `-- Seleccionar Salida --`, pulsar **Aceptar**.
- **Resultado esperado:** mensaje **Error de selección** con el texto `Falta seleccionar: al menos una columna de entrada (features) y una columna de salida (target).`

#### CP-12. Misma columna como entrada y como salida
- **Historia:** #11
- **Objetivo:** comprobar que la salida no puede ser también una entrada.
- **Precondiciones:** P-1.
- **Datos de prueba:** `median_house_value` como entrada y como salida.
- **Pasos:**
  1. En **Entradas:**, hacer clic en `median_house_value`.
  2. En **Salida:**, elegir `median_house_value`.
  3. Pulsar **Aceptar**.
- **Resultado esperado:** mensaje **Error de selección** con el texto `La columna de salida 'median_house_value' no puede seleccionarse también como entrada.` La sección 3 sigue deshabilitada.

#### CP-13. Columna no numérica como entrada
- **Historia:** #11
- **Objetivo:** comprobar que se rechazan las columnas de texto.
- **Precondiciones:** P-1.
- **Datos de prueba:** entrada `ocean_proximity`; salida `median_house_value`.
- **Pasos:**
  1. En **Entradas:**, hacer clic en `ocean_proximity`.
  2. En **Salida:**, elegir `median_house_value`.
  3. Pulsar **Aceptar**.
- **Resultado esperado:** mensaje **Error de selección** con el texto `Las siguientes columnas no son numéricas y no se pueden usar en regresión: ocean_proximity.` La sección 3 sigue deshabilitada.

#### CP-14. Selección de columnas sin dataset
- **Historia:** #11
- **Objetivo:** comprobar que no se pueden seleccionar columnas si no hay datos.
- **Precondiciones:** la aplicación está recién arrancada, sin dataset.
- **Datos de prueba:** ninguno.
- **Pasos:**
  1. Observar las secciones 2 a 6.
  2. Intentar pulsar el botón **Aceptar** de la sección 2.
- **Resultado esperado:** las secciones 2, 3, 4, 5 y 6 aparecen deshabilitadas (en gris). La lista **Entradas:** y el desplegable **Salida:** están vacíos. Al intentar pulsar **Aceptar** no ocurre nada. Junto a los botones de la sección 1 aparece el texto `Para empezar, cargue un dataset para crear un modelo o cargue un modelo guardado.`

### 3.3 Separación en entrenamiento y test

#### CP-15. Dataset con menos de 5 filas
- **Historia:** #41
- **Objetivo:** comprobar que un dataset demasiado pequeño no se puede separar.
- **Precondiciones:** la aplicación está recién arrancada. Se ha creado `data\pequeno.csv` (ver 2.2).
- **Datos de prueba:** `pequeno.csv` (4 filas); entrada `a`; salida `b`; porcentaje de test 20.
- **Pasos:**
  1. Pulsar **Cargar dataset**, ir a la carpeta `data`, seleccionar `pequeno.csv` y pulsar **Abrir**.
  2. En **Entradas:**, hacer clic en `a`.
  3. En **Salida:**, elegir `b`.
  4. Pulsar **Aceptar** y cerrar el mensaje con **OK**.
  5. En **% Test (1-99):**, borrar el contenido y escribir `20`.
  6. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje de error **Error en la separación** con el texto `El dataset debe tener al menos 5 filas para poder separarlo.` La sección 4 sigue deshabilitada.

#### CP-16. Separación válida con 20 % de test y semilla 42
- **Historia:** #41
- **Objetivo:** comprobar una separación normal y la detección de valores inexistentes en cada conjunto.
- **Precondiciones:** P-2 (columnas con valores inexistentes seleccionadas).
- **Datos de prueba:** porcentaje de test 20; semilla 42.
- **Pasos:**
  1. En **% Test (1-99):**, borrar el contenido y escribir `20`.
  2. En **Semilla (Seed):**, borrar el contenido y escribir `42`.
  3. Pulsar **Separar datos**.
- **Resultado esperado:** aparece el mensaje **Separación y detección exitosa**. Indica que el conjunto de entrenamiento tiene **16512** filas y el de test **4128**. En `Valores inexistentes detectados:` aparecen las líneas `- median_income -> Train: 0 | Test: 0`, `- total_bedrooms -> Train: 0 | Test: 207` y `- median_house_value -> Train: 0 | Test: 0`. Al cerrarlo, la sección 4 queda habilitada y muestra ese mismo texto. La sección 5 sigue deshabilitada.

#### CP-17. La misma semilla da la misma separación
- **Historia:** #41
- **Objetivo:** comprobar que repetir la separación con la misma semilla da el mismo resultado, y otra semilla da otro.
- **Precondiciones:** P-2.
- **Datos de prueba:** porcentaje 20; semillas 0 y 42.
- **Pasos:**
  1. En **% Test (1-99):** escribir `20` y en **Semilla (Seed):** escribir `0`. Pulsar **Separar datos**, anotar la línea de `total_bedrooms` y cerrar el mensaje.
  2. Sin cambiar nada, pulsar otra vez **Separar datos**, anotar la línea de `total_bedrooms` y cerrar el mensaje.
  3. En **Semilla (Seed):** escribir `42`. Pulsar **Separar datos**, anotar la línea de `total_bedrooms` y cerrar el mensaje.
- **Resultado esperado:** en los pasos 1 y 2 la línea es la misma: `- total_bedrooms -> Train: 158 | Test: 49`. En el paso 3 es `- total_bedrooms -> Train: 0 | Test: 207`.

#### CP-18. Separación sin valores inexistentes
- **Historia:** #41, #26
- **Objetivo:** comprobar que, si no hay valores inexistentes, se puede crear el modelo sin preprocesar.
- **Precondiciones:** P-3 (columnas sin valores inexistentes seleccionadas).
- **Datos de prueba:** porcentaje 20; semilla 42.
- **Pasos:**
  1. En **% Test (1-99):** escribir `20` y en **Semilla (Seed):** escribir `42`.
  2. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje **Separación y detección exitosa** con las líneas `- median_income -> Train: 0 | Test: 0`, `- housing_median_age -> Train: 0 | Test: 0` y `- median_house_value -> Train: 0 | Test: 0`, y el texto `No hay valores inexistentes. Puede continuar sin preprocesar o aplicar una estrategia.` Al cerrarlo, las secciones 4 y 5 quedan habilitadas y el botón **Crear Modelo de Regresión Lineal** se puede pulsar.

#### CP-19. Porcentaje de test 0 (límite no válido)
- **Historia:** #41
- **Objetivo:** comprobar que el valor límite 0 se rechaza.
- **Precondiciones:** P-3.
- **Datos de prueba:** porcentaje de test 0.
- **Pasos:**
  1. En **% Test (1-99):**, borrar el contenido y escribir `0`.
  2. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje de error **Error en la separación** con el texto `El porcentaje de test debe ser un número entre 1 y 99.` Al cerrarlo, las secciones 4 y 5 siguen deshabilitadas.

#### CP-20. Porcentaje de test 1 (límite inferior válido)
- **Historia:** #41
- **Objetivo:** comprobar que el valor límite 1 se acepta.
- **Precondiciones:** P-3.
- **Datos de prueba:** porcentaje de test 1; semilla 42.
- **Pasos:**
  1. En **% Test (1-99):** escribir `1` y en **Semilla (Seed):** escribir `42`.
  2. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje **Separación y detección exitosa**, que indica **20433** filas de entrenamiento y **207** de test.

#### CP-21. Porcentaje de test 99 (límite superior válido)
- **Historia:** #41
- **Objetivo:** comprobar que el valor límite 99 se acepta.
- **Precondiciones:** P-3.
- **Datos de prueba:** porcentaje de test 99; semilla 42.
- **Pasos:**
  1. En **% Test (1-99):** escribir `99` y en **Semilla (Seed):** escribir `42`.
  2. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje **Separación y detección exitosa**, que indica **206** filas de entrenamiento y **20434** de test.

#### CP-22. Porcentaje de test 100 (límite no válido)
- **Historia:** #41
- **Objetivo:** comprobar que el valor límite 100 se rechaza.
- **Precondiciones:** P-3.
- **Datos de prueba:** porcentaje de test 100.
- **Pasos:**
  1. En **% Test (1-99):**, borrar el contenido y escribir `100`.
  2. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje de error **Error en la separación** con el texto `El porcentaje de test debe ser un número entre 1 y 99.` Las secciones 4 y 5 siguen deshabilitadas.

#### CP-23. Porcentaje de test no numérico
- **Historia:** #41
- **Objetivo:** comprobar que un texto en el porcentaje se rechaza.
- **Precondiciones:** P-3.
- **Datos de prueba:** porcentaje de test `abc`.
- **Pasos:**
  1. En **% Test (1-99):**, borrar el contenido y escribir `abc`.
  2. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje de error **Porcentaje de test no válido** con el texto `El porcentaje de test debe ser un número (por ejemplo 20). Corríjalo e inténtelo de nuevo.`

#### CP-24. Semilla no numérica
- **Historia:** #41
- **Objetivo:** comprobar que una semilla que no es un número entero se rechaza.
- **Precondiciones:** P-3.
- **Datos de prueba:** porcentaje 20; semilla `abc`.
- **Pasos:**
  1. En **% Test (1-99):** escribir `20`.
  2. En **Semilla (Seed):**, borrar el contenido y escribir `abc`.
  3. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje de error **Semilla no válida** con el texto `La semilla debe ser un número entero (por ejemplo 42). Corríjala e inténtelo de nuevo.`

#### CP-25. Semilla negativa
- **Historia:** #41
- **Objetivo:** comprobar que una semilla negativa se rechaza con un mensaje comprensible.
- **Precondiciones:** P-3.
- **Datos de prueba:** porcentaje 20; semilla `-1`.
- **Pasos:**
  1. En **% Test (1-99):** escribir `20`.
  2. En **Semilla (Seed):**, borrar el contenido y escribir `-1`.
  3. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje de error que explica en español que la semilla no es válida, sin detalles técnicos en inglés (según el README, los detalles técnicos van a la consola y no a la interfaz). Las secciones 4 y 5 siguen deshabilitadas.

#### CP-26. Porcentaje que deja vacío el conjunto de entrenamiento
- **Historia:** #41
- **Objetivo:** comprobar el aviso cuando el porcentaje deja sin filas uno de los conjuntos.
- **Precondiciones:** la aplicación está recién arrancada. Se ha creado `data\cinco.csv` (ver 2.2).
- **Datos de prueba:** `cinco.csv` (5 filas); entrada `a`; salida `b`; porcentaje 99.
- **Pasos:**
  1. Pulsar **Cargar dataset**, ir a la carpeta `data`, seleccionar `cinco.csv` y pulsar **Abrir**.
  2. En **Entradas:**, hacer clic en `a`. En **Salida:**, elegir `b`. Pulsar **Aceptar** y cerrar el mensaje.
  3. En **% Test (1-99):**, borrar el contenido y escribir `99`.
  4. Pulsar **Separar datos**.
- **Resultado esperado:** mensaje de error **Error en la separación** con el texto `El porcentaje elegido deja alguno de los conjuntos vacío. Ajusta el porcentaje`, sin detalles técnicos en inglés. La sección 4 sigue deshabilitada.

### 3.4 Preprocesado de valores inexistentes

Estos casos usan la semilla 0, con la que hay valores inexistentes tanto en entrenamiento (158) como en test (49). Cada caso crea después el modelo para comprobar que la estrategia se ha aplicado de verdad: cada estrategia da una fórmula distinta.

#### CP-27. Preprocesar sin haber separado los datos
- **Historia:** #26
- **Objetivo:** comprobar que no se puede preprocesar sin hacer antes el paso 3.
- **Precondiciones:** P-2 (columnas seleccionadas, sin pulsar **Separar datos**).
- **Datos de prueba:** ninguno.
- **Pasos:**
  1. Observar la sección 4 **Preprocesar valores inexistentes**.
  2. Intentar pulsar **Aplicar preprocesado**.
- **Resultado esperado:** la sección 4 está deshabilitada (en gris) y muestra el texto `Realice la separación de datos para detectar valores inexistentes.` Al intentar pulsar **Aplicar preprocesado** no ocurre nada.

#### CP-28. Eliminar las filas con valores inexistentes
- **Historia:** #26
- **Objetivo:** comprobar la estrategia de eliminación de filas.
- **Precondiciones:** P-4 (datos separados con semilla 0).
- **Datos de prueba:** estrategia de eliminación de filas.
- **Pasos:**
  1. En la sección 4, marcar **Eliminar las filas que contengan valores inexistentes**.
  2. Pulsar **Aplicar preprocesado** y anotar el mensaje. Cerrarlo con **OK**.
  3. En la sección 5, pulsar **Crear Modelo de Regresión Lineal** y cerrar el mensaje.
- **Resultado esperado:** tras el paso 2, el mensaje **Preprocesamiento exitoso** contiene `Filas eliminadas en Train: 158` y `Filas eliminadas en Test: 49`. Tras el paso 3, la fórmula es `median_house_value = 42105.2080 * median_income + 13.5931 * total_bedrooms + 36717.6490`.

#### CP-29. Rellenar con la media
- **Historia:** #26
- **Objetivo:** comprobar la estrategia de la media.
- **Precondiciones:** P-4.
- **Datos de prueba:** estrategia de la media.
- **Pasos:**
  1. En la sección 4, marcar **Rellenar con la media de cada columna (Train)**.
  2. Pulsar **Aplicar preprocesado** y cerrar el mensaje.
  3. Pulsar **Crear Modelo de Regresión Lineal** y cerrar el mensaje.
- **Resultado esperado:** tras el paso 2, el mensaje **Preprocesamiento exitoso** dice `Preprocesamiento aplicado con éxito:` y `Valores rellenados usando la MEDIA calculada en el conjunto de entrenamiento.` Tras el paso 3, la fórmula es `median_house_value = 42050.2828 * median_income + 13.5916 * total_bedrooms + 36943.0919`.

#### CP-30. Rellenar con la mediana
- **Historia:** #26
- **Objetivo:** comprobar la estrategia de la mediana.
- **Precondiciones:** P-4.
- **Datos de prueba:** estrategia de la mediana.
- **Pasos:**
  1. En la sección 4, marcar **Rellenar con la mediana de cada columna (Train)**.
  2. Pulsar **Aplicar preprocesado** y cerrar el mensaje.
  3. Pulsar **Crear Modelo de Regresión Lineal** y cerrar el mensaje.
- **Resultado esperado:** tras el paso 2, el mensaje **Preprocesamiento exitoso** dice `Valores rellenados usando la MEDIANA calculada en el conjunto de entrenamiento.` Tras el paso 3, la fórmula es `median_house_value = 42050.2376 * median_income + 13.5769 * total_bedrooms + 36964.6011`.

#### CP-31. Rellenar con un valor constante válido
- **Historia:** #26
- **Objetivo:** comprobar la estrategia del valor constante.
- **Precondiciones:** P-4.
- **Datos de prueba:** constante 0.
- **Pasos:**
  1. En la sección 4, marcar **Rellenar con un valor constante:**. El campo de su derecha se habilita.
  2. En ese campo, escribir `0`.
  3. Pulsar **Aplicar preprocesado** y cerrar el mensaje.
  4. Pulsar **Crear Modelo de Regresión Lineal** y cerrar el mensaje.
- **Resultado esperado:** tras el paso 3, el mensaje **Preprocesamiento exitoso** dice `Valores rellenados con el valor constante: 0.0`. Tras el paso 4, la fórmula es `median_house_value = 42049.8286 * median_income + 13.3492 * total_bedrooms + 37143.8349`.

#### CP-32. Valor constante no numérico
- **Historia:** #26
- **Objetivo:** comprobar que una constante que no es un número se rechaza.
- **Precondiciones:** P-4.
- **Datos de prueba:** constante `abc`.
- **Pasos:**
  1. En la sección 4, marcar **Rellenar con un valor constante:**.
  2. En el campo de la constante, escribir `abc`.
  3. Pulsar **Aplicar preprocesado**.
- **Resultado esperado:** mensaje de error **Valor constante no válido** con el texto `El valor constante debe ser un número (por ejemplo 0 o 3.5). Corríjalo e inténtelo de nuevo.` Al cerrarlo, la sección 5 sigue deshabilitada.

#### CP-33. Valor constante vacío
- **Historia:** #26
- **Objetivo:** comprobar que dejar la constante en blanco se rechaza.
- **Precondiciones:** P-4.
- **Datos de prueba:** constante vacía.
- **Pasos:**
  1. En la sección 4, marcar **Rellenar con un valor constante:**.
  2. Dejar el campo de la constante en blanco.
  3. Pulsar **Aplicar preprocesado**.
- **Resultado esperado:** mensaje de error **Valor constante no válido** con el texto `El valor constante debe ser un número (por ejemplo 0 o 3.5). Corríjalo e inténtelo de nuevo.` La sección 5 sigue deshabilitada.

### 3.5 Creación del modelo

#### CP-34. Crear el modelo sin completar los pasos previos
- **Historia:** #16
- **Objetivo:** comprobar que no se puede crear un modelo sin separar y preprocesar los datos.
- **Precondiciones:** P-4 (datos separados con valores inexistentes, sin preprocesar).
- **Datos de prueba:** ninguno.
- **Pasos:**
  1. Observar la sección 5 **Crear modelo**.
  2. Intentar pulsar **Crear Modelo de Regresión Lineal**.
- **Resultado esperado:** la sección 5 está deshabilitada (en gris) y al intentar pulsar el botón no ocurre nada. La línea de fórmula muestra `Fórmula: -`.

#### CP-35. Crear un modelo con dos entradas
- **Historia:** #16
- **Objetivo:** comprobar que se crea el modelo y se muestran el gráfico, la fórmula y las métricas en entrenamiento y test.
- **Precondiciones:** P-4.
- **Datos de prueba:** entradas `median_income` y `total_bedrooms`; salida `median_house_value`; semilla 0; media.
- **Pasos:**
  1. En la sección 4, marcar **Rellenar con la media de cada columna (Train)**, pulsar **Aplicar preprocesado** y cerrar el mensaje.
  2. En la sección 5, pulsar **Crear Modelo de Regresión Lineal**.
  3. Cerrar el mensaje y observar la sección 5 y la barra de estado.
- **Resultado esperado:**
  - Tras el paso 2 aparece el mensaje **Modelo creado** con el texto `Modelo de regresión lineal creado y evaluado correctamente.`
  - La fórmula es `median_house_value = 42050.2828 * median_income + 13.5916 * total_bedrooms + 36943.0919`.
  - La tabla **Métricas de Error:** muestra:

    | | Entrenamiento (Train) | Test |
    |---|---|---|
    | R² (Coeff) | 0.4824 | 0.4518 |
    | MSE (Error) | 6928049666.4864 | 7147880207.7521 |

  - El gráfico tiene en el eje horizontal `Valor Real` y en el vertical `Valor Predicho`. Muestra puntos azules (Train) y naranjas (Test) y una línea discontinua gris `Ideal (y=x)`, con la leyenda de las tres series.
  - El cuadro **Descripción (opcional):** y el botón **Guardar modelo** se habilitan.
  - La sección 6 se habilita, con los campos `median_income:` y `total_bedrooms:`.
  - La barra de estado muestra `Modelo: creado  |  Modelo con cambios sin guardar`.

#### CP-36. Crear un modelo con una sola entrada
- **Historia:** #16
- **Objetivo:** comprobar el gráfico y la fórmula de un modelo con una sola entrada.
- **Precondiciones:** P-1.
- **Datos de prueba:** entrada `median_income`; salida `median_house_value`; porcentaje 20; semilla 42.
- **Pasos:**
  1. En **Entradas:**, hacer clic solo en `median_income`. En **Salida:**, elegir `median_house_value`. Pulsar **Aceptar** y cerrar el mensaje.
  2. En **% Test (1-99):** escribir `20` y en **Semilla (Seed):** escribir `42`. Pulsar **Separar datos** y cerrar el mensaje.
  3. Pulsar **Crear Modelo de Regresión Lineal** y cerrar el mensaje.
- **Resultado esperado:** la fórmula es `median_house_value = 41933.8494 * median_income + 44459.7292`. Las métricas son R² 0.4770 (Train) y 0.4589 (Test), y MSE 6991447170.1828 (Train) y 7091157771.7655 (Test). El gráfico tiene en el eje horizontal `median_income` y en el vertical `median_house_value`. Muestra puntos azules (Train) y naranjas (Test) y una recta roja `Ajuste`.

#### CP-37. Repetir la separación descarta el modelo creado
- **Historia:** #16, #37
- **Objetivo:** comprobar que, al cambiar la separación, el modelo anterior deja de mostrarse y no se puede usar.
- **Precondiciones:** P-5 (modelo de referencia creado).
- **Datos de prueba:** semilla 42.
- **Pasos:**
  1. En **Semilla (Seed):**, borrar el contenido y escribir `42`.
  2. Pulsar **Separar datos** y cerrar el mensaje.
  3. Observar las secciones 5 y 6 y la barra de estado.
- **Resultado esperado:** la barra de estado muestra `Modelo: ninguno  |  Sin cambios pendientes`. La sección 5 está deshabilitada y el botón **Guardar modelo** no se puede pulsar. Ya no se muestran la fórmula, las métricas ni el gráfico del modelo anterior (la línea de fórmula vuelve a `Fórmula: -`). La sección 6 está deshabilitada.

#### CP-38. Cargar otro dataset con un modelo creado y cancelar
- **Historia:** #37
- **Objetivo:** comprobar que se avisa antes de descartar un modelo y que cancelar lo conserva.
- **Precondiciones:** P-5.
- **Datos de prueba:** ninguno.
- **Pasos:**
  1. En la sección 1, pulsar **Cargar dataset**.
  2. En el mensaje que aparece, pulsar **Cancel**.
- **Resultado esperado:** tras el paso 1 aparece el mensaje **Descartar modelo** con el texto `Tiene un modelo cargado o creado. Si carga un nuevo dataset se descartará. ¿Desea continuar?` y los botones **Yes** y **Cancel**. Tras el paso 2 no se abre el explorador de archivos, la fórmula del modelo de referencia sigue visible y la barra de estado sigue mostrando `Modelo: creado`.

### 3.6 Descripción y guardado del modelo

Antes de empezar este bloque, borrar del Escritorio el archivo `modelo_prueba.joblib` si existe.

#### CP-39. Guardar un modelo con descripción
- **Historia:** #33, #21
- **Objetivo:** comprobar que se escribe una descripción y que el modelo se guarda en disco con la extensión `.joblib`.
- **Precondiciones:** P-5. No existe `modelo_prueba.joblib` en el Escritorio.
- **Datos de prueba:** descripción `Modelo de prueba de precios`; nombre de archivo `modelo_prueba`.
- **Pasos:**
  1. En la sección 5, hacer clic en el cuadro **Descripción (opcional):** (texto gris `Escriba aquí una descripción o propósito de este modelo...`) y escribir `Modelo de prueba de precios`.
  2. Pulsar **Guardar modelo**.
  3. En la ventana **Guardar modelo**, ir al Escritorio, escribir `modelo_prueba` en el campo del nombre y pulsar **Guardar**.
  4. Cerrar el mensaje y observar la barra de estado.
- **Resultado esperado:** tras el paso 1, el texto aparece en el cuadro y la barra de estado muestra `Modelo con cambios sin guardar`. Tras el paso 3 aparece el mensaje **Modelo guardado** con el texto `Modelo guardado en:` seguido de una ruta que termina en `modelo_prueba.joblib`. Tras el paso 4, la barra de estado muestra `Sin cambios pendientes`. El archivo `modelo_prueba.joblib` está en el Escritorio.

#### CP-40. Guardar un modelo sin descripción y cancelar
- **Historia:** #33, #21
- **Objetivo:** comprobar el aviso cuando la descripción está vacía.
- **Precondiciones:** P-5, con el cuadro **Descripción (opcional):** vacío.
- **Datos de prueba:** ninguno.
- **Pasos:**
  1. Pulsar **Guardar modelo**.
  2. En el mensaje que aparece, pulsar **Cancel**.
- **Resultado esperado:** tras el paso 1 aparece el mensaje **Descripción vacía** con el texto `El modelo no tiene descripción. ¿Guardar igualmente?` y los botones **Yes** y **Cancel**. Tras el paso 2 no se abre la ventana **Guardar modelo** y no se guarda nada.

#### CP-41. Intentar sobrescribir un modelo existente y no hacerlo
- **Historia:** #21
- **Objetivo:** comprobar que un modelo se puede volver a guardar en la misma sesión y que se pide confirmación antes de sobrescribir un archivo.
- **Precondiciones:** se acaba de ejecutar CP-39 y la aplicación sigue abierta, con el mismo modelo.
- **Datos de prueba:** descripción `Otro modelo`; nombre `modelo_prueba`.
- **Pasos:**
  1. En el cuadro **Descripción (opcional):**, borrar el texto y escribir `Otro modelo`.
  2. Pulsar **Guardar modelo**.
  3. En la ventana **Guardar modelo**, ir al Escritorio, escribir `modelo_prueba` y pulsar **Guardar**.
  4. En la confirmación que aparece, pulsar **No**.
- **Resultado esperado:** tras el paso 2 se abre la ventana **Guardar modelo**. Tras el paso 3 aparece una confirmación que indica que `modelo_prueba.joblib` ya existe y pregunta si se desea reemplazar. Tras el paso 4 no aparece el mensaje **Modelo guardado**, la fecha de modificación de `modelo_prueba.joblib` no cambia y la barra de estado sigue mostrando `Modelo con cambios sin guardar`.

### 3.7 Recuperación del modelo desde disco

#### CP-42. Cargar un archivo de modelo no válido
- **Historia:** #24
- **Objetivo:** comprobar que un archivo que no es un modelo se rechaza.
- **Precondiciones:** la aplicación está recién arrancada. Se ha creado `data\modelo_invalido.joblib` (ver 2.2).
- **Datos de prueba:** `modelo_invalido.joblib`.
- **Pasos:**
  1. En la sección 1, pulsar **Cargar modelo**.
  2. En el explorador de archivos, ir a la carpeta `data`, seleccionar `modelo_invalido.joblib` y pulsar **Abrir**.
- **Resultado esperado:** mensaje de error **No se pudo cargar el modelo** con el texto `El archivo está dañado, no tiene el formato esperado o le falta parte de la información. Seleccione otro archivo de modelo.` La barra de estado sigue mostrando `Modelo: ninguno`.

#### CP-43. Cargar un modelo guardado
- **Historia:** #24
- **Objetivo:** comprobar que el modelo recuperado conserva la fórmula, las métricas y la descripción.
- **Precondiciones:** existe `modelo_prueba.joblib` en el Escritorio (CP-39). La aplicación está recién arrancada.
- **Datos de prueba:** `modelo_prueba.joblib`.
- **Pasos:**
  1. En la sección 1, pulsar **Cargar modelo**.
  2. En el explorador de archivos, ir al Escritorio, seleccionar `modelo_prueba.joblib` y pulsar **Abrir**.
  3. Cerrar el mensaje y observar la ventana.
- **Resultado esperado:** tras el paso 2 aparece el mensaje **Modelo cargado** con el texto `El modelo se ha cargado correctamente.` Tras el paso 3:
  - Junto a los botones de la sección 1 aparece `Modelo cargado: ` seguido de la ruta del archivo.
  - La tabla **Datos** no se muestra y las secciones 2, 3 y 4 están deshabilitadas.
  - La fórmula es `median_house_value = 42050.2828 * median_income + 13.5916 * total_bedrooms + 36943.0919`.
  - Las métricas son R² 0.4824 y 0.4518, y MSE 6928049666.4864 y 7147880207.7521 (Train y Test).
  - El cuadro de descripción contiene `Modelo de prueba de precios`.
  - La sección 6 tiene los campos `median_income:` y `total_bedrooms:`.
  - La barra de estado muestra `Dataset: ninguno  |  Modelo: cargado  |  Sin cambios pendientes`.

#### CP-44. Modificar la descripción de un modelo cargado
- **Historia:** #33, #24
- **Objetivo:** comprobar que se puede cambiar la descripción de un modelo cargado y guardar el cambio.
- **Precondiciones:** CP-43 ejecutado (modelo `modelo_prueba.joblib` cargado).
- **Datos de prueba:** nueva descripción `Descripción modificada`.
- **Pasos:**
  1. En el cuadro **Descripción (opcional):**, borrar el texto y escribir `Descripción modificada`.
  2. Pulsar **Guardar modelo**.
  3. En la ventana **Guardar modelo**, comprobar que el nombre propuesto es `modelo_prueba.joblib`, en el Escritorio, y pulsar **Guardar**.
  4. En la confirmación de reemplazo, pulsar **Sí** (o **Yes**). Cerrar el mensaje.
  5. Reiniciar la aplicación, pulsar **Cargar modelo**, seleccionar `modelo_prueba.joblib` en el Escritorio y pulsar **Abrir**. Cerrar el mensaje.
- **Resultado esperado:** tras el paso 1, la barra de estado muestra `Modelo con cambios sin guardar`. Tras el paso 4 aparece **Modelo guardado** y la barra pasa a `Sin cambios pendientes`. Tras el paso 5, el cuadro de descripción muestra `Descripción modificada`.

### 3.8 Predicciones

#### CP-45. Predicción con un modelo creado
- **Historia:** #22
- **Objetivo:** comprobar que se calcula la predicción con un modelo recién creado.
- **Precondiciones:** P-5 (modelo de referencia creado).
- **Datos de prueba:** `median_income` = 5; `total_bedrooms` = 500.
- **Pasos:**
  1. En la sección 6, en el campo `median_income:` (texto gris `Valor para median_income`), escribir `5`.
  2. En el campo `total_bedrooms:`, escribir `500`.
  3. Pulsar **Realizar predicción**.
- **Resultado esperado:** debajo del botón aparece `median_house_value = 253990.2937`.

#### CP-46. Predicción con un modelo cargado
- **Historia:** #22, #24
- **Objetivo:** comprobar que un modelo recuperado desde disco predice lo mismo que el modelo original.
- **Precondiciones:** la aplicación está recién arrancada. Existe `modelo_prueba.joblib` en el Escritorio (CP-39).
- **Datos de prueba:** `modelo_prueba.joblib`; `median_income` = 5; `total_bedrooms` = 500.
- **Pasos:**
  1. Pulsar **Cargar modelo**, seleccionar `modelo_prueba.joblib` en el Escritorio, pulsar **Abrir** y cerrar el mensaje.
  2. En el campo `median_income:`, escribir `5`.
  3. En el campo `total_bedrooms:`, escribir `500`.
  4. Pulsar **Realizar predicción**.
- **Resultado esperado:** debajo del botón aparece `median_house_value = 253990.2937`, igual que en CP-45.

#### CP-47. Predicción con coma decimal
- **Historia:** #22
- **Objetivo:** comprobar que se acepta la coma como separador decimal.
- **Precondiciones:** P-5.
- **Datos de prueba:** `median_income` = 3,5 y después 3.5; `total_bedrooms` = 500.
- **Pasos:**
  1. En `median_income:`, escribir `3,5`. En `total_bedrooms:`, escribir `500`. Pulsar **Realizar predicción** y anotar el resultado.
  2. En `median_income:`, borrar el contenido y escribir `3.5`. Pulsar **Realizar predicción** y anotar el resultado.
- **Resultado esperado:** en los dos pasos aparece `median_house_value = 190914.8695`.

#### CP-48. Predicción con texto en lugar de un número
- **Historia:** #22
- **Objetivo:** comprobar que un valor no numérico se rechaza.
- **Precondiciones:** P-5.
- **Datos de prueba:** `median_income` = abc; `total_bedrooms` = 500.
- **Pasos:**
  1. En `median_income:`, escribir `abc`.
  2. En `total_bedrooms:`, escribir `500`.
  3. Pulsar **Realizar predicción**.
- **Resultado esperado:** mensaje de aviso **Error de validación** con el texto `Valores no numéricos en: median_income` y `Corríjalos e inténtelo de nuevo.` Debajo del botón no aparece ningún resultado.

#### CP-49. Predicción con un campo vacío
- **Historia:** #22
- **Objetivo:** comprobar que dejar un campo en blanco se rechaza.
- **Precondiciones:** P-5.
- **Datos de prueba:** `median_income` vacío; `total_bedrooms` = 500.
- **Pasos:**
  1. Dejar vacío el campo `median_income:`.
  2. En `total_bedrooms:`, escribir `500`.
  3. Pulsar **Realizar predicción**.
- **Resultado esperado:** mensaje de aviso **Error de validación** con el texto `Faltan valores en: median_income` y `Corríjalos e inténtelo de nuevo.` Debajo del botón no aparece ningún resultado.

#### CP-50. Predicción sin ningún modelo
- **Historia:** #22
- **Objetivo:** comprobar que no se puede predecir si no hay modelo.
- **Precondiciones:** P-1 (dataset cargado, sin modelo).
- **Datos de prueba:** ninguno.
- **Pasos:**
  1. Observar la sección 6 **Realizar predicción**.
  2. Intentar pulsar **Realizar predicción**.
- **Resultado esperado:** la sección 6 está deshabilitada (en gris), no tiene campos de entrada y al intentar pulsar el botón no ocurre nada.

### 3.9 Flujo completo

#### CP-51. Flujo completo: cargar, crear, guardar, recargar y predecir
- **Historia:** #10, #14, #11, #41, #26, #16, #33, #21, #24, #22
- **Objetivo:** comprobar el recorrido completo de la aplicación con un dataset válido.
- **Precondiciones:** la aplicación está recién arrancada. Existe `data\housing.csv`. No existe `modelo_flujo.joblib` en el Escritorio.
- **Datos de prueba:** `housing.csv`; entradas `median_income` y `housing_median_age`; salida `median_house_value`; porcentaje 20; semilla 42; media; descripción `Flujo completo`; predicción con `median_income` = 5 y `housing_median_age` = 30.
- **Pasos:**
  1. Pulsar **Cargar dataset**, ir a la carpeta `data`, seleccionar `housing.csv` y pulsar **Abrir**.
  2. En **Entradas:**, hacer clic en `median_income` y después en `housing_median_age`.
  3. En **Salida:**, elegir `median_house_value`.
  4. Pulsar **Aceptar** y cerrar el mensaje.
  5. En **% Test (1-99):** escribir `20` y en **Semilla (Seed):** escribir `42`.
  6. Pulsar **Separar datos** y cerrar el mensaje.
  7. Marcar **Rellenar con la media de cada columna (Train)**, pulsar **Aplicar preprocesado** y cerrar el mensaje.
  8. Pulsar **Crear Modelo de Regresión Lineal** y cerrar el mensaje. Anotar la fórmula y las métricas.
  9. En **Descripción (opcional):**, escribir `Flujo completo`.
  10. Pulsar **Guardar modelo**, ir al Escritorio, escribir `modelo_flujo` y pulsar **Guardar**. Cerrar el mensaje.
  11. En `median_income:` escribir `5` y en `housing_median_age:` escribir `30`. Pulsar **Realizar predicción** y anotar el resultado A.
  12. Reiniciar la aplicación.
  13. Pulsar **Cargar modelo**, seleccionar `modelo_flujo.joblib` en el Escritorio, pulsar **Abrir** y cerrar el mensaje.
  14. En `median_income:` escribir `5` y en `housing_median_age:` escribir `30`. Pulsar **Realizar predicción** y anotar el resultado B.
- **Resultado esperado:**
  - Tras el paso 8, la fórmula es `median_house_value = 43342.2840 * median_income + 1748.5735 * housing_median_age - 11029.7493`, con R² 0.5128 (Train) y 0.4941 (Test) y MSE 6513066873.6164 (Train) y 6629874283.0482 (Test).
  - Tras el paso 10 aparece **Modelo guardado**, con una ruta que termina en `modelo_flujo.joblib`.
  - Tras el paso 11, el resultado A es `median_house_value = 258138.8768`.
  - Tras el paso 13, la fórmula, las métricas y la descripción `Flujo completo` coinciden con las del paso 8 y el paso 9.
  - Tras el paso 14, el resultado B es `median_house_value = 258138.8768`, idéntico al resultado A.

## 4. Registro de ejecución

Rellenar una fila por caso en la primera ejecución. En la segunda ejecución (casos fallidos y CP-51, tras las correcciones), añadir una fila nueva por caso con `2` en la columna **Ejecución**. **Estado:** `Correcto` o `Fallido`. Si el caso falla, en **Resultado obtenido** se describe lo que mostró la aplicación.

| Caso | Ejecución | Resultado obtenido | Estado | Ejecutado por | Fecha |
|---|---|---|---|---|---|
| CP-01 | 1 | | | | |
| CP-02 | 1 | | | | |
| CP-03 | 1 | | | | |
| CP-04 | 1 | | | | |
| CP-05 | 1 | | | | |
| CP-06 | 1 | | | | |
| CP-07 | 1 | | | | |
| CP-08 | 1 | | | | |
| CP-09 | 1 | | | | |
| CP-10 | 1 | | | | |
| CP-11 | 1 | | | | |
| CP-12 | 1 | | | | |
| CP-13 | 1 | | | | |
| CP-14 | 1 | | | | |
| CP-15 | 1 | | | | |
| CP-16 | 1 | | | | |
| CP-17 | 1 | | | | |
| CP-18 | 1 | | | | |
| CP-19 | 1 | | | | |
| CP-20 | 1 | | | | |
| CP-21 | 1 | | | | |
| CP-22 | 1 | | | | |
| CP-23 | 1 | | | | |
| CP-24 | 1 | | | | |
| CP-25 | 1 | | | | |
| CP-26 | 1 | | | | |
| CP-27 | 1 | | | | |
| CP-28 | 1 | | | | |
| CP-29 | 1 | | | | |
| CP-30 | 1 | | | | |
| CP-31 | 1 | | | | |
| CP-32 | 1 | | | | |
| CP-33 | 1 | | | | |
| CP-34 | 1 | | | | |
| CP-35 | 1 | | | | |
| CP-36 | 1 | | | | |
| CP-37 | 1 | | | | |
| CP-38 | 1 | | | | |
| CP-39 | 1 | | | | |
| CP-40 | 1 | | | | |
| CP-41 | 1 | | | | |
| CP-42 | 1 | | | | |
| CP-43 | 1 | | | | |
| CP-44 | 1 | | | | |
| CP-45 | 1 | | | | |
| CP-46 | 1 | | | | |
| CP-47 | 1 | | | | |
| CP-48 | 1 | | | | |
| CP-49 | 1 | | | | |
| CP-50 | 1 | | | | |
| CP-51 | 1 | | | | |

## Anexo: origen de los valores esperados

Las cifras de filas, valores inexistentes, fórmulas, métricas y predicciones se han calculado con el propio código de la aplicación (`src/winamax`) sobre `housing.csv`, con scikit-learn 1.9.1, la versión fijada en `uv.lock`. La separación es reproducible porque usa una semilla fija. Si en la ejecución aparecen cifras distintas, comprobar primero que el entorno usa las versiones de `uv.lock` (`uv sync`).

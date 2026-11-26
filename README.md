# Documentación de Winamax
# WINAMAX · Pipeline de Machine Learning

Aplicación de escritorio para cargar un dataset, preparar los datos, crear un modelo de regresión lineal, guardarlo y usarlo para hacer predicciones.

## Requisitos e instalación

- Python >=3.14
- [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias.

Clona el repositorio y entra en la carpeta del proyecto:

```bash
git clone https://github.com/telmocl/WINAMAX.git
cd WINAMAX
```

Desde la carpeta raíz del repositorio:

```bash
uv sync
```

Esto crea el entorno virtual e instala las dependencias del proyecto.

## Ejecutar la aplicación

```bash
uv run python -m winamax.gui
```

Al iniciar, la aplicación indica cómo empezar: cargar un dataset para crear un modelo o cargar un modelo guardado. La barra inferior muestra siempre el dataset cargado, el modelo actual (creado o cargado) y si hay cambios sin guardar.

## Formato de los archivos de datos

- **Extensiones admitidas:** `.csv`, `.xlsx`, `.xls`, `.sqlite` y `.db`.
- **CSV y Excel:** la primera fila debe contener los nombres de las columnas.
- **SQLite:** la base de datos debe contener una sola tabla.
- **Columnas y valores inexistentes:** las columnas de entrada y salida del modelo deben ser numéricas, y los valores inexistentes pueden tratarse en la aplicación (eliminar filas, media, mediana o valor constante).

## Guía rápida

Los pasos aparecen numerados y en orden. Los pasos que aún no se pueden realizar aparecen deshabilitados.

### 1. Cargar un dataset y crear un modelo

1. En **1. Cargar datos**, pulsa **Cargar dataset** y elige un archivo (`.csv`, `.xlsx`, `.xls`, `.sqlite` o `.db`). Si el archivo es grande, verás una barra de progreso en la parte inferior y el resto de botones quedarán deshabilitados hasta que termine.
2. En **2. Seleccionar columnas**, marca una o varias **Entradas**, elige la **Salida** y pulsa **Aceptar**.
3. En **3. Separar datos**, indica el porcentaje de test (entre 1 y 99) y la semilla, y pulsa **Separar datos**. Se mostrará cuántos valores inexistentes hay en cada columna.
4. En **4. Preprocesar valores inexistentes**, elige una estrategia (eliminar filas, media, mediana o valor constante) y pulsa **Aplicar preprocesado**. Si no hay valores inexistentes, este paso es opcional.
5. En **5. Crear modelo**, pulsa **Crear Modelo de Regresión Lineal**. Verás la fórmula, las métricas de error (R² y MSE en train y test) y un gráfico del ajuste.

### 2. Guardar el modelo

1. En **5. Crear modelo**, escribe si quieres una **Descripción** del modelo.
2. Pulsa **Guardar modelo**, elige la carpeta y el nombre del archivo.
3. La barra inferior pasará a indicar que no hay cambios pendientes.

### 3. Cargar un modelo guardado

1. En **1. Cargar datos**, pulsa **Cargar modelo** y elige un archivo de modelo guardado (extensión propia de la aplicación).
2. Se mostrarán su fórmula, su descripción y sus métricas. Los pasos de datos quedan deshabilitados, porque no hace falta un dataset para usar un modelo guardado.

### 4. Modificar la descripción de un modelo

1. Con un modelo creado o cargado, edita el texto de **Descripción** en **5. Crear modelo**.
2. La barra inferior indicará que el modelo tiene cambios sin guardar.
3. Pulsa **Guardar modelo** para conservar el cambio (puedes sobrescribir el archivo original o guardar otro).

### 5. Hacer una predicción

1. Con un modelo creado o cargado, ve a **6. Realizar predicción**.
2. Escribe un valor numérico para cada entrada del modelo (se admite coma o punto decimal).
3. Pulsa **Realizar predicción**. El resultado aparece debajo del botón.

## Si algo falla

La aplicación muestra ventanas emergentes que explican qué ha fallado y qué puedes hacer. Los detalles técnicos se escriben en la consola, no en la interfaz.

## ⚠️ Advertencia de Seguridad
Esta aplicación utiliza `joblib` para la persistencia de los modelos de regresión lineal. Debido al riesgo de ejecución de código arbitrario durante la deserialización, **cargue únicamente archivos de modelo de origen conocido y confiable**.

## Tests

```bash
uv run pytest
```

## Documentación del proyecto

En la carpeta [`docs/`](docs/) se encuentra:

- `tablas_grandes.md`: técnica elegida para mostrar datasets grandes.
- `prueba_usabilidad.md`: resultados de la prueba de usabilidad y cambios realizados.
- `persistencia.md` e `integracion_continua.md`: documentación técnica del proyecto.
- `plan_pruebas.md` e `informe_pruebas.md`: plan de pruebas funcionales (51 casos) e informe de ejecución previo a la release.

Para contribuir, consulta [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Limitaciones conocidas

No se han registrado limitaciones conocidas en la ejecución previa a esta versión: los 51 casos del plan de pruebas funcionales pasaron tras corregirse las incidencias detectadas en la primera ejecución.



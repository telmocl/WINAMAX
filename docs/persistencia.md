# Investigación sobre la Persistencia de Modelos (#20)

## 1. Comparativa de Métodos
| Criterio | Joblib / Pickle | JSON |
| :--- | :--- | :--- |
| **Facilidad de uso** | Alta (guarda el objeto completo del modelo). | Media (requiere extraer coeficientes manualmente). |
| **Tamaño y eficiencia** | Muy eficiente para arrays grandes de NumPy/scikit-learn. | Ligero pero no optimizado para objetos de estimadores. |
| **Seguridad** | **Baja** (ejecuta código al deserializar si el archivo es malicioso). | **Alta** (solo almacena texto estructurado sin código). |
| **Metadatos** | Permite empaquetar un diccionario con el objeto y los metadatos. | Almacena los parámetros como claves de texto plano. |

## 2. Riesgos de Seguridad de Joblib / Pickle
La deserialización en formatos binarios como `joblib` o `pickle` evalúa código interno que puede ejecutar instrucciones del sistema operativo si se cargan archivos no confiables. Esto se demuestra de forma controlada en el script `prototipos/ejemplo_seguridad.py`.

**Consecuencia para la aplicación:** solo deben abrirse modelos de origen confiable. La carga (#24) debe advertirlo al usuario.

## 3. Decisión Técnica y Estructura
Se selecciona **Joblib** con extensión `.joblib` debido a su integración nativa y optimización con `scikit-learn`.

### Estructura de datos almacenada
El archivo contiene un diccionario con estas claves:

- `version_formato`: número entero de versión del formato (actualmente `1`). Permite comprobar compatibilidad al cargar.
- `modelo`: instancia entrenada de `LinearRegression` (coeficientes y término independiente).
- `columnas_entrada`: lista con los nombres de las columnas de entrada.
- `columna_salida`: nombre de la variable objetivo.
- `formula`: cadena con la ecuación matemática ajustada.
- `metricas`: diccionario con el R² y el error cuadrático medio (MSE) en entrenamiento y test: `r2_train`, `mse_train`, `r2_test`, `mse_test`.
- `descripcion`: texto descriptivo escrito por el usuario (cadena vacía si no hay).

### Información que NO se guarda
- Los datos utilizados: ni el dataset completo ni los conjuntos de entrenamiento y test.
- Los gráficos generados.

## 4. Pasos para Guardar y Recuperar
1. Empaquetar el modelo entrenado y los metadatos en un diccionario (`modelo_a_diccionario`).
2. Guardar en disco con `joblib.dump(diccionario, "ruta.joblib")`.
3. Recuperar con `datos = joblib.load("ruta.joblib")`.

## 5. Implementación (#21)
La lógica está en `src/winamax/persistencia.py`, independiente de la GUI:

- `guardar_modelo(modelo_info, ruta)`: guarda el modelo y devuelve la ruta final. Propaga `OSError` / `PermissionError` si falla.
- `asegurar_extension(ruta)`: añade `.joblib` si la ruta no lo incluye.
- `modelo_a_diccionario(modelo_info)`: construye el diccionario de la sección 3.

**Escritura segura:** se escribe primero en un archivo temporal de la misma carpeta y después se renombra al destino. Así, si falla a mitad de escritura (disco lleno, permisos), no queda un archivo corrupto y el archivo anterior, si existía, se conserva.

**Rutas:** se admiten espacios, tildes y la letra ñ.

Las pruebas unitarias están en `tests/test_persistencia.py` y `tests/test_persistencia_extra.py`.
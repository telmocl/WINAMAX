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

## 3. Decisión Técnica y Estructura
Se selecciona **Joblib** con extensión `.joblib` debido a su integración nativa y optimización con `scikit-learn`.

### Estructura de datos almacenada:
- `modelo`: Instancia entrenada de `LinearRegression`.
- `columnas_entrada`: Lista con las características de entrada.
- `columna_salida`: Nombre de la variable objetivo.
- `formula`: Cadena con la ecuación matemática ajustada.
- `metricas`: Diccionario con el rendimiento ($R^2$).
- `descripcion`: Texto descriptivo del modelo.

## 4. Pasos para Guardar y Recuperar
1. Empaquetar el modelo entrenado y los metadatos en un diccionario de Python.
2. Guardar en disco mediante `joblib.dump(diccionario, "ruta.joblib")`.
3. Recuperar llamando a `datos = joblib.load("ruta.joblib")`.
## Pruebas

- Ejecutar todas las pruebas: `uv run pytest` (desde la raíz del repositorio).
- Cada módulo de la aplicación tiene su archivo de pruebas en `tests/`
  (por ejemplo, `tests/test_importacion.py`).
- Las pruebas importan el código por el nombre del paquete (`from winamax... import ...`),
  sin tocar `sys.path`.
- Los datos se definen dentro de la propia prueba: unas pocas filas con valores
  conocidos, incluidos los casos especiales (valores inexistentes, columnas no numéricas).
  No se usan archivos del repositorio ni de la carpeta `data/`.
- Si una prueba necesita un archivo, se crea en una carpeta temporal con `tmp_path`:

      def test_importar_csv(tmp_path):
          ruta = tmp_path / "datos.csv"
          ruta.write_text("x,y\n1,2\n3,4\n")
          ...

### Reglas de fusión

- Antes de fusionar una rama (`feature`, `fix` o `docs`) en `dev`: actualizarla con
  los últimos cambios de `dev` y ejecutar `uv run pytest`. Solo se fusiona si todas pasan.
- `dev` solo se fusiona en `main` si todas las pruebas pasan sobre `dev`.

## Estilo de código

- Seguimos PEP 8. Herramienta: autopep8 con formato al guardar en VS Code.
- Nombres claros: `snake_case` para funciones y variables, `CamelCase` para clases.
- Cada función o módulo tiene una única responsabilidad.
- Comentarios solo cuando aportan lo que el código no dice.

## Cómo escribimos los commits

Usamos Conventional Commits. La idea es que cualquiera que mire el historial entienda de un vistazo qué se hizo en cada commit, sin tener que abrirlo.

El formato es:

    tipo: qué hemos hecho

Si el cambio afecta a una parte concreta, se puede añadir entre paréntesis, por ejemplo `feat(importacion): cargar datos desde CSV`. La descripción va en minúscula, en una sola línea y sin punto al final.

### Tipos que usamos

| Tipo | Cuándo lo usamos | Ejemplo real de nuestro repo |
|---|---|---|
| `feat` | Añadimos algo nuevo a la app | `feat(importacion): cargar datos desde CSV` |
| `fix` | Arreglamos un error | `fix: corregir nombre de autor en pyproject` |
| `docs` | Tocamos solo documentación | `docs: añadir sección de pruebas a CONTRIBUTING` |
| `test` | Escribimos o cambiamos pruebas | `test: añadir primera prueba con pytest` |
| `build` | Dependencias o configuración | `build: añadir pytest como dependencia de desarrollo` |
| `refactor` | Ordenamos código sin cambiar lo que hace | `refactor: extraer función de validación de columnas` |
| `chore` | Mantenimiento menor | `chore: actualizar .gitignore` |

### Qué tiene que ver con las versiones

Cada tipo influye en el número de versión (SemVer): un `fix` sube la última cifra (1.0.1), un `feat` la del medio (1.1.0), y un cambio que rompe cosas antiguas sube la primera (2.0.0). El resto de tipos no cambian la versión.

### Reglas del equipo

- Un commit, un cambio. Si hemos hecho dos cosas, son dos commits.
- Antes de hacer commit miramos `git status` para asegurarnos de que no se cuela ningún dato ni la carpeta `.venv`.
- Los mensajes que Git crea solos al fusionar (`Merge branch ...`) se dejan como están.
- Evitamos mensajes vagos como `Update archivo.py` o `cambios`.

## Pull Requests

Quien revisa una PR comprueba que:

- El código sigue PEP 8 y los nombres se entienden.
- No hay código duplicado.
- Los mensajes de commit siguen Conventional Commits.
- `uv run pytest` pasa.
- No se han subido datos ni `.venv/`.
## Librería gráfica (GUI)

Para la interfaz usamos **PySide6**. Antes de decidir comparamos dos opciones:
Tkinter y PySide6 / PyQt6.

| Criterio | Tkinter | PySide6 / PyQt6 |
|---|---|---|
| Facilidad de uso | Muy fácil, ideal para prototipos | Media-alta (señales y slots) |
| Compatibilidad | Multiplataforma, viene con Python | Multiplataforma, aspecto nativo en cada sistema |
| Licencia | PSF (permisiva) | LGPL (PySide6) / GPL o comercial (PyQt6) |
| Documentación | Muchos ejemplos, pero fragmentada | Excelente documentación oficial y comunidad activa |
| Componentes | `filedialog`, `ttk.Treeview` (tablas limitadas), `Combobox`, Matplotlib con `backend_tkagg` | `QFileDialog`, `QTableView`/`QTableWidget`, `QComboBox`, Matplotlib con `FigureCanvasQTAgg` |
| Instalación con `uv` | `uv add tk` (si hace falta) | `uv add pyside6` |

### Por qué PySide6 y no PyQt6

- PyQt6 y PySide6 son casi equivalentes, pero usamos **PySide6 porque PyQt6
  no funciona en el equipo de Telmo. Para que todos podamos ejecutar y
  probar la aplicación, elegimos la que funciona en todos los equipos.
- Su licencia LGPL encaja mejor con un entorno académico que la de PyQt6.
- Ofrece una aplicación de aspecto profesional, con tablas robustas y manejo
  avanzado de eventos, útil para mostrar los resultados de nuestros modelos
  (curvas de pérdida, métricas, etc.).
- Tkinter sería más rápido de empezar, pero se queda corto en tablas e
  integración de gráficos.

Se instala con:
    uv add pyside6

#Investigación librería regresión lineal

## 1. Comparativa de Librerías Investigadas

Para seleccionar el enfoque adecuado se investigaron tres alternativas principales en el ecosistema Python:

| Aspecto | `scikit-learn` | `statsmodels` | `numpy` (`lstsq` / `polyfit`) |
| :--- | :--- | :--- | :--- |
| **Facilidad de uso y documentación** :
    Excelente. API orientada a objetos estandarizada (`fit`, `predict`), muy intuitiva y bien documentada.

    Buena pero académica. Enfocada en estadística formal; requiere añadir la constante manualmente (`add_constant`).

    Baja/Media. Nivel matemático puro. Requiere construir y manipular matrices a mano. |
| **Regresión Simple y Múltiple** 
     Misma sintaxis (`.fit(X, y)`) sin importar el número de variables de entrada.

     Requiere definir fórmulas estilo R (vía `patsy`) o construir matrices de diseño explícitas. 

     Requiere construir la matriz de diseño $X$ manualmente para regresión múltiple.
| **Extracción de Coeficientes** :
    Directa mediante atributos del modelo: `model.coef_` y `model.intercept_`. 
    Directa tras el ajuste: `results.params`. 
    Directa desde el vector de solución devuelto por el solver. 
| **Métricas de Error** :
    Integradas y directas mediante `sklearn.metrics` (`mean_squared_error`, `r2_score`). 

    Incluidas en el resumen estadístico (`summary()`), aunque algunas métricas requieren cálculo adicional. 

    No disponibles de forma nativa; deben implementarse manualmente con fórmulas matemáticas.

| **Instalación en el proyecto (`uv`)** :
    `uv add scikit-learn pandas` 
    `uv add statsmodels pandas` 
    `uv add numpy pandas` 

---

## 2. Librería Seleccionada y Justificación

### **Selección:** `scikit-learn`

### **Justificación:**
1. **Estándar de la industria y mantenibilidad:** Su interfaz unificada (`fit`, `predict`, `score`) facilita la incorporación de nuevos desarrolladores al equipo sin curvas de aprendizaje complejas.
2. **simplicidad:** Permite escalar de regresión lineal simple a múltiple sin reescribir ni añadir complejidad a la estructura del código.
3. **Ecosistema integrado:** Ofrece métricas nativas optimizadas para evaluar modelos en entornos de desarrollo y producción.

---

## 3. Gestión de Dependencias

Se añadió `scikit-learn` como dependencia oficial del proyecto ejecutando:

```bash
uv add scikit-learn pandas numpy

## 4. Procedimiento de release

Pasos para publicar una versión (ejemplo con `v0.1.0`; sustituir por la versión que toque). Ejecutar los comandos **uno por uno**: en PowerShell antiguo `&&` no funciona.

### 4.1 Requisitos previos

- Las historias de la versión están terminadas y fusionadas en `dev`.
- Todas las pruebas pasan sobre `dev`:
  ```powershell
  git checkout dev
  git pull
  uv run pytest
  ```
- Un miembro del equipo que **no** haya implementado esas historias prueba el flujo con un dataset de `data/` (cargar, seleccionar columnas, separar, preprocesar). Los errores se corrigen en ramas `fix/...` hacia `dev` antes de continuar.
- El `README.md` describe las funcionalidades de la versión y cómo ejecutarla, y el comando indicado funciona.

### 4.2 Actualizar la versión

Comprobar que `version` en `pyproject.toml` coincide con la versión a publicar (SemVer: `0.x.y` = en desarrollo). Si no coincide:

```powershell
git checkout dev
git pull
git checkout -b chore/version-0.1.0
# editar pyproject.toml
git add pyproject.toml
git commit -m "chore: actualizar versión a 0.1.0"
git push -u origin chore/version-0.1.0
```

Abrir una Pull Request hacia `dev` y fusionarla.

> **Aviso:** al crear una Pull Request, GitHub puede proponer `main` como base. Comprobar siempre que la base es `dev`. La única fusión hacia `main` es la de `dev` en una release.

### 4.3 Fusionar `dev` en `main`

```powershell
git checkout dev
git pull
git checkout

main
git pull
git merge dev
git push origin main
````

Git abre el editor con el mensaje del merge: guardar y **cerrar la pestaña `MERGE_MSG`** para que continúe. Comprobar con `git status` que el árbol está limpio.

### 4.4 Crear y subir la etiqueta

Desde `main`:

```powershell
git tag -a v0.1.0 -m "Versión 0.1.0"
git push origin v0.1.0
git --no-pager show v0.1.0
git --no-pager ls-remote --tags origin
```

No mover ni borrar una etiqueta ya publicada: si hay un error, publicar una versión nueva.

### 4.5 Alinear `dev` con `main`

```powershell
git checkout dev
git merge main
git push origin dev
git diff main dev
```

El último comando no debe mostrar nada: `main` y `dev` contienen el mismo código. El desarrollo continúa en ramas creadas desde `dev`.

### 4.6 Crear la release en GitHub

1. Repositorio → **Releases** → **Draft a new release**.
2. **Choose a tag**: `v0.1.0`. Título: `v0.1.0`.
3. En **Release label**, marcar **Pre-release** mientras la aplicación no permita crear modelos.
4. Pegar las notas (apartado 4.7) y pulsar **Publish release**.

Si la release ya aparece creada como "Latest" con el mensaje del tag como único texto, pulsar el lápiz, cambiar a **Pre-release** y pegar las notas.

### 4.7 Redactar las notas

Sacar los commits de la versión:

```powershell
git --no-pager log --oneline --no-merges --grep="^feat"
git --no-pager log --oneline --no-merges --grep="^fix"
```

Usar `--no-pager` evita el paginador (si se queda abierto, salir con `q`). Estructura de las notas:

```markdown
## WINAMAX v0.1.0 (pre-release)

Descripción breve de la aplicación y del estado del proyecto.

### Funcionalidades
- (commits feat)

### Correcciones
- (commits fix, o "Ninguna en esta versión")

### Pendiente para próximas versiones
- (funcionalidades que faltan)

### Documentación
[README.md de esta versión](https://github.com/telmocl/WINAMAX/blob/v0.1.0/README.md)
```

### 4.8 Comprobar la descarga

Un miembro del equipo con acceso al repositorio (es privado):

1. Descargar **Source code (zip)** desde la release.
2. Descomprimirlo en una carpeta **nueva**, fuera del proyecto de trabajo.
3. Ejecutar:
   ```powershell
   uv sync
   uv run <comando indicado en el README.md>
   ```
4. Confirmar que la aplicación arranca como describe el `README.md`.

Si algo falla, no se modifica la etiqueta: se corrige en una rama `fix/...` desde `dev` y se publica una versión nueva.
````


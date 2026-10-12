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
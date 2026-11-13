# Integración Continua (CI)

El flujo de trabajo de GitHub Actions está configurado en `.github/workflows/ci.yml`.

### ¿Cuándo se ejecuta?
- Automáticamente en cada `push` o `pull_request` realizado sobre cualquier rama del repositorio.

### ¿Qué pasos realiza?
1. **Checkout:** Clona el código fuente actual de la rama.
2. **Setup Python & uv:** Prepara el intérprete de Python e instala la herramienta de gestión de dependencias `uv`.
3. **Sincronización:** Ejecuta `uv sync --locked` para instalar estrictamente las dependencias fijadas en el `uv.lock`.
4. **Pruebas:** Lanza `uv run pytest` para verificar que todas las pruebas unitarias pasan correctamente.
# Informe de pruebas funcionales de WINAMAX

Informe de la ejecución del [plan de pruebas funcionales](plan_pruebas.md) antes de la release final.

- **Versión probada:** rama `dev`, commit `<hash>`.
- **Pruebas automatizadas:** `uv run pytest` ejecutado el `<fecha>`: `<N>` tests, todos correctos.

## 1. Resumen por ejecución

| Ejecución | Fecha | Casos ejecutados | Correctos | Fallidos |
|---|---|---|---|---|
| 1. Ejecución completa del plan | | 51 | | |
| 2. Repetición tras las correcciones (casos fallidos y CP-51) | | | | |

El detalle de cada caso (resultado obtenido, estado, quién lo ejecutó y fecha) está en la sección 4 del plan de pruebas.

## 2. Errores encontrados

| Nº | Caso que lo detectó | Descripción | Tarea en Taiga | Rama | Estado |
|---|---|---|---|---|---|
| 1 | CP-XX | | #NNN | `fix/NNN-descripcion` | Corregido / Limitación conocida |

**Estado:** `Corregido` si el caso pasa en la ejecución 2; `Limitación conocida` si el equipo decide no corregirlo antes de la release.

## 3. Limitaciones conocidas

Errores que no se corrigen en esta release. Cada uno se documenta también en el `README.md`.

| Nº de error | Limitación | Motivo para no corregirla | Cómo evitarla |
|---|---|---|---|
| | | | |

## 4. Conclusión

- [ ] Todos los casos de prueba son correctos, o los fallos restantes están documentados como limitaciones conocidas.
- [ ] Las limitaciones conocidas están en el `README.md`.
- [ ] Se puede crear la release final.

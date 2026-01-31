# Lista de Tareas Pendientes - Sincronización y Despliegue

## Situación Actual
- La App Móvil (Local/Web) conecta al Backend Local (localhost:5001).
- El Backend Local usa una base de datos SQLite vacía o desactualizada (`diamante.db`).
- La información real está en Heroku (PostgreSQL).
- Por eso la app se ve vacía: no está consultando la base de datos de producción.

## Pasos para Arreglar Mañana
1. **Opción A (Desarrollo Seguro):** 
   - Descargar los datos de Heroku a la base de datos local.
   - Ejecutar script de importación: `python importar_todo_heroku.py`
   - Esto llenará la app local con datos reales sin arriesgar la producción.

2. **Opción B (Conexión Directa):**
   - Configurar la App Móvil para que apunte a la URL de Heroku en lugar de localhost.
   - Modificar `Config.apiBaseUrl` en el código de Flutter (si existe configuración) o en `api_service.dart`.

3. **Verificar Endpoints de Sincronización:**
   - Revisar `api.py` para asegurar que las rutas `/api/v1/sync` o `/api/v1/clientes` estén devolviendo los datos correctamente.
   - Comprobar permisos y tokens JWT.

## Acciones Realizadas Hoy
- Reparado el entorno de Python (venv_fix) para correr el backend.
- Arreglado error de librería 'Pillow' en Windows.
- Configurada la App Móvil para correr en Web (Chrome) ya que no hay emuladores disponibles.
- Despliegue de correcciones a GitHub y Heroku.

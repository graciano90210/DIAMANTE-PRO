# 📅 Plan para Mañana - 13 de Enero 2026

## 🔴 Prioridad Alta (Errores Críticos)

### 1. Corregir Error "Error 401: Missing Authorization Header"
El servidor rechaza el registro de pagos porque el token no está llegando.
- **Hipótesis:** `AuthService.getToken()` está devolviendo `null` o el formato del header está mal en `sync_service.dart`.
- **Acción:**
  - Depurar `AuthService.getToken()` en el dispositivo.
  - Asegurar que el token persista al cerrar la app.
  - Verificar que el prefijo `Bearer ` (con espacio) se esté añadiendo correctamente.

### 2. Verificar Flujo Offline -> Online
Confirmar que si se guarda un pago sin internet, este se envíe automáticamente al recuperar la conexión.

## 🟡 Prioridad Media (Mejoras)

### 3. Eliminar Advertencias de Consola
- **Deprecated:** `WillPopScope` ha sido reemplazado por `PopScope` en las nuevas versiones de Flutter.
- **Gradle:** Actualizar configuración de `android/build.gradle` para eliminar warnings de Kotlin y AGP.

### 4. Pruebas de Usabilidad
- Verificar tamaño de fuentes en pantallas pequeñas.
- Probar el flujo completo de creación de clientes desde la app.

## 🟢 Prioridad Baja (Futuro)

### 5. Notificaciones Push
Implementar avisos cuando se asigne una nueva ruta al cobrador.

---
**Nota:** El despliegue en Heroku (v38) ya incluye el driver de PostgreSQL, por lo que el Error 503 está resuelto. El foco ahora es la autenticación móvil.

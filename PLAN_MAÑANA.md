# Plan de Finalización - Diamante PRO (Móvil)

## Estado Actual (09/01/2026)
- **Login**: Funcional.
- **Lista de Clientes**: Funcional.
- **Creación de Clientes**: Implementada y conectada.
- **Creación de Préstamos**: Implementada y conectada.
- **Listado de Préstamos por Cliente**: Implementado.
- **Registro de Cobros (Abonos)**: Implementado (Core logic).
- **Backend**: Endpoints de Cobrador Completos.

## Tareas Pendientes para Mañana

### 1. Refinamiento y Pruebas
- [ ] **Probar ciclo completo**: Crear Cliente -> Crear Préstamo -> Registrar Cobro. (Verificar que el saldo baje).
- [ ] **Validaciones UI**: Mejorar mensajes de error y loaders.
- [ ] **Dashboard**: Verificar que los contadores del Dashboard (Cobrado Hoy) se actualicen tras un cobro.

### 2. Sincronización Offline (Critico)
- [ ] **SQLite Local**: Implementar tablas locales (`clientes`, `prestamos`, `pagos`).
- [ ] **Cola de Sincronización**: Guardar POSTs fallidos en local y reintentar cuando haya conexión.
- [ ] **Descarga Inicial**: Al login, descargar toda la data del cobrador a SQLite.

### 3. Funciones Adicionales
- [ ] **Impresión Bluetooth**: Investigar librería para imprimir recibos (termales).
- [ ] **Subida de Fotos**: Habilitar multipart/form-data para subir foto del recibo en `registrar_cobro_screen.dart`.
- [ ] **Edición**: Permitir editar datos básicos del cliente.

### 4. Despliegue
- [ ] **Build Android APK**: Generar APK firmado (`flutter build apk --release`).
- [ ] **Distribuir**: Subir APK a un drive o distribuir a cobradores para pruebas de campo.
- [ ] **Switch a Producción**: Cambiar `baseUrl` en `api_config.dart` a la URL de Heroku antes del build.

## Comandos Útiles

**Correr Backend Local:**
```bash
python run.py
```

**Correr App Web:**
```bash
flutter run -d chrome --web-port 8080
```

**Generar APK:**
```bash
flutter build apk --release
```

# PLAN DE IMPLEMENTACIÓN - APP MÓVIL DIAMANTE PRO

## 📱 Estado Actual (4 de Enero 2026)

### ✅ Completado:
- Login funcional con JWT
- Dashboard con estadísticas (2 préstamos, $5040 cartera)
- API sincronizada con backend (usando cobrador_id)
- Modelos actualizados (User, Cliente, Prestamo)
- Navegación básica implementada

### 🔧 Por Completar:

## 1. DEPURACIÓN Y PRUEBAS (PRIORIDAD ALTA)

### 1.1 Verificar Carga Completa
- [ ] Revisar logs del navegador (F12 Console)
- [ ] Verificar que todas las tarjetas del dashboard muestren datos
- [ ] Confirmar que el menú lateral funciona correctamente

### 1.2 Probar Pantallas Existentes
- [ ] **Clientes Screen**
  - Verificar que cargue la lista de clientes
  - Probar búsqueda por nombre
  - Verificar datos mostrados (nombre, teléfono, dirección)
  
- [ ] **Préstamos Screen**
  - Verificar lista de préstamos activos
  - Confirmar datos correctos (monto, saldo, cuotas)
  - Probar filtro por cliente
  
- [ ] **Cobros Screen**
  - Verificar ruta de cobro del día
  - Probar registro de pagos
  - Confirmar actualización de saldos

## 2. FUNCIONALIDADES ESENCIALES (PRIORIDAD MEDIA)

### 2.1 Modo Offline
**Paquete:** sqflite
**Objetivo:** Permitir trabajo sin conexión

Tareas:
- [ ] Instalar sqflite y path_provider
- [ ] Crear base de datos local (clientes, prestamos, pagos_pendientes)
- [ ] Implementar sincronización automática
- [ ] Agregar indicador de estado online/offline
- [ ] Gestionar cola de pagos pendientes

### 2.2 Captura de Fotos
**Paquete:** image_picker
**Objetivo:** Foto de recibo al registrar cobro

Tareas:
- [ ] Instalar image_picker
- [ ] Agregar botón de cámara en registro de pago
- [ ] Comprimir imagen antes de enviar
- [ ] Subir foto a servidor o base64 en API
- [ ] Mostrar preview antes de guardar

### 2.3 Geolocalización
**Paquetes:** geolocator, permission_handler
**Objetivo:** Guardar ubicación GPS al cobrar

Tareas:
- [ ] Instalar geolocator y permission_handler
- [ ] Solicitar permisos de ubicación
- [ ] Capturar coordenadas al registrar pago
- [ ] Enviar GPS al backend junto con el pago
- [ ] Mostrar distancia del cliente en lista

## 3. FUNCIONALIDADES AVANZADAS (PRIORIDAD BAJA)

### 3.1 Mapas y Rutas
**Paquete:** mapbox_gl o google_maps_flutter
**Objetivo:** Ver clientes en mapa y optimizar ruta

Tareas:
- [ ] Elegir proveedor de mapas (Mapbox con GitHub Student Pack)
- [ ] Instalar mapbox_gl
- [ ] Crear pantalla de mapa
- [ ] Mostrar clientes como marcadores
- [ ] Implementar navegación a cliente
- [ ] Agregar optimización de ruta

### 3.2 Notificaciones Push
**Paquete:** firebase_messaging
**Objetivo:** Alertas de pagos atrasados

Tareas:
- [ ] Configurar Firebase (GitHub Student Pack)
- [ ] Instalar firebase_messaging
- [ ] Implementar registro de token
- [ ] Crear servicio de notificaciones en backend
- [ ] Probar envío de notificaciones

### 3.3 WhatsApp Integration
**Paquete:** url_launcher
**Objetivo:** Contactar clientes por WhatsApp

Tareas:
- [ ] Instalar url_launcher
- [ ] Agregar botón de WhatsApp en detalle de cliente
- [ ] Implementar envío de mensaje predefinido
- [ ] Agregar recordatorio de pago automático

## 4. MEJORAS DE UI/UX

- [ ] Agregar splash screen
- [ ] Implementar tema oscuro
- [ ] Mejorar animaciones de transición
- [ ] Agregar indicadores de carga
- [ ] Implementar pull-to-refresh en listas
- [ ] Agregar gráficos de estadísticas (fl_chart)

## 5. TESTING Y DEPLOYMENT

### 5.1 Testing
- [ ] Crear tests unitarios (modelos)
- [ ] Crear tests de integración (API)
- [ ] Probar en dispositivo Android real
- [ ] Probar en iOS (si es posible)

### 5.2 Build y Deploy
- [ ] Configurar iconos y splash screen
- [ ] Build APK para Android
- [ ] Probar instalación en teléfono
- [ ] Configurar firma de app
- [ ] Preparar para Google Play Store

## 📋 ORDEN RECOMENDADO DE IMPLEMENTACIÓN

### Fase 1 - Esta Sesión (4 Enero)
1. Depurar y verificar dashboard ✓
2. Probar pantallas de Clientes y Préstamos
3. Corregir errores encontrados

### Fase 2 - Siguiente Sesión
4. Implementar captura de fotos (más visible para cliente)
5. Agregar geolocalización en cobros
6. Implementar modo offline básico

### Fase 3 - Semana Siguiente
7. Integrar mapas con Mapbox
8. Configurar notificaciones push
9. Agregar integración WhatsApp

### Fase 4 - Finalización
10. Testing completo
11. Mejoras de UI/UX
12. Build final y deployment

## 🔑 CREDENCIALES Y URLs

- **Backend:** https://diamante-pro-1951dcdb66df.herokuapp.com
- **API Base:** https://diamante-pro-1951dcdb66df.herokuapp.com/api/v1
- **Usuarios de prueba:**
  - cvampi / 1234 (cobrador con 2 préstamos)
  - santiago / 1234 (cobrador)
  - tasmania / 5678 (cobrador)

## 📦 PAQUETES A INSTALAR

```yaml
dependencies:
  # Ya instalados
  flutter:
    sdk: flutter
  provider: ^6.1.1
  http: ^1.1.2
  shared_preferences: ^2.2.2
  
  # Por instalar
  sqflite: ^2.3.0          # Base de datos local
  path_provider: ^2.1.1    # Rutas del sistema
  image_picker: ^1.0.4     # Captura de fotos
  geolocator: ^10.1.0      # GPS
  permission_handler: ^11.0.1  # Permisos
  url_launcher: ^6.2.1     # WhatsApp y llamadas
  mapbox_gl: ^0.16.0       # Mapas (con Student Pack)
  firebase_messaging: ^14.7.5  # Notificaciones push
  fl_chart: ^0.65.0        # Gráficos
```

## 🎯 OBJETIVO FINAL

Aplicación móvil completa para cobradores con:
- ✅ Login y autenticación
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Lista de clientes y préstamos
- ✅ Registro de cobros con foto y GPS
- ⏳ Modo offline con sincronización
- ⏳ Mapas con optimización de rutas
- ⏳ Notificaciones push
- ⏳ Integración WhatsApp
- ⏳ APK listo para distribución

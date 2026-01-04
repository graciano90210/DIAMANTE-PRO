# FUNCIONES DE LA PLATAFORMA WEB VS APP MÓVIL

## ✅ FUNCIONES YA IMPLEMENTADAS EN APP MÓVIL

### 1. Autenticación
- ✅ Login con usuario/contraseña
- ✅ JWT token
- ✅ Cerrar sesión

### 2. Dashboard
- ✅ Préstamos activos
- ✅ Total cartera
- ✅ Cobrado hoy
- ✅ Por cobrar hoy
- ✅ Préstamos al día
- ✅ Préstamos atrasados
- ✅ Préstamos mora grave

### 3. Clientes
- ✅ Lista de clientes
- ✅ Búsqueda de clientes
- ✅ Ver teléfono y dirección

### 4. Préstamos
- ⏳ Lista de préstamos (en proceso de arreglo)
- ⏳ Filtros (Todos, Al Día, Atrasados)

### 5. Registrar Cobro
- ⏳ Básico implementado pero sin probar

---

## ❌ FUNCIONES PENDIENTES DE IMPLEMENTAR

### MÓDULO: CLIENTES

#### En la Web:
1. **Ver detalle completo del cliente**
   - Datos personales
   - Historial de préstamos
   - Total prestado
   - Total pagado
   - Préstamos actuales

2. **Agregar nuevo cliente**
   - Formulario con todos los campos
   - Validaciones
   - Guardar en BD

3. **Editar cliente**
   - Modificar datos
   - Actualizar información

4. **Marcar como VIP**
   - Toggle VIP

5. **Ver ubicación GPS**
   - Si tiene coordenadas guardadas

#### Para App Móvil:
- [ ] Pantalla de detalle de cliente
- [ ] Formulario agregar cliente
- [ ] Formulario editar cliente
- [ ] Botón WhatsApp directo
- [ ] Botón llamar directo
- [ ] Ver ubicación en mapa
- [ ] Capturar ubicación GPS actual

---

### MÓDULO: PRÉSTAMOS

#### En la Web:
1. **Ver detalle del préstamo**
   - Información completa
   - Cliente asociado
   - Historial de pagos
   - Gráfico de progreso
   - Cuotas pendientes

2. **Crear nuevo préstamo**
   - Seleccionar cliente
   - Ingresar monto
   - Configurar plazo
   - Calcular cuotas
   - Asignar frecuencia de pago

3. **Editar préstamo**
   - Modificar datos básicos

4. **Ver historial de pagos**
   - Lista completa de pagos
   - Fechas
   - Montos
   - Recibos

5. **Imprimir recibo**
   - PDF con detalles

6. **Marcar como pagado/cancelado**
   - Cambiar estado

#### Para App Móvil:
- [x] Lista de préstamos ✅
- [x] Filtros (Todos/Al Día/Atrasados) ✅
- [ ] Pantalla detalle de préstamo
- [ ] Ver historial de pagos del préstamo
- [ ] Ver cuotas pendientes
- [ ] Gráfico de progreso visual
- [ ] Crear nuevo préstamo
- [ ] Editar préstamo existente

---

### MÓDULO: COBROS (PAGOS)

#### En la Web:
1. **Ruta de cobro del día**
   - Clientes que deben pagar hoy
   - Ordenados por prioridad
   - Filtrar por estado

2. **Registrar pago/cobro**
   - Seleccionar préstamo
   - Ingresar monto
   - Agregar observaciones
   - Capturar ubicación GPS
   - Foto del recibo (opcional)
   - Registrar fecha y hora

3. **Ver lista de cobros realizados**
   - Historial de cobros
   - Filtros por fecha
   - Por cliente
   - Exportar

4. **Imprimir recibo**
   - PDF del cobro

5. **Anular/Editar cobro**
   - Solo si tiene permisos

#### Para App Móvil:
- [x] Lista de préstamos activos ✅
- [ ] **Ruta de cobro diaria** (clientes pendientes de hoy)
- [ ] **Registrar pago con:**
  - [ ] Captura de foto del recibo
  - [ ] GPS automático al cobrar
  - [ ] Observaciones
  - [ ] Firma digital del cliente
- [ ] Historial de cobros del día
- [ ] Ver recibo generado
- [ ] Modo offline (guardar cobros sin internet)
- [ ] Sincronización automática

---

### MÓDULO: REPORTES Y ESTADÍSTICAS

#### En la Web:
1. **Dashboard general**
   - Gráficos
   - Métricas del día/semana/mes
   - Proyecciones

2. **Reportes de cobrador**
   - Desempeño individual
   - Cobrado por día
   - Eficiencia de cobro

3. **Reportes de mora**
   - Clientes atrasados
   - Montos en mora
   - Días de atraso

4. **Reportes financieros**
   - Total prestado
   - Total cobrado
   - Utilidades
   - Cartera total

5. **Exportar reportes**
   - Excel
   - PDF

#### Para App Móvil:
- [x] Dashboard básico ✅
- [ ] Gráficos visuales (fl_chart)
- [ ] Reporte diario del cobrador
- [ ] Reporte semanal
- [ ] Mis estadísticas personales
- [ ] Exportar reporte básico

---

### MÓDULO: CAJA (GASTOS)

#### En la Web:
1. **Cuadre de caja**
   - Inicio del día (efectivo inicial)
   - Cobros del día
   - Gastos del día
   - Traslados
   - Cuadre final

2. **Registrar gastos**
   - Tipo de gasto
   - Monto
   - Descripción
   - Foto del comprobante

3. **Registrar traslados**
   - De cobrador a gerente
   - Monto trasladado
   - Fecha y hora

4. **Ver historial de caja**
   - Movimientos del día
   - Filtros

#### Para App Móvil:
- [ ] **Inicio de caja** (efectivo al comenzar el día)
- [ ] **Registrar gasto:**
  - [ ] Foto del comprobante
  - [ ] Categoría de gasto
  - [ ] Monto y descripción
- [ ] **Cuadre de caja al final del día**
- [ ] **Registrar traslado de efectivo**
- [ ] **Resumen de movimientos del día**

---

### MÓDULO: RUTAS

#### En la Web:
1. **Ver lista de rutas**
   - Todas las rutas
   - Filtrar activas/inactivas

2. **Crear nueva ruta**
   - Nombre
   - Zona
   - Asignar cobrador

3. **Editar ruta**
   - Cambiar datos
   - Reasignar cobrador

4. **Ver clientes de la ruta**
   - Lista de clientes asignados

5. **Asociar ruta a sociedad**
   - Para gestión multi-empresa

#### Para App Móvil:
- [ ] Ver mis rutas asignadas
- [ ] Ver clientes por ruta
- [ ] Mapa de la ruta (con todos los clientes)
- [ ] Optimizar ruta del día (orden de visitas)
- [ ] Ver progreso de cobro por ruta

---

### MÓDULO: SOCIEDADES

#### En la Web:
1. **Ver sociedades**
   - Lista de sociedades/empresas

2. **Crear sociedad**
   - Datos de la empresa
   - Capital inicial

3. **Editar sociedad**
   - Modificar datos

4. **Ver reportes por sociedad**
   - Financieros
   - Rendimiento

#### Para App Móvil:
- [ ] Ver sociedades (solo lectura)
- [ ] Cambiar entre sociedades (si aplica)

---

### MÓDULO: CAPITAL Y ACTIVOS

#### En la Web:
1. **Registrar aportes de capital**
2. **Gestionar retiros**
3. **Ver balance**
4. **Registrar activos**
5. **Depreciación**

#### Para App Móvil:
- No aplica para cobradores (solo gerente/dueño)

---

### MÓDULO: USUARIOS Y PERMISOS

#### En la Web:
1. **Ver usuarios**
2. **Crear usuario**
3. **Editar usuario**
4. **Asignar roles**
5. **Activar/Desactivar**

#### Para App Móvil:
- [ ] Ver mi perfil
- [ ] Cambiar mi contraseña
- [ ] Actualizar mis datos

---

## 🎯 FUNCIONALIDADES EXCLUSIVAS PARA APP MÓVIL

### 1. **Modo Offline**
- [ ] Base de datos local (sqflite)
- [ ] Sincronización automática
- [ ] Indicador de estado (online/offline)
- [ ] Cola de acciones pendientes

### 2. **Cámara**
- [ ] Foto del recibo al cobrar
- [ ] Foto del comprobante de gasto
- [ ] Foto de identificación del cliente

### 3. **GPS/Ubicación**
- [ ] Captura automática al cobrar
- [ ] Ver ubicación del cliente en mapa
- [ ] Navegación al cliente (Google Maps/Waze)
- [ ] Optimización de ruta diaria

### 4. **Notificaciones Push**
- [ ] Recordatorio de cobros pendientes
- [ ] Alertas de mora
- [ ] Mensajes del gerente

### 5. **Integración WhatsApp**
- [ ] Enviar recordatorio de pago
- [ ] Compartir recibo
- [ ] Contacto directo

### 6. **Llamadas**
- [ ] Llamar directamente desde la app
- [ ] Historial de llamadas

### 7. **Escáner QR**
- [ ] Escanear QR del cliente
- [ ] Generar QR del préstamo

---

## 📋 PLAN DE IMPLEMENTACIÓN SUGERIDO

### FASE 1 - FUNCIONALIDAD CORE (Esta semana)
1. [x] Arreglar pantalla de Préstamos ✅
2. [ ] Pantalla detalle de Cliente
3. [ ] Pantalla detalle de Préstamo
4. [ ] Registro de Cobro completo con foto
5. [ ] Captura GPS al cobrar
6. [ ] Ruta de cobro del día

### FASE 2 - MODO OFFLINE (Semana 2)
7. [ ] Base de datos local (sqflite)
8. [ ] Sincronización automática
9. [ ] Indicadores de estado

### FASE 3 - MAPAS Y NAVEGACIÓN (Semana 3)
10. [ ] Integración Mapbox
11. [ ] Ver clientes en mapa
12. [ ] Navegación a cliente
13. [ ] Optimización de ruta

### FASE 4 - CAJA Y GASTOS (Semana 4)
14. [ ] Inicio de caja
15. [ ] Registrar gastos
16. [ ] Cuadre de caja
17. [ ] Traslados

### FASE 5 - NOTIFICACIONES E INTEGRACIONES (Semana 5)
18. [ ] Firebase Push Notifications
19. [ ] Integración WhatsApp
20. [ ] Llamadas directas

### FASE 6 - REPORTES Y ESTADÍSTICAS (Semana 6)
21. [ ] Gráficos (fl_chart)
22. [ ] Reportes personales
23. [ ] Exportar datos

### FASE 7 - CREAR Y EDITAR (Semana 7)
24. [ ] Crear nuevo cliente
25. [ ] Editar cliente
26. [ ] Crear nuevo préstamo

### FASE 8 - PULIDO Y TESTING (Semana 8)
27. [ ] Testing completo
28. [ ] Optimizaciones
29. [ ] Build APK
30. [ ] Preparar para Play Store

---

## 🚀 PRIORIDADES INMEDIATAS

### HOY:
1. ✅ Arreglar error de Préstamos
2. Crear pantalla de detalle de Préstamo
3. Mejorar registro de Cobro

### MAÑANA:
4. Implementar captura de foto
5. Agregar GPS automático
6. Crear pantalla de Ruta del Día

---

## 📊 PROGRESO ACTUAL

**Funcionalidades completadas:** 5/30 (17%)
**En desarrollo:** 3/30 (10%)
**Pendientes:** 22/30 (73%)

**Tiempo estimado para completar todas las funciones:** 8 semanas
**Tiempo para funcionalidad básica completa:** 2-3 semanas

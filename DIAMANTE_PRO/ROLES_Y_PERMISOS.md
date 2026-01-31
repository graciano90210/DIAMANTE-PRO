# 🏢 ROLES Y PERMISOS - DIAMANTE PRO

## 👥 Estructura de la Empresa

### 1. 💎 DUEÑO DEL CAPITAL (Rol: `dueno`)
**Descripción**: Propietario del negocio, invierte el capital y recibe ganancias.

**Permisos**:
- ✅ Ver Dashboard completo con todas las estadísticas financieras
- ✅ Ver ganancias y márgenes de utilidad
- ✅ Ver todos los préstamos y clientes
- ✅ Ver reportes financieros completos
- ✅ Ver historial de pagos y cobros
- ✅ Gestionar usuarios (crear/editar/eliminar)
- ✅ Cambiar configuraciones del sistema
- ❌ NO puede cobrar directamente (no es su función)
- ❌ NO puede crear préstamos (delega a secretaria/supervisor)

---

### 2. 📋 SECRETARIA (Rol: `secretaria`)
**Descripción**: Atiende oficina, registra clientes y crea préstamos.

**Permisos**:
- ✅ Ver Dashboard con estadísticas operativas (sin ganancias)
- ✅ Registrar nuevos clientes
- ✅ Editar información de clientes
- ✅ Crear nuevos préstamos
- ✅ Ver lista de préstamos activos
- ✅ Ver historial de pagos
- ✅ Generar reportes operativos
- ❌ NO puede ver ganancias/utilidades
- ❌ NO puede eliminar préstamos
- ❌ NO puede gestionar usuarios
- ❌ NO puede cobrar en ruta

---

### 3. 👔 SUPERVISOR (Rol: `supervisor`)
**Descripción**: Supervisa a los cobradores, gestiona rutas y resuelve problemas.

**Permisos**:
- ✅ Ver Dashboard completo operativo
- ✅ Ver todos los préstamos y su estado
- ✅ Ver ruta de cobro de todos los cobradores
- ✅ Ver historial de cobros realizados
- ✅ Reasignar préstamos a otros cobradores
- ✅ Ver estadísticas por cobrador
- ✅ Marcar clientes en mora
- ✅ Generar reportes de cobranza
- ✅ Ver mapa de ubicaciones (GPS)
- ❌ NO puede ver ganancias/utilidades del dueño
- ❌ NO puede crear préstamos
- ❌ NO puede eliminar préstamos
- ❌ NO puede gestionar usuarios

---

### 4. 🚶 COBRADOR (Rol: `cobrador`)
**Descripción**: Sale a la calle a cobrar las cuotas diarias/semanales.

**Permisos**:
- ✅ Ver Dashboard simple con sus propias estadísticas
- ✅ Ver SOLO su ruta de cobro asignada
- ✅ Ver lista de clientes que debe visitar HOY
- ✅ Registrar pagos de sus clientes
- ✅ Ver historial de pagos de sus clientes
- ✅ Ver detalles del préstamo (monto, cuotas, saldo)
- ✅ Enviar recibo por WhatsApp
- ✅ Ver mapa con ubicación de clientes asignados
- ❌ NO puede ver clientes de otros cobradores
- ❌ NO puede ver ganancias/utilidades
- ❌ NO puede crear préstamos
- ❌ NO puede eliminar pagos
- ❌ NO puede cambiar montos de préstamos
- ❌ NO puede ver lista completa de clientes

---

## 📊 Matriz de Permisos

| Función | Dueño | Secretaria | Supervisor | Cobrador |
|---------|-------|-----------|-----------|----------|
| Ver ganancias | ✅ | ❌ | ❌ | ❌ |
| Crear clientes | ✅ | ✅ | ❌ | ❌ |
| Editar clientes | ✅ | ✅ | ✅ | ❌ |
| Eliminar clientes | ✅ | ❌ | ❌ | ❌ |
| Crear préstamos | ✅ | ✅ | ❌ | ❌ |
| Ver todos los préstamos | ✅ | ✅ | ✅ | ❌ |
| Ver solo sus préstamos | - | - | - | ✅ |
| Registrar cobros | ❌ | ❌ | ✅ | ✅ |
| Ver ruta completa | ✅ | ✅ | ✅ | ❌ |
| Ver solo su ruta | - | - | - | ✅ |
| Gestionar usuarios | ✅ | ❌ | ❌ | ❌ |
| Ver reportes financieros | ✅ | ❌ | ❌ | ❌ |
| Ver reportes operativos | ✅ | ✅ | ✅ | ❌ |
| Reasignar préstamos | ✅ | ❌ | ✅ | ❌ |

---

## 🎯 Casos de Uso

### Día típico del COBRADOR:
1. Inicia sesión en la app
2. Ve su Dashboard: "Tienes 25 clientes por cobrar hoy - Meta: $500,000"
3. Abre "Mi Ruta de Cobro"
4. Ve lista de 25 clientes con semáforo (verde/amarillo/rojo)
5. Visita al primer cliente
6. Registra el pago
7. Sistema envía recibo por WhatsApp automáticamente
8. Continúa con el siguiente cliente

### Día típico de la SECRETARIA:
1. Llega nuevo cliente al negocio
2. Registra sus datos en "Nuevo Cliente"
3. Cliente solicita préstamo de $500,000
4. Crea el préstamo con calculadora automática
5. Imprime contrato o lo envía por WhatsApp
6. Asigna el cobro a un cobrador específico
7. Cliente recibe primer desembolso

### Día típico del SUPERVISOR:
1. Revisa Dashboard: estado general de cobranza
2. Ve que el Cobrador #3 tiene 8 clientes en mora
3. Revisa ubicación GPS de los clientes
4. Optimiza la ruta del cobrador
5. Llama al cobrador para dar instrucciones
6. Reasigna 2 clientes difíciles a otro cobrador
7. Genera reporte de cobranza del día

### Semana típica del DUEÑO:
1. Revisa Dashboard financiero cada lunes
2. Ve ganancias semanales: $2,500,000
3. Revisa cartera total: $45,000,000
4. Ve que tiene $10,000,000 disponibles para prestar
5. Analiza qué cobradores son más efectivos
6. Decide si necesita contratar más cobradores
7. Retira sus ganancias

---

## 🔐 Implementación Técnica

### Decorador de permisos (a implementar):
```python
def requiere_rol(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('rol') not in roles_permitidos:
                flash('No tienes permisos para acceder a esta página')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Uso:
@app.route('/reportes/financieros')
@requiere_rol('dueno')
def reportes_financieros():
    # Solo el dueño puede ver esto
    pass
```

---

## 📱 Próximas Funcionalidades por Rol

### Para DUEÑO:
- Gráficos de crecimiento del negocio
- ROI (retorno de inversión)
- Comparación mes a mes
- Exportar reportes a Excel

### Para SECRETARIA:
- Sistema de aprobación de préstamos
- Verificación de identidad con fotos
- Historial crediticio del cliente
- Calculadora de riesgo

### Para SUPERVISOR:
- Mapa en tiempo real de cobradores
- Sistema de chat con cobradores
- Alertas de clientes en mora crítica
- Optimizador de rutas con IA

### Para COBRADOR:
- App móvil nativa (Android/iOS)
- Modo offline para zonas sin internet
- Tomar foto del comprobante de pago
- Navegación GPS a próximo cliente

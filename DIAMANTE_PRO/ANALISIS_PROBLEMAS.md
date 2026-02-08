# Análisis de Problemas - DIAMANTE PRO

## Fecha: 2026-02-08

### PROBLEMAS IDENTIFICADOS:

#### 1. **CLIENTES Y GASTOS VACÍOS** ✅ IDENTIFICADO
**Problema:** Vista muestra "Total Clientes: 305" pero tabla vacía
**Causa:** Filtro por `ruta_seleccionada_id` en sesión
**Ubicación:** `app/blueprints/clientes.py` línea 35-45
```python
ruta_seleccionada_id = session.get('ruta_seleccionada_id')
if ruta_seleccionada_id:
    query = query.filter(...)  # OCULTA TODOS SI NO HAY RUTA SELECCIONADA
```

**Solución:** Remover filtro por defecto o mostrar TODOS cuando no hay selección

---

#### 2. **GASTOS VACÍOS** ✅ IDENTIFICADO
**Problema:** Vista de gastos vacía
**Causa:** Filtro por `usuario_origen_id` para cobradores
**Ubicación:** `app/blueprints/finanzas.py` línea 234-237
```python
if rol == 'cobrador':
    query = query.filter_by(usuario_origen_id=usuario_id)
```

**Solución:** Para dueño/gerente, NO filtrar por usuario

---

#### 3. **SALDOS NEGATIVOS EN COBRADORES** ⚠️ CRÍTICO
**Problema:** Cobradores con -$1,016,821.36 COP
**Causa:** Préstamos registrados SIN fondear caja primero
**Ubicación:** `app/services/caja_service.py` línea 50-70

**Flujo ACTUAL (INCORRECTO):**
```
AporteCapital → Transaccion(INGRESO) → ❌ NO SE REFLEJA EN CAJAS
Prestamo creado → Resta de caja cobrador → ❌ SALDO NEGATIVO
```

**Flujo CORRECTO:**
```
1. AporteCapital → CajaDueno (aumenta saldo)
2. Traslado: CajaDueno → CajaRuta
3. Traslado: CajaRuta → Cobrador (virtual)
4. Préstamo → Resta de saldo cobrador
```

**Solución:** 
- Modificar `capital_guardar()` para actualizar `CajaDueno`
- Crear script de migración para ajustar saldos históricos

---

#### 4. **DASHBOARD MUESTRA 0** ✅ IDENTIFICADO
**Problema:** Dashboard y Caja del Dueño en 0
**Causa:** Consultas NO suman aportes de capital en cajas
**Ubicación:** `app/routes.py` línea 13-200

**Variables afectadas:**
- `capital_total_aportado = 0` (línea 177)
- `capital_disponible = 0` (línea 179)

**Solución:** Calcular desde `CajaDueno` y `AporteCapital`

---

#### 5. **MOROSIDAD 76.84%** ⚠️ IRREAL
**Problema:** Tasa de morosidad irreal
**Causa:** Lógica marca como atrasado si `cuotas_atrasadas > 0`
**Ubicación:** `app/routes.py` línea 52
```python
prestamos_atrasados = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 0)
```

**Solución:** Cambiar umbral a `cuotas_atrasadas > 2` (gracia de 2 días)

---

#### 6. **ATRIBUTO fecha_fin INCONSISTENTE** ✅ CORREGIDO
**Problema:** AttributeError 'Prestamo' object has no attribute 'fecha_fin'
**Causa:** Modelo usa `fecha_fin_estimada`, código usa `fecha_fin`
**Ubicación:** `app/blueprints/reportes.py` línea 180
**Estado:** ✅ YA CORREGIDO

---

## PLAN DE ACCIÓN:

### FASE 1: Correcciones Inmediatas (30 min)
1. ✅ Remover filtros que ocultan datos en clientes.py
2. ✅ Remover filtros que ocultan datos en gastos
3. ✅ Ajustar umbral de morosidad a 2 cuotas

### FASE 2: Corrección de Cajas (1 hora)
4. Modificar `capital_guardar()` para actualizar CajaDueno
5. Crear script de migración para ajustar saldos históricos
6. Actualizar dashboard para leer de CajaDueno

### FASE 3: Verificación (30 min)
7. Probar flujo completo: Aporte → Traslado → Préstamo
8. Verificar que saldos sean positivos
9. Confirmar que dashboard muestre datos reales

---

## ARCHIVOS A MODIFICAR:

1. `app/blueprints/clientes.py` - Línea 35-45
2. `app/blueprints/finanzas.py` - Línea 234-237, 70-90
3. `app/routes.py` - Línea 52, 177-179
4. `app/services/caja_service.py` - Revisar lógica completa
5. Crear: `DIAMANTE_PRO/fix_saldos_negativos.py` (script migración)

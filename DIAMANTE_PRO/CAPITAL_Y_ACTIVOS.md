# 💰 Sistema de Capital y Activos - DIAMANTE PRO

## 📊 ¿Cómo funciona?

### 1. APORTES DE CAPITAL (Ejemplo: 3 socios aportan 10,000 reales c/u)

Los aportes de capital se registran para documentar las inversiones de los socios.

**Pasos para registrar:**

1. **Crear la Sociedad** (ya lo hiciste):
   - Ve a **Administración → Sociedades → Nueva Sociedad**
   - Registra los 3 socios con sus porcentajes
   - Ejemplo: Socio 1 (33.33%), Socio 2 (33.33%), Socio 3 (33.34%)

2. **Registrar cada Aporte** (próximamente en la interfaz):
   - Cada vez que un socio aporta dinero
   - Se registra: Nombre del socio, Monto, Fecha, Comprobante
   - Quedan registrados en la tabla `aportes_capital`

### 2. ACTIVOS FIJOS (Ejemplo: Compra de moto por 10,000 reales)

Los activos son bienes duraderos del negocio (vehículos, equipos, inmuebles).

**Pasos para registrar:**

1. **Registrar el Activo**:
   - Nombre: "Moto Honda Wave"
   - Categoría: VEHICULO
   - Valor: 10,000 reales
   - Placa/Serial: ABC-123
   - Asignado a: Cobrador X

2. **El activo queda registrado** y se puede:
   - Ver en el inventario de activos
   - Asignarlo a un cobrador específico
   - Asociarlo a una ruta
   - Vincular a una sociedad (si es de la sociedad) o marcarlo como PROPIO

## 💡 Ejemplo Práctico Completo

### Escenario: Sociedad de 3 socios

```
📝 PASO 1: Crear Sociedad
- Nombre: "Sociedad Reales Unidos"
- Socio 1: Juan (33.33%) - Tel: 3001111111
- Socio 2: María (33.33%) - Tel: 3002222222
- Socio 3: Pedro (33.34%) - Tel: 3003333333
- Dueño: 0% (todo es de los socios)

💵 PASO 2: Registrar Aportes
- Aporte 1: Juan - 10,000 reales - 15/12/2025
- Aporte 2: María - 10,000 reales - 15/12/2025
- Aporte 3: Pedro - 10,000 reales - 16/12/2025
TOTAL CAPITAL: 30,000 reales

🏍️ PASO 3: Comprar Moto
- Nombre: "Moto Honda Wave 110"
- Valor: 10,000 reales
- Placa: ABC-123
- Asignado a: Cobrador Santiago
- Sociedad: "Sociedad Reales Unidos"
- Estado: ACTIVO

💰 PASO 4: Capital Disponible
- Capital total: 30,000 reales
- Activos comprados: 10,000 reales  
- Capital disponible: 20,000 reales (para prestar)
```

## 📱 Cómo usar el sistema (Temporal - Mientras se crea la interfaz)

### Para registrar APORTES directamente en la base de datos:

```python
# Ejecuta en python
from app import create_app
from app.models import db, AporteCapital
from datetime import datetime

app = create_app()
with app.app_context():
    # Aporte Socio 1
    aporte1 = AporteCapital(
        sociedad_id=1,  # ID de tu sociedad
        nombre_aportante="Juan Pérez",
        monto=10000,
        moneda="BRL",  # Reales brasileños
        tipo_aporte="EFECTIVO",
        descripcion="Aporte inicial de capital",
        registrado_por_id=1  # ID del usuario admin
    )
    db.session.add(aporte1)
    
    # Repetir para los otros socios...
    
    db.session.commit()
    print("✅ Aportes registrados")
```

### Para registrar ACTIVOS directamente:

```python
from app import create_app
from app.models import db, Activo

app = create_app()
with app.app_context():
    moto = Activo(
        nombre="Moto Honda Wave 110",
        categoria="VEHICULO",
        descripcion="Moto para cobros",
        valor_compra=10000,
        moneda="BRL",
        sociedad_id=1,  # ID de la sociedad
        usuario_responsable_id=3,  # ID de santiago
        marca="Honda",
        modelo="Wave 110",
        placa_serial="ABC-123",
        estado="ACTIVO",
        notas="Comprada con capital de la sociedad",
        registrado_por_id=1  # ID del admin
    )
    db.session.add(moto)
    db.session.commit()
    print("✅ Activo registrado")
```

## 📊 Consultas Útiles

### Ver todos los aportes de una sociedad:

```python
from app import create_app
from app.models import AporteCapital

app = create_app()
with app.app_context():
    aportes = AporteCapital.query.filter_by(sociedad_id=1).all()
    total = sum(a.monto for a in aportes)
    print(f"Total aportado: {total}")
```

### Ver todos los activos:

```python
from app import create_app
from app.models import Activo

app = create_app()
with app.app_context():
    activos = Activo.query.filter_by(estado='ACTIVO').all()
    for activo in activos:
        print(f"{activo.nombre} - ${activo.valor_compra}")
```

## 🔜 Próximas Mejoras

Voy a crear las interfaces web para:
1. ✅ Ver lista de aportes por sociedad
2. ✅ Registrar nuevos aportes
3. ✅ Ver inventario de activos
4. ✅ Registrar nuevos activos
5. ✅ Generar reporte de capital vs activos
6. ✅ Dashboard financiero de cada sociedad

## 💡 Contabilidad Básica

```
ECUACIÓN CONTABLE:
Capital Social = Aportes - Activos - Gastos + Ganancias

Para tu caso:
- Aportes: 30,000 reales
- Activos: 10,000 reales (moto)
- Capital disponible: 20,000 reales
- Este capital se usa para dar préstamos
- Las ganancias de intereses aumentan el capital
```

¿Quieres que te cree un script rápido para registrar tus aportes y la moto ahora mismo?

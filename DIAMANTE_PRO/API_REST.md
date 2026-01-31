# 📱 API REST - DIAMANTE PRO

API REST para la aplicación móvil de cobradores. Todos los endpoints retornan JSON.

## 🔐 Autenticación

La API usa JWT (JSON Web Tokens) para autenticación. El token debe incluirse en todas las peticiones (excepto login).

### Login
```http
POST /api/v1/login
Content-Type: application/json

{
  "usuario": "cristian",
  "password": "1234"
}
```

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "usuario": {
    "id": 1,
    "nombre": "Cristian Vampi",
    "usuario": "cristian",
    "rol": "cobrador"
  }
}
```

**Errores:**
- `400`: Usuario y contraseña requeridos
- `401`: Credenciales inválidas o usuario inactivo

---

## 📍 Rutas del Cobrador

### Obtener Rutas Asignadas
```http
GET /api/v1/cobrador/rutas
Authorization: Bearer {token}
```

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "nombre": "Ruta Centro",
    "descripcion": "Zona comercial centro",
    "es_sociedad": false,
    "sociedad_nombre": null
  }
]
```

---

## 👥 Clientes

### Obtener Clientes con Préstamos Activos
```http
GET /api/v1/cobrador/clientes?ruta_id=1
Authorization: Bearer {token}
```

**Query Params:**
- `ruta_id` (opcional): Filtrar por ruta específica

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "documento": "12345678",
    "telefono": "3001234567",
    "whatsapp": "573001234567",
    "direccion_negocio": "Calle 10 #20-30",
    "gps_latitud": 4.6097,
    "gps_longitud": -74.0817,
    "es_vip": false
  }
]
```

---

## 💰 Préstamos

### Obtener Préstamos Activos
```http
GET /api/v1/cobrador/prestamos?ruta_id=1&cliente_id=1
Authorization: Bearer {token}
```

**Query Params:**
- `ruta_id` (opcional): Filtrar por ruta
- `cliente_id` (opcional): Filtrar por cliente

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "cliente": {
      "id": 1,
      "nombre": "Juan Pérez",
      "telefono": "3001234567",
      "whatsapp": "573001234567"
    },
    "monto_prestado": 5000000,
    "monto_a_pagar": 6000000,
    "saldo_actual": 4200000,
    "valor_cuota": 120000,
    "moneda": "COP",
    "frecuencia": "DIARIO",
    "numero_cuotas": 50,
    "cuotas_pagadas": 15,
    "cuotas_atrasadas": 2,
    "fecha_inicio": "2025-01-01T00:00:00",
    "fecha_ultimo_pago": "2025-01-15T10:30:00",
    "estado": "ACTIVO"
  }
]
```

---

## 🚗 Ruta de Cobro Diaria

### Obtener Lista de Cobros del Día
Retorna todos los préstamos que deben cobrar hoy y **no han pagado aún**.

```http
GET /api/v1/cobrador/ruta-cobro?ruta_id=1
Authorization: Bearer {token}
```

**Query Params:**
- `ruta_id` (opcional): Filtrar por ruta

**Respuesta (200):**
```json
{
  "total_cobros": 15,
  "total_a_cobrar": 1800000,
  "cobros": [
    {
      "prestamo_id": 1,
      "cliente": {
        "id": 1,
        "nombre": "Juan Pérez",
        "telefono": "3001234567",
        "whatsapp": "573001234567",
        "direccion": "Calle 10 #20-30",
        "gps_latitud": 4.6097,
        "gps_longitud": -74.0817
      },
      "valor_cuota": 120000,
      "saldo_actual": 4200000,
      "moneda": "COP",
      "cuotas_atrasadas": 2,
      "estado_mora": "LEVE"
    }
  ]
}
```

**Estados de mora:**
- `AL_DIA`: 0 cuotas atrasadas
- `LEVE`: 1-3 cuotas atrasadas
- `GRAVE`: 4+ cuotas atrasadas

---

## 💵 Registrar Pago

### Registrar un Pago desde la App
```http
POST /api/v1/cobrador/registrar-pago
Authorization: Bearer {token}
Content-Type: application/json

{
  "prestamo_id": 1,
  "monto": 120000,
  "observaciones": "Pago completo"
}
```

**Body:**
- `prestamo_id` (requerido): ID del préstamo
- `monto` (requerido): Monto del pago
- `observaciones` (opcional): Notas adicionales

**Respuesta exitosa (201):**
```json
{
  "success": true,
  "pago_id": 42,
  "monto_pagado": 120000,
  "saldo_anterior": 4200000,
  "saldo_nuevo": 4080000,
  "cuotas_pagadas": 1,
  "prestamo_liquidado": false,
  "fecha_pago": "2025-12-16T14:30:00"
}
```

**Errores:**
- `400`: Faltan parámetros requeridos
- `403`: No tienes permiso para cobrar este préstamo
- `404`: Préstamo no encontrado
- `500`: Error al guardar en base de datos

---

## 📊 Estadísticas

### Obtener Estadísticas del Cobrador
```http
GET /api/v1/cobrador/estadisticas?ruta_id=1
Authorization: Bearer {token}
```

**Query Params:**
- `ruta_id` (opcional): Filtrar por ruta

**Respuesta (200):**
```json
{
  "total_prestamos": 25,
  "total_cartera": 52000000,
  "cobrado_hoy": 1440000,
  "numero_cobros_hoy": 12,
  "por_cobrar_hoy": 1800000,
  "prestamos_al_dia": 18,
  "prestamos_atrasados": 7,
  "prestamos_mora_grave": 2
}
```

---

## 🔒 Seguridad

### Headers Requeridos
Todas las peticiones (excepto login) deben incluir:
```
Authorization: Bearer {token}
Content-Type: application/json
```

### Tokens JWT
- Duración: 30 días
- Se debe incluir en header Authorization
- Formato: `Bearer {token}`

### Permisos
- Solo cobradores pueden acceder a `/api/v1/cobrador/*`
- Solo pueden ver/cobrar préstamos de sus rutas asignadas

---

## 🌍 Base URL

**Desarrollo:** `http://localhost:5000/api/v1`

**Producción:** `https://diamante-pro.herokuapp.com/api/v1` (por configurar)

---

## 📱 Flujo de la App Móvil

### 1. **Login** → Guardar token localmente
```
POST /api/v1/login
↓
Guardar access_token en AsyncStorage/SecureStore
```

### 2. **Cargar Rutas** → Seleccionar ruta activa
```
GET /api/v1/cobrador/rutas
↓
Mostrar selector de rutas (si tiene múltiples)
```

### 3. **Ver Ruta de Cobro** → Lista de clientes a cobrar hoy
```
GET /api/v1/cobrador/ruta-cobro?ruta_id={id}
↓
Mostrar lista ordenada por GPS/prioridad
```

### 4. **Registrar Pago** → Actualizar en tiempo real
```
POST /api/v1/cobrador/registrar-pago
↓
Actualizar lista local
↓
Mostrar confirmación con recibo
```

### 5. **Ver Estadísticas** → Dashboard del cobrador
```
GET /api/v1/cobrador/estadisticas
↓
Mostrar gráficos de rendimiento
```

---

## ⚙️ Instalación (Para Desarrollo)

### 1. Instalar dependencias
```bash
pip install flask-jwt-extended flask-cors
```

### 2. Ejecutar servidor
```bash
python run.py
```

### 3. Probar API
```bash
python test_api.py
```

---

## 🧪 Testing

Usar el script `test_api.py` para probar todos los endpoints:

```bash
python test_api.py
```

O usar herramientas como:
- **Postman**: Importar colección desde `api_collection.json`
- **curl**: Ver ejemplos en `api_examples.sh`
- **Insomnia**: Importar workspace

---

## 🚀 Próximos Pasos

- [ ] Implementar refresh tokens
- [ ] Agregar paginación en listas grandes
- [ ] Sincronización offline (store & forward)
- [ ] Webhooks para notificaciones
- [ ] Geolocalización en tiempo real
- [ ] Fotos de comprobantes
- [ ] Firma digital del cliente

---

## 📞 Soporte

Para dudas sobre la API, contactar a:
- **Email**: graciano90210@gmail.com
- **GitHub**: https://github.com/graciano90210/DIAMANTE-PRO

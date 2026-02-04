<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.0+-green?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15+-blue?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Heroku-Deployed-purple?style=for-the-badge&logo=heroku&logoColor=white" alt="Heroku"/>
</p>

<h1 align="center">💎 DIAMANTE PRO</h1>

<p align="center">
  <strong>Sistema Integral de Gestión de Préstamos y Cobranzas</strong><br>
  Plataforma web profesional para administración de microcréditos
</p>

<p align="center">
  <a href="#características">Características</a> •
  <a href="#tecnologías">Tecnologías</a> •
  <a href="#instalación">Instalación</a> •
  <a href="#uso">Uso</a> •
  <a href="#api">API</a> •
  <a href="#estructura">Estructura</a>
</p>

---

## 📋 Descripción

**Diamante Pro** es un sistema completo de gestión financiera diseñado para empresas de microcréditos y préstamos. Permite administrar clientes, préstamos, cobros, rutas de cobranza, sociedades y generar reportes detallados.

### ✨ Características Principales

| Módulo | Funcionalidades |
|--------|-----------------|
| 👥 **Clientes** | Registro completo, scoring crediticio, historial de préstamos |
| 💰 **Préstamos** | Creación, cálculo automático de intereses, múltiples frecuencias de pago |
| 📱 **Cobros** | Registro de pagos, recibos digitales, envío por WhatsApp |
| 🛣️ **Rutas** | Organización por zonas, asignación de cobradores |
| 🏢 **Oficinas** | Agrupación de rutas por zona/región, metas de cobro y préstamos |
| 🤝 **Sociedades** | Inversores ilimitados (Many-to-Many), distribución de porcentajes |
| 👥 **Socios** | Gestión de múltiples inversores por sociedad con porcentajes |
| 💼 **Finanzas** | Control de capital, activos, caja y gastos |
| 📊 **Reportes** | Dashboard en tiempo real, estadísticas, gráficos |

---

## 🏗️ Arquitectura

### Capa de Servicios (Services Layer)

El proyecto implementa una **arquitectura en capas** con servicios dedicados:

| Servicio | Responsabilidad |
|----------|-----------------|
| `DashboardService` | Estadísticas y métricas del dashboard |
| `PrestamoService` | Lógica de negocio de préstamos |
| `ClienteService` | Operaciones con clientes |
| `SociedadService` | Gestión de sociedades y socios |
| `OficinaService` | CRUD y estadísticas de oficinas |
| `ReporteService` | Generación de reportes |

---

## 🛠️ Tecnologías

### Backend
- **Python 3.10+** - Lenguaje principal
- **Flask 3.0** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos en producción
- **SQLite** - Base de datos en desarrollo

### Frontend
- **HTML5 / CSS3** - Estructura y estilos
- **Bootstrap 5** - Framework CSS responsive
- **JavaScript** - Interactividad
- **Chart.js** - Gráficos y estadísticas

### Despliegue
- **Heroku** - Hosting en la nube
- **Gunicorn** - Servidor WSGI
- **Git** - Control de versiones

---

## 🚀 Instalación

### Requisitos Previos
- Python 3.10 o superior
- pip (gestor de paquetes)
- Git

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/graciano90210/DIAMANTE-PRO.git
cd DIAMANTE-PRO

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 6. Inicializar base de datos
python crear_admin.py

# 7. Ejecutar aplicación
python run.py
```

La aplicación estará disponible en `http://127.0.0.1:5001`

---

## 📖 Uso

### Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **Dueño** | Acceso total al sistema |
| **Gerente** | Gestión completa excepto configuraciones críticas |
| **Secretaria** | Registro de clientes y préstamos |
| **Cobrador** | Registro de cobros, vista de sus clientes asignados |

### Credenciales por Defecto
```
Usuario: admin
Contraseña: admin123
```

> ⚠️ **Importante:** Cambiar las credenciales después del primer inicio de sesión.

---

## 🔌 API REST

### Endpoints Principales

```
GET  /estado              - Estado del servidor
GET  /clientes/           - Lista de clientes
POST /clientes/guardar    - Crear cliente
GET  /prestamos/          - Lista de préstamos
POST /prestamos/guardar   - Crear préstamo
POST /cobro/guardar       - Registrar pago
GET  /reportes            - Dashboard de reportes
GET  /oficinas/           - Lista de oficinas
POST /oficinas/guardar    - Crear oficina
GET  /sociedades/         - Lista de sociedades
GET  /sociedades/<id>/socios - Gestionar socios
```

### Ejemplo de Respuesta
```json
{
  "estado": "OK",
  "version": "1.0"
}
```

---

## 📁 Estructura del Proyecto

```
DIAMANTE_PRO/
├── app/
│   ├── blueprints/          # Módulos organizados (11 blueprints)
│   │   ├── __init__.py      # Registro de blueprints
│   │   ├── auth.py          # Autenticación (login/logout)
│   │   ├── clientes.py      # CRUD de clientes
│   │   ├── prestamos.py     # Gestión de préstamos
│   │   ├── cobros.py        # Registro de pagos
│   │   ├── rutas.py         # Rutas de cobranza
│   │   ├── oficinas.py      # Gestión de oficinas (NUEVO)
│   │   ├── sociedades.py    # Gestión de socios
│   │   ├── finanzas.py      # Capital, caja, gastos
│   │   └── reportes.py      # Dashboard y estadísticas
│   ├── services/            # Capa de servicios (NUEVO)
│   │   ├── __init__.py
│   │   ├── dashboard_service.py
│   │   ├── prestamo_service.py
│   │   ├── cliente_service.py
│   │   ├── sociedad_service.py
│   │   ├── oficina_service.py
│   │   └── reporte_service.py
│   ├── utils/               # Utilidades
│   │   └── pagination.py    # Paginación optimizada
│   ├── templates/           # Plantillas HTML (Jinja2)
│   ├── static/              # CSS, JS, imágenes
│   ├── models.py            # Modelos SQLAlchemy (Oficina, Socio, etc.)
│   ├── extensions.py        # Extensiones Flask
│   ├── routes_clean.py      # Rutas principales refactorizadas
│   └── __init__.py          # Application Factory
├── migrations/              # Scripts de migración
│   ├── add_performance_indexes.py
│   └── migrate_socios.py
├── instance/                # Base de datos SQLite local
├── requirements.txt         # Dependencias Python
├── Procfile                 # Configuración Heroku
├── run.py                   # Punto de entrada
├── check_db.py              # Verificación de esquema BD
├── run_migrations.py        # Ejecutar migraciones
├── SECURITY.md              # Guía de seguridad
├── .env.example             # Plantilla de variables
└── README.md
```

### Arquitectura Modular

El proyecto utiliza el patrón **Blueprint** de Flask para organizar el código:

| Blueprint | Rutas | Responsabilidad |
|-----------|-------|-----------------|
| `auth` | `/login`, `/logout` | Autenticación |
| `clientes` | `/clientes/*` | CRUD clientes |
| `prestamos` | `/prestamos/*` | Gestión préstamos |
| `cobros` | `/cobro/*` | Registro pagos |
| `rutas` | `/rutas/*` | Rutas cobranza |
| `oficinas` | `/oficinas/*` | Gestión de oficinas |
| `sociedades` | `/sociedades/*` | Socios e inversores |
| `finanzas` | `/capital/*`, `/caja/*` | Finanzas |
| `reportes` | `/reportes/*` | Estadísticas |

---

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Flask | `tu-clave-secreta-aqui` |
| `DATABASE_URL` | URL de conexión a BD | `postgresql://user:pass@host/db` |
| `FLASK_ENV` | Entorno de ejecución | `production` / `development` |

### Configuración de Producción (Heroku)

```bash
# Configurar variables obligatorias
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FLASK_ENV=production

# Servicios opcionales
heroku config:set SENDGRID_API_KEY=SG.xxxxx
heroku config:set SENTRY_DSN=https://xxx@sentry.io/xxx

# Desplegar
git push heroku master
```

---

## 🔐 Seguridad

### Variables de Entorno Sensibles

| Variable | Descripción | Obligatorio |
|----------|-------------|-------------|
| `SECRET_KEY` | Clave secreta Flask (32+ caracteres) | ✅ Sí |
| `JWT_SECRET_KEY` | Clave para tokens JWT móvil | ✅ Sí |
| `SENDGRID_API_KEY` | API key para emails | ❌ Opcional |
| `SENTRY_DSN` | Monitoreo de errores | ❌ Opcional |
| `AWS_ACCESS_KEY_ID` | Almacenamiento S3 | ❌ Opcional |

### Generar Claves Seguras

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Archivos de Configuración

- `.env` - Credenciales locales (⚠️ NO subir a Git)
- `.env.example` - Plantilla sin valores reales
- `SECURITY.md` - Guía completa de seguridad y rotación de keys

---

## 📊 Características Detalladas

### Dashboard
- Vista general de estadísticas en tiempo real
- Gráficos de cobros diarios (últimos 7 días)
- Indicadores de préstamos activos, atrasados y en mora
- Proyección de cobros para el día siguiente
- **Acciones rápidas** para gestión ágil

### 🏢 Gestión de Oficinas (NUEVO)
- Crear oficinas para agrupar rutas por zona o región
- Estadísticas por oficina: rutas, cartera, cobros del día
- Asignar/desasignar rutas a oficinas
- Metas de cobro diario y préstamos mensuales
- Responsable asignado por oficina
- Vista de rutas sin oficina para organización

### 🤝 Sociedades e Inversores (MEJORADO)
- **Modelo Many-to-Many**: Inversores ilimitados por sociedad
- Distribución de porcentajes entre múltiples socios
- Migración automática de socios legacy
- Fechas de ingreso y salida de inversores
- Estado activo/inactivo de socios

### Gestión de Préstamos
- Múltiples frecuencias de pago: Diario, Semanal, Quincenal, Mensual
- Cálculo automático de intereses y cuotas
- Generación de comprobantes con imagen para WhatsApp
- Control de cuotas atrasadas

### Registro de Cobros
- Lista de cobros pendientes del día
- Registro rápido con validación de duplicados
- Generación de recibos digitales
- Integración con WhatsApp para envío de comprobantes

### Control Financiero
- Registro de aportes de capital por sociedad
- Control de activos fijos
- Gestión de caja (ingresos/egresos)
- Traslados entre usuarios

---

## 🗄️ Modelos de Datos

### Modelos Principales

| Modelo | Descripción |
|--------|-------------|
| `Usuario` | Usuarios del sistema (dueño, gerente, secretaria, cobrador) |
| `Cliente` | Clientes con scoring crediticio |
| `Prestamo` | Préstamos con cuotas y estado |
| `Cobro` | Pagos registrados |
| `Ruta` | Rutas de cobranza |
| `Oficina` | Agrupación de rutas por zona **(NUEVO)** |
| `Sociedad` | Sociedades de inversión |
| `Socio` | Inversores con porcentaje **(NUEVO - Many-to-Many)** |
| `Capital` | Aportes de capital |
| `Activo` | Activos fijos |
| `Caja` | Movimientos de caja |

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abrir Pull Request

---

## 📄 Licencia

Este proyecto es de uso privado. Todos los derechos reservados.

---

## 👨‍💻 Autor

**Diamante Pro Team**

---

<p align="center">
  <strong>💎 Diamante Pro - Sistema de Gestión de Préstamos</strong><br>
  <sub>Desarrollado con ❤️ en Python + Flask</sub>
</p>

# 💎 DIAMANTE PRO - Sistema de Préstamos y Cobros

Sistema completo de gestión de préstamos con API REST para aplicación móvil.

---
## Diamante Pro

**Sistema de gestión de créditos con predicción de riesgo.**

### Tecnologías principales
- Python
- SQL (PostgreSQL, SQLite)
- Docker
- Flask
- Heroku
- API REST

---

## 🚀 Despliegue en Heroku

### Paso 1: Crear cuenta y aplicación en Heroku

1. Registrarse en [Heroku](https://heroku.com) con GitHub Student Pack
2. Instalar [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Iniciar sesión:
```bash
heroku login
```

### Paso 2: Crear aplicación

```bash
heroku create diamante-pro
```

<!-- Prueba de deploy GitHub Actions 2025-12-22 -->

### Paso 3: Configurar Base de Datos PostgreSQL

```bash
heroku addons:create heroku-postgresql:essential-0
```

### Paso 4: Configurar variables de entorno

```bash
heroku config:set SECRET_KEY="tu-clave-secreta-muy-segura"
heroku config:set JWT_SECRET_KEY="tu-jwt-secret-muy-segura"
```

### Paso 5: Desplegar

```bash
git push heroku main
```

### Paso 6: Inicializar base de datos

```bash
heroku run python crear_admin.py
```

## 🌍 Configurar Dominio Personalizado

### En Heroku:
```bash
heroku domains:add www.diamantepro.me
heroku domains:add diamantepro.me
```

### En Namecheap (diamantepro.me):

1. Ir a **Advanced DNS**
2. Agregar registros CNAME:

| Type  | Host | Value                          | TTL  |
|-------|------|--------------------------------|------|
| CNAME | www  | diamante-pro.herokuapp.com     | Auto |
| CNAME | @    | diamante-pro.herokuapp.com     | Auto |

3. Esperar propagación DNS (5-30 minutos)

### Habilitar HTTPS:
```bash
heroku certs:auto:enable
```

## 📱 API REST

### URL Base:
- **Local**: `http://localhost:5001/api/v1`
- **Producción**: `https://diamantepro.me/api/v1`

### Endpoints disponibles:
- `POST /api/v1/login` - Autenticación
- `GET /api/v1/cobrador/rutas` - Rutas del cobrador
- `GET /api/v1/cobrador/clientes` - Clientes activos
- `GET /api/v1/cobrador/prestamos` - Préstamos activos
- `GET /api/v1/cobrador/ruta-cobro` - Ruta de cobro diaria
- `POST /api/v1/cobrador/registrar-pago` - Registrar pago
- `GET /api/v1/cobrador/estadisticas` - Estadísticas

Ver documentación completa en [API_REST.md](API_REST.md)

## 💻 Desarrollo Local

### 1. Clonar repositorio
```bash
git clone https://github.com/graciano90210/DIAMANTE-PRO.git
cd DIAMANTE-PRO
```

### 2. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Inicializar base de datos
```bash
python recrear_bd.py
python crear_admin.py
```

### 5. Ejecutar servidor
```bash
python run.py
```

Abrir: http://localhost:5001

## 🔧 Comandos Útiles

### Ver logs en producción:
```bash
heroku logs --tail
```

### Acceder a consola Python en producción:
```bash
heroku run python
```

### Backup de base de datos:
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

### Reiniciar aplicación:
```bash
heroku restart
```

## 📊 Monitoreo

### Heroku Dashboard:
https://dashboard.heroku.com/apps/diamante-pro

### Métricas:
- Uptime
- Response time
- Throughput
- Memory usage

## 🔐 Seguridad

- ✅ HTTPS automático
- ✅ JWT para autenticación API
- ✅ Contraseñas cifradas (próximamente)
- ✅ CORS configurado
- ✅ Variables de entorno seguras

## 🎯 Próximos Pasos

- [x] Implementar encriptación de contraseñas (bcrypt)
- [x] Agregar tests automatizados
- [x] Implementar CI/CD con GitHub Actions
- [x] Agregar monitoreo con Sentry
- [ ] Implementar cache con Redis
- [ ] Crear documentación Swagger/OpenAPI

## 🎓 GitHub Student Pack Implementado

Este proyecto usa herramientas GRATUITAS del GitHub Student Pack:

| Herramienta | Beneficio | Estado |
|-------------|-----------|--------|
| **GitHub Actions** | CI/CD ilimitado | ✅ Configurado |
| **Sentry** | 100k eventos/mes | ✅ Integrado |
| **SendGrid** | 100 emails/día | ✅ Integrado |
| **Heroku** | $13 créditos/mes | ✅ Activo |
| **Namecheap** | Dominio gratis 1 año | ✅ diamantepro.me |

📖 **[Ver guía completa de configuración →](GITHUB_STUDENT_PACK.md)**

## 📞 Soporte

- **Email**: graciano90210@gmail.com
- **GitHub**: https://github.com/graciano90210
- **Dominio**: https://diamantepro.me

---

Desarrollado con ❤️ para gestión profesional de préstamos

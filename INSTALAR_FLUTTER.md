# 🚀 Instalar Flutter - Guía Rápida

## ✅ Opción 1: Descarga Directa (MÁS RÁPIDA - 5 minutos)

### Paso 1: Descargar Flutter
1. Ve a: https://docs.flutter.dev/get-started/install/windows
2. Click en **"Download Flutter SDK"**
3. O descarga directo: https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.27.1-stable.zip

### Paso 2: Extraer
```powershell
# Extrae el ZIP a:
C:\src\flutter
```

### Paso 3: Agregar al PATH
```powershell
# En PowerShell COMO ADMINISTRADOR:

# Opción A: Variable de Usuario (recomendado)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\src\flutter\bin", "User")

# Opción B: Variable de Sistema (requiere admin)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\src\flutter\bin", "Machine")

# Refrescar PATH en sesión actual
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Paso 4: Verificar
```powershell
# Cierra y abre nueva terminal
flutter --version
flutter doctor
```

---

## ✅ Opción 2: Con Chocolatey (si ya lo instalaste)

```powershell
# Cerrar y abrir terminal como ADMINISTRADOR, luego:
choco install flutter -y

# Verificar
flutter --version
```

---

## ✅ Opción 3: Con winget (Windows 11)

```powershell
winget install --id=9NRWMJP3717K -e
```

---

## 📋 COMANDOS DESPUÉS DE INSTALAR

### 1. Verificar instalación
```powershell
cd "C:\Proyectodiamantepro\DIAMANTE PRO\mobile-app"
flutter doctor
```

### 2. Instalar dependencias de la app
```powershell
flutter pub get
```

### 3. Ver dispositivos disponibles
```powershell
flutter devices
```

### 4. Ejecutar en Chrome (más fácil)
```powershell
flutter run -d chrome
```

### 5. Ejecutar en Edge
```powershell
flutter run -d edge
```

---

## 🐛 Solución de Problemas

### Error: "cmdline-tools component is missing"
```bash
flutter doctor --android-licenses
```

### Error: "Chrome not found"
Solo necesario si quieres probar en navegador. La app está pensada para móvil.

### Error: "Visual Studio not found"
No es necesario para desarrollo básico. Ignóralo por ahora.

---

## ⚡ RUTA RÁPIDA (Sin instalaciones extra)

Si solo quieres **probar la app YA**:

1. **Descarga Flutter:** https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.27.1-stable.zip

2. **Extrae a:** `C:\flutter`

3. **Ejecuta esto en PowerShell:**
```powershell
$env:Path += ";C:\flutter\bin"
cd "C:\Proyectodiamantepro\DIAMANTE PRO\mobile-app"
flutter pub get
flutter run -d chrome
```

4. **Listo!** La app se abrirá en Chrome

---

## 🎯 ¿Qué hacer mientras se instala?

### Opcional: Instalar Android Studio (para emular Android)
1. Descargar: https://developer.android.com/studio
2. Instalar
3. Abrir → Tools → SDK Manager
4. Install Android SDK

**PERO NO ES NECESARIO AHORA** - Puedes probar en Chrome primero.

---

## 📱 Probar en tu Celular Android (SIN Android Studio)

### 1. Habilitar USB Debugging en tu celular
- Ajustes → Acerca del teléfono → Tocar "Número de compilación" 7 veces
- Ajustes → Opciones de desarrollador → USB Debugging → ON

### 2. Conectar por USB
```bash
flutter devices
# Debería aparecer tu celular
```

### 3. Ejecutar
```bash
flutter run
```

---

## ✨ Resumen

**Tiempo estimado:**
- Descarga: 2-3 minutos
- Extracción: 1 minuto
- Configurar PATH: 30 segundos
- Instalar dependencias: 1 minuto
- **TOTAL: ~5 minutos**

**¿Listo para empezar?** 🚀

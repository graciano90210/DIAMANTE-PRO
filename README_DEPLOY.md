# Guía de Despliegue y Generación de APK

## 1. Configuración de Entorno
El archivo `lib/config/api_config.dart` ha sido configurado para **Producción** (Heroku).
- URL Base: `https://diamante-pro-1951dcdb66df.herokuapp.com/api/v1`

## 2. Generar APK para Android
Debido a que el proceso de construcción puede tomar varios minutos, ejecuta el siguiente comando en tu terminal:

```powershell
cd "C:\Proyectodiamantepro\DIAMANTE PRO\mobile-app"
flutter build apk --release
```

**Ubicación del archivo generado:**
`build/app/outputs/flutter-apk/app-release.apk`

## 3. Instalación
1. Copia el archivo `app-release.apk` a tu dispositivo Android (vía USB, Drive, WhatsApp, etc.).
2. Abre el archivo y selecciona "Instalar".
3. Asegúrate de tener activa la opción "Instalar de fuentes desconocidas".

## 4. Notas de la Versión
- **Sincronización Offline**: Los cobros se guardan localmente si no hay internet y se sincronizan al recuperar conexión (Dashboard).
- **Base de Datos**: Se utiliza SQLite localmente. La estructura se actualiza automáticamente.
- **Roles**: Esta APK está optimizada para el rol de **Cobrador**.

## 5. Solución de Problemas
Si la app no conecta:
- Verifica que el servidor en Heroku esté corriendo (`heroku ps`).
- Verifica que el dispositivo tenga internet.
- Si usas entorno local, recuerda cambiar la IP en `api_config.dart`.

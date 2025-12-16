# Diamante PRO - Aplicación Móvil

Aplicación móvil para el sistema Diamante PRO, desarrollada con Flutter para Android y iOS.

## 🚀 Requisitos Previos

- Flutter SDK (versión 3.0.0 o superior)
- Dart SDK
- Android Studio (para desarrollo Android)
- Xcode (para desarrollo iOS, solo en Mac)

## 📦 Instalación

### 1. Instalar Flutter

Si aún no tienes Flutter instalado:

**Windows:**
```bash
# Descarga Flutter desde https://docs.flutter.dev/get-started/install/windows
# Extrae el archivo ZIP y agrega el directorio flutter\bin a tu PATH
```

**macOS/Linux:**
```bash
# Descarga Flutter desde https://docs.flutter.dev/get-started/install
# Extrae y agrega a PATH
```

Verifica la instalación:
```bash
flutter doctor
```

### 2. Instalar Dependencias del Proyecto

```bash
flutter pub get
```

## ⚙️ Configuración

### Configurar la URL del Backend

Edita el archivo `lib/config/api_config.dart` y actualiza la URL de tu backend en Heroku:

```dart
static const String baseUrl = 'https://tu-app-heroku.herokuapp.com/api';
```

## 🏃‍♂️ Ejecutar la Aplicación

### En un emulador/simulador:
```bash
flutter run
```

### En un dispositivo físico:
1. Conecta tu dispositivo por USB
2. Habilita la depuración USB (Android) o confía en la computadora (iOS)
3. Ejecuta:
```bash
flutter run
```

### Modo release:
```bash
flutter run --release
```

## 📁 Estructura del Proyecto

```
lib/
├── main.dart              # Punto de entrada de la app
├── config/
│   └── api_config.dart    # Configuración de la API
├── models/
│   └── user_model.dart    # Modelos de datos
├── screens/
│   └── home_screen.dart   # Pantallas de la app
├── services/
│   └── api_service.dart   # Servicio para peticiones HTTP
└── widgets/
    └── loading_widget.dart # Widgets reutilizables
```

## 🔧 Dependencias Principales

- **provider**: Gestión de estado
- **http**: Peticiones HTTP a la API
- **shared_preferences**: Almacenamiento local

## 🌐 Conexión con el Backend

El proyecto está configurado para conectarse a tu API Flask en Heroku. Los métodos disponibles son:

- `GET`: Para obtener datos
- `POST`: Para crear recursos
- `PUT`: Para actualizar recursos
- `DELETE`: Para eliminar recursos

Ejemplo de uso:
```dart
final apiService = context.read<ApiService>();
final data = await apiService.get('/endpoint');
```

## 📱 Construcción para Producción

### Android:
```bash
flutter build apk --release
# o para App Bundle
flutter build appbundle --release
```

### iOS:
```bash
flutter build ios --release
```

## 🐛 Solución de Problemas

- **Flutter no reconocido**: Asegúrate de que Flutter esté en tu PATH
- **Dependencias no instaladas**: Ejecuta `flutter pub get`
- **Error de conexión a la API**: Verifica la URL en `api_config.dart`

## 📝 Notas

- Recuerda actualizar la URL del backend en `lib/config/api_config.dart`
- Para producción, considera agregar manejo de autenticación y tokens
- Implementa caché local para mejorar la experiencia sin conexión

## 🤝 Soporte

Para más información sobre Flutter:
- [Documentación oficial](https://docs.flutter.dev/)
- [Cookbook de Flutter](https://docs.flutter.dev/cookbook)

# 📱 Tareas Pendientes - App Móvil Diamante PRO

## ✅ Lo que YA tienes Funcionando

- ✅ Estructura base de Flutter con Provider
- ✅ Pantalla de Login con validaciones
- ✅ Dashboard con estadísticas
- ✅ Lista de clientes con búsqueda
- ✅ Lista de préstamos
- ✅ Pantalla de registro de cobros
- ✅ Servicio de API configurado
- ✅ Autenticación con JWT
- ✅ Configuración correcta del backend

## 🚧 Lo que FALTA para que Funcione 100%

### 1. **CRÍTICO: Arreglar endpoints de la API** 🔴

**Problema:** La app llama a endpoints que no existen o están mal configurados.

#### Endpoints que necesitas:
```dart
// En api_service.dart, cambiar las rutas:
'/clientes'          → '/api/v1/cobrador/clientes'
'/prestamos'         → '/api/v1/cobrador/prestamos'
'/cobros'            → '/api/v1/cobrador/registrar-pago'
'/dashboard'         → '/api/v1/cobrador/estadisticas'
```

**Archivos a modificar:**
- `lib/screens/clientes_screen.dart` (línea ~32)
- `lib/screens/prestamos_screen.dart` 
- `lib/screens/cobros_screen.dart` (línea ~42 y ~85)
- `lib/screens/dashboard_screen.dart` (línea ~29)

---

### 2. **Completar los Modelos** 🔴

Faltan campos en los modelos para que coincidan con la API:

#### `lib/models/user_model.dart`
```dart
class User {
  final int id;
  final String name;
  final String username;
  final String? email;
  final String rol;

  User({
    required this.id,
    required this.name,
    required this.username,
    this.email,
    required this.rol,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['nombre'],
      username: json['usuario'],
      email: json['email'],
      rol: json['rol'],
    );
  }
}
```

#### `lib/models/prestamo_model.dart`
Agregar campos faltantes:
- `cuotasPagadas`
- `cuotasAtrasadas`
- `fechaUltimoPago`
- `diasAtraso`

#### `lib/models/cliente_model.dart`
Agregar:
- `whatsapp`
- `gpsLatitud`
- `gpsLongitud`
- `esVip`

---

### 3. **Arreglar AuthService** 🟡

El archivo `lib/services/auth_service.dart` necesita:

```dart
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';
import '../models/user_model.dart';

class AuthService {
  final ApiService _apiService;
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';

  AuthService(this._apiService);

  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await _apiService.post(
      '/api/v1/login',
      body: {
        'usuario': username,
        'password': password,
      },
    );

    // Guardar token y usuario
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, response['access_token']);
    await prefs.setString(_userKey, json.encode(response['usuario']));

    return response;
  }

  Future<User?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userData = prefs.getString(_userKey);
    
    if (userData == null) return null;
    
    return User.fromJson(json.decode(userData));
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<Map<String, String>> getAuthHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
  }

  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null;
  }
}
```

---

### 4. **Arreglar AuthProvider** 🟡

El archivo `lib/providers/auth_provider.dart` necesita:

```dart
import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService;
  
  User? _currentUser;
  bool _isLoading = false;
  String? _errorMessage;

  User? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  AuthProvider(this._authService);

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _authService.login(username, password);
      _currentUser = User.fromJson(response['usuario']);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> checkSession() async {
    try {
      final user = await _authService.getCurrentUser();
      if (user != null) {
        _currentUser = user;
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _currentUser = null;
    notifyListeners();
  }
}
```

---

### 5. **Funcionalidades Pendientes** 🟢

#### A. **Pantalla de Ruta de Cobro Diaria**
Crear `lib/screens/ruta_cobro_screen.dart`:
- Lista de clientes ordenados por proximidad
- Mapa con ubicaciones (Google Maps)
- Marcar como "visitado"
- Navegación GPS

#### B. **Registrar Pago Offline**
- Guardar pagos localmente cuando no hay internet
- Sincronizar automáticamente cuando vuelva la conexión
- Usar `sqflite` para BD local

#### C. **Cámara para Evidencias**
- Tomar foto del recibo
- Adjuntar a cada cobro
- Subir fotos al servidor

#### D. **Notificaciones Push**
- Alertas de cobros pendientes
- Recordatorios diarios
- Usar `firebase_messaging`

#### E. **Geolocalización**
- Registrar ubicación al cobrar
- Validar que esté cerca del cliente
- Usar `geolocator`

---

## 🎯 Plan de Acción (4-5 días)

### **Día 1: Arreglar lo Básico**
1. ✅ Corregir endpoints en todas las pantallas
2. ✅ Completar modelos (User, Prestamo, Cliente)
3. ✅ Arreglar AuthService y AuthProvider
4. ✅ Probar login y ver dashboard

### **Día 2: Completar Funcionalidades Core**
1. ✅ Terminar pantalla de cobros
2. ✅ Agregar validaciones
3. ✅ Mejorar UX/UI
4. ✅ Agregar loading states

### **Día 3: Ruta de Cobro**
1. 🔨 Crear pantalla de ruta diaria
2. 🔨 Integrar mapa
3. 🔨 Agregar navegación GPS

### **Día 4: Modo Offline**
1. 🔨 Implementar BD local (sqflite)
2. 🔨 Sincronización automática
3. 🔨 Manejo de conflictos

### **Día 5: Extras**
1. 🔨 Cámara para fotos
2. 🔨 Geolocalización
3. 🔨 Notificaciones push
4. 🔨 Testing y bugs

---

## 📦 Dependencias Adicionales Necesarias

Agregar a `pubspec.yaml`:

```yaml
dependencies:
  # Ya tienes:
  provider: ^6.1.1
  http: ^1.1.2
  shared_preferences: ^2.2.2
  
  # AGREGAR:
  sqflite: ^2.3.0              # Base de datos local
  path_provider: ^2.1.1        # Rutas del sistema
  image_picker: ^1.0.4         # Cámara y galería
  geolocator: ^10.1.0          # GPS
  google_maps_flutter: ^2.5.0 # Mapas
  firebase_messaging: ^14.7.6  # Push notifications
  connectivity_plus: ^5.0.2    # Detectar internet
  intl: ^0.18.1               # Formato de fechas
```

---

## 🚀 Comando para Instalar Dependencias

```bash
cd "C:\Proyectodiamantepro\DIAMANTE PRO\mobile-app"
flutter pub get
```

---

## 🧪 Probar la App

```bash
# Ver dispositivos disponibles
flutter devices

# Ejecutar en Android
flutter run

# Ejecutar en modo debug con hot reload
flutter run --debug
```

---

## 📝 Notas Importantes

1. **URL del Backend:** Ya está correcta: `https://diamante-pro-1951dcdb66df.herokuapp.com`

2. **Endpoints Disponibles:**
   - `POST /api/v1/login`
   - `GET /api/v1/cobrador/rutas`
   - `GET /api/v1/cobrador/clientes`
   - `GET /api/v1/cobrador/prestamos`
   - `GET /api/v1/cobrador/ruta-cobro`
   - `POST /api/v1/cobrador/registrar-pago`
   - `GET /api/v1/cobrador/estadisticas`

3. **Formato de Token JWT:**
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. **Credenciales de Prueba:**
   - Usuario: `admin`
   - Password: `123`

---

## ✨ Cuando termines esto, tu app podrá:

✅ Login seguro con JWT  
✅ Ver lista de clientes  
✅ Ver préstamos activos  
✅ Registrar cobros  
✅ Ver estadísticas  
✅ Trabajar offline  
✅ Tomar fotos  
✅ Usar GPS  
✅ Recibir notificaciones  

---

**¿Por dónde empezamos? 🚀**

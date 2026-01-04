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

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': name,
      'usuario': username,
      'email': email,
      'rol': rol,
    };
  }

  bool get isDueno => rol == 'dueno';
  bool get isGerente => rol == 'gerente';
  bool get isCobrador => rol == 'cobrador';
  bool get canManageUsers => isDueno || isGerente;
}

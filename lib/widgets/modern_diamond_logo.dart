import 'package:flutter/material.dart';

class ModernDiamondLogo extends StatelessWidget {
  final double size;
  final Color baseColor;

  const ModernDiamondLogo({
    super.key,
    this.size = 120,
    this.baseColor = const Color(0xFF2196F3), // Blue 500
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: baseColor.withOpacity(0.05),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: baseColor.withOpacity(0.1),
            blurRadius: 20,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Center(
        child: CustomPaint(
          size: Size(size * 0.6, size * 0.6),
          painter: _DiamondPainter(color: baseColor),
        ),
      ),
    );
  }
}

class _DiamondPainter extends CustomPainter {
  final Color color;

  _DiamondPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = size.width * 0.08
      ..strokeJoin = StrokeJoin.round
      ..strokeCap = StrokeCap.round;

    final fillPaint = Paint()
      ..style = PaintingStyle.fill
      ..shader = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          color.withOpacity(0.2),
          color.withOpacity(0.05),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    final path = Path();
    final w = size.width;
    final h = size.height;

    // Puntos del diamante (Minimalista, vista frontal estilizada)
    //        p1 (top)
    //   p2        p3 (lados anchos)
    //        p4 (bottom)
    
    // Proporciones modernas
    final topY = h * 0.0;
    final midY = h * 0.35;
    final botY = h * 1.0;
    
    final leftX = w * 0.0;
    final rightX = w * 1.0;
    final centerX = w * 0.5;
    
    final topFlatW = w * 0.3; // Ancho de la "mesa" del diamante
    
    final pTopLeft = Offset(centerX - topFlatW, topY);
    final pTopRight = Offset(centerX + topFlatW, topY);
    final pMidLeft = Offset(leftX, midY);
    final pMidRight = Offset(rightX, midY);
    final pBot = Offset(centerX, botY);

    // Contorno exterior
    path.moveTo(pTopLeft.dx, pTopLeft.dy);
    path.lineTo(pTopRight.dx, pTopRight.dy);
    path.lineTo(pMidRight.dx, pMidRight.dy);
    path.lineTo(pBot.dx, pBot.dy);
    path.lineTo(pMidLeft.dx, pMidLeft.dy);
    path.close();

    // Dibujar relleno gradiente
    canvas.drawPath(path, fillPaint);
    
    // Dibujar contorno limpio
    canvas.drawPath(path, paint);

    // Líneas internas minimalistas (facetas)
    // Conectar punta de abajo con esquinas superiores de la "mesa"
    // Esto crea un triangulo central elegante
    final innerPath = Path();
    innerPath.moveTo(pMidLeft.dx, pMidLeft.dy);
    innerPath.lineTo(pTopLeft.dx, pTopLeft.dy); // Repasar borde (opcional o diseño)
    
    // Faceta central triángulo invertido
    // Desde pTopLeft a pMidRight? No.
    // Faceta clásica simple:
    canvas.drawLine(pMidLeft, pTopLeft, paint); // Ya es parte del borde
    canvas.drawLine(pMidRight, pTopRight, paint);
    
    // Lineas transversales que dan volumen (mesa)
    final facetPaint = Paint()
      ..color = color.withOpacity(0.5)
      ..style = PaintingStyle.stroke
      ..strokeWidth = size.width * 0.04;

    // De las esquinas medias a las esquinas de la mesa opuestas?
    // Diseño minimalista:
    // Un simple triángulo en el medio de la parte superior
    // Conectar pTopLeft -> pBot? Muy sucio.
    // Conectar pMidLeft -> pTopRight?
    
    // Vamos a hacer un "corte brillante" simplificado
    canvas.drawLine(pTopLeft, pMidRight, facetPaint);
    canvas.drawLine(pTopRight, pMidLeft, facetPaint);
    
    // Linea horizontal en midY?
    // canvas.drawLine(pMidLeft, pMidRight, facetPaint); 
    // Preferible no saturar para que sea minimalista.
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

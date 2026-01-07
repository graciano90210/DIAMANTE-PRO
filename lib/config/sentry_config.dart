class SentryConfig {
  // Sentry DSN - Proyecto Flutter en sentry.io
  // GitHub Student Pack: 500,000 errores/mes gratis
  static const String dsn = 'https://83814eafa9d43fcb9a150bc793153dd7@o4510580095647744.ingest.us.sentry.io/4510670524252160';
  
  // Configuración
  static const bool enableInDevMode = false;
  static const double tracesSampleRate = 1.0;
  static const String environment = 'production';
  
  // Configurar después de obtener tu DSN de:
  // https://sentry.io/signup/ (usa tu cuenta de GitHub Student)
}

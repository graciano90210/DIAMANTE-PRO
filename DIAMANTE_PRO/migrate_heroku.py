"""Script to migrate Heroku PostgreSQL schema"""
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    migrations = [
        "ALTER TABLE rutas ADD COLUMN IF NOT EXISTS oficina_id INTEGER",
        "ALTER TABLE rutas ADD COLUMN IF NOT EXISTS descripcion VARCHAR(200)",
        "ALTER TABLE rutas ADD COLUMN IF NOT EXISTS pais VARCHAR(50) DEFAULT 'Colombia'",
        "ALTER TABLE rutas ADD COLUMN IF NOT EXISTS moneda VARCHAR(3) DEFAULT 'COP'",
        "ALTER TABLE rutas ADD COLUMN IF NOT EXISTS simbolo_moneda VARCHAR(5) DEFAULT '$'",
    ]

    for sql in migrations:
        try:
            db.session.execute(db.text(sql))
            db.session.commit()
            print(f"OK: {sql[:60]}")
        except Exception as e:
            db.session.rollback()
            print(f"SKIP: {e}")

    # Create any missing tables
    db.create_all()
    print("create_all() done - all missing tables created")

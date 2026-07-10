from app import create_app
from extensions import db
from models.usuario import Usuario

app = create_app()
with app.app_context():
    existente = Usuario.query.filter_by(email='admin@exclusiveautodetail.com').first()
    if existente:
        print("Ya existe, reseteando password...")
        existente.set_password('Admin1234!')
    else:
        admin = Usuario(
            nombre='Administrador', apellido='Sistema',
            email='admin@exclusiveautodetail.com', rol='admin', activo=True,
        )
        admin.set_password('Admin1234!')
        db.session.add(admin)
    db.session.commit()
    print("Listo. Admin:", admin.email if not existente else existente.email)
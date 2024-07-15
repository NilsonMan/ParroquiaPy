from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
from sqlalchemy import LargeBinary
app = Flask(__name__)

# Configura la URI de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cripta_administracion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define tus modelos aquí

class Clientes(db.Model):
    Cripta = db.Column(db.TEXT, primary_key=True)
    Nombre_titular = db.Column(db.TEXT)
    Apellido_paterno = db.Column(db.TEXT)
    Apellido_materno = db.Column(db.TEXT)
    Familia = db.Column(db.TEXT)  # Nuevo campo para la familia
    Telefono1 = db.Column(db.TEXT)
    Direccion1 = db.Column(db.TEXT)
    Nombre_Beneficiario = db.Column(db.TEXT)
    Apellido_paterno_Beneficiario = db.Column(db.TEXT)
    Apellido_materno_Beneficiario = db.Column(db.TEXT)
    Telefono_Beneficiario = db.Column(db.TEXT)
    Direccion_Beneficiario = db.Column(db.TEXT)
    Nombre_Beneficiario2 = db.Column(db.TEXT)
    Apellido_paterno_Beneficiario2 = db.Column(db.TEXT)
    Apellido_materno_Beneficiario2 = db.Column(db.TEXT)
    Telefono_Beneficiario2 = db.Column(db.TEXT)
    Direccion_Beneficiario2 = db.Column(db.TEXT)

class Difuntos(db.Model):
    ID_difunto = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    Nombre_completo = db.Column(db.TEXT)
    Apellido_paterno = db.Column(db.TEXT)
    Apellido_materno = db.Column(db.TEXT)
    Cripta = db.Column(db.TEXT, db.ForeignKey('clientes.Cripta'))
    Fecha_defuncion = db.Column(db.DATE)
    Fecha = db.Column(db.DATE)
    Fecha_Retiro = db.Column(db.DATE)

    # Relación con la tabla Clientes
    cliente = db.relationship('Clientes', backref=db.backref('difuntos', lazy=True))

class Pagos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Folio = db.Column(db.TEXT)
    Cripta = db.Column(db.TEXT, db.ForeignKey('criptas.Cripta'), nullable=False)
    Saldo = db.Column(db.REAL, nullable=False)
    Abono = db.Column(db.REAL, nullable=False)
    Saldo_total = db.Column(db.REAL, nullable=False)
    Fecha_pago = db.Column(db.DateTime, nullable=False)
    Notas = db.Column(db.TEXT)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Clave foránea a Usuarios

    cripta_relacionada = db.relationship('Criptas', backref=db.backref('pagos', lazy=True))
    usuario = db.relationship('Usuarios', backref=db.backref('pagos', lazy=True))  # Relación con Usuarios

    

class Documentacion(db.Model):
    ID_documentacion = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    Cripta = db.Column(db.TEXT, db.ForeignKey('clientes.Cripta'))
    Tipo_documento = db.Column(db.TEXT)
    Documento = db.Column(db.LargeBinary, nullable=True)
    Observaciones = db.Column(db.TEXT)
    nombre_archivo = db.Column(db.String(255), nullable=True)

    # Relación con la tabla Clientes
    cliente = db.relationship('Clientes', backref=db.backref('documentacion', lazy=True))

class Usuarios(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.TEXT, unique=True)
    password = db.Column(db.TEXT)
    role = db.Column(db.TEXT)

class Criptas(db.Model):
    Cripta = db.Column(db.TEXT, primary_key=True)
    Saldo = db.Column(db.REAL, nullable=False)

    @classmethod
    def actualizar_saldo(cls, cripta, nuevo_saldo):
        cripta_obj = cls.query.get(cripta)
        if cripta_obj:
            cripta_obj.Saldo = nuevo_saldo
            db.session.commit()

    
if __name__ == '__main__':
    #with app.app_context():
     #   db.create_all()
     #   print("Tablas creadas exitosamente")
     # Elimina la tabla Pagos si existe
    with app.app_context():
        # Construye la sentencia DROP TABLE para Pagos
        drop_statement = text(f"DROP TABLE IF EXISTS {Clientes.__tablename__};")

        # Ejecuta la sentencia SQL
        db.session.execute(drop_statement)
        db.session.commit()

        print("Tabla Pagos eliminada exitosamente.")

        # Crea la tabla Pagos de nuevo
        db.create_all()
        print("Tabla Pagos creada exitosamente.")
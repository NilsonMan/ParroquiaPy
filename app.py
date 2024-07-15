from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, make_response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
import re
from flask import send_from_directory
import sqlite3
from sqlalchemy import desc  
from datetime import datetime, timedelta, date
from functools import wraps
from sqlalchemy import text
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define la carpeta de carga para los archivos subidos
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')


# Configura la URI de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cripta_administracion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class Clientes(db.Model):
    Cripta = db.Column(db.TEXT, primary_key=True)
    Nombre_titular = db.Column(db.TEXT)
    Apellido_paterno = db.Column(db.TEXT)
    Apellido_materno = db.Column(db.TEXT)
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

class Familia(db.Model):
    Familia_id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    Nombre_familia = db.Column(db.TEXT)
    Cripta = db.Column(db.TEXT, db.ForeignKey('clientes.Cripta'))
    ID_difunto = db.Column(db.INTEGER, db.ForeignKey('difuntos.ID_difunto'))

    # Relaciones con las tablas Clientes y Difuntos
    cliente = db.relationship('Clientes', backref=db.backref('familias', lazy=True))
    difunto = db.relationship('Difuntos', backref=db.backref('familias', lazy=True))

class Pagos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Folio = db.Column(db.TEXT)
    Cripta = db.Column(db.TEXT, db.ForeignKey('criptas.Cripta'), nullable=False)
    Saldo = db.Column(db.REAL, nullable=False)
    Abono = db.Column(db.REAL, nullable=False)
    Saldo_total = db.Column(db.REAL, nullable=False)
    Fecha_pago = db.Column(db.DateTime, nullable=False)
    Notas = db.Column(db.TEXT)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    cripta_relacionada = db.relationship('Criptas', backref=db.backref('pagos', lazy=True))
    usuario = db.relationship('Usuarios', backref=db.backref('pagos', lazy=True))

    

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
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)  # Asegúrate de que este campo esté definido
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __init__(self, nombre, username, password, role):
        self.nombre = nombre
        self.username = username
        self.password = password
        self.role = role

class ConfiguracionPagos(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    monto_mantenimiento = db.Column(db.REAL)
    fecha_inicio = db.Column(db.DATE)
    hora_inicio = db.Column(db.TEXT)

class Criptas(db.Model):
    Cripta = db.Column(db.TEXT, primary_key=True)
    Saldo = db.Column(db.REAL, nullable=False)

    @classmethod
    def actualizar_saldo(cls, cripta, nuevo_saldo):
        cripta_obj = cls.query.get(cripta)
        if cripta_obj:
            cripta_obj.Saldo = nuevo_saldo
            db.session.commit()

    

class Documentos(db.Model):
    ID = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.TEXT, nullable=False)
    Tipo = db.Column(db.TEXT, nullable=False)
    Archivo = db.Column(db.BLOB, nullable=False)
    Fecha_subida = db.Column(db.TEXT)
    Observaciones = db.Column(db.TEXT)

class Checklist(db.Model):
    ID = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    Cripta = db.Column(db.TEXT, db.ForeignKey('clientes.Cripta'), unique=True)
    Identificacion_titular = db.Column(db.BOOLEAN)
    Identificacion_beneficiario1 = db.Column(db.BOOLEAN)
    Identificacion_beneficiario2 = db.Column(db.BOOLEAN)
    Acta_defuncion = db.Column(db.BOOLEAN)
    Autorizacion_cremacion = db.Column(db.BOOLEAN)
    Acta_traslado_cenizas = db.Column(db.BOOLEAN)

    # Relación con la tabla Clientes
    cliente = db.relationship('Clientes', backref=db.backref('checklist', uselist=False))

class HistoricoSumaSaldos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Cripta = db.Column(db.String(50))  # Cambia el tipo según tu modelo de criptas
    Monto = db.Column(db.Float)
    Motivo = db.Column(db.String(200))
    Fecha = db.Column(db.DateTime)

    def __repr__(self):
        return f'<HistoricoSumaSaldos {self.id}>'
# Crea todas las tablas en la base de datos si no existen

# Crea todas las tablas en la base de datos si no existen

# Define la función del decorador role_required
def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'role' in session and session['role'] in allowed_roles:
                return func(*args, **kwargs)
            else:
                flash('No tienes permiso para acceder a esta página.', 'error')
                return redirect(url_for('login'))  # Redirige a la página de inicio o a donde sea apropiado
        return wrapper
    return decorator 



################# importaciones para el sqlAlchemy ############ 

login_manager = LoginManager()
login_manager.init_app(app)

# Define la vista de login

###################### Optenciones de la Bd #######


@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))



# Obtener todos los clientes
def get_clientes():
    clientes = Clientes.query.all()
    return clientes

# Obtener todos los usuarios
def get_usuarios():
    usuarios = Usuarios.query.all()
    return usuarios

# Obtener todos los difuntos
def get_difuntos():
    difuntos = Difuntos.query.all()
    return difuntos

# Generar folios para pagos
def generate_folio():
    last_folio = db.session.query(db.func.max(Pagos.Folio)).scalar()

    if last_folio:
        last_folio_digits = re.findall(r'\d+', last_folio)
        if last_folio_digits:
            last_folio_number = int(last_folio_digits[0])
            new_folio = last_folio_number + 1
        else:
            new_folio = 1
    else:
        new_folio = 1

    return new_folio

# Obtener todos los pagos
def get_pagos():
    return Pagos.query.all()

# Sumar un monto a los saldos de las criptas
def sumar_a_saldos(monto_sumar, cripta=None):
    if cripta:
        # Sumar monto a una cripta específica
        cripta_obj = Criptas.query.filter_by(Cripta=cripta).first()
        if cripta_obj:
            cripta_obj.Saldo += monto_sumar
            db.session.commit()
    else:
        # Sumar monto a todas las criptas
        criptas = Criptas.query.all()
        for cripta in criptas:
            cripta.Saldo += monto_sumar
        db.session.commit()

def guardar_historico(cripta, monto_sumar, motivo):
    # Guardar registro en el historial
    historico = HistoricoSumaSaldos(
        Cripta=cripta,
        Monto=monto_sumar,
        Motivo=motivo,
        Fecha=datetime.now()
    )
    db.session.add(historico)
    db.session.commit()


# Guardar un registro de cobro de mantenimiento
def guardar_cobro_mantenimiento(monto):
    try:
        conn = db.session.connection()
        fecha_cobro = datetime.now().date()
        conn.execute('INSERT INTO CobrosMantenimiento (fecha_cobro, monto) VALUES (?, ?)', (fecha_cobro, monto))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    finally:
        conn.close()

# Función para obtener la configuración de pagos
def obtener_configuracion_de_pagos():
    try:
        configuracion = ConfiguracionPagos.query.filter_by(id=1).first()

        if configuracion:
            return {
                'monto_mantenimiento': configuracion.monto_mantenimiento,
                'fecha_inicio': configuracion.fecha_inicio.strftime('%Y-%m-%d'),
                'hora_inicio': configuracion.hora_inicio
            }
        else:
            # Si no se encuentra la configuración, se retorna un valor por defecto
            return {
                'monto_mantenimiento': 0.0,
                'fecha_inicio': datetime.now().strftime('%Y-%m-%d'),
                'hora_inicio': datetime.now().strftime('%H:%M')
            }

    except Exception as e:
        raise e


def obtener_saldo_cripta(cripta):
    try:
        # Consulta SQL para obtener el saldo actual de la cripta
        saldo = db.session.query(Criptas.Saldo).filter_by(Cripta=cripta).scalar()
        return saldo if saldo is not None else 0.0  # Devuelve el saldo o cero si no se encuentra la cripta
    except Exception as e:
        flash(f'Error al calcular el saldo de la cripta: {str(e)}', 'error')
        return 0.0  # Manejo de error: devuelve cero


 
def actualizar_saldo(cls, cripta, nuevo_saldo):
        cripta_obj = cls.query.get(cripta)
        if cripta_obj:
            cripta_obj.Saldo = nuevo_saldo
            db.session.commit()

############################# Rutas  se sitio #############

# Ruta definida para inicion de sesion
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('menu'))
    else:
        return redirect(url_for('login'))
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuarios.query.filter_by(username=username).first()

        if user is None:
            flash('Usuario no encontrado', 'error')
        elif not check_password_hash(user.password, password):
            flash('Contraseña incorrecta', 'error')
        else:
            session['username'] = user.username
            session['role'] = user.role
            session['user_id'] = user.id  # Almacena el ID del usuario en la sesión
            
            # Limpiar mensajes flash antes de mostrar el mensaje de bienvenida
            session.pop('_flashes', None)
            
            flash(f'Bienvenido {username}', 'info')
            return redirect(url_for('menu'))

    return render_template('login.html')

#Routa definida para salida de la sesion
@app.route('/logout')
def logout():
    # Limpiar todos los mensajes flash al cerrar sesión
    session.pop('_flashes', None)
    
    session.pop('username', None)
    session.pop('role', None)
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))


@app.route('/menu')
def menu():
    # Verifica si el usuario está autenticado en la sesión
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa
    
    # Renderiza la plantilla del menú y pasa el nombre de usuario y el rol a la plantilla
    return render_template('menu.html', username=session['username'], role=session['role'])

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    if request.method == 'POST':
        # Obtiene los datos del formulario
        nombre = request.form['nombre']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # Genera el hash de la contraseña
        hashed_password = generate_password_hash(password)  # Utiliza el método por defecto

        # Crea un nuevo usuario utilizando SQLAlchemy
        new_user = Usuarios(nombre=nombre, username=username, password=hashed_password, role=role)
        
        # Agrega el nuevo usuario a la sesión y lo guarda en la base de datos
        db.session.add(new_user)
        db.session.commit()

        flash('Usuario creado correctamente', 'info')
        return redirect(url_for('create_user'))  # Redirige nuevamente a la página de creación de usuarios después de la operación exitosa

    return render_template('create_user.html')




@app.route('/change_password', methods=['GET', 'POST'])
@role_required('admin')  # Requiere que el usuario tenga el rol 'admin' para acceder a esta ruta
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    if request.method == 'POST':
        # Obtiene los datos del formulario
        username = request.form['username']
        new_password = request.form['new_password']
        
        # Genera el hash de la nueva contraseña
        hashed_password = generate_password_hash(new_password)

        # Busca al usuario por nombre de usuario
        user = Usuarios.query.filter_by(username=username).first()

        if not user:
            flash('Usuario no encontrado', 'error')
        else:
            # Actualiza la contraseña del usuario
            user.password = hashed_password
            db.session.commit()

            flash(f'Contraseña cambiada para {username}', 'info')
            return redirect(url_for('change_password'))  # Redirige nuevamente a la página de cambio de contraseña después de la operación exitosa
    
    # Obtiene la lista de usuarios para mostrar en la plantilla
    usuarios = Usuarios.query.all()
    return render_template('change_password.html', users=usuarios)



@app.route('/delete_user', methods=['GET', 'POST'])
@role_required('admin')  # Requiere que el usuario tenga el rol 'admin' para acceder a esta ruta
def delete_user():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    if request.method == 'POST':
        # Obtiene el nombre de usuario a eliminar desde el formulario
        username = request.form['username']
        
        # Busca al usuario por nombre de usuario
        user = Usuarios.query.filter_by(username=username).first()

        if not user:
            flash('Usuario no encontrado', 'error')
        else:
            # Elimina al usuario de la base de datos
            db.session.delete(user)
            db.session.commit()

            flash(f'Usuario {username} eliminado exitosamente', 'info')
            return redirect(url_for('delete_user'))  # Redirige nuevamente a la página de eliminación de usuario después de la operación exitosa
    
    # Obtiene la lista de usuarios para mostrar en la plantilla
    usuarios = Usuarios.query.all()
    return render_template('delete_user.html', users=usuarios)



@app.route('/agregar_cliente', methods=['GET', 'POST'])
def agregar_cliente():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    if request.method == 'POST':
        cripta = request.form['cripta']
        nombre_titular = request.form['nombre_titular']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        telefono1 = request.form['telefono1']
        direccion1 = request.form['direccion1']
        nombre_beneficiario = request.form['nombre_beneficiario']
        apellido_paterno_beneficiario = request.form['apellido_paterno_beneficiario']
        apellido_materno_beneficiario = request.form['apellido_materno_beneficiario']
        telefono_beneficiario = request.form['telefono_beneficiario']
        direccion_beneficiario = request.form['direccion_beneficiario']
        nombre_beneficiario2 = request.form['nombre_beneficiario2']
        apellido_paterno_beneficiario2 = request.form['apellido_paterno_beneficiario2']
        apellido_materno_beneficiario2 = request.form['apellido_materno_beneficiario2']
        telefono_beneficiario2 = request.form['telefono_beneficiario2']
        direccion_beneficiario2 = request.form['direccion_beneficiario2']

        # Verificar si ya existe un cliente con el mismo valor de cripta
        existing_cliente = Clientes.query.filter_by(Cripta=cripta).first()

        if existing_cliente:
            flash('Ya existe un cliente con el mismo valor de cripta', 'error')
        else:
            # Crea un nuevo objeto Cliente utilizando SQLAlchemy
            new_cliente = Clientes(Cripta=cripta, Nombre_titular=nombre_titular, Apellido_paterno=apellido_paterno,
                                   Apellido_materno=apellido_materno, Telefono1=telefono1, Direccion1=direccion1,
                                   Nombre_Beneficiario=nombre_beneficiario,
                                   Apellido_paterno_Beneficiario=apellido_paterno_beneficiario,
                                   Apellido_materno_Beneficiario=apellido_materno_beneficiario,
                                   Telefono_Beneficiario=telefono_beneficiario, Direccion_Beneficiario=direccion_beneficiario,
                                   Nombre_Beneficiario2=nombre_beneficiario2,
                                   Apellido_paterno_Beneficiario2=apellido_paterno_beneficiario2,
                                   Apellido_materno_Beneficiario2=apellido_materno_beneficiario2,
                                   Telefono_Beneficiario2=telefono_beneficiario2, Direccion_Beneficiario2=direccion_beneficiario2)
            
            # Agrega el nuevo cliente a la sesión y lo guarda en la base de datos
            db.session.add(new_cliente)
            db.session.commit()

            flash('Cliente agregado correctamente', 'info')

        return redirect(url_for('agregar_cliente'))

    # Obtiene la lista de clientes para mostrar en la plantilla
    clientes = Clientes.query.all()
    return render_template('agregar_cliente.html', clientes=clientes)



@app.route('/agregar_difunto', methods=['GET', 'POST'])
def agregar_difunto():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    if request.method == 'POST':
        nombre_completo = request.form['nombre_completo']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        fecha_defuncion_str = request.form['fecha_defuncion']
        fecha_str = request.form['fecha']
        cripta = request.form['cripta']

        # Convertir las fechas de cadena a objetos date
        fecha_defuncion = datetime.strptime(fecha_defuncion_str, '%Y-%m-%d').date()
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

        # Crear un nuevo objeto Difuntos utilizando SQLAlchemy
        new_difunto = Difuntos(
            Nombre_completo=nombre_completo,
            Apellido_paterno=apellido_paterno,
            Apellido_materno=apellido_materno,
            Cripta=cripta,
            Fecha_defuncion=fecha_defuncion,
            Fecha=fecha
        )
        
        # Agregar el nuevo difunto a la sesión y guardarlo en la base de datos
        db.session.add(new_difunto)
        db.session.commit()

        flash('Difunto agregado correctamente', 'info')
        return redirect(url_for('agregar_difunto'))

    # Obtener la lista de difuntos para mostrar en la plantilla
    difuntos = Difuntos.query.all()
    return render_template('agregar_difunto.html', difuntos=difuntos)




@app.route('/verificar_documentacion', methods=['GET', 'POST'])
def verificar_documentacion():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    if request.method == 'POST':
        cripta = request.form['cripta']
        tipo_documento = request.form['tipo_documento']
        observaciones = request.form['observaciones']
        documento = request.files.get('documento')

        # Verifica si se envió algún archivo
        if documento:
            filename = secure_filename(documento.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            documento.save(file_path)

            # Lee el archivo en modo binario ('rb') para obtener los datos binarios
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Crea un nuevo objeto Documentacion utilizando SQLAlchemy
            new_documentacion = Documentacion(
                Cripta=cripta,
                Tipo_documento=tipo_documento,
                Observaciones=observaciones,
                Documento=file_data,  # Guarda los datos binarios del archivo
                nombre_archivo=filename  # Guarda el nombre original del archivo
            )

            # Agrega la nueva documentación a la sesión y la guarda en la base de datos
            db.session.add(new_documentacion)
            db.session.commit()

            flash('Documentación verificada correctamente', 'info')
            return redirect(url_for('verificar_documentacion'))

    # Obtiene la lista de clientes para mostrar en el formulario
    clientes = Clientes.query.all()
    return render_template('verificar_documentacion.html', clientes=clientes)

@app.route('/download/<filename>')
def download_file(filename):
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    return send_from_directory(upload_folder, filename, as_attachment=True)

@app.route('/listar_documentacion', methods=['GET', 'POST'])
def listar_documentacion():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    if request.method == 'POST':
        cripta = request.form['cripta']
        documentos = Documentacion.query.filter_by(Cripta=cripta).all()
        return render_template('listar_documentacion.html', documentos=documentos)

    # Si no se envió un formulario POST, simplemente renderiza la plantilla con la lista completa de documentos
    documentos = Documentacion.query.all()
    return render_template('listar_documentacion.html', documentos=documentos)




@app.route('/editar_documentacion/<cripta>', methods=['GET', 'POST'])
def editar_documentacion(cripta):
    if request.method == 'POST':
        tipo_documento = request.form['tipo_documento']
        observaciones = request.form['observaciones']
        documento = request.files.get('documento')
        filename = None
        
        # Obtener el documento actual de la base de datos
        documentacion = Documentacion.query.filter_by(Cripta=cripta, ID_documentacion=request.form['id_documentacion']).first()

        if documento:
            filename = secure_filename(documento.filename)
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            path_to_save = os.path.join(upload_folder, filename)
            documento.save(path_to_save)
            
            # Leer el archivo en modo binario ('rb') para obtener los datos binarios
            with open(path_to_save, 'rb') as f:
                file_data = f.read()
            
            # Eliminar el archivo anterior si existe
            if documentacion.Documento:
                old_file_path = os.path.join(upload_folder, documentacion.Documento.decode('utf-8', 'ignore'))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Actualizar el archivo en la base de datos
            documentacion.Documento = file_data

        # Actualizar los campos de la base de datos
        documentacion.Tipo_documento = tipo_documento
        documentacion.Observaciones = observaciones
        
        db.session.commit()
        flash('Documentación actualizada correctamente', 'info')
        return redirect(url_for('listar_documentacion'))
    
    # Obtener el documento actual para mostrar en el formulario de edición
    documentacion = Documentacion.query.filter_by(Cripta=cripta).first()
    return render_template('editar_documentacion.html', documentacion=documentacion)




@app.route('/eliminar_documentacion/<cripta>/<int:id_documentacion>', methods=['POST'])
def eliminar_documentacion(cripta, id_documentacion):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    # Obtener la documentación específica desde la base de datos
    documentacion = Documentacion.query.filter_by(Cripta=cripta, ID_documentacion=id_documentacion).first()

    if not documentacion:
        flash('La documentación especificada no existe', 'error')
    else:
        try:
            # Eliminar el archivo físico si existe
            if documentacion.Documento:
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                file_name = secure_filename(documentacion.nombre_archivo)
                old_file_path = os.path.join(upload_folder, file_name)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Eliminar la entrada de la base de datos
            db.session.delete(documentacion)
            db.session.commit()
            flash('Documentación eliminada correctamente', 'info')
        except Exception as e:
            flash(f'Error al eliminar la documentación: {str(e)}', 'error')

    return redirect(url_for('listar_documentacion'))

@app.route('/buscar', methods=['GET'])
def buscar():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    query = request.args.get('query')
    if not query:
        flash('Por favor ingrese un término de búsqueda', 'error')
        return redirect(url_for('menu'))

    # Inicializar variables
    clientes = []
    documentos = []
    difuntos = []
    pagos = {}
    retiros = {}
    saldos = {}
    historico_sumas_saldos = {}

    # Buscar en la tabla de clientes
    clientes = Clientes.query.filter(Clientes.Nombre_titular.like(f'%{query}%') | Clientes.Cripta.like(f'%{query}%')).all()

    # Buscar en la tabla de difuntos
    difuntos = Difuntos.query.filter(Difuntos.Nombre_completo.like(f'%{query}%') | Difuntos.Cripta.like(f'%{query}%')).all()

    # Si se encontró algún difunto, buscar la información de la cripta asociada
    if difuntos:
        criptas = {difunto.Cripta for difunto in difuntos}

        clientes = Clientes.query.filter(Clientes.Cripta.in_(criptas)).all()
        documentos = Documentacion.query.filter(Documentacion.Cripta.in_(criptas)).all()

        for cripta in criptas:
            pagos[cripta] = Pagos.query.filter_by(Cripta=cripta).all()

            # Obtener saldo de la cripta
            saldo = obtener_saldo_cripta(cripta)
            saldos[cripta] = saldo

            retiro = Difuntos.query.filter_by(Cripta=cripta).filter(Difuntos.Fecha_Retiro.isnot(None)).first()
            if retiro:
                retiros[cripta] = retiro.Fecha_Retiro

            # Obtener histórico de sumas y saldos
            historico_sumas_saldos[cripta] = HistoricoSumaSaldos.query.filter_by(Cripta=cripta).all()

            # Asignar el nombre completo del usuario que cobró el pago y calcular saldo total
            for pago in pagos[cripta]:
                usuario = Usuarios.query.get(pago.usuario_id)  # Asumiendo que usuario_id es la clave foránea en Pagos
                pago.Cobrado_por = usuario.nombre  # Cambiar a usuario.nombre si nombre contiene el nombre completo

                # Calcular el saldo total después del pago
                saldo_anterior = pago.Saldo
                abono = pago.Abono
                saldo_total = saldo_anterior - abono
                pago.Saldo_total = saldo_total

    return render_template('resultados_busqueda.html', 
                           query=query, 
                           clientes=clientes, 
                           documentos=documentos, 
                           difuntos=difuntos, 
                           pagos=pagos, 
                           retiros=retiros, 
                           saldos=saldos,
                           historico_sumas_saldos=historico_sumas_saldos)

 

from flask import session
@app.route('/pagos-cajero', methods=['GET', 'POST'])
@role_required(['cajera', 'admin'])
def pagos_cajero():
    if request.method == 'POST':
        cripta = request.form['cripta']
        abono = float(request.form['abono'])
        notas = request.form['notas']

        try:
            # Obtener el saldo actual de la cripta
            saldo_actual_cripta = obtener_saldo_cripta(cripta)
            saldo_total_cripta = saldo_actual_cripta - abono

            # Generar el folio automáticamente
            new_folio = generate_folio()

            fecha_pago = datetime.now()

            # Obtener el ID del usuario desde la sesión
            usuario_id = session.get('user_id')

            if usuario_id is None:
                raise ValueError('No se encontró el ID de usuario en la sesión.')

            # Insertar el pago en la base de datos de pagos
            pago = Pagos(Folio=new_folio, Cripta=cripta, Saldo=saldo_actual_cripta, Abono=abono,
                         Saldo_total=saldo_total_cripta, Fecha_pago=fecha_pago, Notas=notas, usuario_id=usuario_id)
            db.session.add(pago)
            db.session.commit()

            # Actualizar el saldo en la tabla Criptas
            Criptas.actualizar_saldo(cripta, saldo_total_cripta)

            # Mostrar mensaje flash y redirigir
            flash('Pago añadido exitosamente', 'success')
            return redirect(url_for('pagos_cajero'))

        except Exception as e:
            db.session.rollback()  # Rollback explícito en caso de error
            flash(f'Error al agregar el pago: {str(e)}', 'error')

    # Obtener todos los pagos y actualizar Saldo Total para cada pago
    pagos = get_pagos()
    for pago in pagos:
        pago.Saldo_total = pago.Saldo - pago.Abono

    return render_template('pagos.html', pagos=pagos)



# Ruta para configurar pagos (GET y POST)
# Ruta para configurar pagos
@app.route('/configurar_pagos', methods=['GET', 'POST'])
def configurar_pagos():
    if request.method == 'POST':
        try:
            # Obtener el monto del formulario y guardarlo en la base de datos de configuración de pagos
            monto_mantenimiento = float(request.form['monto_mantenimiento'])
            
            # Guardar el cobro de mantenimiento en la base de datos de configuración de pagos
            guardar_cobro_mantenimiento(monto_mantenimiento)  # Función a definir para guardar en la base de datos
            
            flash('Cobro de mantenimiento registrado correctamente.', 'success')
            return redirect(url_for('configurar_pagos'))

        except Exception as e:
            flash(f'Error al registrar el cobro de mantenimiento: {str(e)}', 'error')
            return redirect(url_for('configurar_pagos'))

    # Obtener la configuración actual de pagos desde la segunda base de datos
    configuracion = obtener_configuracion_de_pagos()

    return render_template('configurar_pagos.html', configuracion=configuracion)


@app.route('/sumar_saldos', methods=['POST'])
@role_required('admin')
def sumar_saldos():
    monto_sumar = float(request.form['monto_sumar'])
    motivo = request.form['motivo']
    opcion = request.form['opcion']

    if opcion == 'todas':
        sumar_a_saldos(monto_sumar)
        guardar_historico(None, monto_sumar, motivo)
        flash('Se ha sumado el monto a todos los saldos de las criptas.', 'success')
    elif opcion == 'una':
        cripta = request.form['cripta']
        sumar_a_saldos(monto_sumar, cripta)
        guardar_historico(cripta, monto_sumar, motivo)
        flash(f'Se ha sumado el monto a la cripta {cripta}.', 'success')

    return redirect(url_for('configurar_pagos'))

@app.route('/agregar_cripta', methods=['POST'])
def agregar_cripta():
    try:
        # Captura los datos del formulario
        cripta = request.form['cripta']
        saldo = float(request.form['saldo'])

        # Crea una nueva instancia del modelo Criptas y guarda en la base de datos
        nueva_cripta = Criptas(Cripta=cripta, Saldo=saldo)
        db.session.add(nueva_cripta)
        db.session.commit()

        flash(f'Cripta "{cripta}" agregada correctamente con saldo {saldo}.', 'success')
    except Exception as e:
        flash(f'Error al agregar cripta: {str(e)}', 'error')

    return redirect(url_for('configurar_pagos'))

@app.route('/retiro_cenizas', methods=['GET', 'POST'])
@role_required(['cajera', 'admin'])
def retiro_cenizas():
    if request.method == 'POST':
        cripta = request.form['cripta']
        fecha_retiro = datetime.now()

        try:
            # Verificar si hay difuntos no retirados en la cripta especificada
            difuntos = Difuntos.query.filter_by(Cripta=cripta, Fecha_Retiro=None).all()

            if not difuntos:
                flash(f'No se encontraron difuntos en la cripta {cripta} o ya fueron retirados', 'error')
            else:
                for difunto in difuntos:
                    difunto.Fecha_Retiro = fecha_retiro

                db.session.commit()
                flash('Cenizas retiradas exitosamente', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al retirar las cenizas: {str(e)}', 'error')

    # Obtener difuntos que aún no han sido retirados
    difuntos = Difuntos.query.filter_by(Fecha_Retiro=None).all()

    return render_template('retiro_cenizas.html', difuntos=difuntos)




@app.route('/filtrado_pagos', methods=['GET', 'POST'])
@role_required('admin')
def filtrado_pagos():
    filtro = request.args.get('filtro', 'mes')
    cripta = request.args.get('cripta', None)

    today = datetime.today()
    start_date = None

    if filtro == 'semana':
        start_date = today - timedelta(days=today.weekday())  # Inicio de la semana actual
    elif filtro == 'mes':
        start_date = today.replace(day=1)  # Inicio del mes actual
    elif filtro == 'año':
        start_date = today.replace(month=1, day=1)  # Inicio del año actual

    try:
        query = Pagos.query

        if start_date:
            query = query.filter(Pagos.Fecha_pago >= start_date)

        if cripta:
            query = query.filter_by(Cripta=cripta)

        pagos = query.all()

    except Exception as e:
        flash(f'Error al filtrar los pagos: {str(e)}', 'error')
        pagos = []

    return render_template('filtrado_pagos.html', pagos=pagos, filtro=filtro, cripta=cripta)


@app.route('/clientes', methods=['GET', 'POST'])
def listar_clientes():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        cripta = request.form['cripta']
        clientes = Clientes.query.filter_by(Cripta=cripta).all()
        return render_template('listar_clientes.html', clientes=clientes, cripta=cripta)

    clientes = Clientes.query.all()
    return render_template('listar_clientes.html', clientes=clientes)




@app.route('/editar_cliente/<cripta>', methods=['GET', 'POST'])
def editar_cliente(cripta):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre_titular = request.form['nombre_titular']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        telefono1 = request.form['telefono1']
        direccion1 = request.form['direccion1']
        nombre_beneficiario = request.form['nombre_beneficiario']
        apellido_paterno_beneficiario = request.form['apellido_paterno_beneficiario']
        apellido_materno_beneficiario = request.form['apellido_materno_beneficiario']
        telefono_beneficiario = request.form['telefono_beneficiario']
        direccion_beneficiario = request.form['direccion_beneficiario']
        nombre_beneficiario2 = request.form['nombre_beneficiario2']
        apellido_paterno_beneficiario2 = request.form['apellido_paterno_beneficiario2']
        apellido_materno_beneficiario2 = request.form['apellido_materno_beneficiario2']
        telefono_beneficiario2 = request.form['telefono_beneficiario2']
        direccion_beneficiario2 = request.form['direccion_beneficiario2']

        cliente = Clientes.query.filter_by(Cripta=cripta).first()
        
        if cliente:
            cliente.Nombre_titular = nombre_titular
            cliente.Apellido_paterno = apellido_paterno
            cliente.Apellido_materno = apellido_materno
            cliente.Telefono1 = telefono1
            cliente.Direccion1 = direccion1
            cliente.Nombre_Beneficiario = nombre_beneficiario
            cliente.Apellido_paterno_Beneficiario = apellido_paterno_beneficiario
            cliente.Apellido_materno_Beneficiario = apellido_materno_beneficiario
            cliente.Telefono_Beneficiario = telefono_beneficiario
            cliente.Direccion_Beneficiario = direccion_beneficiario
            cliente.Nombre_Beneficiario2 = nombre_beneficiario2
            cliente.Apellido_paterno_Beneficiario2 = apellido_paterno_beneficiario2
            cliente.Apellido_materno_Beneficiario2 = apellido_materno_beneficiario2
            cliente.Telefono_Beneficiario2 = telefono_beneficiario2
            cliente.Direccion_Beneficiario2 = direccion_beneficiario2

            try:
                db.session.commit()
                flash('Cliente actualizado correctamente', 'info')
                return redirect(url_for('listar_clientes'))
            except Exception as e:
                flash(f'Error al actualizar el cliente: {str(e)}', 'error')
                return redirect(url_for('listar_clientes'))

        else:
            flash(f'No se encontró el cliente con la cripta {cripta}', 'error')
            return redirect(url_for('listar_clientes'))

    cliente = Clientes.query.filter_by(Cripta=cripta).first()
    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/eliminar_cliente/<cripta>', methods=['POST'])
def eliminar_cliente(cripta):
    if 'username' not in session:
        return redirect(url_for('login'))

    cliente = Clientes.query.filter_by(Cripta=cripta).first()

    if cliente:
        try:
            db.session.delete(cliente)
            db.session.commit()
            flash('Cliente eliminado correctamente', 'info')
        except Exception as e:
            flash(f'Error al eliminar el cliente: {str(e)}', 'error')
    else:
        flash(f'No se encontró el cliente con la cripta {cripta}', 'error')

    return redirect(url_for('listar_clientes'))





@app.route('/pagos', methods=['GET', 'POST'])
def listar_pagos():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        cripta = request.form['cripta']
        pagos = Pagos.query.filter_by(Cripta=cripta).all()
    else:
        pagos = Pagos.query.all()

    return render_template('listar_pagos.html', pagos=pagos)

@app.route('/editar_pago/<int:folio>', methods=['GET', 'POST'])
def editar_pago(folio):
    if 'username' not in session:
        return redirect(url_for('login'))

    pago = Pagos.query.get_or_404(folio)  # Busca el pago por el número de folio

    if request.method == 'POST':
        pago.Cripta = request.form['cripta']
        pago.Saldo = float(request.form['saldo'])
        pago.Abono = float(request.form['abono'])
        pago.Saldo_total = pago.Saldo - pago.Abono
        pago.Fecha_pago = request.form['fecha_pago']
        pago.Notas = request.form['notas']

        db.session.commit()

        flash('Pago actualizado correctamente', 'info')
        return redirect(url_for('listar_pagos'))

    return render_template('editar_pago.html', pago=pago)

@app.route('/eliminar_pago/<int:folio>', methods=['POST'])
def eliminar_pago(folio):
    if 'username' not in session:
        return redirect(url_for('login'))

    pago = Pagos.query.get_or_404(folio)  # Busca el pago por el número de folio

    db.session.delete(pago)  # Elimina el objeto pago de la sesión
    db.session.commit()  # Confirma la eliminación en la base de datos

    flash('Pago eliminado correctamente', 'info')
    return redirect(url_for('listar_pagos'))


@app.route('/select_cripta', methods=['GET', 'POST'])
def select_cripta():
    if request.method == 'POST':
        cripta = request.form['cripta']
        return redirect(url_for('checklist', cripta=cripta))
    
    return render_template('select_cripta.html')


@app.route('/checklist', methods=['GET', 'POST'])
def checklist():
    cripta = request.args.get('cripta')

    # Obtén el rol del usuario actual desde la sesión
    role = session.get('role', 'guest')  # Por defecto, el rol es 'guest' si no está definido en la sesión

    if request.method == 'POST':
        # Lógica para manejar el formulario POST
        try:
            # Obtener los valores del formulario y actualizar la base de datos
            identificacion_titular = 'Identificacion_titular' in request.form
            identificacion_beneficiario1 = 'Identificacion_beneficiario1' in request.form
            identificacion_beneficiario2 = 'Identificacion_beneficiario2' in request.form
            acta_defuncion = 'Acta_defuncion' in request.form
            autorizacion_cremacion = 'Autorizacion_cremacion' in request.form
            acta_traslado_cenizas = 'Acta_traslado_cenizas' in request.form

            # Actualizar o insertar los datos en la tabla Checklist usando SQLAlchemy
            checklist_entry = Checklist.query.filter_by(Cripta=cripta).first()
            if checklist_entry:
                checklist_entry.Identificacion_titular = identificacion_titular
                checklist_entry.Identificacion_beneficiario1 = identificacion_beneficiario1
                checklist_entry.Identificacion_beneficiario2 = identificacion_beneficiario2
                checklist_entry.Acta_defuncion = acta_defuncion
                checklist_entry.Autorizacion_cremacion = autorizacion_cremacion
                checklist_entry.Acta_traslado_cenizas = acta_traslado_cenizas
            else:
                new_checklist = Checklist(Cripta=cripta, Identificacion_titular=identificacion_titular,
                                          Identificacion_beneficiario1=identificacion_beneficiario1,
                                          Identificacion_beneficiario2=identificacion_beneficiario2,
                                          Acta_defuncion=acta_defuncion, Autorizacion_cremacion=autorizacion_cremacion,
                                          Acta_traslado_cenizas=acta_traslado_cenizas)
                db.session.add(new_checklist)
            
            db.session.commit()
            flash('Checklist actualizado correctamente.', 'info')
            return redirect(url_for('checklist', cripta=cripta))
        
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el checklist: ' + str(e), 'error')
        
        finally:
            db.session.close()

    # Obtén el estado actual del checklist
    checklist = Checklist.query.filter_by(Cripta=cripta).first()
    return render_template('checklist.html', checklist=checklist, cripta=cripta, role=role)



if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash, session,  make_response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re  
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, flash


app = Flask(__name__)
app.secret_key = 'your_secret_key'


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
# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('cripta_administracion.db')
    conn.row_factory = sqlite3.Row
    return conn

# Obtener todos los clientes
def get_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    conn.close()
    return clientes

# Obtener todos los usuarios
def get_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

# Obtener todos los difuntos
def get_difuntos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM difuntos')
    difuntos = cursor.fetchall()
    conn.close()
    return difuntos

# Rutas del sitio web
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        conn.close()

        if user is None:
            flash('Usuario no encontrado', 'error')
        elif not check_password_hash(user['password'], password):
            flash('Contraseña incorrecta', 'error')
        else:
            session['username'] = user['username']
            session['role'] = user['role']
            
            # Limpiar mensajes flash antes de mostrar el mensaje de bienvenida
            session.pop('_flashes', None)
            
            flash(f'Bienvenido {username}', 'info')
            return redirect(url_for('menu'))

    return render_template('login.html')

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
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', username=session['username'], role=session['role'])

@app.route('/create_user', methods=['GET', 'POST'])

def create_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)',
                       (username, hashed_password, role))
        conn.commit()
        conn.close()

        flash('Usuario creado correctamente', 'info')
        return redirect(url_for('create_user'))

    return render_template('create_user.html')

@app.route('/change_password', methods=['GET', 'POST'])
@role_required('admin')
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        
        hashed_password = generate_password_hash(new_password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET password = ? WHERE username = ?',
                       (hashed_password, username))
        conn.commit()
        conn.close()

        flash(f'Contraseña cambiada para {username}', 'info')
        return redirect(url_for('change_password'))
    
    usuarios = get_usuarios()
    return render_template('change_password.html', users=usuarios)

@app.route('/delete_user', methods=['GET', 'POST'])
@role_required('admin')
def delete_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE username = ?', (username,))
        conn.commit()
        conn.close()

        flash(f'Usuario {username} eliminado exitosamente', 'info')
        return redirect(url_for('delete_user'))
    
    usuarios = get_usuarios()
    return render_template('delete_user.html', users=usuarios)

@app.route('/agregar_cliente', methods=['GET', 'POST'])
def agregar_cliente():
    if 'username' not in session:
        return redirect(url_for('login'))

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

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clientes (CRIPTA, Nombre_titular, Apellido_paterno, Apellido_materno, Telefono1, Direccion1, '
                       'Nombre_Beneficiario, Apellido_paterno_Beneficiario, Apellido_materno_Beneficiario, Telefono_Beneficiario, '
                       'Direccion_Beneficiario, Nombre_Beneficiario2, Apellido_paterno_Beneficiario2, Apellido_materno_Beneficiario2, '
                       'Telefono_Beneficiario2, Direccion_Beneficiario2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (cripta, nombre_titular, apellido_paterno, apellido_materno, telefono1, direccion1, nombre_beneficiario,
                        apellido_paterno_beneficiario, apellido_materno_beneficiario, telefono_beneficiario, direccion_beneficiario,
                        nombre_beneficiario2, apellido_paterno_beneficiario2, apellido_materno_beneficiario2, telefono_beneficiario2,
                        direccion_beneficiario2))
        conn.commit()
        conn.close()

        flash('Cliente agregado correctamente', 'info')
        return redirect(url_for('agregar_cliente'))

    clientes = get_clientes()
    return render_template('agregar_cliente.html', clientes=clientes)

@app.route('/agregar_difunto', methods=['GET', 'POST'])
def agregar_difunto():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre_completo = request.form['nombre_completo']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        fecha_defuncion = request.form['fecha_defuncion']
        fecha = request.form['fecha']
        cripta = request.form['cripta']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO difuntos (Nombre_completo, Apellido_paterno, Apellido_materno, Cripta, Fecha_defuncion, Fecha) VALUES (?, ?, ?, ?, ?, ?)',
                       (nombre_completo, apellido_paterno, apellido_materno, cripta, fecha_defuncion, fecha))
        conn.commit()
        conn.close()

        flash('Difunto agregado correctamente', 'info')
        return redirect(url_for('agregar_difunto'))

    return render_template('agregar_difunto.html', difuntos=get_difuntos())


@app.route('/verificar_documentacion', methods=['GET', 'POST'])
def verificar_documentacion():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        cripta = request.form['cripta']
        tipo_documento = request.form['tipo_documento']
        observaciones = request.form['observaciones']
        documento = request.files.get('documento')

        # Verificamos si se ha enviado algún archivo
        if documento:
            filename = secure_filename(documento.filename)
            path_to_save = os.path.join(app.root_path, 'uploads', filename)
            documento.save(path_to_save)
            flash('Documento subido correctamente', 'info')
        else:
            filename = None

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO documentacion (Cripta, Tipo_documento, Observaciones, Documento) VALUES (?, ?, ?, ?)',
                       (cripta, tipo_documento, observaciones, filename if filename else ''))
        conn.commit()
        conn.close()

        flash('Documentación verificada correctamente', 'info')
        return redirect(url_for('verificar_documentacion'))

    clientes = get_clientes()
    return render_template('agregar_cliente.html', clientes=clientes)
#buscador menu 
@app.route('/buscar', methods=['GET'])
def buscar():
    if 'username' not in session:
        return redirect(url_for('login'))

    query = request.args.get('query')
    if not query:
        flash('Por favor ingrese un término de búsqueda', 'error')
        return redirect(url_for('menu'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Inicializar variables
    clientes = []
    documentos = []
    difuntos = []
    pagos = {}
    retiros = {}

    # Buscar en la tabla de clientes
    cursor.execute('''
        SELECT * FROM Clientes WHERE Nombre_titular LIKE ? OR Cripta LIKE ?
    ''', ('%' + query + '%', '%' + query + '%'))
    clientes = cursor.fetchall()

    # Buscar en la tabla de difuntos
    cursor.execute('''
        SELECT * FROM Difuntos WHERE Nombre_completo LIKE ? OR Cripta LIKE ?
    ''', ('%' + query + '%', '%' + query + '%'))
    difuntos = cursor.fetchall()

    # Si se encontró algún difunto, buscar la información de la cripta asociada
    if difuntos:
        criptas = {difunto['Cripta'] for difunto in difuntos}
        placeholders = ', '.join('?' for _ in criptas)
        cursor.execute(f'''
            SELECT * FROM Clientes WHERE Cripta IN ({placeholders})
        ''', list(criptas))
        clientes = cursor.fetchall()

        cursor.execute(f'''
            SELECT * FROM Documentacion WHERE Cripta IN ({placeholders})
        ''', list(criptas))
        documentos = cursor.fetchall()

        for cripta in criptas:
            cursor.execute('''
                SELECT * FROM Pagos WHERE Cripta = ?
            ''', (cripta,))
            pagos[cripta] = cursor.fetchall()

            cursor.execute('''
                SELECT Fecha_Retiro FROM Difuntos WHERE Cripta = ? AND Fecha_Retiro IS NOT NULL
            ''', (cripta,))
            retiro = cursor.fetchone()
            if retiro:
                retiros[cripta] = retiro['Fecha_Retiro']

    conn.close()

    return render_template('resultados_busqueda.html', query=query, clientes=clientes, documentos=documentos, difuntos=difuntos, pagos=pagos, retiros=retiros)


@app.route('/editar_pago/<folio>', methods=['GET', 'POST'])
@role_required('admin')
def editar_pago(folio):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cripta = request.form['cripta']
        abono = float(request.form['abono'])
        notas = request.form['notas']

        # Obtener el saldo actual de la cripta
        cursor.execute('SELECT Saldo FROM Criptas WHERE Cripta = ?', (cripta,))
        result = cursor.fetchone()

        if result is None:
            flash(f'Cripta {cripta} no encontrada', 'error')
            return redirect(url_for('editar_pago', folio=folio))

        saldo_actual = float(result['Saldo'])

        # Calculamos el saldo total después del abono
        saldo_total = saldo_actual - abono

        fecha_pago = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insertar el pago con el saldo actualizado
        cursor.execute('''
            INSERT INTO Pagos (Folio, Cripta, Saldo, Abono, Saldo_total, Fecha_pago, Notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (folio, cripta, saldo_actual, abono, saldo_total, fecha_pago, notas))

        # Actualizar el saldo de la cripta
        cursor.execute('UPDATE Criptas SET Saldo = ? WHERE Cripta = ?', (saldo_total, cripta))

        conn.commit()
        flash('Pago añadido exitosamente', 'success')
        return redirect(url_for('editar_pago', folio=folio))  # Redirigir a la misma página de edición después de guardar el pago

    # Obtener los datos del pago actual
    cursor.execute('SELECT * FROM Pagos WHERE Folio = ?', (folio,))
    pagos = cursor.fetchall()

    conn.close()
    return render_template('editar_pago.html', pagos=pagos)



# Función para generar un nuevo folio automáticamente
def generate_folio():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Folio) FROM Pagos")  # Obtener el folio más alto
    last_folio = cursor.fetchone()[0]
    conn.close()

    if last_folio:
        # Extraer solo los dígitos del folio
        last_folio_digits = re.findall(r'\d+', last_folio)
        if last_folio_digits:
            last_folio_number = int(last_folio_digits[0])  # Convertir la primera secuencia de dígitos a entero
            new_folio = last_folio_number + 1
        else:
            new_folio = 1  # Si no hay folios existentes, comenzar desde 1
    else:
        new_folio = 1  # Si no hay folios existentes, comenzar desde 1

    return new_folio

#optener todos los pagos
def get_pagos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Pagos')
    pagos = cursor.fetchall()
    conn.close()
    return pagos
#Pagos para cajeros 
@app.route('/pagos_cajero', methods=['GET', 'POST'])
@role_required(['cajera', 'admin']) 

def pagos_cajero():
    if request.method == 'POST':
        cripta = request.form['cripta']
        abono = float(request.form['abono'])
        notas = request.form['notas']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Obtener el saldo actual de la cripta
            cursor.execute('SELECT Saldo FROM Criptas WHERE Cripta = ?', (cripta,))
            result = cursor.fetchone()

            if result:
                saldo_actual = float(result['Saldo'])
                saldo_total = saldo_actual - abono

                # Generar el folio automáticamente
                new_folio = generate_folio()

                fecha_pago = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Insertar el pago en la base de datos
                cursor.execute('''
                    INSERT INTO Pagos (Folio, Cripta, Saldo, Abono, Saldo_total, Fecha_pago, Notas)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (new_folio, cripta, saldo_actual, abono, saldo_total, fecha_pago, notas))

                # Actualizar el saldo de la cripta
                cursor.execute('UPDATE Criptas SET Saldo = ? WHERE Cripta = ?', (saldo_total, cripta))

                conn.commit()

                # Mostrar mensaje flash y redirigir
                flash('Pago añadido exitosamente', 'success')
                return redirect(url_for('pagos_cajero'))

            else:
                flash(f'La cripta {cripta} no existe en la base de datos.', 'error')
                return redirect(url_for('pagos_cajero'))

        except Exception as e:
            flash(f'Error al agregar el pago: {str(e)}', 'error')

        finally:
            conn.close()

    # Obtener todos los pagos
    pagos = get_pagos()

    return render_template('pagos.html', pagos=pagos)

# Ruta para configurar pagos
@app.route('/configurar_pagos', methods=['GET', 'POST'])
@role_required('admin')
def configurar_pagos():
    if request.method == 'POST':
        # Obtener los datos del formulario
        monto_mantenimiento = float(request.form['monto_mantenimiento'])
        fecha_inicio = request.form['fecha_inicio']

        # Aquí deberías implementar la lógica para guardar la configuración en la base de datos
        # Supongamos que guardamos la configuración en una lista para simulación
        configuracion = {
            'monto_mantenimiento': monto_mantenimiento,
            'fecha_inicio': fecha_inicio
        }
        # Lógica para guardar la configuración en la base de datos

        # Redirigir nuevamente a la misma página para evitar reenvíos de formulario
        return redirect(url_for('configurar_pagos'))

    # Obtener la configuración actual (esto dependerá de cómo almacenes la configuración)
    configuracion = obtener_configuracion_de_pagos()  # Esta función debe obtener la configuración actual

    # Renderizar la plantilla con la configuración actual
    return render_template('configurar_pagos.html', configuracion=configuracion)

# Función de ejemplo para obtener la configuración de pagos
def obtener_configuracion_de_pagos():
    # Esta es una función de ejemplo, debes adaptarla según cómo almacenes la configuración
    return {
        'monto_mantenimiento': 1500.0,
        'fecha_inicio': '2024-01-01'
    }



################################################################################3
@app.route('/agregar_cripta', methods=['POST'])
def agregar_cripta():
    cripta = request.form['cripta']
    saldo = request.form['saldo']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Criptas (Cripta, Saldo) VALUES (?, ?)", (cripta, saldo))
        conn.commit()
        conn.close()
        print("Cripta agregada correctamente.")
    except sqlite3.IntegrityError:
        print("Error: Ya existe una cripta con ese nombre.")

    return redirect(url_for('configurar_pagos'))

#funcion de retiro de cenizas 
@app.route('/retiro_cenizas', methods=['GET', 'POST'])
@role_required(['cajera', 'admin'])
def retiro_cenizas():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cripta = request.form['cripta']
        fecha_retiro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('SELECT * FROM Difuntos WHERE Cripta = ? AND Fecha_Retiro IS NULL', (cripta,))
        difuntos = cursor.fetchall()

        if not difuntos:
            flash(f'No se encontraron difuntos en la cripta {cripta} o ya fueron retirados', 'error')
        else:
            cursor.execute('UPDATE Difuntos SET Fecha_Retiro = ? WHERE Cripta = ?', (fecha_retiro, cripta))
            conn.commit()
            flash('Cenizas retiradas exitosamente', 'success')

    cursor.execute('SELECT * FROM Difuntos WHERE Fecha_Retiro IS NULL')
    difuntos = cursor.fetchall()
    conn.close()

    return render_template('retiro_cenizas.html', difuntos=difuntos)

#funcion de giltrado de pagos 

@app.route('/filtrado_pagos', methods=['GET', 'POST'])
@role_required('admin')
def filtrado_pagos():
    filtro = request.args.get('filtro', 'mes')
    cripta = request.args.get('cripta', None)
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.today()
    start_date = None

    if filtro == 'semana':
        start_date = today - timedelta(days=today.weekday())  # Start of the current week
    elif filtro == 'mes':
        start_date = today.replace(day=1)  # Start of the current month
    elif filtro == 'año':
        start_date = today.replace(month=1, day=1)  # Start of the current year

    query = 'SELECT * FROM Pagos WHERE 1=1'
    params = []

    if start_date:
        start_date_str = start_date.strftime('%Y-%m-%d')
        query += ' AND Fecha_pago >= ?'
        params.append(start_date_str)

    if cripta:
        query += ' AND Cripta = ?'
        params.append(cripta)

    cursor.execute(query, params)
    pagos = cursor.fetchall()
    conn.close()
    
    return render_template('filtrado_pagos.html', pagos=pagos, filtro=filtro, cripta=cripta)

# Asegúrate de tener otras rutas y funciones aquí, como login, menu, etc.


if __name__ == '__main__':
    app.run(debug=True)
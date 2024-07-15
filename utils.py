# utils.py

from app import db
from .models import Clientes, Usuarios, Difuntos, Pagos, Criptas, ConfiguracionPagos, CobrosMantenimiento
from datetime import datetime
import re

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
def sumar_a_saldos(monto_sumar):
    try:
        db.session.execute('UPDATE Criptas SET Saldo = Saldo + :monto_sumar', {'monto_sumar': monto_sumar})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

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

# Obtener la configuración de pagos
def obtener_configuracion_de_pagos():
    try:
        conn = db.session.connection()
        result = conn.execute('SELECT monto_mantenimiento, fecha_inicio, hora_inicio FROM ConfiguracionPagos WHERE id = 1').fetchone()
        
        if result:
            return {
                'monto_mantenimiento': result[0],
                'fecha_inicio': result[1].strftime('%Y-%m-%d'),
                'hora_inicio': result[2]
            }
        else:
            return {
                'monto_mantenimiento': 0.0,
                'fecha_inicio': datetime.now().strftime('%Y-%m-%d'),
                'hora_inicio': datetime.now().strftime('%H:%M')
            }
    except Exception as e:
        raise e
    finally:
        conn.close()

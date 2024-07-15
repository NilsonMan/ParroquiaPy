# importaciones necesarias
import pandas as pd
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Leer el archivo Excel
archivo_excel = 'C:/Users/nilso/Downloads/RELLENADO.xlsx'
hoja = 'Hoja1'  # Especifica el nombre correcto de la hoja
df = pd.read_excel(archivo_excel, sheet_name=hoja)

# Renombrar las columnas del DataFrame para que coincidan con la estructura de la tabla Clientes
df.columns = [
    'Cripta', 'Nombre_titular', 'Apellido_paterno', 'Apellido_materno', 'Telefono1', 'Direccion1',
    'Nombre_Beneficiario', 'Apellido_paterno_Beneficiario', 'Apellido_materno_Beneficiario', 'Telefono_Beneficiario',
    'Direccion_Beneficiario', 'Nombre_Beneficiario2', 'Apellido_paterno_Beneficiario2', 'Apellido_materno_Beneficiario2',
    'Telefono_Beneficiario2', 'Direccion_Beneficiario2'
]

# Insertar los datos en la base de datos
from app import db, Clientes

# Iterar sobre las filas del DataFrame e insertar en la base de datos
for indice, fila in df.iterrows():
    nuevo_cliente = Clientes(
        Cripta=fila['Cripta'],
        Nombre_titular=fila['Nombre_titular'],
        Apellido_paterno=fila['Apellido_paterno'],
        Apellido_materno=fila['Apellido_materno'],
        Telefono1=fila['Telefono1'],
        Direccion1=fila['Direccion1'],
        Nombre_Beneficiario=fila['Nombre_Beneficiario'],
        Apellido_paterno_Beneficiario=fila['Apellido_paterno_Beneficiario'],
        Apellido_materno_Beneficiario=fila['Apellido_materno_Beneficiario'],
        Telefono_Beneficiario=fila['Telefono_Beneficiario'],
        Direccion_Beneficiario=fila['Direccion_Beneficiario'],
        Nombre_Beneficiario2=fila['Nombre_Beneficiario2'],
        Apellido_paterno_Beneficiario2=fila['Apellido_paterno_Beneficiario2'],
        Apellido_materno_Beneficiario2=fila['Apellido_materno_Beneficiario2'],
        Telefono_Beneficiario2=fila['Telefono_Beneficiario2'],
        Direccion_Beneficiario2=fila['Direccion_Beneficiario2']
    )
    
    # Agregar el nuevo cliente a la sesión
    db.session.add(nuevo_cliente)

# Confirmar todos los cambios en la sesión
db.session.commit()

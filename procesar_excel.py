
import pandas as pd
import sqlite3

# Leer el archivo Excel
archivo_excel = 'C:/Users/nilso/Downloads/RELLENADO.xlsx'
hoja = 'Hoja1'  # Especifica el nombre correcto de la hoja
df = pd.read_excel(archivo_excel, sheet_name=hoja)

# Imprimir las primeras filas del DataFrame para verificar que se ha leído correctamente
print(df.head())

# Renombrar las columnas del DataFrame para que coincidan con la estructura de la tabla Clientes
df.columns = [
    'Cripta', 'Nombre_titular', 'Apellido_paterno', 'Apellido_materno', 'Telefono1', 'Direccion1',
    'Nombre_Beneficiario', 'Apellido_paterno_Beneficiario', 'Apellido_materno_Beneficiario', 'Telefono_Beneficiario',
    'Direccion_Beneficiario', 'Nombre_Beneficiario2', 'Apellido_paterno_Beneficiario2', 'Apellido_materno_Beneficiario2',
    'Telefono_Beneficiario2', 'Direccion_Beneficiario2'
]

# Imprimir las primeras filas del DataFrame para verificar los cambios en las columnas
print(df.head())

# Conectarse a la base de datos SQLite
conexion = sqlite3.connect('C:/Users/nilso/Downloads/proyectos/Parroquia!/cripta_administracion.db')

# Crear un cursor
cursor = conexion.cursor()


# Insertar los datos en la tabla de la base de datos
for indice, fila in df.iterrows():
    cursor.execute(
        '''
        INSERT INTO Clientes (
            Cripta, Nombre_titular, Apellido_paterno, Apellido_materno, Telefono1, Direccion1,
            Nombre_Beneficiario, Apellido_paterno_Beneficiario, Apellido_materno_Beneficiario, Telefono_Beneficiario,
            Direccion_Beneficiario, Nombre_Beneficiario2, Apellido_paterno_Beneficiario2, Apellido_materno_Beneficiario2,
            Telefono_Beneficiario2, Direccion_Beneficiario2
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            fila['Cripta'], fila['Nombre_titular'], fila['Apellido_paterno'], fila['Apellido_materno'], fila['Telefono1'],
            fila['Direccion1'], fila['Nombre_Beneficiario'], fila['Apellido_paterno_Beneficiario'], fila['Apellido_materno_Beneficiario'],
            fila['Telefono_Beneficiario'], fila['Direccion_Beneficiario'], fila['Nombre_Beneficiario2'],
            fila['Apellido_paterno_Beneficiario2'], fila['Apellido_materno_Beneficiario2'], fila['Telefono_Beneficiario2'],
            fila['Direccion_Beneficiario2']
        )
    )

# Confirmar los cambios
conexion.commit()

# Cerrar la conexión
conexion.close()

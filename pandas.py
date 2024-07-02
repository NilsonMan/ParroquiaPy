import pandas as pd
import sqlite3

# Leer el archivo Excel
archivo_excel = 'ruta/al/archivo.xlsx'
hoja = 'nombre_hoja'  # Especifica el nombre de la hoja si es necesario
df = pd.read_excel(archivo_excel, sheet_name=hoja)

# Imprimir las primeras filas del DataFrame para verificar que se ha leído correctamente
print(df.head())

# Conectarse a la base de datos SQLite
conexion = sqlite3.connect('ruta/a/la/base_de_datos.db')

# Crear un cursor
cursor = conexion.cursor()

# Insertar los datos en la tabla de la base de datos
for indice, fila in df.iterrows():
    cursor.execute(
        '''
        INSERT INTO TablaDestino (columna1, columna2, columna3)
        VALUES (?, ?, ?)
        ''',
        (fila['columna1'], fila['columna2'], fila['columna3'])
    )

# Confirmar los cambios
conexion.commit()

# Cerrar la conexión
conexion.close()

import pandas as pd
from app import app, db, Criptas  # Asegúrate de importar la app y el modelo

# Leer el archivo Excel
archivo_excel = 'C:/Users/nilso/Downloads/RELLENADO.xlsx'
hoja = 'Hoja2'  # Especifica el nombre correcto de la segunda hoja
df = pd.read_excel(archivo_excel, sheet_name=hoja)

# Renombrar las columnas del DataFrame para que coincidan con la estructura de la tabla Criptas
df.columns = ['Cripta', 'Saldo']

with app.app_context():  # Crear el contexto de la aplicación
    # Iterar sobre las filas del DataFrame e insertar en la base de datos
    for indice, fila in df.iterrows():
        nueva_cripta = Criptas(
            Cripta=fila['Cripta'],
            Saldo=fila['Saldo']
        )
        
        # Agregar la nueva cripta a la sesión
        db.session.add(nueva_cripta)

    # Confirmar todos los cambios en la sesión
    db.session.commit()

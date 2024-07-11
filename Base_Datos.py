import sqlite3

# Conectar a la base de datos
conexion = sqlite3.connect('cripta_administracion.db')
cursor = conexion.cursor()

# Crear tabla Clientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS Clientes (
    Cripta TEXT PRIMARY KEY,
    Nombre_titular TEXT,
    Apellido_paterno TEXT,
    Apellido_materno TEXT,
    Telefono1 TEXT,
    Direccion1 TEXT,
    Nombre_Beneficiario TEXT,
    Apellido_paterno_Beneficiario TEXT,
    Apellido_materno_Beneficiario TEXT,
    Telefono_Beneficiario TEXT,
    Direccion_Beneficiario TEXT,
    Nombre_Beneficiario2 TEXT,
    Apellido_paterno_Beneficiario2 TEXT,
    Apellido_materno_Beneficiario2 TEXT,
    Telefono_Beneficiario2 TEXT,
    Direccion_Beneficiario2 TEXT
)
''')

#cursor.execute('DROP TABLE IF EXISTS Clientes')
# Crear tabla Difuntos
cursor.execute('''
CREATE TABLE IF NOT EXISTS Difuntos (
    ID_difunto INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_completo TEXT,
    Apellido_paterno TEXT,
    Apellido_materno TEXT,
    Cripta TEXT,
    Fecha_defuncion DATE,
    Fecha DATE,
    Fecha_Retiro DATE,
    FOREIGN KEY (Cripta) REFERENCES Clientes(Cripta)
)
''')
#cursor.execute('DROP TABLE IF EXISTS Difuntos')
# Crear tabla Familia
cursor.execute('''
CREATE TABLE IF NOT EXISTS Familia (
    Familia_id INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre_familia TEXT,
    Cripta TEXT,
    ID_difunto INTEGER,
    FOREIGN KEY (Cripta) REFERENCES Clientes(Cripta),
    FOREIGN KEY (ID_difunto) REFERENCES Difuntos(ID_difunto)
)
''')

# Crear tabla Pagos
cursor.execute('''
CREATE TABLE IF NOT EXISTS Pagos (
    Folio TEXT PRIMARY KEY,
    Cripta TEXT,
    Saldo REAL,
    Abono REAL,
    Saldo_total REAL,
    Fecha_pago TEXT,
    Notas TEXT,
    FOREIGN KEY (Cripta) REFERENCES Clientes(Cripta)
)
''')

#cursor.execute('DROP TABLE IF EXISTS pagos')

# Crear tabla Documentacion
cursor.execute('''
CREATE TABLE IF NOT EXISTS Documentacion (
    ID_documentacion INTEGER PRIMARY KEY AUTOINCREMENT,
    Cripta TEXT,
    Tipo_documento TEXT,
    Documento BLOB,
    Observaciones TEXT,
    FOREIGN KEY (Cripta) REFERENCES Clientes(Cripta)
)
''')

#cursor.execute('DROP TABLE IF EXISTS Documentacion')

# Crear tabla Usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ConfiguracionPagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monto_mantenimiento REAL,
    fecha_inicio DATE,
    hora_inicio TEXT
)
''')
#cursor.execute('DROP TABLE IF EXISTS Configuracionpagos')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS Criptas (
            Cripta TEXT PRIMARY KEY,
            Saldo REAL NOT NULL
        )
    ''')
#ursor.execute('DROP TABLE IF EXISTS Criptas')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS Documentos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Tipo TEXT NOT NULL,
            Archivo BLOB NOT NULL,
            Fecha_subida TEXT,
            Observaciones TEXT
        )
    ''')
#cursor.execute('DROP TABLE IF EXISTS Criptas')

#cursor.execute('DROP TABLE IF EXISTS CobrosMantenimiento')



#cursor.execute('DROP TABLE IF EXISTS CobrosMantenimiento')

# Confirmar cambios y cerrar la conexión
conexion.commit()
conexion.close()

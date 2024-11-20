import mysql
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'soporte',
    'port': 3306  # Cambia si tu MySQL usa otro puerto
}
try:
    connection = mysql.connector.connect(**DB_CONFIG)
    if connection.is_connected():
        print("Conexión exitosa a MySQL.")
        connection.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
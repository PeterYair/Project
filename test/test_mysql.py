import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Autonoma24$',
        database='soporte',
        port=3306
    )
    if connection.is_connected():
        print("Conexión exitosa a la base de datos.")
        connection.close()
except mysql.connector.Error as err:
    print(f"Error al conectar: {err}")

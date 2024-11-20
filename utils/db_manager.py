import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def conectar():
    """
    Establece una conexión con la base de datos usando los parámetros de configuración.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None


def obtener_servicios():
    """
    Obtiene todos los servicios almacenados en la base de datos.
    """
    try:
        connection = conectar()
        if connection is None:
            raise Exception("No se pudo conectar a la base de datos.")

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, url, estado FROM servicios")
        servicios = cursor.fetchall()
        connection.close()
        return servicios
    except Error as e:
        print(f"Error al obtener servicios: {e}")
        return []


def agregar_servicio(nombre, url):
    """
    Agrega un nuevo servicio a la base de datos.
    """
    try:
        connection = conectar()
        if connection is None:
            raise Exception("No se pudo conectar a la base de datos.")

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO servicios (nombre, url, estado) VALUES (%s, %s, %s)",
            (nombre, url, "offline")
        )
        connection.commit()
        connection.close()
        return True
    except Error as e:
        print(f"Error al agregar el servicio '{nombre}': {e}")
        return False


def eliminar_servicio(servicio_id):
    """
    Elimina un servicio de la base de datos por su ID.
    """
    try:
        connection = conectar()
        if connection is None:
            raise Exception("No se pudo conectar a la base de datos.")

        cursor = connection.cursor()
        cursor.execute("DELETE FROM servicios WHERE id = %s", (servicio_id,))
        connection.commit()
        connection.close()
        return True
    except Error as e:
        print(f"Error al eliminar el servicio con ID '{servicio_id}': {e}")
        return False


def actualizar_servicio(servicio_id, nombre, url):
    """
    Actualiza los datos de un servicio existente en la base de datos.
    """
    try:
        connection = conectar()
        if connection is None:
            raise Exception("No se pudo conectar a la base de datos.")

        cursor = connection.cursor()
        cursor.execute(
            "UPDATE servicios SET nombre = %s, url = %s WHERE id = %s",
            (nombre, url, servicio_id)
        )
        connection.commit()
        connection.close()
        return True
    except Error as e:
        print(f"Error al actualizar el servicio con ID '{servicio_id}': {e}")
        return False


def actualizar_estado_servicio(servicio_id, estado):
    """
    Actualiza el estado de un servicio en la base de datos.
    """
    try:
        connection = conectar()
        if connection is None:
            raise Exception("No se pudo conectar a la base de datos.")

        cursor = connection.cursor()
        cursor.execute(
            "UPDATE servicios SET estado = %s WHERE id = %s",
            (estado, servicio_id)
        )
        connection.commit()
        connection.close()
        return True
    except Error as e:
        print(f"Error al actualizar el estado del servicio con ID '{servicio_id}': {e}")
        return False


def registrar_estado(servicio_id, estado, hora):
    """
    Registra un cambio de estado en la tabla historial.
    """
    try:
        connection = conectar()
        if connection is None:
            raise Exception("No se pudo conectar a la base de datos.")

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO historial (servicio_id, estado, hora) VALUES (%s, %s, %s)",
            (servicio_id, estado, hora)
        )
        connection.commit()
        connection.close()
        return True
    except Error as e:
        print(f"Error al registrar el estado del servicio con ID '{servicio_id}': {e}")
        return False


def obtener_historial_estado(servicio_id):
    """
    Obtiene el historial de cambios de estado de un servicio específico.
    """
    try:
        connection = conectar()
        if connection is None:
            raise Exception("No se pudo conectar a la base de datos.")

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT hora, estado FROM historial WHERE servicio_id = %s ORDER BY hora ASC",
            (servicio_id,)
        )
        historial = cursor.fetchall()
        connection.close()
        return historial
    except Error as e:
        print(f"Error al obtener el historial del servicio con ID '{servicio_id}': {e}")
        return []

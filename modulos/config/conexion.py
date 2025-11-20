import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='bxn6iph4ppjxlv2yiykm-mysql.services.clever-cloud.com',
            user='ubjkfbdeovoghrwe',
            password='eLp25GP5H0OKWtJ8Lggt',
            database='bxn6iph4ppjxlv2yiykm',
            port=3306
        )
        if conexion.is_connected():
            print("✅ Conexión establecida")
            return conexion
        else:
            print("❌ Conexión fallida (is_connected = False)")
            return None
    except mysql.connector.Error as e:
        print(f"❌ Error al conectar: {e}")
        return None


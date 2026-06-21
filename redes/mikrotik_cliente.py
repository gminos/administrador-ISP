import routeros_api
import logging

logger = logging.getLogger(__name__)

def _conectar(ip, usuario, password, puerto=8728):
    connection = routeros_api.RouterOsApiPool(
        host=ip,
        username=usuario,
        password=password,
        port=puerto,
        plaintext_login=True
    )
    return connection

def suspender_cliente(router, pppoe_user):
    try:
        connection = _conectar(router.ip, router.usuario, router.password, router.puerto_api)
        api = connection.get_api()

        secrets = api.get_resource('/ppp/secret')
        usuario_encontrado = secrets.get(name=pppoe_user)

        if not usuario_encontrado:
            connection.disconnect()
            return False, f"El usuario '{pppoe_user}' no existe en el router."

        secret_id = usuario_encontrado[0]['id']
        secrets.set(id=secret_id, disabled='true')

        activas = api.get_resource('/ppp/active')
        sesion_activa = activas.get(name=pppoe_user)
        if sesion_activa:
            active_id = sesion_activa[0]['id']
            activas.remove(id=active_id)
        connection.disconnect()

        return True, "Cliente suspendido exitosamente."
    except Exception as e:
        logger.error(f"Error suspendiendo {pppoe_user} en {router.ip}: {str(e)}")
        return False, f"Error de conexión: {str(e)}"

def reactivar_cliente(router, pppoe_user):
    try:
        connection = _conectar(router.ip, router.usuario, router.password, router.puerto_api)
        api = connection.get_api()

        secrets = api.get_resource('/ppp/secret')
        usuario_encontrado = secrets.get(name=pppoe_user)

        if not usuario_encontrado:
            connection.disconnect()
            return False, f"El usuario '{pppoe_user}' no existe en el router."

        secret_id = usuario_encontrado[0]['id']
        secrets.set(id=secret_id, disabled='false')

        connection.disconnect()

        return True, "Cliente reactivado exitosamente."
    except Exception as e:
        logger.error(f"Error reactivando {pppoe_user} en {router.ip}: {str(e)}")
        return False, f"Error de conexión: {str(e)}"

def consultar_estado_cliente(router, pppoe_user):
    try:
        connection = _conectar(router.ip, router.usuario, router.password, router.puerto_api)
        api = connection.get_api()

        activas = api.get_resource('/ppp/active')
        sesion_activa = activas.get(name=pppoe_user)
        connection.disconnect()

        if sesion_activa:
            ip_asignada = sesion_activa[0].get('address', 'Desconocida')
            tiempo = sesion_activa[0].get('uptime', 'Desconocido')
            return True, True, f"Conectado (IP: {ip_asignada}, Uptime: {tiempo})"
        else:
            return True, False, "Desconectado"

    except Exception as e:
        logger.error(f"Error consultando {pppoe_user} en {router.ip}: {str(e)}")
        return False, False, f"Error de conexión: {str(e)}"

def obtener_desconectados(router):
    try:
        connection = _conectar(router.ip, router.usuario, router.password, router.puerto_api)
        api = connection.get_api()

        secrets = api.get_resource('/ppp/secret').get()
        activos = api.get_resource('/ppp/active').get()
        connection.disconnect()

        usuarios_habilitados = set([s.get('name') for s in secrets if s.get('disabled') == 'false'])
        usuarios_conectados = set([a.get('name') for a in activos])

        desconectados = usuarios_habilitados - usuarios_conectados

        return True, list(desconectados)
    except Exception as e:
        logger.error(f"Error obteniendo desconectados en {router.ip}: {str(e)}")
        return False, str(e)

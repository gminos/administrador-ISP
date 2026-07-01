import routeros_api
import logging

logger = logging.getLogger(__name__)

def _conectar(router):
    ip_destino = router.ip_vpn if router.ip_vpn else router.ip
    
    if not ip_destino:
        raise ValueError("El router no tiene ni IP de VPN ni IP pública configurada.")
        
    connection = routeros_api.RouterOsApiPool(
        host=ip_destino,
        username=router.usuario,
        password=router.password,
        port=router.puerto_api,
        plaintext_login=True
    )
    return connection

def suspender_cliente(router, pppoe_usuario):
    try:
        connection = _conectar(router)
        api = connection.get_api()

        secrets = api.get_resource('/ppp/secret')
        usuario_encontrado = secrets.get(name=pppoe_usuario)

        if not usuario_encontrado:
            connection.disconnect()
            return False, f"El usuario '{pppoe_usuario}' no existe en el router."

        secret_id = usuario_encontrado[0]['id']
        secrets.set(id=secret_id, disabled='true')

        activas = api.get_resource('/ppp/active')
        sesion_activa = activas.get(name=pppoe_usuario)
        if sesion_activa:
            active_id = sesion_activa[0]['id']
            activas.remove(id=active_id)

        connection.disconnect()

        return True, "Cliente suspendido exitosamente."
    except Exception as e:
        logger.error(f"Error suspendiendo {pppoe_usuario} en {router.ip}: {str(e)}")
        return False, f"Error de conexión: {str(e)}"

def suspender_clientes_masivo(router, pppoe_usuarios):
    suspendidos_exitosos = []
    suspendidos_fallidos = []

    try:
        connection = _conectar(router)
        api = connection.get_api()
        secrets = api.get_resource('/ppp/secret')
        activas = api.get_resource('/ppp/active')

        for pppoe_usuario in pppoe_usuarios:
            usuario_encontrado = secrets.get(name=pppoe_usuario)

            if not usuario_encontrado:
                suspendidos_fallidos.append(pppoe_usuario)
                continue

            secret_id = usuario_encontrado[0]['id']
            secrets.set(id=secret_id, disabled='true')
            suspendidos_exitosos.append(pppoe_usuario)
            sesion_activa = activas.get(name=pppoe_usuario)

            if sesion_activa:
                active_id = sesion_activa[0]['id']
                activas.remove(id=active_id)

        connection.disconnect()

        return suspendidos_exitosos, suspendidos_fallidos
    except Exception as e:
        logger.error(f"Error suspendiendo a {len(pppoe_usuarios)} pppoe_users: {str(e)}")
        return suspendidos_exitosos, [usuario for usuario in pppoe_usuarios if usuario not in suspendidos_exitosos]

def reactivar_cliente(router, pppoe_user):
    try:
        connection = _conectar(router)
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
        connection = _conectar(router)
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
        connection = _conectar(router)
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

def obtener_conectados(router):
    try:
        connection = _conectar(router)
        api = connection.get_api()
        activos = api.get_resource('/ppp/active').get()
        connection.disconnect()
        usuarios_conectados = [a.get('name') for a in activos]
        return True, usuarios_conectados
    except Exception as e:
        logger.error(f"Error obteniendo conectados en {router.ip}: {str(e)}")
        return False, str(e)

def sincronizar_perfil_ppp(router, plan_nombre, megas):
    try:
        connection = _conectar(router)
        api = connection.get_api()
        profiles = api.get_resource('/ppp/profile')
        perfil_existente = profiles.get(name=plan_nombre)
        rate_limit = f"{megas}M/{megas}M"

        if perfil_existente:
            profile_id = perfil_existente[0]['id']
            profiles.set(id=profile_id, **{'rate-limit': rate_limit})
        else:
            profiles.add(name=plan_nombre, **{'rate-limit': rate_limit, 'only-one': 'yes'})

        connection.disconnect()
        return True, "Perfil sincronizado exitosamente."
    except Exception as e:
        logger.error(f"Error sincronizando perfil {plan_nombre} en {router.ip}: {str(e)}")
        return False, f"Error de conexión: {str(e)}"

def eliminar_perfil_ppp(router, plan_nombre):
    try:
        connection = _conectar(router)
        api = connection.get_api()
        profiles = api.get_resource('/ppp/profile')
        perfil_existente = profiles.get(name=plan_nombre)

        if perfil_existente:
            profile_id = perfil_existente[0]['id']
            profiles.remove(id=profile_id)

        connection.disconnect()
        return True, "Perfil eliminado exitosamente."
    except Exception as e:
        logger.error(f"Error eliminando perfil {plan_nombre} en {router.ip}: {str(e)}")
        return False, str(e)

def sincronizar_secret_ppp(router, usuario, password, plan_nombre, ip_estatica=None):
    try:
        connection = _conectar(router)
        api = connection.get_api()
        secrets = api.get_resource('/ppp/secret')
        secret_existente = secrets.get(name=usuario)

        params = {
            'password': password,
            'profile': plan_nombre,
            'service': 'pppoe'
        }
        if ip_estatica:
            params['remote-address'] = ip_estatica
        elif secret_existente and 'remote-address' in secret_existente[0]:
             params['remote-address'] = ""

        if secret_existente:
            secret_id = secret_existente[0]['id']
            secrets.set(id=secret_id, **params)
        else:
            secrets.add(name=usuario, **params)

        connection.disconnect()
        return True, "Secret sincronizado exitosamente."
    except Exception as e:
        logger.error(f"Error sincronizando secret {usuario} en {router.ip}: {str(e)}")
        return False, f"Error de conexión: {str(e)}"

def eliminar_secret_ppp(router, usuario):
    try:
        connection = _conectar(router)
        api = connection.get_api()
        secrets = api.get_resource('/ppp/secret')
        secret_existente = secrets.get(name=usuario)

        if secret_existente:
            secret_id = secret_existente[0]['id']
            secrets.remove(id=secret_id)

        connection.disconnect()
        return True, "Secret eliminado exitosamente."
    except Exception as e:
        logger.error(f"Error eliminando secret {usuario} en {router.ip}: {str(e)}")
        return False, str(e)

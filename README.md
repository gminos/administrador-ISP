# Administrador ISP - Arint Conexiones

## Descripción

Sistema integral para la gestión y administración de proveedores de servicios de internet (ISP). Desarrollado en Django, este proyecto funciona como una plataforma completa que automatiza operaciones críticas como facturación, control de pagos, notificaciones a clientes y aprovisionamiento directo de routers Mikrotik.

## Características Principales

* **Gestión de Clientes e Instalaciones:** Registro detallado de abonados, planes de internet asignados y datos técnicos de conexión (asignación de routers y credenciales PPPoE).
* **Facturación y Caja Rápida:** Generación masiva de facturas mensuales, registro de abonos y cancelación de deudas con sistema de prioridades matemáticas (mensualidad, reconexión, instalación). Generación de recibos de pago en formato PDF.
* **Integración con Mikrotik (RouterOS API):** Comunicación en tiempo real con los equipos de red. Permite visualizar clientes conectados, suspender servicios de forma manual o automática y reactivarlos sin salir del sistema.
* **Automatización de Procesos (Celery y Redis):** Ejecución de procesos en segundo plano para el corte automático de clientes morosos en la madrugada, reactivación inmediata al registrar pagos y generación masiva de facturación sin interrumpir el servidor web.
* **Notificaciones por WhatsApp:** Integración para el envío automatizado de facturas pendientes y comprobantes de pago directamente a los números de los clientes.
* **Interfaz de Administración Avanzada:** Interfaz de usuario potenciada por Django Unfold para una experiencia administrativa moderna, fluida y responsiva.

## Requisitos del Sistema

* Docker y Docker Compose
* Python 3.13+ (para desarrollo local con UV)
* Router Mikrotik accesible a través del puerto de la API (por defecto 8728)

## Instalación y Ejecución

1. **Clonar el repositorio:**

```bash 
git clone https://github.com/gminos/arint_conexiones_admin.git
cd arint_conexiones_admin
```

2. **Configurar las variables de entorno:**

Crea un archivo llamado `.env` en la raíz del proyecto y añade la siguiente configuración (ajustando los valores a tu entorno):

```bash
# Base de Datos
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=contraseña
DB_PORT=5432

# Django
DJANGO_SECRET_KEY=clave_secreta
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=True
```

Nota: Para generar una clave secreta segura para Django, puedes ejecutar:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. **Iniciar los servicios con Docker Compose:**

El proyecto incluye múltiples contenedores (Web, Base de Datos, Redis, Celery Worker y Celery Beat). Para construir las imágenes e iniciarlos todos en segundo plano:

```bash
docker compose up -d --build
```

4. **Crear un superusuario:**

Este paso es obligatorio para poder iniciar sesión en el panel de control por primera vez:

```bash
docker compose exec web uv run python manage.py createsuperuser
```

5. **Acceso al sistema:**

Una vez que los contenedores estén corriendo, abre tu navegador web e ingresa a `http://localhost:8000` (o el puerto configurado en tu máquina virtual). Utiliza las credenciales del superusuario creado en el paso anterior.

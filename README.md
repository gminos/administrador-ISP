# arint_conexiones_admin

## Descripción

Este proyecto personal es una práctica con el framework Django, enfocada en el uso y aprovechamiento del panel administrativo que Django ofrece por defecto. Está diseñado para gestionar información relacionada con usuarios, planes adquiridos y su creación, así como instalaciones, todo aplicado a empresas que brindan servicios de internet.

Con este proyecto, se busca facilitar un manejo más organizado y eficiente de la información general, utilizando el panel administrativo de Django como herramienta para la administración y seguimiento de los datos relevantes para la empresa.

## Tecnologías utilizadas

- [**Django**](https://www.djangoproject.com/): Framework web en Python que facilita el desarrollo rápido y seguro de aplicaciones web.
- [**PostgreSQL**](https://www.postgresql.org/): Sistema de base de datos relacional, robusto y de código abierto.
- [**uv**](https://github.com/astral-sh/uv): Herramienta rápida para gestionar entornos y dependencias en proyectos Python.

## Instalación

Este proyecto utiliza [uv](https://github.com/astral-sh/uv), un gestor rápido de paquetes y entornos virtuales para Python. Antes de comenzar, asegúrate de tener `uv` instalado en tu sistema. Puedes consultar su documentación oficial para la instalación si aún no lo tienes.

### Pasos para ejecutar el proyecto:

1. Clonar el repositorio:

Abre una terminal y ejecuta el siguiente comando para clonar el repositorio localmente:
```bash 
git clone https://github.com/gminos/arint_conexiones_admin.git
cd arint_conexiones_admin
```

2. Instalar dependencias

Dentro del directorio del proyecto, ejecuta:
```bash
uv sync
```
Esto creará un entorno virtual automáticamente e instalará todas las dependencias listadas en el archivo `pyproject.toml`.

3. Configurar las variables de entorno

Este proyecto requiere la configuración de variables de entorno para asegurar un funcionamiento adecuado.

- Crea un archivo llamado `.env` en la raíz del proyecto.
- Añade el siguiente contenido, reemplazando los valores según tu configuración:

```bash
DB_NAME=nombre_de_tu_base_de_datos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432

DJANGO_SECRET_KEY=clave_secreta
DJANGO_ALLOWED_HOSTS=localhost # Deja este campo por defecto (localhost) si no te interesa visualizar la pagina en tu LAN
```

- Para generar una clave secreta ingresa el siguiente comando:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

La salida del comando es la clave secreta que tienes que agregar en `DJANGO_SECRET_KEY=`

4. Aplicar migraciones

Ejecuta los siguientes comandos para crear las tablas necesarias en la base de datos:
```bash
uv run python manage.py migrate
```

5. Crear un superusuario

Necesario para acceder al panel de administración de Django:
```bash
uv run python manage.py createsuperuser
```

6. Iniciar el servidor de desarrollo

Puedes iniciar el servidor con:
```bash
uv run python manage.py runserver
```
Accede al panel administrativo desde http://localhost:8000 con las credenciales del superusuario que creaste.

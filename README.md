## Descripción

Este proyecto personal es una práctica con el framework Django, enfocada en el uso y aprovechamiento del panel administrativo que Django ofrece por defecto. Está diseñado para gestionar información relacionada con usuarios, planes adquiridos y su creación, así como instalaciones, todo aplicado a empresas que brindan servicios de internet.

Con este proyecto, se busca facilitar un manejo más organizado y eficiente de la información general, utilizando el panel administrativo de Django como herramienta para la administración y seguimiento de los datos relevantes para la empresa.

### Pasos para ejecutar el proyecto:

1. Clonar el repositorio:

Abre una terminal y ejecuta el siguiente comando para clonar el repositorio localmente:
```bash 
git clone https://github.com/gminos/arint_conexiones_admin.git
cd arint_conexiones_admin
```

2. Configurar las variables de entorno

Este proyecto requiere la configuración de variables de entorno para asegurar un funcionamiento adecuado.

- Crea un archivo llamado `.env` en la raíz del proyecto.
- Añade el siguiente contenido, reemplazando los valores según tu configuración:

```bash
DB_NAME=nombre_base_datos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_PORT=5432

DJANGO_SECRET_KEY=clave_secreta
DJANGO_ALLOWED_HOSTS=localhost
```

- Para generar una clave secreta ingresa el siguiente comando:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

La salida del comando es la clave secreta que tienes que agregar en `DJANGO_SECRET_KEY=`

3. Inicia el proyecto con:

```bash
docker compose up -d --build
```

4. Crear un superusuario

Necesario para acceder al panel de administración de Django:
```bash
docker compose exec web uv run python manage.py createsuperuser
```

Acceda al panel administrativo desde http://localhost con las credenciales del superusuario que creaste.

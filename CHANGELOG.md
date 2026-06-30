# Registro de Cambios (Changelog)

Todas las novedades, cambios y correcciones del proyecto Administrador ISP serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto se adhiere a [Versionamiento Semántico (SemVer)](https://semver.org/lang/es/).

## [2.1.0] - 2026-06-29

### Agregado
- **Adoctrinamiento Automático de Routers:** Nuevo sistema de señales (`signals.py`) en la aplicación de redes que detecta cuando un ISP registra un nuevo enrutador Mikrotik. Al ser detectado, se dispara una tarea asíncrona en Celery que busca todos los planes existentes en la base de datos del inquilino y los inyecta automáticamente en el nuevo equipo, eliminando la necesidad de sincronización manual y mejorando la experiencia de onboarding (UX).

## [2.0.1] - 2026-06-29

### Corregido
- **Caché y Assets Estáticos:** Implementado nuevo logotipo vectorial (`.svg`) de fondo transparente con branding oficial de NucleoISP. Se forzó la invalidación del caché estático cambiando las referencias en `settings.py` para asegurar que el cambio se refleje instantáneamente en las interfaces en la nube.

## [2.0.0] - 2026-06-29

Esta versión marca la evolución del proyecto de un Gestor ISP individual a una Plataforma SaaS B2B Multi-Inquilino. Ahora el sistema es capaz de alojar y gestionar a múltiples ISPs simultáneamente con aislamiento de bases de datos, control financiero y automatización de clientes.

### Agregado
- **Facturación SaaS B2B:** Nuevo modelo de gestión financiera para inquilinos (EmpresaISP) que incluye campos de estado de cuenta, fecha de próximo pago y días de gracia.
- **Middleware "Kill Switch":** Sistema de seguridad y proxy reverso que bloquea automáticamente a los ISPs morosos, redirigiendo su tráfico a una pantalla de "Servicio Suspendido".
- **Onboarding Automatizado:** Envío automático de credenciales (usuario y contraseña temporal) por correo electrónico al registrar un nuevo ISP, garantizando el principio de "Cero Confianza" (Zero Trust).
- **App Usuarios:** Nueva aplicación dedicada para la gestión del modelo de usuarios base (`usuarios`).

### Modificado
- **Arquitectura Multi-tenant:** Refactorización masiva de bases de datos utilizando esquemas de PostgreSQL (`django-tenants`), rompiendo la compatibilidad con el esquema público original de la v1.0.0 para lograr aislamiento de datos por ISP.
- **Estructura de Señales (Signals):** Implementación de archivos `signals.py` separados para las apps de facturación, instalaciones y planes para desacoplar la lógica de negocio.
- **Dependencias Docker:** Actualización de `pyproject.toml` y `docker-compose.yml` para reflejar el uso del gestor de paquetes `uv`.

### Corregido
- **Filtro Celery WhatsApp:** Solucionado error en el modelo de consultas asíncronas de facturación, asegurando que los recibos solo se generen para facturas en mora o estado parcial.

## [1.0.0] - 2026-06-21

Esta es la primera versión oficial estable ("Lanzamiento Inicial"). Convierte el proyecto de una prueba de concepto en un software completo de gestión para Proveedores de Servicios de Internet (ISP), incorporando control total sobre la red y automatización de cobros.

### Agregado (Nuevas Funciones)
- **Integración Mikrotik:** Comunicación bidireccional con equipos RouterOS mediante la API (Puerto 8728).
- **Control de Red:** Posibilidad de verificar usuarios conectados (Active Sessions) directamente desde el panel de instalaciones.
- **Botones de Acción (Admin):** Botones manuales en el panel para Suspender y Reactivar clientes de forma instantánea.
- **Corte Automático (Celery):** Sistema en segundo plano (Celery Beat) programado diariamente a las 00:01 AM para identificar y desconectar a los clientes morosos.
- **Reactivación Inmediata:** Restauración automática de la conexión del cliente al momento de registrar un pago en caja.
- **Inteligencia de Facturación:** El sistema de "Caja Rápida" ahora distribuye los pagos aplicando un peso jerárquico que prioriza las mensualidades sobre los cobros de instalación.
- **Notificaciones WhatsApp:** Generación de recibos PDF y envío automático por WhatsApp utilizando PyWa.

### Modificado
- El archivo `README.md` fue reescrito para eliminar detalles de proyectos anteriores y reflejar la naturaleza real de este sistema como un producto ISP.
- Refactorización de las vistas y modelos de la aplicación `facturacion` para soportar las tareas automáticas en segundo plano.

### Corregido
- Solucionado error visual (formato `NoneType`) al intentar eliminar instalaciones que provocaba la caída del panel.
- Solucionado error donde los pagos en caja absorbían el dinero a favor de las instalaciones viejas en lugar de las mensualidades activas.

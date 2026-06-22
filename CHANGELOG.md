# Registro de Cambios (Changelog)

Todas las novedades, cambios y correcciones del proyecto Administrador ISP serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto se adhiere a [Versionamiento Semántico (SemVer)](https://semver.org/lang/es/).

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

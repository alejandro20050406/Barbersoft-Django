# BarberSoft (Sistema de informacion para barberia)

## 1. Resumen del proyecto

BarberSoft es una plataforma web para la gestion operativa de una barberia. Nace del problema identificado en Monkey's Barber Shop: el registro manual en libreta de servicios, ventas e ingresos, lo que dificulta el control diario, el calculo de comisiones y la generacion de reportes confiables.

La propuesta del sistema centraliza en una sola aplicacion:

- ventas de productos y servicios
- control de clientes y empleados
- catalogos de productos, servicios y metodos de pago
- seguimiento de visitas y comisiones
- reportes operativos

## 2. Contexto del caso de estudio

Segun el documento tecnico base:

- Empresa objetivo: Monkey's Barber Shop (Colima, Mexico).
- Problema principal: procesos manuales sin sistema automatizado.
- Objetivo general: construir un sistema web para gestionar ingresos, ganancias y comisiones.
- Usuarios contemplados: administrador y empleados.
- Plataforma esperada: aplicacion web accesible desde navegador.

## 3. Objetivos funcionales (derivados del caso)

BarberSoft busca cumplir, entre otros, estos objetivos:

- llevar control de servicios y productos vendidos
- registrar clientes y mantener historial de visitas
- registrar empleados y su estado (activo/inactivo)
- obtener ingresos y ganancias por periodos
- calcular y consultar comisiones por empleado
- facilitar corte de caja diario

## 4. Stack tecnologico del repositorio

- Backend: Django 5
- Base de datos: MySQL/MariaDB
- Servidor de aplicacion en desarrollo: `runserver` de Django
- Contenedores: Docker + Docker Compose
- Dependencias principales: `django`, `mysqlclient`, `gunicorn`

## 5. Estructura del proyecto

```text
Barbersoft-Django/
├── apps/
│   ├── accounts/
│   ├── catalogos/
│   ├── clientes/
│   ├── empleados/
│   ├── ventas/
│   └── reportes/
├── config/
│   ├── settings/
│   └── urls.py
├── templates/
├── static/
├── docker-compose.yml
├── Dockerfile
└── manage.py
```

## 6. Modulos actuales del sistema

- `accounts`: inicio y tablero general con metricas.
- `catalogos`: categorias de productos, productos, tipos de servicio, servicios y metodos de pago.
- `clientes`: gestion base de clientes.
- `empleados`: gestion base de empleados y porcentaje de comision.
- `ventas`: entidades transaccionales (venta, detalles, pagos, visitas, comisiones).
- `reportes`: tablero de indicadores agregados de ventas y pagos.

## 7. Modelo de datos principal (resumen)

Entidades clave presentes en el codigo:

- `Cliente`
- `Empleado`
- `CategoriaProducto`, `Producto`
- `TipoServicio`, `Servicio`
- `MetodoDePago`
- `Venta`
- `VentaDetalleProducto`, `VentaDetalleServicio`
- `Pago`
- `Visita`
- `Comision`

## 8. Estado actual del repositorio

Implementado:

- estructura modular en Django
- modelos principales del dominio de negocio
- migraciones base para catalogos, clientes, empleados y ventas
- dashboards iniciales para home, ventas y reportes
- configuracion Docker para entorno local

Por completar (alineado al caso de estudio completo):

- flujos CRUD y formularios transaccionales completos
- logica de negocio en servicios (`apps/ventas/services/`)
- autenticacion y permisos por rol de forma integral
- cobertura de pruebas funcionales y de negocio

## 9. Requisitos

- Docker y Docker Compose
- (opcional sin Docker) Python 3.12+, entorno virtual y servidor MySQL/MariaDB

## 10. Configuracion de entorno

Archivo `.env` esperado por el proyecto

## 11. Ejecucion con Docker (recomendado)

1. Construir y levantar contenedores:

```bash
docker compose up --build
```

2. Ejecutar migraciones:

```bash
docker compose exec web python manage.py migrate
```

3. Crear superusuario (opcional):

```bash
docker compose exec web python manage.py createsuperuser
```

4. Acceder al sistema:

- App: `http://localhost:8000/`
- Admin Django: `http://localhost:8000/admin/`

## 12. Comandos utiles

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py test
```

## 13. Trazabilidad con el caso de estudio

Este repositorio implementa la base tecnica del sistema propuesto para Monkey's Barber Shop y conserva la direccion funcional del caso:

- automatizacion de registro de operaciones
- control de ingresos/comisiones
- gestion centralizada de clientes, empleados y catalogos
- soporte para reportes administrativos

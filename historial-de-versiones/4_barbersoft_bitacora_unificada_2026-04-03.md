# Bitácora unificada de continuidad — BarberSoft

**Fecha de consolidación:** 2026-04-03
**Proyecto:** BarberSoft
**Stack actual de trabajo:** Django + Docker + MariaDB/MySQL + VS Code sobre Windows
**Objetivo de este documento:** unificar las bitácoras previas con todo lo trabajado en la semana del Integrante 3 (Núcleo de Negocio), con detalle suficiente para retomar el proceso sin perder contexto técnico, decisiones, comandos ni criterios de diseño.

---

# 1. Alcance de esta bitácora

Este archivo integra en un solo documento:

1. el contenido del archivo de bitácora del arranque y estructuración del proyecto Django + Docker + MySQL/MariaDB;
2. el contenido del archivo de migración de la base de datos desde XAMPP/MariaDB hacia MariaDB en Docker;
3. todo lo trabajado en sesiones anteriores, especialmente:
   - decisión de modelar **comisiones** como tabla independiente;
   - razonamiento detallado sobre los atributos de la tabla `comisiones`;
   - corrección de tipos monetarios de `FLOAT` a `DECIMAL(10,2)`;
   - problemas encontrados con Workbench y MariaDB al crear la tabla;
   - limpieza estructural de la base;
   - decisiones sobre qué reglas dejar en MariaDB y cuáles mover a Django;
   - evaluación incremental de varios respaldos SQL actualizados.
4. **el trabajo completo del Integrante 3 (Núcleo de Negocio) correspondiente a la semana 2026-04-03**, que incluye:
   - modelado de `ventas`, `venta_detalle_producto`, `venta_detalle_servicio`, `pagos`, `visitas` y `comisiones` en Django;
   - implementación del `admin.py` con inlines;
   - implementación de la validación de negocio `clean()` en el modelo `Comision`;
   - acuerdos de coordinación con el Integrante 2;
   - aclaraciones sobre el entorno de desarrollo (Pylance, Docker, terminal de VS Code).

Este documento está redactado para servir como memoria de continuidad entre sesiones.

---

# 2. Proyecto y contexto general

## 2.1 Nombre y propósito del sistema

**BarberSoft** es un sistema web para la gestión operativa y administrativa de una barbería, enfocado en:

- ventas de servicios;
- ventas de productos;
- control de clientes;
- control de empleados;
- inventario;
- métodos de pago;
- pagos;
- visitas;
- reportes de ingresos, costos y ganancias;
- comisiones por empleado.

El caso de estudio y la estructura funcional general del sistema fueron derivados del material técnico del proyecto Monkey's Barber Shop, donde el sistema sustituye registros manuales en libreta por una solución web con persistencia relacional.

---

## 2.2 Decisión tecnológica vigente

Aunque documentación previa del sistema mencionaba otras bases tecnológicas, durante el proceso de este proyecto se tomó la decisión explícita de implementar BarberSoft con:

- **Django** como framework backend principal;
- **Docker / Docker Compose** para contenerización del entorno;
- **MariaDB/MySQL** como motor relacional;
- **VS Code** como entorno de desarrollo principal;
- **Windows** como sistema anfitrión del usuario.

La decisión arquitectónica adoptada fue construir el sistema como un **monolito modular en Django**, organizado por apps.

---

## 2.3 Razón de la arquitectura modular

Se concluyó que el sistema no convenía como microservicios porque el módulo de ventas es un núcleo con muchas dependencias internas, entre ellas:

- productos;
- servicios;
- clientes;
- pagos;
- inventario;
- reportes;
- comisiones;
- historial de visitas.

Por ello, se eligió la separación funcional por apps Django, manteniendo una sola aplicación global organizada por dominios.

---

# 3. Estructura general propuesta para BarberSoft en Django

## 3.1 Apps definidas para el sistema

Las apps funcionales definidas para el proyecto fueron:

- `accounts`
- `empleados`
- `clientes`
- `catalogos`
- `ventas`
- `reportes`
- `auditoria` *(planteada como dominio futuro, aunque no se creó aún en la estructura base del proyecto al momento de las primeras bitácoras)*

---

## 3.2 Justificación funcional de la separación por apps

### `accounts`
Responsable de autenticación, usuarios, roles y permisos.

### `empleados`
Responsable del CRUD de personal y toda lógica asociada a trabajadores del negocio.

### `clientes`
Responsable del CRUD de clientes y, posteriormente, del historial de visitas.

### `catalogos`
Responsable de productos, servicios, categorías y métodos de pago.

### `ventas`
Responsable del núcleo transaccional: ventas, detalles, pagos, movimientos y comisiones.

### `reportes`
Responsable de consultas agregadas, indicadores de ingresos, costos, ganancias, corte de caja y reportes por periodo.

### `auditoria`
Responsable futuro de la bitácora de acciones críticas.

---

## 3.3 Estructura objetivo general del proyecto

```text
barbersoft/
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── manage.py
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── dev.py
│       └── prod.py
├── apps/
│   ├── __init__.py
│   ├── accounts/
│   ├── empleados/
│   ├── clientes/
│   ├── catalogos/
│   ├── ventas/
│   └── reportes/
├── templates/
├── static/
├── media/
└── docs/
```

---

# 4. Orden correcto de arranque del proyecto

Se dejó asentado que no convenía comenzar por formularios grandes ni por el módulo de ventas. El orden correcto para construir BarberSoft era:

1. levantar la base técnica;
2. conectar Docker y MySQL/MariaDB;
3. estructurar el proyecto Django;
4. crear y registrar apps;
5. dejar autenticación y navegación base;
6. modelar catálogos y entidades maestras;
7. finalmente construir ventas y procesos transaccionales.

## 4.1 Fases sugeridas originalmente

### Fase 1
- Docker + Django + MySQL/MariaDB funcionando
- estructura de apps
- settings y conexión a base
- migraciones iniciales

### Fase 2
- usuario / roles
- login / logout
- menú principal
- menú administrador
- menú empleado

### Fase 3
- entidades maestras y catálogos
- empleados
- clientes
- productos
- servicios
- métodos de pago

### Fase 4
- ventas
- detalle de venta
- pagos
- visitas
- stock
- comisiones

---

# 5. Definición del entorno Docker

## 5.1 Archivos base definidos en raíz

Se indicó crear o completar los siguientes archivos en la raíz del proyecto:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `.env`
- `requirements.txt`
- `manage.py`
- carpeta `config/`
- carpeta `apps/`

---

## 5.2 `requirements.txt`

Contenido propuesto:

```txt
Django>=5.0,<6.0
gunicorn>=22.0
mysqlclient>=2.2
```

---

## 5.3 `Dockerfile`

Contenido propuesto:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
```

---

## 5.4 `.dockerignore`

Contenido propuesto:

```dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
*.sqlite3
.env
.git
.gitignore
venv/
.venv/
media/
staticfiles/
```

### Razón de uso
Se aclaró que `.dockerignore` no es lo mismo que `.gitignore`:

- `.gitignore` evita que Git rastree o suba archivos al repositorio;
- `.dockerignore` evita que Docker copie ciertos archivos al contexto de build.

Se recomendó usarlo desde el inicio para evitar:

- builds lentos;
- imágenes pesadas;
- copia de archivos sensibles o innecesarios.

---

## 5.5 `.env`

Contenido sugerido:

```env
DEBUG=1
SECRET_KEY=django-insegura-solo-desarrollo
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=barbersoft
DB_USER=barbersoft_user
DB_PASSWORD=barbersoft_pass
DB_HOST=db
DB_PORT=3306
```

### Aclaración importante
Dentro de Docker, `DB_HOST` **no debe ser** `localhost`, sino `db`, porque `db` es el nombre del servicio definido en `docker-compose.yml`.

---

## 5.6 `docker-compose.yml`

Versión de trabajo propuesta inicialmente:

```yaml
services:
  web:
    build: .
    container_name: barbersoft_web
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: mysql:8.0
    container_name: barbersoft_db
    restart: always
    environment:
      MYSQL_DATABASE: barbersoft
      MYSQL_USER: barbersoft_user
      MYSQL_PASSWORD: barbersoft_pass
      MYSQL_ROOT_PASSWORD: rootpass
    ports:
      - "3307:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

### Interpretación de puertos
- desde Windows/host: MySQL/MariaDB expuesto en `3307`;
- dentro de Docker: Django se conecta a `db:3306`.

---

# 6. Configuración base de Django

## 6.1 `manage.py`

Se confirmó que `manage.py` debía existir en la raíz del proyecto y apuntar a `config.settings.dev`.

Contenido acordado:

```python
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Verifica que esté instalado."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

---

## 6.2 `config/asgi.py`

```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = get_asgi_application()
```

## 6.3 `config/wsgi.py`

```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = get_wsgi_application()
```

## 6.4 `config/urls.py`

Se propuso una vista mínima de prueba:

```python
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def inicio(request):
    return HttpResponse("BarberSoft funcionando correctamente")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", inicio),
]
```

---

## 6.5 `config/settings/base.py`

Se dejó una configuración base con:

- lectura de variables desde `.env`;
- `BASE_DIR`;
- `SECRET_KEY`;
- `DEBUG`;
- `ALLOWED_HOSTS`;
- apps base de Django;
- middleware;
- templates;
- configuración WSGI / ASGI;
- base de datos en MySQL/MariaDB;
- idioma y zona horaria;
- estáticos y media;
- `DEFAULT_AUTO_FIELD`.

Bloque de base de datos:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
```

---

## 6.6 `config/settings/dev.py`

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
```

## 6.7 `config/settings/prod.py`

```python
from .base import *

DEBUG = False
```

---

# 7. Primer arranque del proyecto y resolución inicial de errores

## 7.1 Comando de arranque

```bash
docker compose up --build
```

Opcional en segundo plano:

```bash
docker compose up --build -d
```

Comandos auxiliares asentados:

```bash
docker compose ps
docker compose logs -f
docker compose down
```

---

## 7.2 Error encontrado: `ALLOWED_HOSTS`

En el primer arranque, Django lanzó el error:

```text
CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
```

### Diagnóstico
El problema no estaba en Docker ni en MySQL/MariaDB, sino en que Django estaba arrancando con:

- `DEBUG = False`, o
- `ALLOWED_HOSTS` vacío o mal leído.

### Correcciones aplicadas/sugeridas
- confirmar `DEBUG=1` en `.env`;
- confirmar `ALLOWED_HOSTS=127.0.0.1,localhost` en `.env`;
- confirmar que `manage.py`, `asgi.py` y `wsgi.py` apunten a `config.settings.dev`;
- reforzar `ALLOWED_HOSTS` en `dev.py`.

---

# 8. Arranque correcto del proyecto base

Después de corregir la configuración:

- la imagen se construyó correctamente;
- `barbersoft_db` quedó listo;
- `barbersoft_web` arrancó correctamente;
- Django corrió `system checks` sin errores;
- el servidor inició en `http://0.0.0.0:8000/`.

### Migraciones pendientes detectadas entonces
Quedaban migraciones base de Django para:

- `admin`
- `auth`
- `contenttypes`
- `sessions`

### Comandos aplicados

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

# 9. Confirmación del panel admin

Se confirmó acceso exitoso a:

```text
http://localhost:8000/admin/
```

Con esto quedó verificado que ya funcionaban correctamente:

- Docker;
- Django;
- MySQL/MariaDB;
- migraciones base;
- panel `/admin`;
- superusuario.

---

# 10. Creación manual de apps y registro en Django

El usuario creó manualmente las carpetas:

- `apps/accounts`
- `apps/catalogos`
- `apps/clientes`
- `apps/empleados`
- `apps/reportes`
- `apps/ventas`
- además de `apps/__init__.py`

Como ya existían manualmente, se indicó:

- no usar `startapp`;
- convertir esas carpetas en apps Django válidas.

---

## 10.1 Estructura mínima requerida por app

Cada app debía contener al menos:

- `__init__.py`
- `admin.py`
- `apps.py`
- `models.py`
- `tests.py`
- `urls.py`
- `views.py`
- carpeta `migrations/`
  - `__init__.py`

---

## 10.2 `apps.py` definidos

### `apps/accounts/apps.py`
```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
```

### `apps/catalogos/apps.py`
```python
from django.apps import AppConfig


class CatalogosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalogos"
```

### `apps/clientes/apps.py`
```python
from django.apps import AppConfig


class ClientesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.clientes"
```

### `apps/empleados/apps.py`
```python
from django.apps import AppConfig


class EmpleadosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.empleados"
```

### `apps/reportes/apps.py`
```python
from django.apps import AppConfig


class ReportesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reportes"
```

### `apps/ventas/apps.py`
```python
from django.apps import AppConfig


class VentasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ventas"
```

---

## 10.3 Registro de apps en `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "apps.accounts.apps.AccountsConfig",
    "apps.catalogos.apps.CatalogosConfig",
    "apps.clientes.apps.ClientesConfig",
    "apps.empleados.apps.EmpleadosConfig",
    "apps.reportes.apps.ReportesConfig",
    "apps.ventas.apps.VentasConfig",
]
```

---

## 10.4 Verificación de integridad del proyecto

Se ejecutó:

```bash
docker compose exec web python manage.py check
```

Resultado:

```text
System check identified no issues (0 silenced).
```

Con ello se confirmó que no había errores base de configuración en:

- `INSTALLED_APPS`;
- `apps.py`;
- estructura general del proyecto.

---

# 11. Migración de la base desde XAMPP hacia MariaDB Docker

## 11.1 Estado previo

- proyecto Django funcionando en Docker;
- base original en XAMPP / MariaDB 10.4;
- base existente con datos reales.

## 11.2 Objetivo

Migrar la base de datos desde XAMPP hacia MariaDB en Docker sin perder información.

---

## 11.3 Respaldo de base

Método usado: **MySQL Workbench**.

Pasos:
1. `Server > Data Export`
2. seleccionar base `barbersoft`
3. elegir `Dump Structure and Data`
4. `Export to Self-Contained File`
5. generar archivo SQL de respaldo

Observación importante:
- VS Code mostró errores visuales en rojo, pero se concluyó que eso no afectaba el dump.

---

## 11.4 Problema encontrado: incompatibilidad de volumen

Se presentó el error:

```text
InnoDB: MySQL-8.0 tablespace in ./ibdata1
```

### Causa
- el volumen Docker anterior había sido creado con MySQL 8;
- al cambiar a MariaDB 10.4 surgió incompatibilidad de tablespace.

### Solución aplicada
- bajar contenedores;
- localizar el volumen;
- eliminar el volumen corrupto o cambiar nombre del volumen en `docker-compose`.

Comandos asentados:

```bash
docker compose down
docker volume ls
docker volume rm <nombre_volumen>
```

---

## 11.5 Configuración de MariaDB en Docker

Se dejó un servicio `db` así:

```yaml
db:
  image: mariadb:10.4
  container_name: barbersoft_db
  restart: always
  environment:
    MARIADB_DATABASE: barbersoft
    MARIADB_USER: barbersoft_user
    MARIADB_PASSWORD: barbersoft_pass
    MARIADB_ROOT_PASSWORD: rootpass
  ports:
    - "3307:3306"
  volumes:
    - mariadb_data:/var/lib/mysql
```

---

## 11.6 Arranque del contenedor de base

```bash
docker compose up -d db
docker compose logs -f db
```

Resultado esperado y confirmado:

```text
mysqld: ready for connections
```

---

## 11.7 Importación del respaldo

Problema detectado:
- PowerShell no soporta igual que bash la redirección `<`.

Solución aplicada:

```powershell
cmd /c "docker compose exec -T db mariadb -u root -prootpass barbersoft < respaldo-db\barbersoft-respaldo.sql"
```

---

## 11.8 Verificación posterior

```bash
docker compose exec db mariadb -u root -prootpass -e "USE barbersoft; SHOW TABLES;"
```

Resultado:
- las tablas se cargaron correctamente.

---

## 11.9 Flujo de sincronización correcto en adelante

Se dejó asentado que, una vez el proyecto se controle desde Django, la forma correcta de evolucionar la base debe ser:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

Y la regla clave quedó explícita:

> no modificar la base manualmente si se usa Django, salvo que exista una razón justificada y se controle cuidadosamente la divergencia.

---

# 12. Replanteamiento manual de la base y reconstrucción desde Workbench

En este chat se contempló una alternativa: borrar el contenido actual del volumen de MariaDB Docker, rediseñar la base manualmente en Workbench y volver a importarla.

## 12.1 Viabilidad de la estrategia

Se confirmó que **sí era viable**, siempre dejando claro que:

- se borraría por completo el contenido persistido del volumen actual;
- el proceso debía partir de un nuevo respaldo SQL correcto.

## 12.2 Comandos recordados para borrar y reconstruir

```bash
docker compose down
docker volume ls
docker volume rm NOMBRE_DEL_VOLUMEN
docker compose up -d db
docker compose logs -f db
```

Luego, en PowerShell:

```powershell
cmd /c "docker compose exec -T db mariadb -u root -prootpass barbersoft < ruta\archivo.sql"
```

Y para verificar:

```bash
docker compose exec db mariadb -u root -prootpass -e "USE barbersoft; SHOW TABLES;"
```

---

# 13. Decisión de modelar comisiones como tabla independiente

## 13.1 Pregunta central planteada

Se discutió si el registro de comisiones por empleado debía modelarse como:

- un atributo aislado en alguna tabla existente, o
- una tabla extra.

## 13.2 Conclusión adoptada

La decisión correcta para BarberSoft fue:

> **manejar comisiones como tabla extra**.

### Razones principales

1. **La comisión es histórica**: puede cambiar con el tiempo y debe quedar guardado el valor aplicado en el momento real de la venta.
2. **La comisión depende del detalle vendido**: una sola venta puede contener varias líneas, cada una con comisión distinta.
3. **Facilita reportes y auditoría**: permite consultar comisiones por empleado, por periodo, por producto o servicio.
4. **Evita ambigüedad**: un solo campo `comision` en `ventas` no indicaría si la comisión proviene de producto o de servicio, ni de cuál línea.

---

## 13.3 Estructura conceptual recomendada para `comisiones`

Se propuso una tabla con estos atributos base:

- `id_comision`
- `fk_id_empleado`
- `fk_id_venta`
- `fk_id_venta_detalle_producto`
- `fk_id_venta_detalle_servicio`
- `porcentaje_aplicado`
- `monto_base`
- `monto_comision`
- `fecha`

La idea era que cada fila representara una **comisión generada por una línea de venta específica**.

---

# 14. Razón de ser de los atributos de `comisiones`

Se explicó detalladamente el propósito de cada atributo:

## 14.1 `id_comision`
Clave primaria para identificar cada comisión de forma única.

## 14.2 `fk_id_empleado`
Identifica al empleado que recibe la comisión.

## 14.3 `fk_id_venta`
Permite rastrear la transacción global de donde nace la comisión.

## 14.4 `fk_id_venta_detalle_producto`
Relaciona la comisión con una línea exacta de producto vendido.

## 14.5 `fk_id_venta_detalle_servicio`
Relaciona la comisión con una línea exacta de servicio vendido.

## 14.6 `porcentaje_aplicado`
Guarda el porcentaje real usado al momento del cálculo, preservando histórico.

## 14.7 `monto_base`
Representa la base monetaria sobre la cual se calculó el porcentaje.

## 14.8 `monto_comision`
Importe final que gana el empleado.

## 14.9 `fecha`
Marca temporal de la generación de la comisión.

Se concluyó que la tabla no debía ser una simple configuración, sino una **bitácora transaccional histórica de comisiones generadas**.

---

# 15. Discusión sobre tipos de dato monetarios y porcentajes

## 15.1 Problema detectado

Durante la construcción manual de la tabla `comisiones`, el porcentaje se había dejado como `INT`.

## 15.2 Corrección recomendada

Se recomendó usar:

- `porcentaje_aplicado` → `DECIMAL(5,2)`
- `monto_base` → `DECIMAL(10,2)`
- `monto_comision` → `DECIMAL(10,2)`

### Razones

- `INT` solo almacena enteros;
- `FLOAT` introduce imprecisiones binarias;
- `DECIMAL` es el tipo correcto para dinero y tasas con precisión controlada.

---

## 15.3 Regla general fijada

Se dejó como regla práctica para BarberSoft:

- si representa **dinero**, usar `DECIMAL(10,2)`;
- si representa **porcentaje**, usar `DECIMAL(5,2)`;
- si representa **cantidad entera**, usar `INT` o `SMALLINT`.

Esto aplica a campos como:

- `precio_compra`
- `precio_venta`
- `subtotal`
- `total`
- `monto`
- `monto_base`
- `monto_comision`
- `subtotal_linea`

---

# 16. Problemas encontrados al usar el diseñador gráfico de Workbench

## 16.1 Problema con `DECIMAL`

Se detectó que el creador gráfico de tablas de Workbench no siempre permitía escribir fácilmente `DECIMAL(5,2)` o `DECIMAL(10,2)` en la celda del tipo de dato.

## 16.2 Alternativas propuestas

1. escribir manualmente `DECIMAL(5,2)` o `DECIMAL(10,2)` en la celda;
2. usar el panel inferior de propiedades (`Length/Values`, `Precision/Scale`);
3. crear la tabla directamente por SQL, recomendación considerada la más segura.

---

# 17. Error SQL al crear `comisiones` y diagnóstico

## 17.1 Error encontrado

Workbench generó un `CREATE TABLE` con una cláusula:

```sql
UNIQUE INDEX `id_comision_UNIQUE` (`id_comision` ASC) VISIBLE
```

MariaDB 10.4 respondió con error de sintaxis.

## 17.2 Diagnóstico

El problema no estaba en `DECIMAL`, sino en la parte generada automáticamente por Workbench:

- uso de `VISIBLE`, más afín a MySQL 8;
- creación de un índice único redundante sobre una columna que ya era `PRIMARY KEY`.

## 17.3 Solución

Quitar esa línea y dejar el `CREATE TABLE` solo con:

- `PRIMARY KEY (id_comision)`

---

# 18. Problema al crear foreign keys por nombre duplicado

## 18.1 Error encontrado

Al intentar crear una FK llamada `fk_id_empleado` en `comisiones`, MariaDB lanzó:

```text
errno: 121 "Duplicate key on write or update"
```

## 18.2 Diagnóstico

El nombre `fk_id_empleado` ya existía en la base, asociado a otra tabla, por ejemplo `ventas`.

En MariaDB/MySQL, los nombres de restricciones FK deben ser únicos dentro del esquema.

## 18.3 Solución adoptada

Usar nombres de restricciones más específicos, por ejemplo:

- `comisiones_fk_id_empleado`
- `comisiones_fk_id_venta`
- `comisiones_fk_id_venta_detalle_producto`
- `comisiones_fk_id_venta_detalle_servicio`

Y para índices:

- `comisiones_fk_id_empleado_idx`
- `comisiones_fk_id_venta_idx`
- etc.

---

# 19. Discusión sobre qué validar en MariaDB y qué validar en Django

## 19.1 Problema lógico de la tabla `comisiones`

La estructura de `comisiones` permite dos columnas opcionales:

- `fk_id_venta_detalle_producto`
- `fk_id_venta_detalle_servicio`

La regla de negocio correcta es:

- una comisión debe asociarse a **detalle de producto o detalle de servicio**;
- no a ambos a la vez;
- no a ninguno.

## 19.2 Decisión arquitectónica

Se acordó explícitamente que esta validación **no se impondría en MariaDB**, sino en la **capa de aplicación Django**.

### Razones

- es una regla de negocio;
- depende del flujo del formulario;
- en Django se puede dar mensaje de error claro al usuario;
- resulta más flexible y mantenible en el contexto del proyecto.

## 19.3 Lógica prevista en Django

Se propuso implementarla en `clean()` del modelo `Comision` con una validación tipo:

- si ambos son `None`, error;
- si ambos tienen valor, error;
- solo uno debe estar presente.

---

# 20. Evaluaciones sucesivas de los respaldos SQL actualizados

Durante este chat se revisaron varios respaldos SQL incrementales del usuario para verificar si los cambios realmente se estaban aplicando.

## 20.1 Hallazgos iniciales

Se confirmó como mejora clara:

- creación de la tabla `comisiones`;
- cambio de muchos campos monetarios de `FLOAT` a `DECIMAL(10,2)`;
- corrección de `ventas.total` de `INT` a `DECIMAL(10,2)`.

## 20.2 Observaciones técnicas reiteradas

En revisiones sucesivas se señalaron como pendientes:

- índices duplicados en `comisiones`;
- `UNIQUE KEY` redundantes sobre columnas que ya eran `PRIMARY KEY`;
- ausencia de `AUTO_INCREMENT` en algunos IDs técnicos de tablas detalle;
- falta de FK en `ventas.fk_id_metodo_pago` en una revisión intermedia.

## 20.3 Mejoras implementadas después

El usuario fue incorporando estas mejoras, entre ellas:

- `servicios.id_servicio` con `AUTO_INCREMENT`;
- `ventas.fk_id_metodo_pago` con índice y foreign key correcta;
- `venta_detalle_producto.id_venta_detalle_producto` con `AUTO_INCREMENT`;
- `venta_detalle_servicio.id_venta_detalle_servicio` con `AUTO_INCREMENT`.

## 20.4 Estado final evaluado en este chat

La conclusión final fue:

- la estructura ya es **funcional y razonable para seguir con Django**;
- la regla exclusiva de `comisiones` se manejará en la capa de aplicación;
- persisten algunas **redundancias técnicas menores** en el esquema SQL exportado, especialmente:
  - `UNIQUE KEY` redundantes sobre columnas ya `PRIMARY KEY`;
  - índices duplicados, sobre todo en `comisiones`.

### Veredicto final dado en la revisión

> la base quedó aprobada para continuar con Django, con observación menor de limpieza técnica.

---

# 21. Estado consolidado del proyecto al cierre de las sesiones previas

## 21.1 Estado del backend / infraestructura

- Docker funcionando;
- Django funcionando;
- MariaDB funcionando en contenedor;
- proyecto base levantable con `docker compose up --build`;
- Django admin accesible en `localhost:8000/admin`;
- migraciones base de Django aplicadas;
- apps registradas correctamente;
- `python manage.py check` devolviendo estado sano en la estructura base;
- base relacional reconstruida y refinada manualmente con respaldo SQL actualizado.

---

## 21.2 Estado de la base de datos

### Tablas base existentes y trabajadas
- `categorias_de_productos`
- `clientes`
- `empleados`
- `metodos_de_pago`
- `pagos`
- `productos`
- `servicios`
- `tipos_de_servicios`
- `venta_detalle_producto`
- `venta_detalle_servicio`
- `ventas`
- `comisiones` *(agregada en sesiones previas)*

### Mejoras estructurales ya incorporadas
- importes monetarios en `DECIMAL(10,2)`;
- porcentaje en `DECIMAL(5,2)`;
- IDs técnicos principales ya con `AUTO_INCREMENT` donde se decidió necesario;
- foreign keys principales definidas;
- modelado de comisiones como entidad histórica independiente.

### Asunto pendiente expresamente movido a Django
- validación lógica de exclusividad entre `fk_id_venta_detalle_producto` y `fk_id_venta_detalle_servicio` en `comisiones`.

---

# 22. Flujo técnico correcto a partir de aquí

Como el proyecto seguirá en Django, el criterio recomendado para continuar es:

1. tomar esta base refinada como referencia estructural;
2. decidir si Django administrará completamente la base a partir de ahora o si consumirá parte como esquema legacy;
3. trasladar los modelos a `models.py` por app;
4. definir cuidadosamente relaciones, tipos y `related_name`;
5. implementar validaciones de negocio en la capa de aplicación;
6. usar `makemigrations` y `migrate` como mecanismo formal de evolución del esquema cuando el proyecto quede plenamente bajo control de Django.

Comandos recordados:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py check
```

---

# 23. Decisiones de diseño ya consolidadas

## 23.1 Decisiones de infraestructura
- usar Docker Compose para `web` y `db`;
- usar MariaDB en contenedor;
- usar VS Code sobre Windows;
- usar `config.settings.dev` durante desarrollo.

## 23.2 Decisiones de modelado
- trabajar con monolito modular en Django;
- dividir por apps (`accounts`, `catalogos`, `clientes`, `empleados`, `reportes`, `ventas`);
- mantener ventas como núcleo del sistema;
- usar tabla `comisiones` en lugar de atributo suelto;
- usar `DECIMAL(10,2)` para montos;
- usar `DECIMAL(5,2)` para porcentajes.

## 23.3 Decisiones de validación
- reglas estructurales fuertes en DB: PK, FK, nulabilidad, tipos, autoincremento;
- reglas de negocio complejas en Django, especialmente la exclusividad de origen de `comisiones`.

---

# 24. Riesgos y observaciones que siguen vigentes

1. si se continúa modificando la base manualmente y paralelamente se empieza a modelar en Django, puede aparecer desalineación entre:
   - esquema real en MariaDB;
   - modelos Django;
   - historial de migraciones.

2. conviene definir pronto si Django adoptará el esquema existente como base legacy o si se reconstruirá todo con modelos y migraciones propias.

3. aunque las redundancias de índices/unique detectadas no bloquean, sí convendría limpiarlas después para evitar ruido en el diseño.

---

# 25. Trabajo del Integrante 3 — Núcleo de Negocio (semana 2026-04-03)

Esta sección documenta todo lo trabajado, decidido e implementado por el Integrante 3 durante la semana correspondiente a la construcción del módulo `ventas`.

---

## 25.1 Responsabilidades asignadas al Integrante 3

Conforme a la tabla de distribución de trabajo acordada en el equipo:

- diseñar y modelar `ventas`, `venta_detalle_producto`, `venta_detalle_servicio`, `pagos`, `visitas` y `comisiones`;
- acordar con el Integrante 2 los nombres exactos de FK y tipos de dato;
- dejar las reglas base del dominio en modelos y admin preliminar;
- preparar validaciones de negocio esenciales, especialmente comisiones.

### Entregables obligatorios al cierre de semana
- modelos base del núcleo listos;
- relaciones definidas;
- primera versión de migraciones del módulo ventas;
- documento corto de reglas de negocio implementadas.

---

## 25.2 Acuerdo de coordinación con el Integrante 2

Antes de escribir el código del módulo `ventas`, se estableció que era necesario acordar con el Integrante 2 los nombres exactos de las clases Python en sus modelos, ya que los modelos de ventas dependen directamente de entidades maestras que el Integrante 2 tiene bajo su responsabilidad.

### Razón técnica

En Django, al declarar una FK con cadena de texto como:

```python
cliente = models.ForeignKey('clientes.Cliente', ...)
```

Django resuelve esa referencia buscando una clase llamada exactamente `Cliente` dentro de la app `clientes`. Si el nombre difiere, las migraciones fallarán.

### Acuerdo mínimo necesario

| Entidad maestra | Nombre de clase acordado | App donde vive |
|---|---|---|
| Empleado | `Empleado` | `empleados` |
| Cliente | `Cliente` | `clientes` |
| Producto | `Producto` | `catalogos` |
| Servicio | `Servicio` | `catalogos` |
| Método de pago | `MetodoDePago` | `catalogos` |

La forma práctica de verificar este acuerdo es pedirle al Integrante 2 la primera línea de cada clase en su `models.py`:

```python
class Empleado(models.Model): ...
class Cliente(models.Model): ...
class Producto(models.Model): ...
class Servicio(models.Model): ...
class MetodoDePago(models.Model): ...
```

### Orden de migración requerido

Las migraciones del módulo `ventas` deben ejecutarse **después** de que el Integrante 2 haya aplicado las suyas, ya que `ventas` depende de las tablas creadas por `empleados`, `clientes` y `catalogos`.

Orden correcto:
1. Integrante 2 ejecuta `makemigrations` y `migrate` de sus apps.
2. Integrante 3 ejecuta `makemigrations ventas` y `migrate`.

---

## 25.3 Aclaración sobre advertencias de Pylance en VS Code

Durante el desarrollo se presentaron advertencias visuales de Pylance en VS Code sobre las importaciones de Django:

```text
"models" is not accessed Pylance
Import "django.db.models" could not be resolved from source
```

### Diagnóstico

Pylance analiza el código desde Windows, pero Django y todas sus dependencias están instaladas dentro del contenedor Docker, no en la máquina local. Pylance no puede ver los paquetes del contenedor y por ello marca las importaciones como no resueltas.

**Estas advertencias no son errores reales de Python ni de Django.** El código es perfectamente válido.

### Soluciones disponibles

**Opción A — Entorno virtual local (recomendada):**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install django mysqlclient
```

Luego en VS Code: `Ctrl+Shift+P` → `Python: Select Interpreter` → seleccionar el `.venv`.

**Opción B — Silenciar Pylance:**

Agregar al archivo `.vscode/settings.json`:

```json
{
  "python.analysis.typeCheckingMode": "off"
}
```

### Relación con Docker apagado

Se confirmó que tener Docker apagado agrava las advertencias de Pylance, pero no afecta la validez del código. El flujo correcto es:

- escribir todo el código con Docker apagado si se desea;
- levantar Docker al final para ejecutar los comandos de gestión.

**Docker es obligatorio únicamente para:** `makemigrations`, `migrate`, `check` y pruebas en el navegador.

---

## 25.4 Implementación de `apps/ventas/models.py`

Todo el núcleo transaccional del sistema reside en este archivo. Se importan los módulos necesarios al inicio:

```python
from django.db import models
from django.core.exceptions import ValidationError
```

---

### Modelo `Venta`

Encabezado de cada transacción. Registra al empleado que atendió, al cliente, el método de pago, la fecha y el total general.

```python
class Venta(models.Model):
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Empleado'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Cliente'
    )
    metodo_de_pago = models.ForeignKey(
        'catalogos.MetodoDePago',
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Método de pago'
    )
    fecha = models.DateField(verbose_name='Fecha de venta')
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total'
    )

    class Meta:
        db_table = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f'Venta #{self.pk} — {self.fecha}'
```

**Decisiones clave:**
- `on_delete=models.PROTECT` impide eliminar un empleado, cliente o método de pago si tiene ventas asociadas, preservando la integridad histórica.
- `DECIMAL(10, 2)` para `total`, conforme a la regla general fijada en sesiones previas.
- `related_name` permite navegar la relación inversa (`empleado.ventas.all()`).

---

### Modelo `VentaDetalleProducto`

Registra cada producto vendido dentro de una venta, con su cantidad, precio unitario y subtotal.

```python
class VentaDetalleProducto(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles_producto',
        verbose_name='Venta'
    )
    producto = models.ForeignKey(
        'catalogos.Producto',
        on_delete=models.PROTECT,
        related_name='detalles_venta',
        verbose_name='Producto'
    )
    cantidad = models.PositiveIntegerField(verbose_name='Cantidad')
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio unitario'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal'
    )

    class Meta:
        db_table = 'venta_detalle_producto'
        verbose_name = 'Detalle de producto'
        verbose_name_plural = 'Detalles de productos'

    def __str__(self):
        return f'Detalle producto #{self.pk} — Venta #{self.venta_id}'
```

**Decisiones clave:**
- `on_delete=models.CASCADE` en la FK hacia `Venta`: si se elimina una venta, sus líneas de detalle también se eliminan.
- `precio_unitario` se almacena en el detalle, no solo en el catálogo, para preservar el precio histórico en el momento de la transacción.

---

### Modelo `VentaDetalleServicio`

Análogo al anterior, pero para servicios prestados dentro de la venta.

```python
class VentaDetalleServicio(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles_servicio',
        verbose_name='Venta'
    )
    servicio = models.ForeignKey(
        'catalogos.Servicio',
        on_delete=models.PROTECT,
        related_name='detalles_venta',
        verbose_name='Servicio'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio unitario'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal'
    )

    class Meta:
        db_table = 'venta_detalle_servicio'
        verbose_name = 'Detalle de servicio'
        verbose_name_plural = 'Detalles de servicios'

    def __str__(self):
        return f'Detalle servicio #{self.pk} — Venta #{self.venta_id}'
```

---

### Modelo `Pago`

Registra el pago asociado a una venta. La estructura permite que en el futuro una venta pueda tener pagos parciales o mixtos.

```python
class Pago(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='pagos',
        verbose_name='Venta'
    )
    metodo_de_pago = models.ForeignKey(
        'catalogos.MetodoDePago',
        on_delete=models.PROTECT,
        related_name='pagos',
        verbose_name='Método de pago'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto pagado'
    )
    fecha = models.DateField(verbose_name='Fecha de pago')

    class Meta:
        db_table = 'pagos'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'Pago #{self.pk} — Venta #{self.venta_id}'
```

---

### Modelo `Visita`

Registra cada visita del cliente al establecimiento, construyendo el historial de asistencia independientemente de si se realizó una venta.

```python
class Visita(models.Model):
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='visitas',
        verbose_name='Cliente'
    )
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.PROTECT,
        related_name='visitas',
        verbose_name='Empleado'
    )
    venta = models.ForeignKey(
        Venta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visitas',
        verbose_name='Venta asociada'
    )
    fecha = models.DateField(verbose_name='Fecha de visita')
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )

    class Meta:
        db_table = 'visitas'
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'
        ordering = ['-fecha']

    def __str__(self):
        return f'Visita #{self.pk} — Cliente {self.cliente_id}'
```

**Decisiones clave:**
- La FK hacia `Venta` es opcional (`null=True`, `blank=True`) porque puede existir una visita sin que se concrete una venta.
- `on_delete=models.SET_NULL`: si se eliminara la venta, la visita no desaparece; simplemente pierde la referencia.

---

### Modelo `Comision` con validación `clean()`

Este es el modelo más delicado del módulo. Una comisión puede originarse de un detalle de producto **o** de un detalle de servicio, pero nunca de ambos ni de ninguno. Esta regla se implementa en la capa de aplicación mediante el método `clean()`.

```python
class Comision(models.Model):
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.PROTECT,
        related_name='comisiones',
        verbose_name='Empleado'
    )
    venta = models.ForeignKey(
        Venta,
        on_delete=models.PROTECT,
        related_name='comisiones',
        verbose_name='Venta'
    )
    venta_detalle_producto = models.ForeignKey(
        VentaDetalleProducto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='comisiones',
        verbose_name='Detalle de producto'
    )
    venta_detalle_servicio = models.ForeignKey(
        VentaDetalleServicio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='comisiones',
        verbose_name='Detalle de servicio'
    )
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Porcentaje (%)'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto de comisión'
    )
    fecha = models.DateField(verbose_name='Fecha de comisión')

    class Meta:
        db_table = 'comisiones'
        verbose_name = 'Comisión'
        verbose_name_plural = 'Comisiones'

    def clean(self):
        tiene_producto = self.venta_detalle_producto_id is not None
        tiene_servicio = self.venta_detalle_servicio_id is not None

        if not tiene_producto and not tiene_servicio:
            raise ValidationError(
                'Una comisión debe estar asociada a un detalle de '
                'producto o a un detalle de servicio.'
            )
        if tiene_producto and tiene_servicio:
            raise ValidationError(
                'Una comisión no puede estar asociada simultáneamente '
                'a un detalle de producto y a un detalle de servicio.'
            )

    def __str__(self):
        return f'Comisión #{self.pk} — Empleado {self.empleado_id}'
```

**Notas sobre `clean()`:**
- Se ejecuta automáticamente al validar formularios en el panel admin de Django.
- No se ejecuta al llamar directamente `modelo.save()`. Para forzar la validación fuera del admin, se debe llamar primero `modelo.full_clean()`.
- Es el lugar correcto en Django para reglas de negocio que involucran más de un campo a la vez.

---

## 25.5 Implementación de `apps/ventas/admin.py`

Se registraron todos los modelos del módulo con configuración de inlines para facilitar la captura de datos desde el panel administrativo.

```python
from django.contrib import admin
from .models import (
    Venta,
    VentaDetalleProducto,
    VentaDetalleServicio,
    Pago,
    Visita,
    Comision,
)


class VentaDetalleProductoInline(admin.TabularInline):
    model = VentaDetalleProducto
    extra = 1


class VentaDetalleServicioInline(admin.TabularInline):
    model = VentaDetalleServicio
    extra = 1


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'empleado', 'cliente', 'fecha', 'total']
    list_filter = ['fecha', 'empleado']
    search_fields = ['cliente__nombre', 'empleado__nombre']
    inlines = [
        VentaDetalleProductoInline,
        VentaDetalleServicioInline,
        PagoInline,
    ]


@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'empleado', 'venta', 'porcentaje', 'monto', 'fecha']
    list_filter = ['fecha', 'empleado']


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'empleado', 'fecha']
    list_filter = ['fecha']
```

**Nota sobre `TabularInline`:** permite gestionar los detalles de una venta directamente desde el formulario de la venta en el panel administrativo, simplificando la captura de datos durante las pruebas.

---

## 25.6 Comandos de migración del módulo ventas

Una vez completados `models.py` y `admin.py`, se ejecutan los siguientes comandos dentro del contenedor Docker. **Recordar que Docker debe estar levantado antes de ejecutarlos.**

```bash
# Levantar Docker primero
docker compose up

# En otra terminal, ejecutar las migraciones
docker compose exec web python manage.py makemigrations ventas
docker compose exec web python manage.py migrate
docker compose exec web python manage.py check
```

La terminal integrada de VS Code (`Ctrl + ñ`) es válida para ejecutar estos comandos, siempre que esté apuntando a la carpeta raíz del proyecto donde reside `docker-compose.yml`.

---

## 25.7 Documento de reglas de negocio implementadas

| Regla | Dónde se implementa |
|---|---|
| Una comisión debe originarse en exactamente un detalle (producto o servicio, no ambos ni ninguno) | `Comision.clean()` en Django |
| No se puede eliminar un empleado, cliente, producto o servicio si tiene ventas asociadas | `on_delete=PROTECT` en ForeignKey |
| Si se elimina una venta, sus líneas de detalle también se eliminan | `on_delete=CASCADE` en ForeignKey de detalles |
| Una visita puede existir sin venta asociada | FK opcional con `null=True` y `blank=True` |
| Si se elimina una venta, la visita no desaparece; pierde solo la referencia | `on_delete=SET_NULL` en FK de visita a venta |
| Los montos monetarios se almacenan con precisión de dos decimales | `DecimalField(max_digits=10, decimal_places=2)` |
| Los porcentajes de comisión se almacenan con precisión de dos decimales | `DecimalField(max_digits=5, decimal_places=2)` |
| El precio de venta de un producto o servicio queda congelado en el detalle | Campo `precio_unitario` en cada modelo de detalle |

---

## 25.8 Estado del módulo ventas al cierre de semana

- `apps/ventas/models.py` con 6 modelos implementados: `Venta`, `VentaDetalleProducto`, `VentaDetalleServicio`, `Pago`, `Visita`, `Comision`.
- `apps/ventas/admin.py` con registro completo e inlines funcionales.
- Validación de negocio `clean()` implementada en `Comision`.
- Migraciones pendientes de ejecutar una vez que el Integrante 2 aplique las suyas.
- Documento de reglas de negocio redactado.

---

# 26. Resumen ejecutivo final

Durante todo el proceso consolidado en esta bitácora se logró:

1. reinterpretar el proyecto BarberSoft hacia Django + Docker + MariaDB/MySQL;
2. dejar funcionando el proyecto base con Django y Docker;
3. crear y registrar manualmente las apps principales;
4. resolver errores iniciales de configuración de Django;
5. migrar una base real desde XAMPP/MariaDB hacia MariaDB Docker;
6. documentar el proceso correcto de destrucción y recreación del volumen de base cuando fue necesario;
7. rediseñar parcialmente la estructura relacional desde Workbench;
8. incorporar la tabla `comisiones` como tabla histórica independiente;
9. justificar funcional y contablemente el uso de `DECIMAL(10,2)` para montos y `DECIMAL(5,2)` para porcentajes;
10. resolver varios problemas de sintaxis y nombres de constraints en MariaDB;
11. decidir conscientemente qué reglas dejar en DB y cuáles mover a Django;
12. dejar la base en un punto suficiente para continuar el modelado del sistema desde la capa de aplicación;
13. implementar el módulo completo de ventas en Django (`models.py` y `admin.py`) como parte del trabajo del Integrante 3;
14. documentar el acuerdo de coordinación con el Integrante 2 respecto a nombres de clases y orden de migraciones;
15. aclarar el comportamiento de Pylance en VS Code con Docker y la forma correcta de trabajar en el entorno.

---

# 27. Uso recomendado de este archivo para continuidad

Para retomar este proceso en otro chat, basta con adjuntar este archivo y pedir algo como:

> Retoma el proceso de BarberSoft con base en esta bitácora unificada.

O bien:

> Continuemos con el modelado Django de BarberSoft desde el estado actual descrito aquí.

---

**Fin de la bitácora unificada — actualizada al 2026-04-03.**

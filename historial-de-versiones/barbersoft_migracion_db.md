# Bitácora Técnica – Migración a MariaDB en Docker (BarberSoft)

Fecha: 2026-03-29

---

## 1. Contexto inicial

- Proyecto: BarberSoft (Django + Docker + MySQL/MariaDB)
- Estado previo:
  - Django funcionando en Docker
  - Base de datos en XAMPP (MariaDB 10.4)
  - Base ya existente con datos reales

---

## 2. Objetivo

Migrar la base de datos desde XAMPP hacia MariaDB en Docker sin perder información.

---

## 3. Respaldo de base de datos

### Método utilizado: MySQL Workbench

Pasos:
1. Server > Data Export
2. Seleccionar base: barbersoft
3. Dump Structure and Data
4. Export to Self-Contained File
5. Generar archivo: barbersoft_respaldo.sql

Observación:
- VS Code mostró errores en rojo → ignorado (no afecta el dump)
- Dump generado como MariaDB dump

---

## 4. Problema detectado

Error en logs:

```
InnoDB: MySQL-8.0 tablespace in ./ibdata1
```

Causa:
- Volumen Docker anterior creado con MySQL 8
- Incompatibilidad al cambiar a MariaDB

---

## 5. Solución aplicada

### Eliminación de volumen corrupto

```bash
docker compose down
docker volume ls
docker volume rm <nombre_volumen>
```

Alternativa:
- Cambiar nombre del volumen en docker-compose

---

## 6. Configuración de MariaDB en Docker

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

## 7. Levantamiento del contenedor

```bash
docker compose up -d db
docker compose logs -f db
```

Resultado esperado:
```
mysqld: ready for connections
```

✔ Confirmado

---

## 8. Importación del respaldo

Problema:
- PowerShell no soporta `<`

Solución:

```powershell
cmd /c "docker compose exec -T db mariadb -u root -prootpass barbersoft < respaldo-db\barbersoft-respaldo.sql"
```

---

## 9. Verificación

```bash
docker compose exec db mariadb -u root -prootpass -e "USE barbersoft; SHOW TABLES;"
```

Resultado:
- Tablas cargadas correctamente:
  - clientes
  - empleados
  - productos
  - ventas
  - etc.

✔ Importación exitosa

---

## 10. Conexión Django → MariaDB

### .env

```env
DB_NAME=barbersoft
DB_USER=barbersoft_user
DB_PASSWORD=barbersoft_pass
DB_HOST=db
DB_PORT=3306
```

### settings.py

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

## 11. Sincronización de cambios en BD

### Flujo correcto (Django-first)

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Regla clave

NO modificar la base manualmente si se usa Django.

---

## 12. Consideraciones clave

- MariaDB ≈ MySQL (compatibles para este proyecto)
- VS Code en rojo ≠ error real
- PowerShell ≠ bash (importante para redirecciones)
- Siempre trabajar con respaldo antes de migrar
- Docker garantiza reproducibilidad del entorno

---

## 13. Estado final

✔ MariaDB corriendo en Docker  
✔ Base importada correctamente  
✔ Tablas verificadas  
✔ Entorno listo para desarrollo  

---

## 14. Siguiente paso recomendado

- Verificar conexión desde Django shell
- Definir estrategia de modelos (legacy vs Django-managed)

---

## Nota final

Esta bitácora documenta la migración segura de una base existente hacia Docker, evitando pérdida de datos y asegurando consistencia del entorno para desarrollo colaborativo.

# ARIOS

Desarrollo EVA

## Estructura del Proyecto

```plaintext
Administracion/
batch/
    Admin-ScriptsPowerShell.ps1
    ConstruirProyectoDjango.bat
    EjecutarProyectoDjango.bat
    IniciarEntornoVirtual-Python.ps1
EVA/
Financiero/
GestionDocumental/
Notificaciones/
PostgreSQL/
    CrearDB.sql
    DeleteTables.sql
    DropDB.sql
    InsertTables.sql
Proyectos/
SGI/
TalentoHumano/
utilidades/
.gitignore
django_admin.txt
LICENSE
README.md
requirements.txt
manage.py
```

## Instalación

### Requisitos Previos

- Python 3.8.10
- pip
- virtualenv

### Pasos de Instalación

1. Clonar el repositorio:
    ```sh
    git clone https://github.com/andres-gutierrezri/arios.git
    cd arios
    ```

2. Crear y activar el entorno virtual:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .venv\Scripts\activate
    ```

3. Instalar las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

4. Realizar las migraciones de la base de datos:
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Ejecutar el servidor de desarrollo:
    ```sh
    python manage.py runserver
    ```

## Uso

Instrucciones sobre cómo usar el proyecto, incluyendo ejemplos de código y capturas de pantalla si es necesario.

## Scripts Útiles

PostgreSQL

### Construir el Proyecto

Para construir el proyecto, puedes usar el script [`ConstruirProyectoDjango.bat`]

### Ejecutar el Proyecto

Para ejecutar el proyecto, puedes usar el script [`EjecutarProyectoDjango.bat`]

## Dependencias

Las dependencias del proyecto están listadas en el archivo [`requirements.txt`]

## Contribuir

Si deseas contribuir al proyecto, por favor sigue los siguientes pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios necesarios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube los cambios a tu repositorio ([`git push origin feature/nueva-funcionalidad`].
5. Crea un Pull Request.

## Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [`LICENSE`].
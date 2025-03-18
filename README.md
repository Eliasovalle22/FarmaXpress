# FarmaXpress
 Control de Farmacia

1. Instalación de librerias, creación de entorno virtual y activación.
    pip install virtualenv
    virtualenv venv
    Set-ExecutionPolicy RemoteSigned -- Activar el uso de entornos virtuales
    venv\Scripts\activate
    django-admin startproject farmaxpress .
    python manage.py startapp home
    pip install django
    pip install -r requirements.txt -- instalar las librerias
    pip freeze > requirements.txt -- actualizar la lista de librerias


2. Creación de modulos
    python manage.py startapp nombre_del_modulo

3. Creación de los modelos de la BD con el ORM de Django
    python manage.py makemigrations -- migración de las tablas
    python manage.py migrate -- creación de tablas en la BD


4. Ejecución local
    python manage.py runserver


5. Ejecución local
    python manage.py runserver 0.0.0.0:8000
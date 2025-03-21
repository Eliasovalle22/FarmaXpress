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
   
7. Login
   
   ![image](https://github.com/user-attachments/assets/e824dbe9-4baf-40c7-80b3-c7c92b28d60c)


8. Dashboard segun el Rol ( Admin)

![image](https://github.com/user-attachments/assets/f9861f35-ed40-478b-a05e-6fb8bcd19859)


9. Dashboard segun el Rol ( Vendedor)


![image](https://github.com/user-attachments/assets/f6b68e95-61b7-4207-ab99-ba3d5b0e9312)

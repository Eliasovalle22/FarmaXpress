"""
URL configuration for farmaxpress project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL para la página de inicio
    path('farmaxpress/login/',views.iniciar_sesion, name='iniciar_sesion'),
    # URL para cerrar sesión
    path('farmaxpress/logout/',views.cerrar_sesion, name='cerrar_sesion'),
    # URL para dashboard
    path('farmaxpress/dashboard/',views.dashboard, name='dashboard'),
    # URL para reestablecer contraseña
    path('farmaxpress/reestablecer_contrasena/',views.reestablecer_contrasena, name='reestablecer_contrasena'),
    # URL para registrar clientes
    path('farmaxpress/resgistrar_cliente/',views.registrar_cliente, name='registrar_cliente'),
    #3 URL para registrar ventas
    path('farmaxpress/registrar_venta/',views.registrar_venta, name='registrar_venta'),
    # URL para gestionar productos
    path('farmaxpress/gestionar_productos/',views.gestionar_productos, name='gestionar_productos'),
    # URL para agregar productos
    path('farmaxpress/agregar_producto/',views.agregar_producto, name='agregar_producto'),
    # URL para actualizar productos
    path('farmaxpress/actualizar_producto/<int:producto_id>/',views.actualizar_producto, name='actualizar_producto'),
    # URL para eliminar productos
    path('farmaxpress/eliminar_producto/<int:producto_id>/',views.eliminar_producto, name='eliminar_producto'),
    # URL para dar de baja productos
    path('farmaxpress/dar_baja_producto/<int:producto_id>/',views.dar_baja_producto, name='dar_baja_producto'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




from django.shortcuts import render, redirect
from home.models import User, Cliente, Producto, Rol, Venta, Sede
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django import forms
from django.db.models import Count
# Create your views here.

# ---------------------------- INICIO DE SESIÓN ---------------------------------


# Inicio de Sesión
@csrf_protect
def iniciar_sesion(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autenticar usando el modelo User
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('iniciar_sesion')


#
# ---------------------------- REESTABLECER CONTRASEÑA ---------------------------------
#

def reestablecer_contrasena(request):
    return render(request, 'reestablecer_contrasena.html')

def actualizar_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('reestablecer_contrasena')
        
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            messages.success(request, 'Contraseña actualizada correctamente')
            return redirect('iniciar_sesion')
        except User.DoesNotExist:
            messages.error(request, 'El usuario no existe')
            return redirect('reestablecer_contrasena')


#
# ---------------------------- VISTA INICIO ---------------------------------
#

@login_required
def dashboard(request):

    total_productos = Producto.objects.count()
    total_ventas = Venta.objects.count()
    total_clientes = Cliente.objects.count()
    stock_bajo = Producto.objects.filter(stock_sede1__lt=10).count() + Producto.objects.filter(stock_sede2__lt=10).count()

    # Datos para gráfico de ventas por sede
    ventas_por_sede = Venta.objects.values('sede__nombre').annotate(total=Count('id')).order_by('sede__nombre')
    sedes = [item['sede__nombre'] for item in ventas_por_sede]
    ventas = [item['total'] for item in ventas_por_sede]

    context = {
        'total_productos': total_productos,
        'total_ventas': total_ventas if request.user.role in ['admin', 'contable'] else None,
        'total_clientes': total_clientes,
        'stock_bajo': stock_bajo if request.user.role in ['admin', 'inventario'] else None,
        'role': request.user.role,
        'sedes': sedes,
        'ventas': ventas,
    }
    return render(request, 'dashboard.html', context)

#
# ----------------------------  CERRAR SESIÓN ---------------------------------
#

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('iniciar_sesion')


#
# ----------------------------  REGISTAR CLIENTES---------------------------------
#

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'correo', 'direccion', 'telefono']

def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente registrado correctamente')
            return redirect('dashboard')  # O redirigir a la vista de ventas si prefieres
        else:
            messages.error(request, 'Error al registrar el cliente. Revisa los datos.')
    else:
        form = ClienteForm()
    
    return render(request, 'registrar_cliente.html', {'form': form})
from django.shortcuts import render, redirect
from home.models import User, Cliente, Producto, Venta, Sede, Rol, DetalleVenta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django import forms
from django.db.models import Count, Sum
# Create your views here.

# ---------------------------- INICIO DE SESIÓN ---------------------------------


@csrf_protect
def iniciar_sesion(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('iniciar_sesion')

#
# ----------------------------  CERRAR SESIÓN ---------------------------------
#


@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('iniciar_sesion')

#
# ---------------------------- REESTABLECER CONTRASEÑA ---------------------------------
#

def reestablecer_contrasena(request):
    return render(request, 'reestablecer_contrasena.html')


def actualizar_contrasena(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('reestablecer_contrasena')

        try:
            user = User.objects.get(username=username)
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
    stock_bajo = Producto.objects.filter(stock_sede1__lt=10).count(
    ) + Producto.objects.filter(stock_sede2__lt=10).count()

    # Filtrar ventas por sede del usuario si no es admin o contable
    user_role = request.user.role.rol if request.user.role else None
    if user_role in ['admin', 'contable']:
        ventas_por_sede = Venta.objects.values('sede__nombre').annotate(
            total=Count('id')).order_by('sede__nombre')
    else:
        # Mostrar solo las ventas de la sede del usuario
        ventas_por_sede = Venta.objects.filter(sede=request.user.sede).values(
            'sede__nombre').annotate(total=Count('id')).order_by('sede__nombre')

    sedes = [item['sede__nombre'] for item in ventas_por_sede]
    ventas = [item['total'] for item in ventas_por_sede]

    # Datos específicos según el rol
    context = {
        'total_productos': total_productos,
        'total_ventas': total_ventas if user_role in ['admin', 'contable'] else None,
        'total_clientes': total_clientes if user_role in ['admin', 'vendedor'] else None,
        'stock_bajo': stock_bajo if user_role in ['admin', 'inventario'] else None,
        'role': user_role,
        'sedes': sedes,
        'ventas': ventas,
        'user_sede': request.user.sede.nombre if request.user.sede else 'Sin sede asignada',
    }
    return render(request, 'dashboard.html', context)




#
# ----------------------------  REGISTAR CLIENTES---------------------------------
#

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'correo', 'direccion', 'telefono']


def registrar_cliente(request):
    # Solo admin y vendedor pueden registrar clientes
    if request.user.role.rol not in ['admin', 'vendedor']:
        messages.error(request, 'No tienes permiso para registrar clientes.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.save()
            messages.success(request, 'Cliente registrado correctamente')
            return redirect('dashboard')
        else:
            messages.error(
                request, 'Error al registrar el cliente. Revisa los datos.')
    else:
        form = ClienteForm()
    return render(request, 'registrar_cliente.html', {'form': form})


#
# ----------------------------  REGISTAR VENTAS---------------------------------
#

class VentaForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(), required=False, label="Cliente (opcional)")
    productos = forms.ModelMultipleChoiceField(queryset=Producto.objects.all(
    ), widget=forms.CheckboxSelectMultiple, label="Productos")
    cantidades = forms.CharField(widget=forms.HiddenInput, required=False)


@login_required
def registrar_venta(request):
    if request.user.role.rol not in ['admin', 'vendedor']:
        messages.error(request, 'No tienes permiso para registrar ventas.')
        return redirect('dashboard')

    sede_usuario = request.user.sede
    if not sede_usuario:
        messages.error(request, 'No tienes una sede asignada.')
        return redirect('dashboard')

    productos_disponibles = Producto.objects.filter(
        stock_sede1__gt=0) if sede_usuario.nombre == "Sede 1" else Producto.objects.filter(stock_sede2__gt=0)

    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            from django.db import transaction
            try:
                with transaction.atomic():
                    venta = Venta.objects.create(
                        sede=sede_usuario,
                        vendedor=request.user,
                        cliente=form.cleaned_data['cliente']
                    )
                    productos_seleccionados = form.cleaned_data['productos']
                    cantidades = request.POST.get('cantidades', '').split(',')
                    stock_field = 'stock_sede1' if sede_usuario.nombre == "Sede 1" else 'stock_sede2'

                    for producto, cantidad_str in zip(productos_seleccionados, cantidades):
                        cantidad = int(cantidad_str)
                        if cantidad <= 0:
                            continue

                        stock_actual = getattr(producto, stock_field)
                        if stock_actual < cantidad:
                            raise ValueError(
                                f"Stock insuficiente para {producto.nombre}")

                        setattr(producto, stock_field, stock_actual - cantidad)
                        producto.save()

                        DetalleVenta.objects.create(
                            venta=venta,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=producto.precio
                        )

                    messages.success(request, 'Venta registrada correctamente')
                    return redirect('dashboard')
            except Exception as e:
                messages.error(
                    request, f'Error al registrar la venta: {str(e)}')
    else:
        form = VentaForm()

    context = {
        'form': form,
        'productos_disponibles': productos_disponibles,
        'sede': sede_usuario,
    }
    return render(request, 'registrar_venta.html', context)

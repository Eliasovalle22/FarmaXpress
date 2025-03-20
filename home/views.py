from django.shortcuts import render, redirect
from home.models import User, Cliente, Producto, Venta, Sede, Rol, DetalleVenta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django import forms
from django.db import transaction
from django.db.models import Count, Sum
from django.http import JsonResponse
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
    role = request.user.role.rol.lower() if request.user.role else None
    user_sede = request.user.sede.nombre if request.user.sede else 'Sin sede'
    clientes = Cliente.objects.all()
    productos_disponibles = Producto.objects.filter(fecha_baja__isnull=True)
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

    # Añadimos el formulario de cliente al contexto
    cliente_form = ClienteForm()

    # Datos específicos según el rol
    context = {
        'role': role,
        'user_sede': user_sede,
        'cliente_form': ClienteForm(),
        'clientes': clientes,
        'productos_disponibles': productos_disponibles,
        'total_productos': total_productos,
        'total_ventas': total_ventas if user_role in ['admin', 'contable'] else None,
        'total_clientes': total_clientes if user_role in ['admin', 'vendedor'] else None,
        'stock_bajo': stock_bajo if user_role in ['admin', 'inventario'] else None,
        'role': user_role,
        'sedes': sedes,
        'ventas': ventas,
        'user_sede': request.user.sede.nombre if request.user.sede else 'Sin sede asignada',
        'cliente_form': cliente_form,  # Añadimos el formulario al contexto
    }
    return render(request, 'dashboard.html', context)




#
# ----------------------------  REGISTAR CLIENTES---------------------------------
#

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'correo', 'direccion', 'telefono']


@login_required
def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Cliente registrado exitosamente.'
            })
        else:
            # Devolver los errores del formulario en formato JSON
            errors = {field: error for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'message': 'Por favor, corrija los errores en el formulario.',
                'errors': errors
            }, status=400)
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
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        productos_ids = request.POST.getlist('productos')
        cantidades_str = request.POST.get('cantidades', '')

        if not productos_ids:
            return JsonResponse({
                'success': False,
                'message': 'Debe seleccionar al menos un producto.'
            }, status=400)

        # Validar que cantidades no esté vacío
        if not cantidades_str:
            return JsonResponse({
                'success': False,
                'message': 'No se enviaron las cantidades de los productos. Por favor, intente de nuevo.'
            }, status=400)

        cantidades = cantidades_str.split(',')
        # Asegurarse de que la longitud de cantidades coincida con la cantidad de productos disponibles
        productos_disponibles = Producto.objects.filter(fecha_baja__isnull=True)
        if len(cantidades) != productos_disponibles.count():
            return JsonResponse({
                'success': False,
                'message': f'Error en el formato de las cantidades. Se esperaban {productos_disponibles.count()} valores, pero se recibieron {len(cantidades)}.'
            }, status=400)

        try:
            with transaction.atomic():
                # Crear la venta
                cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None
                sede = request.user.sede
                venta = Venta.objects.create(
                    sede=sede,
                    vendedor=request.user,
                    cliente=cliente,
                    total=0.00
                )

                # Crear los detalles de la venta
                for i, producto_id in enumerate(productos_ids):
                    # Convertir la cantidad a entero, manejando posibles valores vacíos
                    try:
                        cantidad = int(cantidades[i]) if cantidades[i] else 0
                    except ValueError:
                        return JsonResponse({
                            'success': False,
                            'message': f'Cantidad inválida para el producto en la posición {i+1}.'
                        }, status=400)

                    if cantidad <= 0:
                        continue

                    producto = Producto.objects.get(id=producto_id)
                    stock_field = 'stock_sede1' if sede.nombre == "FarmaXpress Sede Sur" else 'stock_sede2'
                    stock_disponible = getattr(producto, stock_field)

                    if cantidad > stock_disponible:
                        return JsonResponse({
                            'success': False,
                            'message': f'Stock insuficiente para {producto.nombre}. Disponible: {stock_disponible}.'
                        }, status=400)

                    # Crear detalle de venta
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio,
                        subtotal=cantidad * producto.precio
                    )

                    # Actualizar stock
                    setattr(producto, stock_field, stock_disponible - cantidad)
                    producto.save()

                # Actualizar el total de la venta
                venta.actualizar_total()

            return JsonResponse({
                'success': True,
                'message': 'Venta registrada exitosamente.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar la venta: {str(e)}'
            }, status=500)

    else:
        clientes = Cliente.objects.all()
        productos_disponibles = Producto.objects.filter(fecha_baja__isnull=True)
        form = VentaForm()
        context = {
            'form': form,
            'clientes': clientes,
            'productos_disponibles': productos_disponibles,
            'sede': request.user.sede.nombre if request.user.sede else 'Sin sede'
        }
        return render(request, 'registrar_venta.html', context)

from django.shortcuts import render, redirect
from home.models import Usuario
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
# Create your views here.

# ---------------------------- INICIO DE SESIÓN ---------------------------------


@csrf_protect
def iniciar_sesion(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        postEmail = request.POST.get('email')
        postPsw = request.POST.get('password')
        
        # Validar si el usuario existe
        user = authenticate(request, username=postEmail, password=postPsw)
        
        if user is None:
            login(request, user)
            return redirect('dashboard')
        else:
            try:
                user = Usuario.objects.get(username=postEmail)
                messages.error(request, 'Contraseña incorrecta')
            except Usuario.DoesNotExist:
                messages.error(request, 'El usuario no existe')
            return redirect('iniciar_sesion')


#
# ---------------------------- REESTABLECER CONTRASEÑA ---------------------------------
#

def reestablecer_contrasena(request):
    return render(request, 'reestablecer_contrasena.html')
def actualizar_contraseña(request):
    if request.method == 'POST':
        postEmail = request.POST.get('email')
        postPassword = request.POST.get('password')
        postPassword2 = request.POST.get('password2')
        
        if postPassword != postPassword2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('reestablecer_contrasena')
        
        try:
            user = Usuario.objects.get(username=postEmail)
        except Usuario.DoesNotExist:
            messages.error(request, 'El usuario no existe')
            return redirect('reestablecer_contrasena')
        
        user.set_password(postPassword)
        user.save()
        messages.success(request, 'Contraseña actualizada correctamente')
        return redirect('iniciar_sesion')


#
# ---------------------------- VISTA INICIO ---------------------------------
#

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def cerrar_sesion(request):
    return render(request, 'inicio_sesion.html')
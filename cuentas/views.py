from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm, RegistroUsuarioForm
from .models import Profile
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import authenticate

# Registro de usuario
def register(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            rol = form.cleaned_data['rol']  # o grupo si lo tenés así

            # Crear perfil si no existe
            perfil, created = Profile.objects.get_or_create(user=user)
            perfil.rol = rol
            perfil.save()

            login(request, user)
            messages.success(request, 'Usuario creado y perfil asignado')
            return redirect('dashboard')
    else:
        form = RegistroUsuarioForm()
    return render(request,'cuentas/register.html', {'form': form})


# Login de usuario

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirigir según rol
            perfil = user.profile
            rol = perfil.rol.lower()
            if rol == "socio":
                return redirect("mis_clases")
            elif rol == "entrenador":
                return redirect("lista_alumnos")
            elif rol in ["admin", "administrador"]:
                return redirect("gestion_usuarios")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "registration/login.html")

# Dashboard dinámico
@login_required
def dashboard(request):
    perfil = request.user.profile  # cada usuario tiene su perfil
    return render(request, 'cuentas/dashboard.html', {"perfil": perfil})


# Editar perfil
@login_required
def editar_perfil(request):
    perfil = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=perfil)
    return render(request, 'cuentas/editar_perfil.html', {'form': form})

# vistas de ejemplo para cada rol
@login_required
def mis_clases(request):
    return render(request, "cuentas/mis_clases.html")

@login_required
def lista_alumnos(request):
    return render(request, "cuentas/lista_alumnos.html")

@login_required
def gestion_usuarios(request):
    return render(request, "cuentas/gestion_usuarios.html")
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .forms import RegistroUsuarioForm


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            #Asignar el grupo 

            grupo = form.cleaned_data['grupo']
            user.groups.add(grupo)
            messages.success(request, 'Usuario creado y perfil asignado')

            #opcional: loguear automaticamente al usuario
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistroUsuarioForm()
    return render(request,'cuentas/register.html', {'form': form})
    
@login_required
def dashboard(request):
    return render(request, 'cuentas/dashboard.html')

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
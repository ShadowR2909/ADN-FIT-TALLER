from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .forms import (
    RegistroUsuarioForm, 
    ProfileForm, 
    # Asegúrate de importar RutinaForm desde donde corresponda
    RutinaForm, 
)
from .models import Profile
# Asegúrate de que estas importaciones de modelos de gestión sean correctas
from gestion.models import Rutina, Membresia, Plan 

# --- Funciones de Comprobación de Roles ---

def es_administrador(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.rol == 'Administrador'

def es_entrenador(user):
    # El administrador también puede realizar tareas de entrenador
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.rol in ['Entrenador', 'Administrador']

def es_socio(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.rol == 'Socio'

# --- Vistas de Autenticación ---

def login_view(request):
    """VISTA DE LOGIN FUNCIONAL: Procesa la autenticación del usuario."""
    if request.user.is_authenticated:
        # Redirección al nuevo nombre de URL 'dashboard'
        return redirect('dashboard') 
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido/a, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Nombre de usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Error en el formulario. Por favor, verifica las credenciales.")
    else:
        form = AuthenticationForm()
        
    context = {'form': form}
    return render(request, 'registration/login.html', context)

@transaction.atomic
def register(request):
    """VISTA DE REGISTRO: Registra un nuevo Socio."""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save() 
            messages.success(request, f"Usuario {user.username} registrado exitosamente como Socio.")
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Error en el formulario de registro.")
    else:
        form = RegistroUsuarioForm()
    context = {'form': form, 'rol_default': 'Socio'}
    return render(request, 'cuentas/register.html', context)

@login_required
def dashboard(request):
    """DASHBOARD PRINCIPAL: Usa un solo template para todos los roles."""
    rol = request.user.profile.rol
    context = {'rol': rol} # Se mantiene rol en el contexto por si se necesita
    return render(request, 'cuentas/dashboard.html', context)

# --- Vistas de Perfil ---

@login_required
@transaction.atomic
def editar_perfil(request):
    """EDITAR PERFIL: Permite a cualquier usuario modificar su perfil."""
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('editar_perfil')
        else:
            messages.error(request, "Error al actualizar el perfil.")
    else:
        form = ProfileForm(instance=profile)
        
    return render(request, 'cuentas/editar_perfil.html', {'form': form})

# --- Vistas de Administración y Entrenador ---

@login_required
@user_passes_test(es_administrador)
def gestion_usuarios(request):
    """GESTION DE USUARIOS: Muestra lista de todos los usuarios (Solo Admin)."""
    usuarios = User.objects.all().order_by('username')
    return render(request, 'cuentas/gestion_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_entrenador)
def lista_alumnos(request):
    """LISTA DE ALUMNOS (SOCIOS): Muestra solo usuarios con rol 'Socio'."""
    socios = User.objects.filter(profile__rol='Socio').order_by('last_name')
    return render(request, 'cuentas/lista_alumnos.html', {'socios': socios})

@login_required
@user_passes_test(es_administrador)
@transaction.atomic
def editar_usuario_view(request, user_id):
    """
    Permite al Administrador editar un usuario (rol, activo, etc.) y su perfil.
    Implementa la lógica para actualizar el estado is_active.
    """
    usuario_a_editar = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=usuario_a_editar)
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile) 
        
        # --- Lógica para el estado is_active ---
        # Si el checkbox está marcado, request.POST.get('is_active') devuelve 'on'. 
        # Si no está marcado, request.POST.get('is_active') devuelve None.
        is_active_new_status = request.POST.get('is_active')
        usuario_a_editar.is_active = (is_active_new_status == 'on') 
        # ----------------------------------------
        
        if profile_form.is_valid():
            profile_form.save()
            
            # Guardamos el estado activo/inactivo en el objeto User
            usuario_a_editar.save() 
            
            messages.success(request, f"Usuario '{usuario_a_editar.username}' actualizado exitosamente. Estado Activo: {usuario_a_editar.is_active}")
            return redirect('gestion_usuarios')
        else:
            messages.error(request, "Error al actualizar el usuario. Revisa el formulario.")
    else:
        profile_form = ProfileForm(instance=profile)
        
    context = {
        'usuario_a_editar': usuario_a_editar,
        'profile_form': profile_form,
        'titulo': f'Editar Usuario: {usuario_a_editar.username}'
    }
    
    return render(request, 'cuentas/editar_usuario.html', context)


@login_required
@user_passes_test(es_entrenador)
def asignar_rutinas_view(request):
    """ASIGNAR RUTINAS: Permite al entrenador asignar rutinas a sus alumnos."""
    if request.method == 'POST':
        # Asume que RutinaForm está disponible y es correcto
        form = RutinaForm(request.POST) 
        if form.is_valid():
            rutina = form.save(commit=False)
            rutina.entrenador = request.user 
            rutina.save()
            
            messages.success(request, f"Rutina '{rutina.nombre}' asignada con éxito a {rutina.socio.username}.")
            return redirect('asignar_rutinas') 
        else:
            messages.error(request, "Error al asignar la rutina. Revisa los datos.")
    else:
        form = RutinaForm() 

    # Asume que la relación existe y es correcta
    rutinas_asignadas = Rutina.objects.filter(entrenador=request.user).order_by('-fecha_asignacion')

    context = {
        'form': form,
        'rutinas_asignadas': rutinas_asignadas,
    }
    return render(request, 'cuentas/asignar_rutinas.html', context)


# --- Vistas del Socio ---

@login_required
@user_passes_test(es_socio)
def mi_plan_view(request):
    """VER MI PLAN/MEMBRESÍA: Muestra la membresía activa del socio."""
    try:
        # Asumiendo que definiste el related_name='gestion_membresia' en gestion/models.py
        membresia = request.user.gestion_membresia 
    except Membresia.DoesNotExist:
        membresia = None
    
    context = {'membresia': membresia}
    return render(request, 'cuentas/mi_plan.html', context)

@login_required
@user_passes_test(es_socio)
def mis_clases(request):
    """
    Muestra el horario de clases disponibles y maneja la inscripción.
    """
    clases_disponibles = Clase.objects.all().order_by('dia_semana', 'hora_inicio')
    
    # Obtener las clases a las que el usuario ya está inscrito
    clases_inscritas = InscripcionClase.objects.filter(socio=request.user).values_list('clase_id', flat=True)
    
    if request.method == 'POST':
        clase_id = request.POST.get('clase_id')
        clase = get_object_or_404(Clase, id=clase_id)
        
        try:
            # Lógica de validación antes de la inscripción
            if InscripcionClase.objects.filter(socio=request.user, clase=clase).exists():
                messages.error(request, f"Ya estás inscrito en la clase '{clase.nombre}'.")
            elif clase.inscritos.count() >= clase.cupo_maximo:
                messages.error(request, f"Lo sentimos, la clase '{clase.nombre}' ya no tiene cupos disponibles.")
            else:
                InscripcionClase.objects.create(socio=request.user, clase=clase)
                messages.success(request, f"¡Inscripción exitosa a la clase '{clase.nombre}'!")
        except Exception as e:
            messages.error(request, f"Ocurrió un error al inscribirte. ({e})")
            
        return redirect('mis_clases')
    
    context = {
        'clases_disponibles': clases_disponibles,
        'clases_inscritas': clases_inscritas, # Usaremos esto en la plantilla
    }
    
    return render(request, 'cuentas/mis_clases.html', context)

@login_required
@user_passes_test(es_socio)
def mi_rutina_view(request):
    """VER MI RUTINA: Muestra las rutinas activas asignadas por el entrenador."""
    rutinas = Rutina.objects.filter(
        socio=request.user, 
        activa=True
    ).order_by('-fecha_asignacion') # Ordena para que la más nueva sea la primera (first())
    
    context = {
        'rutinas': rutinas # Pasamos el queryset completo
    }
    return render(request, 'cuentas/mi_rutina.html', context)

@login_required
def mi_membresia(request):
    try:
        membresia = request.user.membresia  # Ajusta si la relación es diferente
    except Membresia.DoesNotExist:
        membresia = None
    return render(request, 'cuentas/mi_membresia.html', {'membresia': membresia})

# Vistas auxiliares si se necesitan en urls.py
def logout_view(request):
    """Cierra la sesión del usuario."""
    logout(request)
    messages.info(request, "Sesión cerrada con éxito.")
    return redirect('login')
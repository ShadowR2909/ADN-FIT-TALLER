from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import Http404 # Para el helper de eliminación
from .models import Plan, Membresia, Clase # Importamos Clase
from .forms import PlanForm, MembresiaForm, ClaseForm # Importamos ClaseForm
from cuentas.views import es_administrador, es_entrenador # Importamos las funciones de rol

# --- GESTIÓN DE PLANES Y MEMBRESÍAS ---

@login_required
@user_passes_test(es_administrador)
def gestion_planes_view(request):
    """Muestra todos los planes y maneja la creación de nuevos planes."""
    planes = Plan.objects.all().order_by('precio')
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Plan '{form.cleaned_data['nombre']}' creado exitosamente.")
            return redirect('gestion_planes')
        else:
            messages.error(request, "Error al crear el plan. Revisa el formulario.")
    else:
        form = PlanForm()
    context = {'planes': planes, 'form': form, 'titulo': 'Gestión de Planes de Membresía'}
    return render(request, 'gestion/gestion_planes.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_plan_view(request, plan_id):
    """Edita un plan existente."""
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f"Plan '{plan.nombre}' actualizado.")
            return redirect('gestion_planes')
        else:
            messages.error(request, "Error al actualizar el plan.")
    else:
        form = PlanForm(instance=plan)
    context = {'form': form, 'plan': plan, 'titulo': f'Editar Plan: {plan.nombre}'}
    return render(request, 'gestion/editar_plan.html', context)


@login_required
@user_passes_test(es_administrador)
def gestion_membresias_view(request):
    """Muestra todas las membresías y permite crear nuevas."""
    membresias = Membresia.objects.all().select_related('socio', 'plan').order_by('-fecha_vencimiento')
    if request.method == 'POST':
        form = MembresiaForm(request.POST)
        if form.is_valid():
            membresia = form.save(commit=False)
            if Membresia.objects.filter(socio=membresia.socio).exists():
                messages.warning(request, f"El socio {membresia.socio.username} ya tiene una membresía asignada. Por favor, edítela en su lugar.")
                return redirect('gestion_membresias')
            membresia.save()
            messages.success(request, f"Membresía asignada a {membresia.socio.username}.")
            return redirect('gestion_membresias')
        else:
            messages.error(request, "Error al asignar la membresía. Revisa el formulario.")
    else:
        form = MembresiaForm()
    context = {'membresias': membresias, 'form': form, 'titulo': 'Gestión de Membresías de Socios'}
    return render(request, 'gestion/gestion_membresias.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_membresia_view(request, membresia_id):
    """Edita una membresía existente."""
    membresia = get_object_or_404(Membresia, id=membresia_id)
    if request.method == 'POST':
        form = MembresiaForm(request.POST, instance=membresia)
        if form.is_valid():
            form.save()
            messages.success(request, f"Membresía de {membresia.socio.username} actualizada.")
            return redirect('gestion_membresias')
        else:
            messages.error(request, "Error al actualizar la membresía.")
    else:
        form = MembresiaForm(instance=membresia)
    context = {'form': form, 'membresia': membresia, 'titulo': f'Editar Membresía de {membresia.socio.username}'}
    return render(request, 'gestion/editar_membresia.html', context)

# --- GESTIÓN DE CLASES ---

@login_required
@user_passes_test(es_administrador)
def gestion_clases_view(request):
    """Muestra todas las clases y maneja la creación de nuevas clases."""
    clases = Clase.objects.all().select_related('entrenador').order_by('dia_semana', 'hora_inicio')
    
    if request.method == 'POST':
        form = ClaseForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Clase '{form.cleaned_data['nombre']}' creada exitosamente.")
                return redirect('gestion_clases')
            except Exception as e:
                # Captura el error de restricción unique_together si ya existe una clase con ese nombre, día y hora
                messages.error(request, f"Error al guardar: Ya existe una clase con esa combinación de nombre, día y hora. ({e})")
        else:
            messages.error(request, "Error al crear la clase. Revisa el formulario.")
    else:
        form = ClaseForm()

    context = {
        'clases': clases,
        'form': form,
        'titulo': 'Gestión de Clases Grupales'
    }
    return render(request, 'gestion/gestion_clases.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_clase_view(request, clase_id):
    """Edita una clase existente."""
    clase = get_object_or_404(Clase, id=clase_id)
    
    if request.method == 'POST':
        form = ClaseForm(request.POST, instance=clase)
        if form.is_valid():
            form.save()
            messages.success(request, f"Clase '{clase.nombre}' actualizada.")
            return redirect('gestion_clases')
        else:
            messages.error(request, "Error al actualizar la clase.")
    else:
        form = ClaseForm(instance=clase)

    context = {'form': form, 'clase': clase, 'titulo': f'Editar Clase: {clase.nombre}'}
    return render(request, 'gestion/editar_clase.html', context)

# --- REPORTES Y AUXILIARES ---

@login_required
@user_passes_test(es_administrador)
def reportes_view(request):
    """Vista de Reportes y Estadísticas (Requiere implementación)."""
    # Aquí puedes añadir lógica para calcular estadísticas y pasarlas al contexto
    
    context = {
        'titulo': 'Reportes y Estadísticas del Gimnasio'
    }
    return render(request, 'gestion/reportes.html', context)


# VISTA AUXILIAR PARA ELIMINACIÓN GENÉRICA
@login_required
@user_passes_test(es_administrador)
def eliminar_registro_view(request, model_name, pk):
    """
    Vista genérica para eliminar un registro de un modelo específico.
    Se usa con URLs tipo: /gestion/eliminar/plan/1/
    """
    model_map = {
        'plan': (Plan, 'gestion_planes'),
        'membresia': (Membresia, 'gestion_membresias'),
        'clase': (Clase, 'gestion_clases'),
        # Añadir otros modelos aquí si es necesario
    }

    if model_name not in model_map:
        raise Http404("Modelo no encontrado para la eliminación.")

    ModelClass, redirect_name = model_map[model_name]
    
    obj = get_object_or_404(ModelClass, pk=pk)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, f"{ModelClass.__name__} eliminado exitosamente.")
        return redirect(redirect_name)
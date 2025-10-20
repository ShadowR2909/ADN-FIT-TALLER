from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Accesorio, ReporteFaltante, Reposicion, HistorialAccesorio
from .forms import ReporteFaltanteForm, ReposicionForm, AccesorioForm
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin

<<<<<<< HEAD
# Mixin de verificación de rol (Asumiendo que 'Entrenador' o 'Administrador' son Staff)
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Asumiendo que el campo 'rol' está en user.profile
        return self.request.user.is_authenticated and (
            self.request.user.profile.rol in ['Entrenador', 'Administrador']
        )
# NUEVO: Historial completo de accesorios (reportes y reposiciones)
@login_required
def historial_accesorios(request):
    """Muestra todos los reportes y reposiciones, con quién y cuándo se realizaron."""
    reportes = ReporteFaltante.objects.all().select_related('accesorio', 'empleado_reporte', 'empleado_confirmacion')
    reposiciones = Reposicion.objects.all().select_related('reporte', 'administrador')
    
    context = {
        'reportes': reportes,
        'reposiciones': reposiciones,
        'page_title': 'Historial de Accesorios',
    }
    return render(request, 'accesorios/historial_accesorios.html', context)


=======
>>>>>>> 34487de0ffefc5d1361982c210e4596e0410ff2d

# ------------------------------
# HISTORIAL DE ACCESORIOS
# ------------------------------
@login_required
def historial_accesorios(request):
    reportes = ReporteFaltante.objects.all().select_related('accesorio', 'empleado_reporte', 'empleado_confirmacion')
    historial_acciones = HistorialAccesorio.objects.all().select_related('usuario')
    
    context = {
        'reportes': reportes,
        'historial_acciones': historial_acciones,
        'page_title': 'Historial de Accesorios',
    }
    return render(request, 'accesorios/historial_accesorios.html', context)

# ------------------------------
# INVENTARIO
# ------------------------------
@login_required
def inventario_list(request):
    accesorios = Accesorio.objects.filter(activo=True)
    context = {'accesorios': accesorios}
    return render(request, 'accesorios/inventario_list.html', context)

# ------------------------------
# REPORTE DE FALTANTE
# ------------------------------
@login_required
def reporte_faltante_create(request):
    if request.method == 'POST':
        form = ReporteFaltanteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.empleado_reporte = request.user
            reporte.save()
            messages.success(request, 'Reporte de faltante creado exitosamente. Pendiente de confirmación.')
            return redirect('accesorios:reportes_pendientes')
    else:
        form = ReporteFaltanteForm()
    
    context = {'form': form, 'page_title': 'Crear Reporte de Faltante'}
    return render(request, 'accesorios/reporte_form.html', context)

@login_required
def reportes_pendientes_list(request):
    reportes = ReporteFaltante.objects.filter(estado='PENDIENTE')
    context = {'reportes': reportes}
    return render(request, 'accesorios/reportes_pendientes.html', context)

@login_required
def reporte_confirmar(request, pk):
    reporte = get_object_or_404(ReporteFaltante, pk=pk)

<<<<<<< HEAD
=======
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'Administrador':
        messages.error(request, "Permiso denegado: solo los Administradores pueden confirmar o descartar reportes.")
        return redirect('accesorios:reportes_pendientes')

>>>>>>> 34487de0ffefc5d1361982c210e4596e0410ff2d
    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'confirmar':
            reporte.estado = 'CONFIRMADO'
<<<<<<< HEAD
            # Descontamos del stock del accesorio
=======
>>>>>>> 34487de0ffefc5d1361982c210e4596e0410ff2d
            accesorio = reporte.accesorio
            if accesorio.cantidad_total >= reporte.cantidad_faltante:
                accesorio.cantidad_total -= reporte.cantidad_faltante
            else:
<<<<<<< HEAD
                accesorio.cantidad_total = 0  # Por si la cantidad faltante es mayor
            accesorio.save()

=======
                accesorio.cantidad_total = 0
            accesorio.save()
>>>>>>> 34487de0ffefc5d1361982c210e4596e0410ff2d
            messages.success(request, f'Reporte de {accesorio.nombre} confirmado. Stock actualizado.')

        elif accion == 'descartar':
            reporte.estado = 'DESCARTADO'
            messages.warning(request, f'Reporte de {reporte.accesorio.nombre} descartado.')

        reporte.empleado_confirmacion = request.user
        reporte.fecha_confirmacion = timezone.now()
        reporte.save()
        return redirect('accesorios:reportes_pendientes')

    return redirect('accesorios:reportes_pendientes')

<<<<<<< HEAD


# 4. GESTIÓN DE REPOSICIÓN (Flujo de Compra/Actualización de Stock)
class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin que solo permite el acceso a usuarios con rol 'Administrador'."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.rol == 'Administrador'

=======
# ------------------------------
# REPOSICIÓN DE STOCK
# ------------------------------
>>>>>>> 34487de0ffefc5d1361982c210e4596e0410ff2d
@login_required
def reposicion_create(request, pk):
    reporte = get_object_or_404(ReporteFaltante, pk=pk, estado='CONFIRMADO')

    if request.user.profile.rol != 'Administrador':
        messages.error(request, "Permiso denegado: solo Administradores pueden reponer stock.")
        return redirect('accesorios:reportes_pendientes')
    
    if hasattr(reporte, 'reposicion'):
        messages.warning(request, "Este reporte ya fue procesado y el stock fue actualizado.")
        return redirect('accesorios:reportes_pendientes')

    if request.method == 'POST':
        form = ReposicionForm(request.POST)
        if form.is_valid():
            cantidad_comprada = form.cleaned_data['cantidad_comprada']
            reposicion = Reposicion.objects.create(
                reporte=reporte,
                cantidad_comprada=cantidad_comprada,
                administrador=request.user
            )
            accesorio = reporte.accesorio
            accesorio.cantidad_total += cantidad_comprada
            accesorio.save()
            reporte.estado = 'CERRADO'
            reporte.save()
            messages.success(request, f'¡Stock de {accesorio.nombre} actualizado! Se agregaron {cantidad_comprada} unidades.')
            return redirect('accesorios:reportes_pendientes')
    else:
        form = ReposicionForm(initial={'cantidad_comprada': reporte.cantidad_faltante})

    context = {
        'form': form,
        'reporte': reporte,
        'page_title': 'Procesar Reposición de Stock'
    }
    return render(request, 'accesorios/reposicion_form.html', context)

# ------------------------------
# ACCESORIOS CRUD
# ------------------------------
@login_required
def accesorio_create(request):
    if request.user.profile.rol != 'Administrador':
        messages.error(request, "Permiso denegado: solo Administradores pueden agregar accesorios.")
        return redirect('accesorios:inventario_list')
    
    if request.method == 'POST':
        form = AccesorioForm(request.POST)
        if form.is_valid():
            accesorio = form.save(commit=False)
            accesorio.creado_por = request.user
            accesorio.activo = True  # <-- Soft delete
            accesorio.save()
            HistorialAccesorio.objects.create(
                accesorio_nombre=accesorio.nombre,
                accesorio_id=accesorio.id,
                accion='CREADO',
                usuario=request.user,
                detalles=f'Cantidad inicial: {accesorio.cantidad_total} unidades. Descripción: {accesorio.descripcion or "Sin descripción"}'
            )
            messages.success(request, f'¡Accesorio "{accesorio.nombre}" agregado exitosamente al inventario!')
            return redirect('accesorios:inventario_list')
    else:
        form = AccesorioForm()
    
    return render(request, 'accesorios/accesorio_form.html', {'form': form, 'page_title': 'Agregar Nuevo Accesorio'})

@login_required
def accesorio_update(request, pk):
    accesorio = get_object_or_404(Accesorio, pk=pk)
    if request.user.profile.rol != 'Administrador':
        messages.error(request, "Permiso denegado: solo Administradores pueden editar accesorios.")
        return redirect('accesorios:inventario_list')
    
    if request.method == 'POST':
        nombre_anterior = accesorio.nombre
        cantidad_anterior = accesorio.cantidad_total
        descripcion_anterior = accesorio.descripcion

        form = AccesorioForm(request.POST, instance=accesorio)
        if form.is_valid():
            accesorio = form.save(commit=False)
            accesorio.modificado_por = request.user
            accesorio.save()
            cambios = []
            if nombre_anterior != accesorio.nombre:
                cambios.append(f'Nombre: "{nombre_anterior}" → "{accesorio.nombre}"')
            if cantidad_anterior != accesorio.cantidad_total:
                cambios.append(f'Cantidad: {cantidad_anterior} → {accesorio.cantidad_total}')
            if descripcion_anterior != accesorio.descripcion:
                cambios.append(f'Descripción: "{descripcion_anterior or "Sin descripción"}" → "{accesorio.descripcion or "Sin descripción"}"')
            HistorialAccesorio.objects.create(
                accesorio_nombre=accesorio.nombre,
                accesorio_id=accesorio.id,
                accion='EDITADO',
                usuario=request.user,
                detalles=f'Cambios realizados: {"; ".join(cambios)}' if cambios else 'Sin cambios detectados'
            )
            messages.success(request, f'¡Accesorio "{accesorio.nombre}" actualizado exitosamente!')
            return redirect('accesorios:inventario_list')
    else:
        form = AccesorioForm(instance=accesorio)
    
    return render(request, 'accesorios/accesorio_form.html', {'form': form, 'page_title': f'Editar Accesorio: {accesorio.nombre}'})

@login_required
def accesorio_delete(request, pk):
    accesorio = get_object_or_404(Accesorio, pk=pk)
    if request.user.profile.rol != 'Administrador':
        messages.error(request, "Permiso denegado: solo Administradores pueden eliminar accesorios.")
        return redirect('accesorios:inventario_list')

    if request.method == 'POST':
        # Soft delete
        accesorio.activo = False
        accesorio.save()
        HistorialAccesorio.objects.create(
            accesorio_nombre=accesorio.nombre,
            accesorio_id=accesorio.id,
            accion='ELIMINADO',
            usuario=request.user,
            detalles=f'Eliminado con {accesorio.cantidad_total} unidades en stock. Descripción: {accesorio.descripcion or "Sin descripción"}'
        )
        messages.success(request, f'¡Accesorio "{accesorio.nombre}" eliminado exitosamente del inventario!')
        return redirect('accesorios:inventario_list')

    context = {
        'accesorio': accesorio,
        'page_title': f'Eliminar Accesorio: {accesorio.nombre}'
    }
    return render(request, 'accesorios/accesorio_delete.html', context)



@login_required
def inventario_inactivos(request):
    accesorios_inactivos = Accesorio.objects.filter(activo=False)
    context = {
        'accesorios': accesorios_inactivos,
        'page_title': 'Accesorios Inactivos',
        'inactivos': True
    }
    return render(request, 'accesorios/inventario_inactivos.html', context)


@login_required
def accesorio_reactivar(request, pk):
    accesorio = get_object_or_404(Accesorio, pk=pk, activo=False)
    accesorio.activo = True
    accesorio.save()

    # Guardamos en historial usando los campos existentes
    HistorialAccesorio.objects.create(
        accesorio_nombre=accesorio.nombre,
        accesorio_id=accesorio.id,
        accion='REACTIVADO',
        detalles=f'Accesorio {accesorio.nombre} reactivado por {request.user.username}',
        usuario=request.user
    )

    messages.success(request, f'¡Accesorio "{accesorio.nombre}" reactivado exitosamente!')
    return redirect('accesorios:inventario_inactivos')

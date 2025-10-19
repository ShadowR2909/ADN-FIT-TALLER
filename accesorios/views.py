from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Accesorio, ReporteFaltante, Reposicion, HistorialAccesorio
from .forms import ReporteFaltanteForm, ReposicionForm, AccesorioForm
from django.utils import timezone

# Importar lógica de roles si la tienes, por ahora solo requerimos staff
from django.contrib.auth.mixins import UserPassesTestMixin

# Mixin de verificación de rol (Asumiendo que 'Entrenador' o 'Administrador' son Staff)
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Asumiendo que el campo 'rol' está en user.profile
        return self.request.user.is_authenticated and (
            self.request.user.profile.rol in ['Entrenador', 'Administrador']
        )
# NUEVO: Historial completo de accesorios (reportes, reposiciones y acciones CRUD)
@login_required
def historial_accesorios(request):
    """Muestra todos los reportes, reposiciones y acciones CRUD, con quién y cuándo se realizaron."""
    reportes = ReporteFaltante.objects.all().select_related('accesorio', 'empleado_reporte', 'empleado_confirmacion')
    historial_acciones = HistorialAccesorio.objects.all().select_related('usuario')
    
    context = {
        'reportes': reportes,
        'historial_acciones': historial_acciones,
        'page_title': 'Historial de Accesorios',
    }
    return render(request, 'accesorios/historial_accesorios.html', context)



# 1. CONSULTA Y COMPARA ACCESORIOS (Listar Inventario)
@login_required
def inventario_list(request):
    """Permite a los empleados consultar y comparar el inventario actual."""
    accesorios = Accesorio.objects.all()
    context = {'accesorios': accesorios}
    return render(request, 'accesorios/inventario_list.html', context)

# 2. CREAR REPORTE DE FALTANTE (Flujo "Faltante")
@login_required
def reporte_faltante_create(request):
    """Permite a un empleado reportar un accesorio faltante."""
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

# 3. GESTIÓN Y CONFIRMACIÓN DE REPORTES (Flujo "Confirmacion")
@login_required
def reportes_pendientes_list(request):
    """Lista los reportes de faltantes que requieren confirmación."""
    reportes = ReporteFaltante.objects.filter(estado='PENDIENTE')
    context = {'reportes': reportes}
    return render(request, 'accesorios/reportes_pendientes.html', context)

@login_required
def reporte_confirmar(request, pk):
    """Permite a un empleado/admin confirmar o descartar un reporte."""
    reporte = get_object_or_404(ReporteFaltante, pk=pk)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'confirmar':
            reporte.estado = 'CONFIRMADO'
            # Descontamos del stock del accesorio
            accesorio = reporte.accesorio
            if accesorio.cantidad_total >= reporte.cantidad_faltante:
                accesorio.cantidad_total -= reporte.cantidad_faltante
            else:
                accesorio.cantidad_total = 0  # Por si la cantidad faltante es mayor
            accesorio.save()

            messages.success(request, f'Reporte de {accesorio.nombre} confirmado. Stock actualizado.')

        elif accion == 'descartar':
            reporte.estado = 'DESCARTADO'
            messages.warning(request, f'Reporte de {reporte.accesorio.nombre} descartado.')

        reporte.empleado_confirmacion = request.user
        reporte.fecha_confirmacion = timezone.now()
        reporte.save()
        return redirect('accesorios:reportes_pendientes')

    return redirect('accesorios:reportes_pendientes')



# 4. GESTIÓN DE REPOSICIÓN (Flujo de Compra/Actualización de Stock)
class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin que solo permite el acceso a usuarios con rol 'Administrador'."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.rol == 'Administrador'

@login_required
def reposicion_create(request, pk):
    """
    Permite al Administrador procesar la compra de un Reporte CONFIRMADO,
    actualizando el stock del Accesorio.
    """
    reporte = get_object_or_404(ReporteFaltante, pk=pk, estado='CONFIRMADO')
    
    # Simple check de rol, aunque la URL solo estará visible para Admin
    if not request.user.profile.rol == 'Administrador':
        messages.error(request, "Permiso denegado: solo Administradores pueden reponer stock.")
        return redirect('accesorios:reportes_pendientes')
    
    # Si el reporte ya tiene una reposición asociada, no se puede volver a reponer
    if hasattr(reporte, 'reposicion'):
        messages.warning(request, "Este reporte ya fue procesado y el stock fue actualizado.")
        return redirect('accesorios:reportes_pendientes')

    if request.method == 'POST':
        form = ReposicionForm(request.POST)
        if form.is_valid():
            cantidad_comprada = form.cleaned_data['cantidad_comprada']
            
            # 1. Crear el objeto Reposicion
            reposicion = Reposicion.objects.create(
                reporte=reporte,
                cantidad_comprada=cantidad_comprada,
                administrador=request.user
            )
            
            # 2. Actualizar la cantidad total del Accesorio
            accesorio = reporte.accesorio
            accesorio.cantidad_total += cantidad_comprada
            accesorio.save()
            
            # 3. Marcar el reporte como CERRADO (o un estado final, para no reaparecer)
            reporte.estado = 'CERRADO'
            reporte.save()
            
            messages.success(request, f'¡Stock de {accesorio.nombre} actualizado! Se agregaron {cantidad_comprada} unidades.')
            return redirect('accesorios:reportes_pendientes')
    else:
        # Pre-llenar el formulario con la cantidad faltante reportada
        form = ReposicionForm(initial={'cantidad_comprada': reporte.cantidad_faltante})

    context = {
        'form': form,
        'reporte': reporte,
        'page_title': 'Procesar Reposición de Stock'
    }
    return render(request, 'accesorios/reposicion_form.html', context)


# 5. CREAR NUEVO ACCESORIO (Solo Administradores)
@login_required
def accesorio_create(request):
    """
    Permite al Administrador agregar nuevos accesorios al inventario.
    """
    # Verificar que el usuario sea administrador
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'Administrador':
        messages.error(request, "Permiso denegado: solo Administradores pueden agregar nuevos accesorios.")
        return redirect('accesorios:inventario_list')
    
    if request.method == 'POST':
        form = AccesorioForm(request.POST)
        if form.is_valid():
            accesorio = form.save(commit=False)
            accesorio.creado_por = request.user
            accesorio.save()
            
            # Registrar en el historial
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
    
    context = {
        'form': form,
        'page_title': 'Agregar Nuevo Accesorio'
    }
    return render(request, 'accesorios/accesorio_form.html', context)

# 6. EDITAR ACCESORIO EXISTENTE (Solo Administradores)
@login_required
def accesorio_update(request, pk):
    """
    Permite al Administrador editar accesorios existentes en el inventario.
    """
    accesorio = get_object_or_404(Accesorio, pk=pk)
    
    # Verificar que el usuario sea administrador
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'Administrador':
        messages.error(request, "Permiso denegado: solo Administradores pueden editar accesorios.")
        return redirect('accesorios:inventario_list')
    
    if request.method == 'POST':
        # Guardar valores anteriores para el historial
        nombre_anterior = accesorio.nombre
        cantidad_anterior = accesorio.cantidad_total
        descripcion_anterior = accesorio.descripcion
        
        form = AccesorioForm(request.POST, instance=accesorio)
        if form.is_valid():
            accesorio = form.save(commit=False)
            accesorio.modificado_por = request.user
            accesorio.save()
            
            # Registrar cambios en el historial
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
    
    context = {
        'form': form,
        'page_title': f'Editar Accesorio: {accesorio.nombre}',
        'accesorio': accesorio
    }
    return render(request, 'accesorios/accesorio_form.html', context)

# 7. ELIMINAR ACCESORIO (Solo Administradores)
@login_required
def accesorio_delete(request, pk):
    """
    Permite al Administrador eliminar accesorios del inventario.
    """
    accesorio = get_object_or_404(Accesorio, pk=pk)
    
    # Verificar que el usuario sea administrador
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'Administrador':
        messages.error(request, "Permiso denegado: solo Administradores pueden eliminar accesorios.")
        return redirect('accesorios:inventario_list')
    
    # Verificar si el accesorio tiene reportes asociados
    reportes_asociados = ReporteFaltante.objects.filter(accesorio=accesorio).count()
    
    if request.method == 'POST':
        nombre_accesorio = accesorio.nombre
        accesorio_id = accesorio.id
        cantidad_stock = accesorio.cantidad_total
        descripcion_accesorio = accesorio.descripcion
        
        # Registrar en el historial ANTES de eliminar
        HistorialAccesorio.objects.create(
            accesorio_nombre=nombre_accesorio,
            accesorio_id=accesorio_id,
            accion='ELIMINADO',
            usuario=request.user,
            detalles=f'Eliminado con {cantidad_stock} unidades en stock. Descripción: {descripcion_accesorio or "Sin descripción"}'
        )
        
        accesorio.delete()
        messages.success(request, f'¡Accesorio "{nombre_accesorio}" eliminado exitosamente del inventario!')
        return redirect('accesorios:inventario_list')
    
    context = {
        'accesorio': accesorio,
        'reportes_asociados': reportes_asociados,
        'page_title': f'Eliminar Accesorio: {accesorio.nombre}'
    }
    return render(request, 'accesorios/accesorio_delete.html', context)
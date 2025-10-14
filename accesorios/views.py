from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Accesorio, ReporteFaltante, Reposicion
from .forms import ReporteFaltanteForm, ReposicionForm
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

    

    
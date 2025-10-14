from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Accesorio, ReporteFaltante
from .forms import ReporteFaltanteForm
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

    # Opcional: Agregar aquí un chequeo de rol Staff para seguridad

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'confirmar':
            reporte.estado = 'CONFIRMADO'
            # Aquí podrías reducir la cantidad_total del Accesorio si lo deseas
            messages.success(request, f'Reporte de {reporte.accesorio.nombre} confirmado. ¡Necesitas comprar!')

        elif accion == 'descartar':
            reporte.estado = 'DESCARTADO'
            messages.warning(request, f'Reporte de {reporte.accesorio.nombre} descartado.')

        reporte.empleado_confirmacion = request.user
        reporte.fecha_confirmacion = timezone.now() # Asegura que timezone esté importado
        reporte.save()
        return redirect('accesorios:reportes_pendientes')

    # Para GET, simplemente redirigimos o mostramos una página simple
    return redirect('accesorios:reportes_pendientes')
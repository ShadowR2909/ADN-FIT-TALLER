from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from .models import Turno 
from .forms import TurnoForm 
from django.core.exceptions import ValidationError # Necesario para manejar errores de .clean()

# --- MIXINS DE PERMISOS ---

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin para restringir acceso a Admin y Entrenadores."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
            
        # Asume que el perfil está cargado y tiene un campo 'rol'
        return hasattr(user, 'profile') and user.profile.rol in ['Administrador', 'Entrenador']


# --- VISTAS PARA EL SOCIO ---

class TurnosDisponiblesView(LoginRequiredMixin, ListView):
    """Muestra los turnos que el SOCIO puede reservar (PENDIENTE)."""
    model = Turno
    template_name = 'turnos/socio_disponibles.html'
    context_object_name = 'turnos_disponibles'

    def get_queryset(self):
        """Filtra turnos que están PENDIENTES y no tienen socio asignado (o no es el actual)."""
        # IMPORTANTE: Asumimos que los turnos creados por Staff tienen socio=None
        return Turno.objects.filter(estado='PENDIENTE', socio__isnull=True).order_by('fecha_hora_inicio')


class TurnosMisReservasView(LoginRequiredMixin, ListView):
    """Muestra los turnos que el SOCIO ya tiene reservados (CONFIRMADO, CANCELADO, etc.)."""
    model = Turno
    template_name = 'turnos/socio_reservas.html'
    context_object_name = 'mis_reservas'

    def get_queryset(self):
        """Muestra todos los turnos del socio actual."""
        return Turno.objects.filter(socio=self.request.user).order_by('fecha_hora_inicio')


class TomarTurnoView(LoginRequiredMixin, View):
    """Permite al SOCIO tomar un turno PENDIENTE y cambiar su estado a CONFIRMADO."""
    def post(self, request, pk):
        # Buscamos el turno que esté PENDIENTE y sin socio asignado
        turno = get_object_or_404(Turno, pk=pk, estado='PENDIENTE', socio__isnull=True) 
        
        turno.socio = request.user
        turno.estado = 'CONFIRMADO' 
        
        try:
            # Ejecuta la validación de cupo (Turno.clean())
            turno.full_clean() 
            turno.save() 
            messages.success(request, "¡Turno reservado con éxito!")
        except ValidationError as e:
            # Capturamos el error de validación (ej. cupo lleno)
            error_message = list(e.message_dict.values())[0][0] if e.message_dict else "Error desconocido de validación."
            messages.error(request, f"Error al reservar: {error_message}")
            return redirect('turnos:disponibles')

        return redirect('turnos:mis_reservas')


class TurnoCancelView(LoginRequiredMixin, View):
    """Permite al SOCIO cancelar uno de sus turnos (solo si es su turno)."""
    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, socio=request.user) 
        
        if turno.estado == 'CONFIRMADO': 
            turno.estado = 'PENDIENTE' 
            turno.socio = None # Liberar el cupo para que otro lo tome
            turno.save()
            messages.info(request, "Tu turno ha sido cancelado. El cupo se ha liberado.")
        else:
            messages.error(request, "Este turno ya no se puede cancelar (Estado: %s)." % turno.estado)
            
        return redirect('turnos:mis_reservas')


# --- VISTAS PARA EL STAFF (Admin/Entrenador) ---

class TurnoCreationStaffView(StaffRequiredMixin, CreateView):
    """
    Permite al STAFF crear cupos (socio=None) o asignar turnos directamente.
    Usa el TurnoForm completo que incluye socio y estado.
    """
    model = Turno
    form_class = TurnoForm # Usamos el form completo
    template_name = 'turnos/staff_turno_form.html'
    success_url = reverse_lazy('turnos:staff_list')

    def get_form_kwargs(self):
        """Pasa el usuario actual al formulario."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        socio_seleccionado = form.cleaned_data.get('socio')
        
        # El formulario ya incluye 'socio' y 'estado' en cleaned_data si es Staff.
        # Al no usar commit=False, permitimos que el formulario se encargue de la asignación.
        
        # 1. Validación de Cupo
        try:
            form.instance.full_clean()
        except ValidationError as e:
            error_message = list(e.message_dict.values())[0][0] if e.message_dict else "Error de validación."
            messages.error(self.request, f"Error al guardar: {error_message}")
            return self.form_invalid(form)

        # 2. Mensaje de Éxito
        if socio_seleccionado:
            # El formulario ya asignó el socio y el estado.
            messages.success(self.request, f"Turno asignado y CONFIRMADO para {socio_seleccionado.username}.")
        else:
            # El formulario asignó socio=None y estado=PENDIENTE (o el seleccionado por el Staff).
            messages.success(self.request, "Cupo de turno creado con éxito. Disponible para reserva.")
        
        # Ahora llamamos al super() para guardar.
        return super().form_valid(form)




class StaffTurnoListView(StaffRequiredMixin, ListView):
    """El STAFF ve TODOS los turnos para administración."""
    model = Turno
    template_name = 'turnos/staff_turno_list.html'
    context_object_name = 'todos_los_turnos'
    ordering = ['-fecha_hora_inicio']


class TurnoUpdateView(StaffRequiredMixin, UpdateView):
    """Permite al STAFF/ADMIN editar cualquier turno."""
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/staff_turno_form.html' 
    success_url = reverse_lazy('turnos:staff_list')

    def get_form_kwargs(self):
        """Pasa el usuario actual al formulario."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def get_object(self, queryset=None):
        return get_object_or_404(Turno, pk=self.kwargs['pk'])

    def form_valid(self, form):
        try:
            form.instance.full_clean()
            messages.success(self.request, "Turno actualizado correctamente.")
        except ValidationError as e:
            messages.error(self.request, f"Error al actualizar: {list(e.message_dict.values())[0][0]}")
            return self.form_invalid(form)
            
        return super().form_valid(form)
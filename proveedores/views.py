# proveedores/views.py

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test # Para la vista de función
from .models import Proveedor
from .forms import ProveedorForm

# =================================================================
# MIXIN DE AUTORIZACIÓN
# =================================================================

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Asegura que el usuario esté logueado y sea un superusuario O pertenezca 
    al grupo de Django llamado 'Administrador'.
    """
    def test_func(self):
        # La prueba pasa si el usuario es superusuario O pertenece al grupo 'Administrador'.
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administrador').exists()


# =================================================================
# VISTAS CRUD (Aplicando AdminRequiredMixin)
# =================================================================

# R - Lista de Proveedores (Filtra por estado: activo, inactivo, todos)
class ProveedorListView(AdminRequiredMixin, ListView):
    model = Proveedor
    template_name = 'proveedores/proveedor_list.html'
    context_object_name = 'proveedores'
    
    def get_queryset(self):
        # Obtiene el parámetro 'estado' de la URL (ej: /proveedores/?estado=inactivo)
        estado = self.request.GET.get('estado')
        queryset = Proveedor.objects.all()
        
        if estado == 'inactivo':
            # Muestra solo inactivos
            return queryset.filter(activo=False)
        elif estado == 'todos':
            # Muestra todos
            return queryset
        else:
            # Por defecto, muestra solo activos
            return queryset.filter(activo=True)

# R - Detalle de Proveedor
class ProveedorDetailView(AdminRequiredMixin, DetailView):
    model = Proveedor
    template_name = 'proveedores/proveedor_detail.html'
    context_object_name = 'proveedor'

# C - Crear Proveedor
class ProveedorCreateView(AdminRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/proveedor_form.html'
    success_url = reverse_lazy('proveedores:proveedor_list')

# U - Actualizar Proveedor
class ProveedorUpdateView(AdminRequiredMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/proveedor_form.html'
    success_url = reverse_lazy('proveedores:proveedor_list')


# =================================================================
# VISTA DE FUNCIÓN PARA CAMBIO DE ESTADO (Corregida con Decoradores)
# =================================================================

# Función de ayuda para user_passes_test
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Administrador').exists()

@login_required 
@user_passes_test(is_admin) 
def toggle_proveedor_status(request, pk):
    """Cambia el estado activo/inactivo del proveedor."""
    
    # Se usa get_object_or_404 para manejar si el PK no existe
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    # Cambia el estado (True a False, False a True)
    proveedor.activo = not proveedor.activo
    proveedor.save()
    
    # Redirige a la lista para ver el cambio
    return redirect('proveedores:proveedor_list')
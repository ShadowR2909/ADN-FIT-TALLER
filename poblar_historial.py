"""
Script para poblar el historial con accesorios existentes.
Ejecutar desde Django shell: python manage.py shell
"""

from accesorios.models import Accesorio, HistorialAccesorio
from django.contrib.auth import get_user_model

User = get_user_model()

def poblar_historial_existente():
    """
    Crea entradas de historial para accesorios existentes que no tienen 
    información de auditoría.
    """
    # Obtener un usuario admin para asignar como creador (puedes cambiar esto)
    try:
        admin_user = User.objects.filter(profile__rol='Administrador').first()
        if not admin_user:
            admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            print("No se encontró un usuario administrador para asignar las acciones históricas.")
            return
            
        # Buscar accesorios sin creador
        accesorios_sin_creador = Accesorio.objects.filter(creado_por__isnull=True)
        
        if accesorios_sin_creador.exists():
            print(f"Procesando {accesorios_sin_creador.count()} accesorios existentes...")
            
            for accesorio in accesorios_sin_creador:
                # Actualizar el creador
                accesorio.creado_por = admin_user
                accesorio.save()
                
                # Crear entrada en el historial
                HistorialAccesorio.objects.create(
                    accesorio_nombre=accesorio.nombre,
                    accesorio_id=accesorio.id,
                    accion='CREADO',
                    usuario=admin_user,
                    detalles=f'Accesorio existente migrado al sistema de auditoría. Cantidad: {accesorio.cantidad_total} unidades.'
                )
                
            print(f"✅ Historial creado para {accesorios_sin_creador.count()} accesorios existentes.")
        else:
            print("✅ Todos los accesorios ya tienen información de auditoría.")
            
    except Exception as e:
        print(f"❌ Error al poblar historial: {e}")

# Para ejecutar, usar en Django shell:
# exec(open('poblar_historial.py').read())
# poblar_historial_existente()
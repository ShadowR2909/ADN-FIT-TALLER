from .models import Profile

def perfil_context(request):
    """
    Hace que la variable 'perfil' esté disponible en todos los templates.
    """
    if request.user.is_authenticated:
        try:
            perfil = request.user.profile
        except Profile.DoesNotExist:
            perfil = None
    else:
        perfil = None
    return {'perfil': perfil}

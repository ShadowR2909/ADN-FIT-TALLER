from django.contrib import admin
from .models import Profile
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'rol')
    search_fields = ('user__username', 'user__email', 'telefono', 'rol')
    filter_horizontal = ()
    list_filter = ('rol',)

admin.site.register(Profile, ProfileAdmin)
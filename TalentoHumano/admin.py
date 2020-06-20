from django.contrib import admin

from TalentoHumano.models import PermisosFuncionalidad


class PermisosFuncionalidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'content_type', 'grupo', 'solo_admin', 'estado')
    list_display_links = ('id', 'nombre')
    search_fields = ('id', 'nombre', 'aplicacion')


admin.site.register(PermisosFuncionalidad, PermisosFuncionalidadAdmin)
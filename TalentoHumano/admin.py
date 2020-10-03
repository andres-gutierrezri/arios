from django.contrib import admin

from TalentoHumano.models.colaboradores import TipoNovedad


class TipoNovedadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'activar_usuario', 'desactivar_usuario', 'estado')
    list_display_links = ('id', 'nombre', 'descripcion', 'activar_usuario', 'desactivar_usuario', 'estado')
    search_fields = ('id', 'nombre', 'descripcion', 'activar_usuario', 'desactivar_usuario', 'estado')


admin.site.register(TipoNovedad, TipoNovedadAdmin)

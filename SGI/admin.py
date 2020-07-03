from django.contrib import admin

from SGI.models import GrupoDocumento


class GrupoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'estado', 'empresa', 'es_general')
    list_display_links = ('id', 'nombre')
    search_fields = ('id', 'nombre')


admin.site.register(GrupoDocumento, GrupoDocumentoAdmin)

from django.contrib import admin

from SGI.models.documentos import GruposDocumentosProcesos, GrupoDocumento


class GruposDocumentosProcesosAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo_documento', 'proceso')
    list_display_links = ('id', 'grupo_documento', 'proceso')
    search_fields = ('id', 'grupo_documento', 'proceso')


class GrupoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'estado', 'empresa', 'es_general')
    list_display_links = ('id', 'nombre')
    search_fields = ('id', 'nombre')

admin.site.register(GruposDocumentosProcesos, GruposDocumentosProcesosAdmin)
admin.site.register(GrupoDocumento, GrupoDocumentoAdmin)
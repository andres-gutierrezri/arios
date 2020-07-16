from django.contrib import admin

from SGI.models.documentos import GruposDocumentosProcesos


class GruposDocumentosProcesosAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo_documento', 'proceso')
    list_display_links = ('id', 'grupo_documento', 'proceso')
    search_fields = ('id', 'grupo_documento', 'proceso')


admin.site.register(GruposDocumentosProcesos, GruposDocumentosProcesosAdmin)

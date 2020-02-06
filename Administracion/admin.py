from django.contrib import admin

from Administracion.models import Impuesto, TipoDocumento, ConsecutivoDocumento


class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'porcentaje', 'aplica_item', 'aplica_global', 'estado', 'usuario_crea')
    list_display_links = ('id', 'nombre')
    search_fields = ('id', 'nombre', 'porcentaje')


class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'estado')
    list_display_links = ('id', 'nombre')
    search_fields = ('id', 'nombre', 'estado')


class ConsecutivoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa', 'tipo_documento', 'consecutivo', 'estado')
    list_display_links = ('id', 'empresa', 'tipo_documento')
    search_fields = ('id', 'empresa', 'tipo_documento')


admin.site.register(Impuesto, ImpuestoAdmin)
admin.site.register(TipoDocumento, TipoDocumentoAdmin)
admin.site.register(ConsecutivoDocumento, ConsecutivoDocumentoAdmin)

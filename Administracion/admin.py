from django.contrib import admin

from Administracion.models import Impuesto, TipoDocumento, ConsecutivoDocumento, PermisosFuncionalidad
from Administracion.models.models import Parametro


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


class PermisosFuncionalidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'content_type', 'grupo', 'solo_admin', 'estado')
    list_display_links = ('id', 'nombre')
    search_fields = ('id', 'nombre', 'aplicacion')


class ParametrosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'tipo', 'descripcion', 'valor', 'grupo', 'subgrupo', 'estado')
    list_display_links = ('id', 'nombre', 'tipo', 'descripcion', 'valor', 'grupo', 'subgrupo', 'estado')
    search_fields = ('id', 'nombre', 'descripcion',)


admin.site.register(Impuesto, ImpuestoAdmin)
admin.site.register(TipoDocumento, TipoDocumentoAdmin)
admin.site.register(ConsecutivoDocumento, ConsecutivoDocumentoAdmin)
admin.site.register(PermisosFuncionalidad, PermisosFuncionalidadAdmin)
admin.site.register(Parametro, ParametrosAdmin)

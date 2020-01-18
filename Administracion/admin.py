from django.contrib import admin

from Administracion.models import Impuesto


class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'porcentaje', 'aplica_item', 'aplica_global', 'estado', 'usuario_crea')
    list_display_links = ('id', 'nombre')
    search_fields = ('id', 'nombre', 'porcentaje')


admin.site.register(Impuesto, ImpuestoAdmin)

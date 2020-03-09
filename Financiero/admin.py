from django.contrib import admin

from Financiero.models import ResolucionFacturacion


class ResolucionFacturacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa', 'numero_resolucion', 'fecha_resolucion', 'prefijo', 'numero_desde',
                    'numero_hasta', 'estado', 'usuario_crea')
    list_display_links = ('id', 'numero_resolucion')
    search_fields = ('id', 'numero_resolucion', 'prefijo')


admin.site.register(ResolucionFacturacion, ResolucionFacturacionAdmin)

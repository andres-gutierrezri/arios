from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from EVA.General import obtener_reporte
from EVA.views.index import AbstractEvaLoggedProveedorView


class ReportesView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'SGI/Reportes/index.html', {'menu_actual': 'reportes'})


class ReportesDescargarView(AbstractEvaLoggedProveedorView):
    def get(self, request, id, formato):
        reporte = obtener_reporte(f'ListadoMaestroSGI.{formato}', {})
        if reporte:
            http_response = HttpResponse(reporte, 'application/pdf' if formato == 'pdf' else 'application/vnd.ms-excel')
            http_response['Content-Disposition'] = f'inline; filename="Listado Maestro SGI.{formato}"'
            return http_response
        else:
            messages.error(self.request, 'No se pudo generar el reporte')
            return redirect(reverse('sgi:reportes'))

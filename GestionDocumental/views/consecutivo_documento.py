import datetime

from django.shortcuts import render

from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models import ConsecutivoDocumento


class ConsecutivoDocumentoView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoDocumento.objects.all()
        else:
            consecutivos = ConsecutivoDocumento.objects.filter(usuario_id=request.user.id)

        opciones_filtro = [{'campo_valor': 0, 'campo_texto': 'Todos'},
                           {'campo_valor': 1, 'campo_texto': 'Mis consecutivos'}]

        return render(request, 'GestionDocumental/ConsecutivoDocumento/index.html', {'consecutivos': consecutivos,
                                                                                     'opciones_filtro': opciones_filtro,
                                                                                     'fecha': datetime.datetime.now(),
                                                                                     'menu_actual': 'contratos',
                                                                                     'id_filtro': id})


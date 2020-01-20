from django.shortcuts import render
from datetime import datetime

from Administracion.models import Proceso
from EVA.views.index import AbstractEvaLoggedView
from SGI.models import Documento, GrupoDocumento


class IndexView(AbstractEvaLoggedView):
    def get(self, request, id):
        documentos = Documento.objects.filter(grupo_documento_id=id)
        procesos = Proceso.objects.all()
        proceso = Proceso.objects.get(id=id)
        grupo_documentos = GrupoDocumento.objects.all()
        return render(request, 'SGI/documentos/index.html', {'documentos': documentos, 'procesos': procesos,
                                                             'grupo_documentos': grupo_documentos, 'proceso': proceso})


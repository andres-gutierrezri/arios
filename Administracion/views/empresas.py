from sqlite3 import IntegrityError

from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from datetime import datetime
from django.shortcuts import render, redirect

from Administracion.models import Empresa


class EmpresaView(AbstractEvaLoggedView):
    def get(self, request):
        empresas = Empresa.objects.filter(subempresa=False)
        fecha = datetime.now()
        return render(request, 'Administracion/Empresas/index.html', {'empresas': empresas, 'fecha': fecha})


class EmpresaCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'Administracion/Empresas/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        empresa = Empresa.from_dictionary(request.POST)
        empresa.estado = True
        empresa.logo = request.FILES.get('logo', None)
        if not empresa.logo:
            empresa.logo = 'logos-empresas/empresa-default.jpg'
        try:
            empresa.full_clean(exclude=['estado', 'subempresa', 'empresa_ppal'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, empresa)
            datos['errores'] = errores.message_dict
            if 'nit' in errores.message_dict:
                for mensaje in errores.message_dict['nit']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request, 'Ya existe una empresa con nit {0}'.format(empresa.nit))
                        datos['errores'] = ''
                        break
            return render(request, 'Administracion/Empresas/crear-editar.html', datos)

        empresa.save()
        messages.success(request, 'Se ha agregado la empresa {0}'.format(empresa.nombre))
        return redirect(reverse('Administracion:empresas'))


class EmpresaEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        empresa = Empresa.objects.get(id=id)

        return render(request, 'Administracion/Empresas/crear-editar.html', datos_xa_render(self.OPCION, empresa))

    def post(self, request, id):
        update_fields = ['nombre', 'nit', 'estado']

        empresa = Empresa.from_dictionary(request.POST)
        empresa.id = int(id)
        empresa.logo = request.FILES.get('logo', None)
        if empresa.logo:
            update_fields.append('logo')
        try:
            empresa.full_clean(validate_unique=False, exclude=['logo', 'subempresa', 'empresa_ppal'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, empresa)
            datos['errores'] = errores.message_dict
            return render(request, 'Administracion/Empresas/crear-editar.html', datos)

        if Empresa.objects.filter(nit=empresa.nit).exclude(id=id).exists():
            messages.warning(request, 'Ya existe una empresa con NIT {0}'.format(empresa.nit))
            return render(request, 'Administracion/Empresas/crear-editar.html', datos_xa_render(self.OPCION, empresa))

        empresa_db = Empresa.objects.get(id=id)
        if empresa_db.comparar(empresa, excluir=['logo', 'empresa_ppal', 'subempresa']) and not empresa.logo:
            messages.success(request, 'No se hicieron cambios en la empresa {0}'.format(empresa.nombre))
            return redirect(reverse('Administracion:empresas'))

        else:
            empresa.save(update_fields=update_fields)
            messages.success(request, 'Se ha actualizado la empresa {0}'.format(empresa.nombre))
            return redirect(reverse('Administracion:empresas'))


class EmpresaEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            empresa = Empresa.objects.get(id=id)
            empresa.delete()
            messages.success(request, 'Se ha eliminado la empresa {0}'.format(empresa.nombre))
            return JsonResponse({"Mensaje": "OK"})

        except:
            empresa = Empresa.objects.get(id=id)
            messages.warning(request, 'No se puede eliminar la empresa {0}'.format(empresa.nombre) +
                             ' porque ya se encuentra asociado a otros módulos')
            return JsonResponse({"Mensaje": "No se puede eliminar"})


class SubempresasView(AbstractEvaLoggedView):
    def get(self, request):
        subempresas = Empresa.objects.filter(subempresa=True, empresa_ppal_id=get_id_empresa_global(request))
        return render(request, 'Administracion/Subempresas/index.html', {'subempresas': subempresas,
                                                                         'fecha': datetime.now()})


class SubempresaCrearView(AbstractEvaLoggedView):
    def get(self, request):
        OPCION = 'crear'
        return render(request, 'Administracion/Subempresas/crear-editar.html', datos_xa_render(OPCION))

    def post(self, request):

        nombre = request.POST.get('nombre', '')
        nit = request.POST.get('nit', '')
        logo = request.FILES.get('logo', None)
        empresa_ppal_id = get_id_empresa_global(request)

        if Empresa.objects.filter(nit=nit):
            messages.warning(request, 'No se puede eliminar la empresa {0}'.format(empresa.nombre) +
                             ' porque ya se encuentra asociado a otros módulos')
            error = 'Ya existe una empresa con ese número de NIT'
            return render(request, 'Inventario/Subempresas/crear-editar.html', {'error': error})

        subempresa = Empresa(nombre=nombre, nit=nit, logo=logo, estado=True,
                             subempresa=True, empresa_ppal_id=empresa_ppal_id)
        subempresa.save()

        return redirect(reverse('inventario:subempresas'))


def datos_xa_render(opcion: str, empresa: Empresa = None) -> dict:
    """
    Datos necesarios para la creación de los html de Empresas.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param empresa: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """

    datos = {'empresa': empresa, 'opcion': opcion}

    return datos

from django.db import models
from django.contrib.auth.models import User
from django.db.models import QuerySet

from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral


class Empresa(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    nit = models.TextField(max_length=20, verbose_name='NIT', null=False, blank=False, unique=True)
    logo = models.ImageField(upload_to='logos-empresas', verbose_name='Logo', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    subempresa = models.BooleanField(verbose_name='Subempresa', null=False, blank=False)
    empresa_ppal = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name='Empresa Ppal', null=True
                                     , blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def empresa_to_json(self):
        return {
            "nombre": self.nombre,
            "nit": self.nit,
            "logo": self.logo.url,
            "id": self.id,
            "subempresa": self.subempresa,
            "empresa_ppal_id": 0 if self.empresa_ppal is None
            else self.empresa_ppal.id
        }

    @staticmethod
    def get_default():
        return Empresa(nombre='Empresa Default',
                       nit='',
                       logo='',
                       estado=False,
                       subempresa=False,
                       empresa_ppal=None,
                       id=0)

    @staticmethod
    def from_dictionary(datos: dict) -> 'Empresa':
        """
        Crea una instancia de Empresas con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear Empresas.
        :return: Instacia de entidad empresas con la información especificada en el diccionario.
        """
        empresa = Empresa()
        empresa.nombre = datos.get('nombre', '')
        empresa.nit = datos.get('nit', '')
        empresa.logo = datos.get('logo', '')
        empresa.estado = datos.get('estado', '') == 'True'
        empresa.subempresa = datos.get('subempresa', 'False') == 'True'
        empresa.empresa_ppal_id = datos.get('empresa_ppal_id', '')

        return empresa


class Cargo(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa',
                                null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'


class Proceso(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    objeto = models.CharField(max_length=100, verbose_name='Objeto', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'


class Rango(models.Model):
    objects = ManagerGeneral()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa',
                                null=True, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Rango'
        verbose_name_plural = 'Rangos'


class TipoIdentificacion(models.Model):
    objects = ManagerGeneral()
    
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    sigla = models.TextField(max_length=5, verbose_name='Sigla', null=False, blank=False, unique=True)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Identificación'
        verbose_name_plural = 'Tipos de Identificaciones'


class TipoContratoManager(ManagerGeneral):
    def tipos_laborares(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(laboral=True)

    def tipos_comerciales(self, estado: bool = None, xa_select: bool = False) -> QuerySet:
        return self.get_x_estado(estado, xa_select).filter(laboral=False)


class TipoContrato(models.Model):
    objects = TipoContratoManager()
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)
    laboral = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Contrato'
        verbose_name_plural = 'Tipos de Contratos'


class Persona(models.Model):

    identificacion = models.CharField(max_length=20, verbose_name='Identificación', null=False, blank=False,
                                      unique=True)
    fecha_expedicion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Expedición', null=False,
                                            blank=False)
    fecha_nacimiento = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Nacimiento', null=True,
                                            blank=False)
    telefono = models.CharField(max_length=20, verbose_name='Teléfono', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                          blank=False)
    fecha_modificacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)
    genero = models.CharField(max_length=1, verbose_name='Género', null=False, blank=False)
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING,
                                            verbose_name='Tipo de identificación', null=True, blank=False)
    usuario = models.OneToOneField(User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=True,
                                   blank=False, related_name='%(app_label)s_%(class)s_usuario')
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=True,
                                     blank=True, related_name='%(app_label)s_%(class)s_usuario_crea')
    usuario_actualiza = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Actualiza",
                                          null=True, blank=True,
                                          related_name='%(app_label)s_%(class)s_usuario_actualiza')

    def __str__(self):
        return '{0} - {1}'.format(self.identificacion, self.nombre_completo)

    class Meta:
        abstract = True

    @property
    def nombres(self):
        return self.usuario.first_name if self.usuario else 'Sin nombres'

    @property
    def apellidos(self):
        return self.usuario.last_name if self.usuario else 'Sin apellidos'

    @property
    def nombre_completo(self):
        return '{0} {1}'.format(self.usuario.first_name, self.usuario.last_name) if self.usuario else 'Sin nombre'




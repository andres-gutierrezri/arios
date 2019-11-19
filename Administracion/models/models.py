from django.db import models
from django.contrib.auth.models import User

# # Create your models here.
from django.db.models import QuerySet

from EVA.General.modelmanagers import ManagerGeneral


class Empresa(models.Model):
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
    objects = ManagerGeneral()
    identificacion = models.CharField(max_length=20, verbose_name='Identificación', null=False, blank=False,
                                      unique=True)
    fecha_expedicion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Expedición', null=False,
                                            blank=False)
    fecha_nacimiento = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Nacimiento', null=True,
                                            blank=False)
    telefono = models.TextField(max_length=15, verbose_name='Teléfono', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                          blank=False)
    fecha_modificacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)
    genero = models.TextField(max_length=1, verbose_name='Género', null=False, blank=False)
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING,
                                            verbose_name='Tipo de identificación', null=True, blank=False)
    usuario = models.OneToOneField(User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=True,
                                   blank=False, related_name='%(app_label)s_%(class)s_usuario')
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='%(app_label)s_%(class)s_usuario_crea')
    usuario_actualiza = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Actualiza",
                                          null=False, blank=False,
                                          related_name='%(app_label)s_%(class)s_usuario_actualiza')

    def __str__(self):
        return '{0} {1} {2}'.format(self.usuario.first_name, self.usuario.last_name, self.identificacion)

    class Meta:
        abstract = True



from django.db import models
from django.contrib.auth.models import User

# # Create your models here.


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


class Proceso(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    objeto = models.CharField(max_length=100, verbose_name='Objeto', null=False, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa', null=True
                                     , blank=False)

    def __str__(self):
        return self.nombre


class TipoIdentificacion(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    sigla = models.TextField(max_length=5, verbose_name='Sigla', null=False, blank=False, unique=True)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre


class TipoContrato(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Contrato'
        verbose_name_plural = 'Tipos Contratos'


class Persona(models.Model):
    identificacion = models.CharField(max_length=20, verbose_name='Identificación', null=False, blank=False,
                                      unique=True)
    fecha_expedicion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Expedición', null=False,
                                          blank=False)
    fecha_nacimiento = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Nacimiento', null=False,
                                          blank=False)
    telefono = models.TextField(max_length=300, verbose_name='Teléfono', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                            blank=False)
    fecha_modificacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Modificación', null=False,
                                            blank=False)
    genero = models.TextField(max_length=300, verbose_name='Género', null=False, blank=False)
    tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.DO_NOTHING,
                                            verbose_name='Tipo de identificación', null=True, blank=False)
    usuario = models.OneToOneField(User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=True,
                                blank=False, related_name='UserAccess')
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='UserCrea')
    usuario_actualiza = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Actualiza", null=False,
                                         blank=False, related_name='UserModifica')

    def __str__(self):
        return self

    class Meta:
        abstract = True



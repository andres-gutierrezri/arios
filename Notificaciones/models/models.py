# coding=utf-8

from django.contrib.auth.models import User
from django.db import models


class TipoNotificacion(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                          blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Notificación'
        verbose_name_plural = 'Tipos de Notificaciones'

    # region Constantes Tipos de Notificación
    EVENTO_DEL_SISTEMA = 1
    OBLIGATORIA = 2
    INFORMATIVA = 3
    # endregion


class EventoDesencadenador(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', null=False, blank=False)
    descripcion = models.TextField(max_length=300, verbose_name='Descripción', null=False, blank=False)
    ruta = models.TextField(max_length=300, verbose_name='Ruta', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                          blank=False)
    modal = models.BooleanField(verbose_name='Modal', null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Evento Desencadenador'
        verbose_name_plural = 'Eventos Desencadenadores'

    # region Constantes Estados
    BIENVENIDA = 1
    CONTRATO = 2
    TERCERO = 3
    EMPRESAS = 4
    ENTIDADES_CAFE = 5
    COLABORADOR = 6
    SUBEMPRESA = 7
    NOTIFICACION_CA = 8
    SOLICITUD_APROBACION = 9
    # endregion


class Notificacion(models.Model):
    titulo = models.CharField(max_length=100, verbose_name='Título', null=False, blank=False)
    mensaje = models.TextField(max_length=300, verbose_name='Mensaje', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                          blank=False, )
    tipo_notificacion = models.ForeignKey(TipoNotificacion, on_delete=models.DO_NOTHING,
                                          verbose_name='Tipo Notificación', null=True, blank=False)
    evento_desencadenador = models.ForeignKey(EventoDesencadenador, on_delete=models.DO_NOTHING,
                                              verbose_name='Evento Desencadenador', null=True, blank=False)
    id_evento = models.IntegerField(verbose_name='Id Evento', null=True, blank=False)
    imagen = models.ImageField(upload_to='imagenes-notificaciones', verbose_name='Logo', null=True, blank=False)
    url = models.CharField(max_length=100, verbose_name='Url', null=True, blank=False)
    id_usuario = models.CharField(max_length=100, verbose_name='Id Usuario', null=True, blank=False)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'


class DestinatarioNotificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=False, blank=False)
    visto = models.BooleanField(verbose_name='Visto', null=False, blank=False)
    notificacion = models.ForeignKey(Notificacion, on_delete=models.DO_NOTHING,
                                     verbose_name='Tipo Notificación', null=True, blank=False)
    envio_email_exitoso = models.BooleanField(verbose_name='Envío Email Exitoso', null=False, blank=False)

    def __str__(self):
        return self.usuario.first_name

    class Meta:
        verbose_name = 'Destinatario Notificación'
        verbose_name_plural = 'Destinatarios de Notificaciones'


class SeleccionDeNotificacionARecibir(models.Model):
    evento_desencadenador = models.ForeignKey(EventoDesencadenador, on_delete=models.DO_NOTHING,
                                              verbose_name='Evento Desencadenador', null=True, blank=False)
    envio_x_email = models.BooleanField(verbose_name='Envío por Email', null=False, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=False, blank=False)
    estado = models.BooleanField(verbose_name='Estado', null=False, blank=False)

    def __str__(self):
        return '{0} (Selección: {1})'.format(self.evento_desencadenador.nombre, self.usuario)

    class Meta:
        verbose_name = 'Selección de Notificación a Recibir'
        verbose_name_plural = 'Selecciones de Notificaciones a Recibir'


class TextoNotificacionDelSistema(models.Model):
    titulo = models.CharField(max_length=100, verbose_name='Título', null=False, blank=False)
    mensaje = models.TextField(max_length=300, verbose_name='Mensaje', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False,
                                          blank=False)
    fecha_modificacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Modificación', null=False,
                                              blank=False)
    evento_desencadenador = models.ForeignKey(EventoDesencadenador, on_delete=models.DO_NOTHING,
                                              verbose_name='Evento Desencadenador', null=True, blank=False)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Texto de Notificación del Sistema'
        verbose_name_plural = 'Textos de Notificaciones del Sistema'


class TokenRutaCorreo(models.Model):
    token = models.CharField(max_length=100, verbose_name='Token', null=False, blank=False)
    ruta = models.CharField(max_length=100, verbose_name='Ruta', null=False, blank=False)
    activo = models.BooleanField(verbose_name='Activo', null=False, blank=False, default=True)
    destinatario = models.ForeignKey(DestinatarioNotificacion, on_delete=models.DO_NOTHING,
                                     verbose_name="Destinatario", null=False, blank=False)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = 'Token Ruta Correo'
        verbose_name_plural = 'Tokens Rutas Correos'

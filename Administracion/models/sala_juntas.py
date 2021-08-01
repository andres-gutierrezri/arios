from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from Administracion.parametros import ParametrosAdministracion
from EVA.General.conversiones import string_to_datetime, SEGUNDOS_EN_MIN
from EVA.General.modeljson import ModelDjangoExtensiones
from EVA.General.modelmanagers import ManagerGeneral


class ReservaSalaJuntas(models.Model, ModelDjangoExtensiones):
    objects = ManagerGeneral()
    responsable = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Responsable",
                                    null=False, blank=False, related_name='ReservaSalaJuntasResponsable')
    usuario_crea = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Crea", null=False,
                                     blank=False, related_name='ReservaSalaJuntasCrea')
    usuario_modifica = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario Modifica", null=True,
                                         blank=False, related_name='ReservaSalaJuntasModifica')
    fecha_inicio = models.DateTimeField(verbose_name='Fecha de Inicio', null=False, blank=False)
    fecha_fin = models.DateTimeField(verbose_name='Fecha Fin', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación', null=False, blank=False)
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación', null=True,
                                              blank=False)
    tema = models.CharField(max_length=100, verbose_name='Tema', null=False, blank=False)
    descripcion = models.CharField(max_length=300, verbose_name='Descripción', null=True, blank=True)
    motivo = models.TextField(max_length=100, verbose_name='Motivo', blank=False, null=False)
    estado = models.BooleanField(verbose_name='Estado', blank=False, null=False, default=True)
    color = models.CharField(max_length=7, verbose_name='Color', null=False, blank=False, default='#20B8A9')
    finalizacion = models.BooleanField(verbose_name='Finalización', blank=False, null=False, default=False)
    notificacion = models.BooleanField(verbose_name='Notificación', blank=False, null=False, default=False)

    def __str__(self):
        return self.responsable

    class Meta:
        verbose_name = 'Reserva Sala de Juntas'
        verbose_name_plural = 'Reservas Sala de Juntas'

    @staticmethod
    def from_dictionary(datos: dict) -> 'ReservaSalaJuntas':
        """
        Crea una instancia de ReservaSalaJuntas con los datos pasados en el diccionario.
        :param datos: Diccionario con los datos para crear la Reserva de la Sala de Juntas.
        :return: Instacia de Reserva de la Sala de Juntas con la información especificada en el diccionario.
        """
        reserva = ReservaSalaJuntas()
        reserva.responsable_id = datos.get('responsable', None)
        reserva.fecha_inicio = string_to_datetime(datos.get('fecha_intervalo', '').split(' – ')[0], "%Y-%m-%d %H:%M")
        reserva.fecha_fin = string_to_datetime(datos.get('fecha_intervalo', '').split(' – ')[1], "%Y-%m-%d %H:%M")
        reserva.tema = datos.get('tema', '')
        reserva.descripcion = datos.get('descripcion', '')
        reserva.motivo = datos.get('motivo', '')

        return reserva

    def validar_reserva(self, editando: bool = False) -> str:
        """
        Valida que al momento de crear o editar una reserva NO se encuentre traslapada con otra ya existente.
        :param editando: True para indicar que es una instancia que se esta editando y en la comparación no se tenga en
        cuenta a si misma.
        :return: String vacío si pasa la validación de lo contrario un String con el mensaje de error correspondiente.
        """

        traslapos = ReservaSalaJuntas.objects \
            .filter(Q(fecha_inicio__lte=self.fecha_inicio, fecha_fin__gte=self.fecha_inicio)
                    | Q(fecha_inicio__lte=self.fecha_fin, fecha_fin__gte=self.fecha_fin)
                    | Q(fecha_inicio__gt=self.fecha_inicio, fecha_fin__lt=self.fecha_fin)) \
            .exclude(estado=False).values_list('tema', flat=True)

        if editando:
            traslapos = traslapos.exclude(id=self.id)

        if traslapos.exists():
            return 'Ya existe una reunión asignada en este horario'

        return ''

    def validar_holgura(self, editando: bool = False) -> str:
        """
        Valida que la reserva cumpla con el parámetro de holgura, es decir, que la fecha inicial sea mayor por
        los minutos indicados por el PARAMETRO_HOLGURA con respecto a la reunión anterior y que la fecha final sea menor
        por los minutos indicados por el parámetro de PARAMETRO_HOLGURA con respecto a la reunión siguiente.
        :param editando: True para indicar que es una instancia que se esta editando y en la comparación no se tenga en
        cuenta a si misma.
        :return: String vacío si pasa la validación de lo contrario un String con el mensaje de error correspondiente.
        """

        # Parámetro de holgura
        param_holgura_min = ParametrosAdministracion.get_params_sala_juntas().get_holgura()
        param_holgura_seg = param_holgura_min * SEGUNDOS_EN_MIN

        past_dates = ReservaSalaJuntas.objects.filter(fecha_fin__date=self.fecha_inicio.astimezone().date()) \
            .filter(fecha_fin__lt=self.fecha_inicio).exclude(finalizacion=True).exclude(estado=False) \
            .values_list('fecha_fin', flat=True)

        if editando:
            past_dates = past_dates.exclude(id=self.id)

        for date in past_dates:
            holgura = (self.fecha_inicio - date).seconds
            if holgura < param_holgura_seg:
                reserva_actual = self.fecha_inicio.astimezone()
                reserva_anterior = date.astimezone()
                reserva_holgura = (reserva_actual - reserva_anterior).seconds // SEGUNDOS_EN_MIN
                tiempo = 'minuto' if reserva_holgura == 1 else 'minutos'

                return f'Debe haber un espacio mínimo de {param_holgura_min} minutos ' \
                       f'entre el inicio de la de reunión ({reserva_actual.strftime("%H:%M")}) ' \
                       f'y el final de la anterior ({reserva_anterior.strftime("%H:%M")}). ' \
                       f'Hay una diferencia de: {reserva_holgura} {tiempo}'

        later_dates = ReservaSalaJuntas.objects.filter(fecha_inicio__date=self.fecha_fin.astimezone().date()) \
            .filter(fecha_inicio__gt=self.fecha_fin).exclude(estado=False).values_list('fecha_inicio', flat=True)

        if editando:
            later_dates = later_dates.exclude(id=self.id)

        for date in later_dates:
            holgura = (date - self.fecha_fin).seconds
            if holgura < param_holgura_seg:
                reserva_actual = self.fecha_fin.astimezone()
                reserva_posterior = date.astimezone()
                reserva_holgura = (reserva_posterior - reserva_actual).seconds // SEGUNDOS_EN_MIN
                tiempo = 'minuto' if reserva_holgura == 1 else 'minutos'

                return f'Debe haber un espacio mínimo de {param_holgura_min} minutos ' \
                       f'entre el final de la de reunión ({reserva_actual.strftime("%H:%M")}) ' \
                       f'y el inicio de la siguiente ({reserva_posterior.strftime("%H:%M")}). ' \
                       f'Hay una diferencia de: {reserva_holgura} {tiempo}'

        return ''

from datetime import datetime, date
import pytz
from django.utils.timesince import timesince


def app_date_now() -> date:
    """
    Obtiene la fecha actual basada en UTC.
    :return: la fecha actual para el timezone UTC.
    """
    return app_datetime_now().date()


def app_datetime_now() -> datetime:
    """
    Obtiene la fecha y hora actual con el timezone UTC.
    :return: la fecha y hora actual UTC.
    """
    return datetime.now(pytz.utc)


def validar_formato_imagen(archivo) -> bool:
    extension = str(archivo).split('.')[-1].lower()
    if extension == 'jpg' or extension == 'jpeg' or extension == 'png':
        return True
    else:
        return False

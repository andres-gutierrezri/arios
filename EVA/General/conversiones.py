# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

import pytz
from django.conf import settings


def string_to_date(fecha_string: str) -> Optional[datetime]:
    """
    Convierte un string a datetime, la fecha se toma con el timezone configurado en settings.TIME_ZONE
    :param fecha_string: string con formato "%Y-%m-%d"
    :return: retorna el datetime en UTC, si falla la conversión retorna None.
    """
    try:
        return datetime.strptime(fecha_string, "%Y-%m-%d").astimezone(pytz.timezone(settings.TIME_ZONE))\
            .astimezone(pytz.timezone('UTC'))
    except ValueError:
        return None

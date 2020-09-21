# -*- coding: utf-8 -*-
import calendar
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional

import pytz
from django.conf import settings
from django.utils.timesince import timesince
from django.utils.translation import ngettext_lazy

from EVA.General import app_datetime_now


def string_to_datetime(fecha_string: str) -> Optional[datetime]:
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


def string_to_date(fecha_string: str) -> Optional[date]:
    """
    Convierte un string a date
    :param fecha_string: string con formato "%Y-%m-%d"
    :return: retorna el solo la fecha en formato date
    """
    try:
        return string_to_datetime(fecha_string).date()
    except ValueError:
        return None


def add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


def add_months(d, meses):
    mes_nuevo = (meses + d.month) % 12
    anio_nuevo = d.year + (meses + d.month) // 12
    if mes_nuevo == 0:
        mes_nuevo = 12
        anio_nuevo -= 1
    dias_mes_nuevo = calendar.monthrange(anio_nuevo, mes_nuevo)[1]
    dias_nuevo = d.day if dias_mes_nuevo > d.day else dias_mes_nuevo
    return d.replace(year=anio_nuevo, month=mes_nuevo, day=dias_nuevo)


def numero_con_separadores(numero):
    return '{:,}'.format(numero).replace(",", "X").replace(".", ",").replace("X", ".")


def unidades_a_letras(unidad: str, decena_uno: bool) -> str:
    unidades = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
    decenas = ['', 'ONCE', 'DOCE', 'TRECE', 'CATORCE', 'QUINCE', 'DIECISÉIS', 'DIECISIETE', 'DIECIOCHO', 'DIECINUEVE']

    try:
        valor = int(unidad)
        return decenas[valor] if decena_uno else unidades[valor]
    except ValueError or IndexError:
        return ''


def decenas_a_letras(decena: str, exacta: bool) -> str:
    decenas = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']

    try:
        valor = int(decena)
        if valor == 1:
            return decenas[valor] if exacta else ''
        if valor == 2:
            return decenas[valor] if exacta else 'VEINTI'

        return '{0}{1}'.format(decenas[valor], '' if exacta or valor == 0 else ' Y ')

    except ValueError or IndexError:
        return ''


def centenas_a_letras(centena: str, exacta: bool) -> str:
    centenas = ['', 'CIEN', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS',
                'OCHOCIENTOS', 'NOVECIENTOS']
    try:
        valor = int(centena)
        if valor == 1 and not exacta:
            return 'CIENTO'

        return centenas[valor]

    except ValueError or IndexError:
        return ''


def cifra_a_letras(cifra: int) -> str:
    numero = '{:03d}'.format(cifra)
    centenas = centenas_a_letras(numero[0], numero[1] == '0' and numero[2] == '0')
    decenas = decenas_a_letras(numero[1], numero[2] == '0')
    unidades = unidades_a_letras(numero[2], numero[1] == '1')

    cifra_letras = centenas + ('' if numero[0] == '0' or (numero[1] == '0' and numero[2] == '0') else ' ')\
                   + decenas + unidades

    if cifra_letras == 'VEINTIUN':
        return 'VEINTIÚN'
    if cifra_letras == 'VEINTIDOS':
        return 'VEINTIDÓS'

    if cifra_letras == 'VEINTITRES':
        return 'VEINTITRÉS'

    if cifra_letras == 'VEINTISEIS':
        return 'VEINTISÉIS'

    return cifra_letras


def numero_a_letras(numero: int) -> str:
    numero_letras = ''
    if numero > 0:
        mil_millones = numero // 1000000000
        numero %= 1000000000
        millones = numero // 1000000
        numero %= 1000000
        miles = numero // 1000
        cientos = numero % 1000

        mil_millones_letras = cifra_a_letras(mil_millones)
        millones_letras = cifra_a_letras(millones)
        miles_letras = cifra_a_letras(miles)
        cientos_letras = cifra_a_letras(cientos)

        if mil_millones > 0:
            numero_letras = 'MIL' if mil_millones_letras == 'UN' else mil_millones_letras + ' MIL'

        if millones > 0:
            numero_letras += (' ' if mil_millones > 0 else '') + millones_letras
            numero_letras += ' MILLÓN' if millones == 1 and mil_millones == 0 else ' MILLONES'
        elif mil_millones > 0:
            numero_letras += ' MILLONES'

        if miles > 0:
            numero_letras += ' ' if (mil_millones > 0 or millones > 0) else ''
            numero_letras += 'MIL' if miles_letras == 'UN' else miles_letras + ' MIL'

        if cientos > 0:
            numero_letras += ' ' if (mil_millones > 0 or millones > 0 or miles > 0) else ''
            numero_letras += cientos_letras
    else:
        numero_letras = 'CERO'

    return numero_letras


def valor_pesos_a_letras(valor) -> str:
    parte_entera: int
    parte_decimal: int = 0
    if isinstance(valor, Decimal) or isinstance(valor, float):
        parte_entera = int(valor)
        parte_decimal = int((valor * 100) % 100)
    elif isinstance(valor, int):
        parte_entera = valor
    else:
        return 'Valor Invalido'

    if parte_decimal <= 0:
        return '{0} PESOS M/CTE'.format(numero_a_letras(parte_entera))
    else:
        return '{0} PESOS CON {1} CENTAVOS M/CTE'.format(numero_a_letras(parte_entera), numero_a_letras(parte_decimal))


TIME_STRINGS = {
    'year': ngettext_lazy('%d año', '%d años'),
    'month': ngettext_lazy('%d mes', '%d meses'),
    'week': ngettext_lazy('%d semana', '%d semanas'),
    'day': ngettext_lazy('%d día', '%d días'),
    'hour': ngettext_lazy('%d hora', '%d horas'),
    'minute': ngettext_lazy('%d minuto', '%d minutos'),
}


def tiempo_transcurrido(fecha) -> str:
    """
    Utiliza django.utils.timesince.timesince() para la conversión y se calcula con
    respecto a la fecha y hora actual.
    :param fecha: Fecha para la cual se quiere calcular el tiempo transcurrido.
    :return: Retorna un texto con el tiempo transcurrido en español.
    """
    return timesince(fecha, app_datetime_now(), False, TIME_STRINGS)

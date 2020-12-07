from datetime import datetime, date
import pytz
from django.core.paginator import Paginator, Page
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


def validar_extension_de_archivo(archivo):
    nombre = archivo.split(".")[-1]
    if nombre == 'pdf' or nombre == 'xlsx' or nombre == 'docx' or nombre == 'pptx':
        return True
    else:
        return False


def validar_formato_imagen(archivo) -> bool:
    extension = str(archivo).split('.')[-1].lower()
    if extension == 'jpg' or extension == 'jpeg' or extension == 'png':
        return True
    else:
        return False


def paginar(datos_paginar, pagina_actual, cant_x_pagina) -> Page:
    pagina_actual = int(pagina_actual)

    paginator = Paginator(datos_paginar, cant_x_pagina)
    if pagina_actual not in paginator.page_range:
        pagina_actual = 1
    datos_page = paginator.get_page(pagina_actual)
    datos_page.num_paginacion = obtener_num_paginacion(paginator, pagina_actual)
    return datos_page


def obtener_num_paginacion(paginator, pagina):
    cantidad = paginator.num_pages
    paginas = []

    # Si la paginación tiene 7 páginas o menos, se mostrarán todas.
    if paginator.num_pages <= 7:
        paginas = range(1, cantidad + 1)

    elif pagina <= 4:
        # Si la página actual <= 4, se muestra 1 2 3 4 5 ... número de la última.
        paginas += range(1, 6)
        paginas.append('...')
        paginas.append(cantidad)

    elif 4 < pagina <= cantidad - 4:
        # Si la página actual > 4 y <= cantidad -4, se muestra 1 ... pagina-1 pagina pagina+1 ... número de la última.
        paginas.append(1)
        paginas.append('...')
        paginas += range(pagina - 1, pagina + 2)
        paginas.append('...')
        paginas.append(cantidad)

    else:
        # Si la página actual esta entre las 4 ultimas, se muestra 1 ... y las 5 últimas.
        paginas.append(1)
        paginas.append('...')
        paginas += range(cantidad - 4, cantidad + 1)

    return paginas

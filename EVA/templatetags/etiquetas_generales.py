# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from django.db import models
register = template.Library()


@register.inclusion_tag('EVA/_general_tags/_select_tag.html')
def select_tag(lista, nombre, texto_seleccion, is_tupla=False, agrupar=False, **kwargs):

    texto_label = kwargs.pop('texto_label', None)
    mensaje_validacion = kwargs.pop('mensaje_validacion', None)
    valor = kwargs.pop('value', None)
    primer_valor = kwargs.pop('primer_valor', None)
    primer_campo_valor = kwargs.pop('primer_campo_valor', None)
    modal = kwargs.pop('modal', False)
    id_label = kwargs.pop('id_label', None)
    disabled = kwargs.pop('disabled', False)

    return {'lista': lista, 'nombre': nombre, 'texto_seleccion': texto_seleccion, 'texto_label': texto_label,
            'propiedades': propiedades_to_str(kwargs), 'mensaje_validacion': mensaje_validacion, 'valor': valor,
            'primer_valor': primer_valor, 'primer_campo_valor': primer_campo_valor, 'modal': modal, 'id_label': id_label,
            'is_tupla': is_tupla, 'agrupar': agrupar, 'disabled':disabled}


@register.inclusion_tag('EVA/_general_tags/_select_multiple_tag.html')
def select_multiple_tag(lista, nombre, id,  texto_seleccion, is_tupla=False, **kwargs):

    texto_label = kwargs.pop('texto_label', None)
    mensaje_validacion = kwargs.pop('mensaje_validacion', None)
    valor = kwargs.pop('value', None)
    primer_valor = kwargs.pop('primer_valor', None)
    modal = kwargs.pop('modal', False)
    id_label = kwargs.pop('id_label', None)
    return {'lista': lista, 'nombre': nombre, 'texto_seleccion': texto_seleccion, 'texto_label': texto_label,
            'propiedades': propiedades_to_str(kwargs), 'mensaje_validacion': mensaje_validacion, 'valor': valor,
            'primer_valor': primer_valor, 'id': id, 'modal': modal, 'id_label': id_label, 'is_tupla': is_tupla}


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_text_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'text'

    if 'data_inputmask' in kwargs:
        kwargs['data-inputmask'] = kwargs.pop('data_inputmask', '')

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_textarea_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'textarea'

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_date_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'date'

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_number_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'number'

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_currency_tag(nombre, texto_label, **kwargs):
    return input_with_format_tag('evaCurrency', nombre, texto_label, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_number_format_tag(nombre, texto_label, **kwargs):
    return input_with_format_tag('evaNumeric', nombre, texto_label, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_with_format_tag(alias, nombre, texto_label, **kwargs):
    prop_decimales = ''
    if not kwargs.pop('decimales', True):
        prop_decimales = ", 'digitsOptional': true, 'digits': 0"

    remove_mask_onsubmit = ''
    if kwargs.pop('removeMaskOnSubmit', False):
        remove_mask_onsubmit = ", 'removeMaskOnSubmit': true"

    kwargs['data-inputmask'] = f"'alias': '{alias}'{prop_decimales}{remove_mask_onsubmit}"
    kwargs['class'] = 'form-control inputmask'
    if 'mensaje_validacion' not in kwargs:
        kwargs['mensaje_validacion'] = 'Debe ser mayor a 0'

    return input_text_tag(nombre, texto_label, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_email_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'email'

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_file_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'file'

    if 'class' not in kwargs:
        kwargs['class'] = 'custom-file-input'

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_checkbox_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'checkbox'

    if 'class' not in kwargs:
        kwargs['class'] = 'custom-control-input form-control'

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_select_radio_tag(nombre, texto_label, opciones, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'radio'
    kwargs['opciones'] = opciones

    if 'class' not in kwargs:
        kwargs['class'] = 'custom-control-input form-control'

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_hidden_tag(nombre, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)
    kwargs['type'] = u'hidden'
    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_time_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'time'

    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_general_tag(nombre, **kwargs):
    return arma_input_general_tag(nombre, **kwargs)


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def model_autoinput_tag(modelo, nombre_campo, incluir_label, **kwargs):
    tipo = u'text'
    campo = modelo._meta.get_field(nombre_campo)
    valor = kwargs.pop('value', '')
    if 'required' not in kwargs and not campo.null:
        kwargs['required'] = u''

    if 'max_length' not in kwargs and not campo.max_length:
        kwargs['required'] = unicode(campo.max_length)

    # region Tipo de Input
    if 'type' in kwargs:
        kwargs.pop('type')
    if isinstance(campo, models.TextField):
        tipo = u'textarea'
    elif isinstance(campo, models.DecimalField):
        tipo = u'number'
        if 'min' not in kwargs:
            kwargs['min'] = get_min_decimal_string(campo.decimal_places)
        if 'max' not in kwargs:
            kwargs['max'] = get_max_decimal_string(campo.max_digits, campo.decimal_places)
    elif isinstance(campo, (models.IntegerField, models.PositiveIntegerField, models.PositiveSmallIntegerField,
                            models.BigIntegerField)):
        tipo = u'number'
    elif isinstance(campo, models.BooleanField):
        tipo = u'checkbox'
        if 'class' not in kwargs:
            kwargs['class'] = 'form-check-input'
    elif isinstance(campo, models.EmailField):
        tipo = u'email'

    # endregion

    if 'class' not in kwargs:
        kwargs['class'] = u'form-control'

    if 'nombre' in kwargs:
        nombre = kwargs.pop('nombre')
    else:
        nombre = campo

    if incluir_label:
        if 'texto_label' in kwargs:
            texto_label = kwargs.pop('texto_label')
        else:
            texto_label = campo.verbose_name
    else:
        texto_label = None

    return {'nombre': nombre, 'texto_label': texto_label, 'type': tipo, 'valor': valor,
            'propiedades': propiedades_to_str(kwargs)}


# region Métodos Ayuda
def arma_input_general_tag(nombre, **kwargs):
    valor = kwargs.pop('value', '')
    tipo = kwargs.pop('type', u'text')
    opciones = kwargs.pop('opciones', '')
    label_id = kwargs.pop('label_id', '')
    is_fecha = tipo == 'date'
    if is_fecha:
        tipo = 'text'

    if 'class' not in kwargs:
        kwargs['class'] = 'form-control' if not is_fecha else 'form-control fecha-control'

    invalido = kwargs.pop('invalido', False)
    if invalido:
        kwargs['class'] = 'form-control is-invalid' if not is_fecha else 'form-control fecha-control is-invalid'

    texto_label = kwargs.pop('texto_label', None)
    mensaje_validacion = kwargs.pop('mensaje_validacion', None)

    modal = kwargs.pop('modal', False)

    return {'nombre': nombre, 'texto_label': texto_label, 'tipo': tipo, 'valor': valor,
            'propiedades': propiedades_to_str(kwargs), 'mensaje_validacion': mensaje_validacion, 'is_fecha': is_fecha,
            'modal': modal, 'opciones': opciones, 'label_id': label_id}


def get_min_decimal_string(decimal_places):
    return unicode('0.' + '0' * (decimal_places - 1) + '1')


def get_max_decimal_string(max_digits, decimal_places):
    return unicode('9' * (max_digits - decimal_places) + '.' + '9' * decimal_places)


def propiedades_to_str(propiedades):
    ustr = u''
    for llave in propiedades:
        ustr += u' {0}="{1}"'.format(llave, propiedades[llave])
    return mark_safe(ustr)


def extraer_min_max(**kwargs) -> str:
    max_min = ''
    if 'min' in kwargs:
        max_min += f", 'min':{kwargs.pop('min')}"
    if 'max' in kwargs:
        max_min += f", 'max':{kwargs.pop('max')}"
    return max_min

# endregion

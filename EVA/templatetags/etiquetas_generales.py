# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from django.db import models
register = template.Library()


@register.inclusion_tag('EVA/_general_tags/_select_tag.html')
def select_tag(lista, nombre, texto_seleccion, **kwargs):

    texto_label = kwargs.pop('texto_label', None)
    mensaje_validacion = kwargs.pop('mensaje_validacion', None)
    valor = kwargs.pop('value', None)
    primer_valor = kwargs.pop('primer_valor', None)
    modal = kwargs.pop('modal', False)
    return {'lista': lista, 'nombre': nombre, 'texto_seleccion': texto_seleccion, 'texto_label': texto_label,
            'propiedades': propiedades_to_str(kwargs), 'mensaje_validacion': mensaje_validacion, 'valor': valor,
            'primer_valor': primer_valor, 'modal': modal}


@register.inclusion_tag('EVA/_general_tags/_select_multiple_tag.html')
def select_multiple_tag(lista, nombre, id,  texto_seleccion, **kwargs):

    texto_label = kwargs.pop('texto_label', None)
    mensaje_validacion = kwargs.pop('mensaje_validacion', None)
    valor = kwargs.pop('value', None)
    primer_valor = kwargs.pop('primer_valor', None)
    modal = kwargs.pop('modal', False)
    return {'lista': lista, 'nombre': nombre, 'texto_seleccion': texto_seleccion, 'texto_label': texto_label,
            'propiedades': propiedades_to_str(kwargs), 'mensaje_validacion': mensaje_validacion, 'valor': valor,
            'primer_valor': primer_valor, 'id': id, 'modal': modal}


@register.inclusion_tag('EVA/_general_tags/_input_general_tag.html')
def input_text_tag(nombre, texto_label, **kwargs):

    kwargs.pop('texto_label', None)
    kwargs.pop('type', None)

    kwargs['texto_label'] = texto_label
    kwargs['type'] = u'text'

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
            'modal': modal}


def get_min_decimal_string(decimal_places):
    return unicode('0.' + '0' * (decimal_places - 1) + '1')


def get_max_decimal_string(max_digits, decimal_places):
    return unicode('9' * (max_digits - decimal_places) + '.' + '9' * decimal_places)


def propiedades_to_str(propiedades):
    ustr = u''
    for llave in propiedades:
        ustr += u' {0}="{1}"'.format(llave, propiedades[llave])
    return mark_safe(ustr)
# endregion

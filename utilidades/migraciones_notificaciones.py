# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-08-21 15:32
from __future__ import unicode_literals

import datetime

from django.db import migrations


def agregar_eventos_desencadenadores(apps, schema_editor):

    eventos_desencadenadores = apps.get_model('Notificaciones', 'EventoDesencadenador')

    eventos_desencadenadores.objects.create(id=1, nombre="Bienvenido a Eva",
                                            descripcion="Bienvenido a Eva",
                                            ruta="/",
                                            fecha_creacion=datetime.datetime.today(), estado=True)

    eventos_desencadenadores.objects.create(id=2, nombre="Creación de Contratos",
                                            descripcion="Creación de Contratos",
                                            ruta="/proyectos/contratos",
                                            fecha_creacion=datetime.datetime.today(), estado=True)

    eventos_desencadenadores.objects.create(id=3, nombre="Creación de Tercero",
                                            descripcion="Creación de Tercero",
                                            ruta="/administracion/terceros",
                                            fecha_creacion=datetime.datetime.today(), estado=True)

    eventos_desencadenadores.objects.create(id=4, nombre="Creación de Empresas",
                                            descripcion="Creación de Empresas",
                                            ruta="/administracion/empresas",
                                            fecha_creacion=datetime.datetime.today(), estado=True)

    eventos_desencadenadores.objects.create(id=5, nombre="Creación Entidades CAFE",
                                            descripcion="Creación Entidades CAFE",
                                            ruta="/talento-humano/entidades-index/0",
                                            fecha_creacion=datetime.datetime.today(), estado=True)

    eventos_desencadenadores.objects.create(id=6, nombre="Creación de Colaboradores",
                                            descripcion="Creación de Colaboradores",
                                            ruta="/talento-humano/colaboradores-index/0",
                                            fecha_creacion=datetime.datetime.today(), estado=True)


def textos_eventos_desencadenadores(apps, schema_editor):

    textos = apps.get_model('Notificaciones', 'TextoNotificacionDelSistema')

    textos.objects.create(titulo="Bienvenido a EVA",
                          mensaje="Bienvenido a EVA",
                          evento_desencadenador_id=1)

    textos.objects.create(titulo="Creación de Contratos",
                          mensaje="Creación de Contratos",
                          evento_desencadenador_id=2)

    textos.objects.create(titulo="Creación de Tercero",
                          mensaje="Creación de Tercero",
                          evento_desencadenador_id=3)

    textos.objects.create(titulo="Creación de Empresas",
                          mensaje="Creación de Empresas",
                          evento_desencadenador_id=4)

    textos.objects.create(titulo="Creación Entidades CAFE",
                          mensaje="Creación Entidades CAFE",
                          evento_desencadenador_id=5)

    textos.objects.create(titulo="Creación de Colaboradores",
                          mensaje="Creación de Colaboradores",
                          evento_desencadenador_id=6)


def tipos_de_notificaciones(apps, schema_editor):

    tipo_notificacion = apps.get_model('Notificaciones', 'TipoNotificacion')

    tipo_notificacion.objects.create(id=1,
                                     nombre="Evento del Sistema",
                                     descripcion="Tipo de notificación que se genera con eventos del sistema",
                                     estado=True)

    tipo_notificacion.objects.create(id=2,
                                     nombre="Obligatoria",
                                     descripcion="Tipo de notificación que crea el administrador y que la "
                                                 "establece de tipo obligatoria",
                                     estado=True)

    tipo_notificacion.objects.create(id=3,
                                     nombre="Informativa",
                                     descripcion="Tipo de notificación informativa",
                                     estado=True)


class Migration(migrations.Migration):

    dependencies = [
        ('Notificaciones', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(agregar_eventos_desencadenadores),
        migrations.RunPython(textos_eventos_desencadenadores),
        migrations.RunPython(tipos_de_notificaciones),
    ]
# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal
from io import BytesIO

from reportlab.graphics.shapes import Rect, Drawing, Line
from reportlab.lib import colors
from reportlab.lib.colors import red, green, HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, Frame, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from Administracion.models import Empresa
from EVA.General.conversiones import add_years, numero_con_separadores, valor_pesos_a_letras
from Financiero.models import FacturaEncabezado


class FacturaPdf:
    def __init__(self):
        pass

    @staticmethod
    def generar(factura: FacturaEncabezado, empresa: Empresa):

        # region Carga el tipo de letra
        pdfmetrics.registerFont(TTFont('GOTHIC', 'EVA/reportes/fonts/GOTHIC.TTF'))
        pdfmetrics.registerFont(TTFont('GOTHICB', 'EVA/reportes/fonts/GOTHICB.TTF'))
        pdfmetrics.registerFont(TTFont('GOTHICBI', 'EVA/reportes/fonts/GOTHICBI.TTF'))
        pdfmetrics.registerFont(TTFont('GOTHICI', 'EVA/reportes/fonts/GOTHICI.TTF'))

        pdfmetrics.registerFont(TTFont('ARIAL', 'EVA/reportes/fonts/arial.ttf'))
        pdfmetrics.registerFont(TTFont('ARIALB', 'EVA/reportes/fonts/arialbd.ttf'))
        # endregion

        report_buffer = BytesIO()
        elements = []
        if factura.estado == 0:
            titulo_pdf = 'Factura # {}'.format(factura.numero_factura)
        else:
            titulo_pdf = 'Borrador Factura # {}'.format(factura.id)

        letra_resolucion = 'GOTHIC'
        letra_factura = 'ARIAL'
        color_titulos = HexColor(0xBFBFBF)
        doc = SimpleDocTemplate(report_buffer, pagesize=letter,
                                leftMargin=0 * cm, rightMargin=0 * cm,
                                bottomMargin=0 * cm, topMargin=0 * cm,
                                title=titulo_pdf,
                                author='EVA',
                                subject='Realizada por usuario: {0}'.format(factura.usuario_crea),
                                showBoundary=2
                                )

        resolucion_style = ParagraphStyle(name='Items', fontName=letra_resolucion + 'B', fontSize=9, leading=9)
        titulo_detalle_style = ParagraphStyle(name='titulo_detalle', fontName=letra_factura + 'B', fontSize=10)
        descripcion_detalle_style = ParagraphStyle(name='descripcion_detalle', fontName=letra_factura, fontSize=10)
        total_letras_style = ParagraphStyle(name='total_letras', fontName=letra_factura + 'B', fontSize=10)
        nombre_legal_style = ParagraphStyle(name='nombre_legal', fontName=letra_factura + 'B', fontSize=10)

        elements.append(Spacer(1, 5.4 * cm))

        # region Resolución de facturación
        resolucion = factura.resolucion
        p = Paragraph('Habilitación de resolución de facturación número {0} del {1:%d-%m-%Y} al {2:%d-%m-%Y}'
                      .format(resolucion.numero_resolucion, resolucion.fecha_resolucion,
                              add_years(resolucion.fecha_resolucion, 2)), resolucion_style)
        t = Table([['', p]], colWidths=[3.8 * cm, 17.4 * cm])

        elements.append(t)
        # endregion

        elements.append(Spacer(1, 0.2 * cm))

        # region Info cliente.
        cliente = factura.tercero
        data = [['', 'Cliente', '', ''],
                ["Nombre:", cliente.nombre, cliente.tipo_identificacion.sigla + ':', cliente.identificacion],
                ['', '', "Tel:", cliente.telefono],
                ['Dirección:', cliente.direccion, 'Fax:', cliente.fax],
                ]
        t = Table(data, style=[('FACE', (1, 0), (1, 0), letra_factura + 'B'),
                               ('FACE', (0, 1), (-1, -1), letra_factura),
                               ('SIZE', (0, 0), (-1, -1), 10),
                               ('VALIGN', (2, 0), (-1, -1), 'MIDDLE'),
                               ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                               ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                               ('LINEBELOW', (1, 1), (1, -1), 0.5, colors.black),
                               ('LINEBELOW', (3, 1), (3, -1), 0.5, colors.black),
                               ],
                  colWidths=[1.8 * cm, 10.5 * cm, 1 * cm, 3.8 * cm],
                  rowHeights=0.6 * cm)

        tc = Table([['', t]], colWidths=[2 * cm, 17.4 * cm])

        elements.append(tc)
        # endregion

        # region Fechas y Ciudad.
        data = [['Ciudad:', '{1} - {0}'.format(cliente.centro_poblado.municipio.departamento.nombre,
                                             cliente.centro_poblado.nombre), 'Fecha Expedición:',
                 '{:%d/%m/%Y}'.format(factura.fecha_creacion)],
                ['', '', 'Fecha Vencimiento:', '']]
        t = Table(data, style=[('FACE', (0, 0), (-1, -1), letra_factura),
                               ('SIZE', (0, 0), (-1, -1), 10),
                               ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                               ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                               ('LINEBELOW', (1, 0), (1, 0), 0.5, colors.black),
                               ('LINEBELOW', (3, 0), (3, -1), 0.5, colors.black),
                               ],
                  colWidths=[1.8 * cm, 8.25 * cm, 3.25 * cm, 3.8 * cm],
                  rowHeights=0.6 * cm)

        tc = Table([['', t]], colWidths=[2 * cm, 17.4 * cm])

        elements.append(tc)
        # endregion

        elements.append(Spacer(1, 0.6 * cm))

        # region detalle y totales
        data = [['No.', 'Descripción', 'Valor']]

        for index, detalle in enumerate(factura.facturadetalle_set.all(), start=1):
            titulo = Paragraph(detalle.titulo, titulo_detalle_style)
            descripcion = Paragraph(detalle.descripcion, descripcion_detalle_style)
            valor = numero_con_separadores(detalle.valor_total)

            data.append([index, [titulo, descripcion], valor])

        data.append(['SUBTOTAL', '', numero_con_separadores(factura.subtotal)])

        impuestos = factura.facturaimpuesto_set.all()
        for impuesto in impuestos:
            nombre = impuesto.impuesto.nombre
            valor = numero_con_separadores(round((impuesto.valor_base * impuesto.impuesto.porcentaje) / Decimal('100'),
                                                 2))

            data.append([nombre, '', valor])

        data.append(['TOTAL', '', numero_con_separadores(factura.total)])

        data.append([Paragraph('SON: ' + valor_pesos_a_letras(factura.total), total_letras_style), '', ''])

        tabla_detalle_style = [('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('ALIGN', (0, 0), (-1, 0), 'CENTRE'),
                               ('FACE', (0, 0), (-1, 0), letra_factura + 'B'),
                               ('SIZE', (0, 0), (-1, 0), 10),
                               ('BACKGROUND', (0, 0), (-1, 0), color_titulos),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                               ('FACE', (0, 1), (-1, -1), letra_factura),
                               ('SIZE', (0, 1), (-1, -1), 10),
                               ('ALIGN', (0, 1), (0, -1), 'CENTRE'),
                               ('ALIGN', (2, 1), (2, -1), 'RIGHT')
                               ]

        can_totales = len(impuestos) + 3
        for i in range(2, can_totales + 1):
            tabla_detalle_style.append(('SPAN', (0, -i), (1, -i)))

        # Estilos para el Subtotal y total.
        tabla_detalle_style.append(('ALIGN', (0, -can_totales), (0, -2), 'RIGHT'))
        tabla_detalle_style.append(('FACE', (0, -can_totales), (-1, -can_totales), letra_factura + 'B'))
        tabla_detalle_style.append(('FACE', (0, -2), (-1, -2), letra_factura + 'B'))

        # Estilos para el total en letras.
        tabla_detalle_style.append(('SPAN', (0, -1), (-1, -1)))
        tabla_detalle_style.append(('BOX',  (0, -1), (-1, -1), 1.5, colors.black))

        t = Table(data, style=tabla_detalle_style,
                  colWidths=[1.5 * cm, 11.8 * cm, 4.1 * cm], spaceBefore=0.0 * cm, spaceAfter=0.0 * cm
                  )

        tc = Table(data=[['', t]],
                   colWidths=[1.8 * cm, 17.4 * cm], spaceAfter=0.0 * cm)
        ancho_detalle, alto_detalle = t.wrap(doc.width, doc.height)
        elements.append(tc)
        # endregion

        elements.append(Spacer(1, 8.4 * cm - alto_detalle))
        # region detalle y totales
        data = [['Recibida por:', ''],
                ['', 'Nombre'],
                ['', ''],
                ['', 'Firma'],
                ['', ''],
                ['', 'No. Documento de Identificación'],
                ['', ''],
                ['', 'Fecha de recepción (dd/mm/aaaa)']]

        t = Table(data, style=[('FACE', (0, 0), (-1, -1), letra_factura),
                               ('SIZE', (0, 0), (-1, -1), 10),
                               ('ALIGN', (1, 0), (1, -1), 'CENTRE'),
                               ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                               ('LINEBELOW', (1, 0), (1, 0), 0.5, colors.black),
                               ('LINEBELOW', (1, 2), (1, 2), 0.5, colors.black),
                               ('LINEBELOW', (1, 4), (1, 4), 0.5, colors.black),
                               ('LINEBELOW', (1, 6), (1, 6), 0.5, colors.black),
                               ],
                  colWidths=[2.25 * cm, 7 * cm],
                  rowHeights=0.5 * cm)

        nombre = Paragraph('CHRISTIAN ALEXANDER ARDILA RIOS', nombre_legal_style)
        label_nombre = Paragraph('Representante Legal', descripcion_detalle_style)
        tc = Table(data=[['', [nombre, label_nombre], t]],
                   style=[('VALIGN', (1, 0), (1, -1), 'MIDDLE'),
                          ('SPAN', (1, 0), (1, -1)),
                          ('LEFTPADDING', (1, 0), (1, -1), 12)],
                   colWidths=[1.8 * cm, 7.95 * cm, 9.45 * cm])

        elements.append(tc)
        # endregion


        # write the document to buffer
        doc.build(elements, onFirstPage=FacturaPdf.pagina_prueba)

        report = report_buffer.getvalue()
        report_buffer.close()
        return report

    @staticmethod
    def pagina_prueba(canvas: Canvas, doc: SimpleDocTemplate):
        canvas.saveState()
        canvas.setStrokeColor(colors.blue)
        canvas.roundRect(3.2 * cm, doc.height - (11 * cm), 17.4 * cm, 4.5 * cm, 15)
        print(doc.height)
        canvas.roundRect(3.2 * cm, doc.height - (24 * cm), 17.4 * cm, 4.5 * cm, 15)
        canvas.restoreState()

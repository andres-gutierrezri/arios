from unittest import TestCase

from Administracion.models import Impuesto
from Financiero.models import FacturaEncabezado


class TestFacturaEncabezado(TestCase):
    factura_encabezado_1 = FacturaEncabezado(porcentaje_administracion=22.00, porcentaje_imprevistos=3.00,
                                             porcentaje_utilidad=10.00, subtotal=22712038.00)
    factura_encabezado_2 = FacturaEncabezado(impuesto=Impuesto(id=1), valor_impuesto=1730964.67, subtotal=9110340.36)
    factura_encabezado_3 = FacturaEncabezado(amortizacion=41331.84, subtotal=103329.60)

    def setUp(self):
        pass

    def test_is_aplica_aiu(self):
        self.assertEqual(self.factura_encabezado_1.is_aplica_aiu, True)
        self.assertEqual(self.factura_encabezado_2.is_aplica_aiu, False)
        self.assertEqual(self.factura_encabezado_3.is_aplica_aiu, False)

    def test_is_amortizacion(self):
        self.assertEqual(self.factura_encabezado_1.is_amortizacion, False)
        self.assertEqual(self.factura_encabezado_2.is_amortizacion, False)
        self.assertEqual(self.factura_encabezado_3.is_amortizacion, True)

    def test_total_administracion(self):
        self.assertEqual(self.factura_encabezado_1.total_administracion, 4996648.36)
        self.assertEqual(self.factura_encabezado_2.total_administracion, 0.00)
        self.assertEqual(self.factura_encabezado_3.total_administracion, 0.00)

    def test_total_imprevistos(self):
        self.assertEqual(self.factura_encabezado_1.total_imprevistos, 681361.14)
        self.assertEqual(self.factura_encabezado_2.total_imprevistos, 0.00)
        self.assertEqual(self.factura_encabezado_3.total_imprevistos, 0.00)

    def test_total_utilidad(self):
        self.assertEqual(self.factura_encabezado_1.total_utilidad, 2271203.80)
        self.assertEqual(self.factura_encabezado_2.total_utilidad, 0.00)
        self.assertEqual(self.factura_encabezado_3.total_utilidad, 0.00)

    def test_total_amortizacion(self):
        self.assertEqual(self.factura_encabezado_1.total_amortizacion, 0.00)
        self.assertEqual(self.factura_encabezado_2.total_amortizacion, 0.00)
        self.assertEqual(self.factura_encabezado_3.total_amortizacion, 41331.84)

    def test_total_impuesto(self):
        self.assertEqual(self.factura_encabezado_1.total_impuesto, 0.00)
        self.assertEqual(self.factura_encabezado_2.total_impuesto, 1730964.67)
        self.assertEqual(self.factura_encabezado_3.total_impuesto, 0.00)

    def test_total_factura(self):
        self.assertEqual(self.factura_encabezado_1.total_factura, 30661251.30)
        self.assertEqual(self.factura_encabezado_2.total_factura, 10841305.03)
        self.assertEqual(self.factura_encabezado_3.total_factura, 61997.76)

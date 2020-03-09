from decimal import Decimal
from unittest import TestCase

from EVA.General.conversiones import valor_pesos_a_letras


class TestValorPesosALetras(TestCase):
    def test_miles(self):
        self.assertEqual(valor_pesos_a_letras(1000), 'MIL PESOS M/CTE')
        self.assertEqual(valor_pesos_a_letras(134812427),
                         'CIENTO TREINTA Y CUATRO MILLONES OCHOCIENTOS DOCE MIL CUATROCIENTOS VEINTISIETE PESOS M/CTE')
        self.assertEqual(valor_pesos_a_letras(150850.23),
                         'CIENTO CINCUENTA MIL OCHOCIENTOS CINCUENTA PESOS CON VEINTITRÉS CENTAVOS M/CTE')
        self.assertEqual(valor_pesos_a_letras(Decimal('150850.23')),
                         'CIENTO CINCUENTA MIL OCHOCIENTOS CINCUENTA PESOS CON VEINTITRÉS CENTAVOS M/CTE')

from unittest import TestCase

from EVA.General.conversiones import numero_a_letras


class TestNumeroALetras(TestCase):

    def test_miles(self):
        self.assertEqual(numero_a_letras(1000), 'MIL')
        self.assertEqual(numero_a_letras(1001), 'MIL UN')
        self.assertEqual(numero_a_letras(1000000), 'UN MILLÓN')
        self.assertEqual(numero_a_letras(1000001), 'UN MILLÓN UN')
        self.assertEqual(numero_a_letras(1001000), 'UN MILLÓN MIL')
        self.assertEqual(numero_a_letras(1001001), 'UN MILLÓN MIL UN')
        self.assertEqual(numero_a_letras(1000000000), 'MIL MILLONES')
        self.assertEqual(numero_a_letras(1000000001), 'MIL MILLONES UN')
        self.assertEqual(numero_a_letras(1000001000), 'MIL MILLONES MIL')
        self.assertEqual(numero_a_letras(1000001001), 'MIL MILLONES MIL UN')
        self.assertEqual(numero_a_letras(1001000000), 'MIL UN MILLONES')
        self.assertEqual(numero_a_letras(1001000001), 'MIL UN MILLONES UN')
        self.assertEqual(numero_a_letras(1001001000), 'MIL UN MILLONES MIL')
        self.assertEqual(numero_a_letras(1001001001), 'MIL UN MILLONES MIL UN')

    def test_varios(self):
        self.assertEqual(numero_a_letras(1001536), 'UN MILLÓN MIL QUINIENTOS TREINTA Y SEIS')
        self.assertEqual(numero_a_letras(103329), 'CIENTO TRES MIL TRESCIENTOS VEINTINUEVE')
        self.assertEqual(numero_a_letras(134812427),
                         'CIENTO TREINTA Y CUATRO MILLONES OCHOCIENTOS DOCE MIL CUATROCIENTOS VEINTISIETE')

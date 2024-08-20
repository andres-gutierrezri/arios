from unittest import TestCase

from EVA.General.conversiones import decenas_a_letras


class TestDecenasALetras(TestCase):
    DECENAS = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']

    def test_decenas_exactas(self):

        for i in range(1, 10):
            self.assertEqual(decenas_a_letras(str(i), True), self.DECENAS[i])

        self.assertEqual(decenas_a_letras('a', True), '')
        self.assertEqual(decenas_a_letras('a12132', True), '')
        self.assertEqual(decenas_a_letras('ahs', True), '')
        self.assertEqual(decenas_a_letras('0', True), '')

    def test_decenas_inexactas(self):

        for i in range(3, 10):
            self.assertEqual(decenas_a_letras(str(i), False), self.DECENAS[i] + ' Y ')

        self.assertEqual(decenas_a_letras('1', False), '')
        self.assertEqual(decenas_a_letras('2', False), 'VEINTI')

        self.assertEqual(decenas_a_letras('a', False), '')
        self.assertEqual(decenas_a_letras('a12132', False), '')
        self.assertEqual(decenas_a_letras('ahs', False), '')
        self.assertEqual(decenas_a_letras('0', False), '')

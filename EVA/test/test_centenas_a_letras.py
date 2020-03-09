from unittest import TestCase

from EVA.General.conversiones import centenas_a_letras


class TestCentenasALetras(TestCase):
    CENTENAS = ['', 'CIEN', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS',
                'OCHOCIENTOS', 'NOVECIENTOS']

    def test_centenas_exactas(self):

        for i in range(1, 10):
            self.assertEqual(centenas_a_letras(str(i), True), self.CENTENAS[i])

        self.assertEqual(centenas_a_letras('a', True), '')
        self.assertEqual(centenas_a_letras('a12132', True), '')
        self.assertEqual(centenas_a_letras('ahs', True), '')
        self.assertEqual(centenas_a_letras('0', True), '')

    def test_centenas_inexactas(self):

        for i in range(2, 10):
            self.assertEqual(centenas_a_letras(str(i), False), self.CENTENAS[i])

        self.assertEqual(centenas_a_letras('1', False), 'CIENTO')
        self.assertEqual(centenas_a_letras('a', False), '')
        self.assertEqual(centenas_a_letras('a12132', False), '')
        self.assertEqual(centenas_a_letras('ahs', False), '')
        self.assertEqual(centenas_a_letras('0', False), '')

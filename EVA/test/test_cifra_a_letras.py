from unittest import TestCase

from EVA.General.conversiones import cifra_a_letras


class TestCifraALetras(TestCase):

    def test_cifras_ultima(self):
        self.assertEqual(cifra_a_letras(100), 'CIEN')
        self.assertEqual(cifra_a_letras(368), 'TRESCIENTOS SESENTA Y OCHO')
        self.assertEqual(cifra_a_letras(101), 'CIENTO UN')
        self.assertEqual(cifra_a_letras(1), 'UN')
        self.assertEqual(cifra_a_letras(21), 'VEINTIÚN')
        self.assertEqual(cifra_a_letras(22), 'VEINTIDÓS')
        self.assertEqual(cifra_a_letras(23), 'VEINTITRÉS')
        self.assertEqual(cifra_a_letras(26), 'VEINTISÉIS')
        self.assertEqual(cifra_a_letras(36), 'TREINTA Y SEIS')

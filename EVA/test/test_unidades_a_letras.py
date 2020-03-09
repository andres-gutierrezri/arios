from unittest import TestCase

from EVA.General.conversiones import unidades_a_letras


class TestUnidadesALetras(TestCase):
    UNIDADES = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
    DECENAS = ['', 'ONCE', 'DOCE', 'TRECE', 'CATORCE', 'QUINCE', 'DIECISÉIS', 'DIECISIETE', 'DIECIOCHO',
               'DIECINUEVE']

    def test_solo_unidades(self):

        for i in range(1, 10):
            self.assertEqual(unidades_a_letras(str(i), False), self.UNIDADES[i])

        self.assertEqual(unidades_a_letras('a', False), '')
        self.assertEqual(unidades_a_letras('a12132', False), '')
        self.assertEqual(unidades_a_letras('ahs', False), '')

    def test_decena_uno(self):

        for i in range(1, 10):
            self.assertEqual(unidades_a_letras(str(i), True), self.DECENAS[i])

        self.assertEqual(unidades_a_letras('a', False), '')
        self.assertEqual(unidades_a_letras('a12132', False), '')
        self.assertEqual(unidades_a_letras('ahs', False), '')


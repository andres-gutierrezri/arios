from datetime import date
from unittest import TestCase

from EVA.General.conversiones import centenas_a_letras, add_months


class TestAddMonths(TestCase):
    def test_dias_positivos(self):
        comparaciones = [(date(2020, 1, 30), 1, date(2020, 2, 29)),
                         (date(2019, 1, 30), 1, date(2019, 2, 28)),
                         (date(2019, 1, 30), 12, date(2020, 1, 30)),
                         (date(2019, 1, 30), 14, date(2020, 3, 30)),
                         (date(2019, 10, 15), 5, date(2020, 3, 15)),
                         (date(2020, 1, 9), 8, date(2020, 9, 9)),
                         (date(2019, 11, 30), 1, date(2019, 12, 30))]

        for i, comparacion in enumerate(comparaciones):
            self.assertEqual(add_months(comparacion[0], comparacion[1]), comparacion[2],
                             f'En comparación {i} positivos')

    def test_dias_negativos(self):
        comparaciones = [(date(2020, 1, 30), -1, date(2019, 12, 30)),
                         (date(2019, 2, 28), -1, date(2019, 1, 28)),
                         (date(2020, 3, 31), -1, date(2020, 2, 29)),
                         (date(2020, 3, 30), -1, date(2020, 2, 29)),
                         (date(2019, 3, 31), -1, date(2019, 2, 28)),
                         (date(2019, 3, 30), -1, date(2019, 2, 28)),
                         (date(2019, 10, 15), -5, date(2019, 5, 15)),
                         (date(2020, 1, 9), -12, date(2019, 1, 9)),
                         (date(2020, 11, 30), -15, date(2019, 8, 30)),
                         (date(2020, 1, 30), -15, date(2018, 10, 30))]

        for i, comparacion in enumerate(comparaciones):
            self.assertEqual(add_months(comparacion[0], comparacion[1]), comparacion[2],
                             f'En comparación {i} negativos')

    def test_dias_0(self):
        comparaciones = [(date(2020, 1, 30), 0, date(2020, 1, 30)),
                         (date(2019, 2, 28), 0, date(2019, 2, 28)),
                         (date(2020, 3, 30), 0, date(2020, 3, 30)),
                         (date(2019, 3, 30), 0, date(2019, 3, 30)),
                         (date(2019, 10, 15), 0, date(2019, 10, 15)),
                         (date(2020, 1, 9), 0, date(2020, 1, 9)),
                         (date(2020, 11, 30), 0, date(2020, 11, 30)),
                         (date(2020, 1, 30), 0, date(2020, 1, 30))]

        for i, comparacion in enumerate(comparaciones):
            self.assertEqual(add_months(comparacion[0], comparacion[1]), comparacion[2], f'En comparación {i} ceros')

import unittest

from src.disponibilidade import (
    disponibilidade_analitica,
    disponibilidade_simulada,
    k_maioria,
)


class TestDisponibilidadeAnalitica(unittest.TestCase):
    def test_casos_extremos(self):
        self.assertAlmostEqual(disponibilidade_analitica(4, 1, 0.8), 1 - 0.2**4)
        self.assertAlmostEqual(disponibilidade_analitica(4, 4, 0.8), 0.8**4)

    def test_distribuicao_completa(self):
        self.assertAlmostEqual(disponibilidade_analitica(2, 1, 0.5), 0.75)
        self.assertAlmostEqual(disponibilidade_analitica(2, 2, 0.5), 0.25)

    def test_limites_de_p(self):
        self.assertEqual(disponibilidade_analitica(10, 3, 0), 0.0)
        self.assertEqual(disponibilidade_analitica(10, 3, 1), 1.0)

    def test_maioria(self):
        self.assertEqual(k_maioria(4), 2)
        self.assertEqual(k_maioria(5), 3)

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            disponibilidade_analitica(0, 1, 0.5)
        with self.assertRaises(ValueError):
            disponibilidade_analitica(4, 5, 0.5)
        with self.assertRaises(ValueError):
            disponibilidade_analitica(4, 2, 1.1)


class TestSimulacao(unittest.TestCase):
    def test_simulacao_reproduzivel_e_proxima(self):
        experimental, sucessos = disponibilidade_simulada(4, 1, 0.8, 100_000, seed=7)
        self.assertEqual(sucessos, round(experimental * 100_000))
        self.assertLess(abs(experimental - disponibilidade_analitica(4, 1, 0.8)), 0.01)


if __name__ == "__main__":
    unittest.main()

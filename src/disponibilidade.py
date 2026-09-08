"""Modelo analítico e simulador para um serviço replicado."""

from __future__ import annotations

import math
from typing import Final

import numpy as np


_EPS: Final[float] = 1e-12


def _validar_parametros(n: int, k: int, p: float) -> None:
    """Valida os parâmetros comuns do modelo."""
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError("n deve ser um inteiro maior que zero")
    if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or not 1 <= k <= n:
        raise ValueError("k deve ser um inteiro entre 1 e n")
    if not 0 <= p <= 1:
        raise ValueError("p deve estar entre 0 e 1")


def disponibilidade_analitica(n: int, k: int, p: float) -> float:
    """Retorna P(X >= k), com X ~ Binomial(n, p)."""
    _validar_parametros(n, k, p)

    if p == 0:
        return 0.0
    if p == 1:
        return 1.0
    if k == 1:
        return 1.0 - (1.0 - p) ** n
    if k == n:
        return p**n

    valor = sum(
        math.comb(n, i) * p**i * (1.0 - p) ** (n - i)
        for i in range(k, n + 1)
    )
    return min(1.0, max(0.0, float(valor)))


def k_maioria(n: int) -> int:
    """Retorna o menor número de servidores que representa uma maioria."""
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError("n deve ser um inteiro maior que zero")
    return (n + 1) // 2


def disponibilidade_simulada(
    n: int,
    k: int,
    p: float,
    rodadas: int = 100_000,
    seed: int | None = 42,
) -> tuple[float, int]:
    """Estima a disponibilidade por Monte Carlo."""
    _validar_parametros(n, k, p)
    if isinstance(rodadas, bool) or not isinstance(rodadas, (int, np.integer)) or rodadas <= 0:
        raise ValueError("rodadas deve ser um inteiro maior que zero")

    rng = np.random.default_rng(seed)
    disponiveis = rng.random((rodadas, n)) <= p
    sucessos = int(np.count_nonzero(disponiveis.sum(axis=1) >= k))
    return sucessos / rodadas, sucessos

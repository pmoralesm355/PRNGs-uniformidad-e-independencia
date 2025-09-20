# pruebas básicas para secuencias pseudoaleatorias
#   Muestreo, χ² (uniformidad 1D), rachas (Wald–Wolfowitz) y
#   autocorrelación lag-1  y sin dependencias externas

import math
import time
from typing import Tuple, Dict, List


def sample(prng, n: int = 10_000) -> List[float]:
    """Genera n valores en [0,1) llamando a prng.random()."""
    return [prng.random() for _ in range(n)]


def chi_square_uniform(samples: List[float], bins: int = 50) -> Tuple[float, int]:
    """
    Test χ² contra Unif[0,1) con bins equiespaciados.
    Retorna (chi2, df) con df = bins - 1.
    """
    n = len(samples)
    counts = [0] * bins
    for x in samples:
        k = min(bins - 1, int(x * bins))  # protege el caso x≈1.0
        counts[k] += 1

    expected = n / bins
    chi2 = sum((c - expected) ** 2 / expected for c in counts)
    return chi2, bins - 1


def runs_test_independence(samples: List[float]) -> Dict[str, float]:
    """
    Test de rachas (Wald–Wolfowitz) alrededor de 0.5.
    Binariza: 1 si x>=0.5, 0 si x<0.5. Devuelve R y Z.
    """
    signs = [1 if x >= 0.5 else 0 for x in samples]
    n1 = sum(signs)               # nº de 1s
    n2 = len(signs) - n1          # nº de 0s
    if n1 == 0 or n2 == 0:
        return {"R": float("nan"), "Z": float("nan"), "n1": n1, "n2": n2}

    R = 1
    for i in range(1, len(signs)):
        if signs[i] != signs[i - 1]:
            R += 1

    mu = 1 + (2 * n1 * n2) / (n1 + n2)
    var = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / (((n1 + n2) ** 2) * (n1 + n2 - 1))
    Z = (R - mu) / math.sqrt(var) if var > 0 else float("nan")
    return {"R": R, "Z": Z, "n1": n1, "n2": n2}


def autocorr_lag1(samples: List[float]) -> float:
    """
    Estimador de autocorrelación con retardo 1:
    rho(1) = Σ (x_t-ȳ)(x_{t-1}-ȳ) / Σ (x_t-ȳ)^2
    """
    n = len(samples)
    mean = sum(samples) / n
    num = sum((samples[i] - mean) * (samples[i - 1] - mean) for i in range(1, n))
    den = sum((x - mean) ** 2 for x in samples)
    return num / den if den != 0 else float("nan")


def time_gen(prng, n: int = 1_000_000) -> float:
    """Tiempo (seg) que tarda en generar n valores con prng.random()."""
    t0 = time.time()
    acc = 0.0
    for _ in range(n):
        acc += prng.random()  # evita que el bucle sea eliminado
    return time.time() - t0

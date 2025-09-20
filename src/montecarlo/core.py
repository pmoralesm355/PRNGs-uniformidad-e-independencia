# montecarlo/core.py
# Integrandos usados en la Parte 2.

import math

def f1(x: float) -> float:
    """
    f1(x) = sin(pi * x), x en [0, 1].
    Integral exacta: ∫_0^1 sin(pi x) dx = 2/pi.
    """
    return math.sin(math.pi * x)


# constante para la norml estándar
_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)

def f2(x: float) -> float:
    """
    f2(x) = phi(x) = (1/sqrt(2*pi)) * exp(-x^2/2), x en [0, 2].
    Integral en [0,2]: Phi(2) - Phi(0) ≈ 0.4772498680518208.
    """
    return _INV_SQRT_2PI * math.exp(-0.5 * x * x)
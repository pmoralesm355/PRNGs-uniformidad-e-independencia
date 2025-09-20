class RANDU:
    # RANDU — LCG histórico de mala calidad (uso educativo).
    # Recurrencia: X_{k+1} = (a * X_k) mod m ; c=0
    # Parámetros: a = 65539 (= 2^16 + 3), m = 2^31
    # Fallo conocido: fuerte correlación en 3D (tríos caen en ~15 planos).
    # Periodo efectivo ≈ 2^29 con semillas impares. No criptográfico.

    a = 65539          # multiplicador
    m = 2**31          # módulo (2147483648)

    def __init__(self, seed: int = 1):
        # Semilla normalizada a [0, m-1] y forzada a impar para evitar perder periodo.
        s = int(seed) % self.m
        self.state = s | 1

    def random(self) -> float:
        # Avanza el estado y devuelve U ∈ [0,1)
        self.state = (self.a * self.state) % self.m
        return self.state / self.m

    def randint(self, low: int, high: int) -> int:
        # Entero en [low, high] vía escala de random(); posible sesgo por discretización.
        return low + int(self.random() * (high - low + 1))

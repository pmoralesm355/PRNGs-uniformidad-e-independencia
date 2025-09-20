class BlumBlumShub:
    # BBS — X_{k+1} = X_k^2 mod M, M = p*q con p≡q≡3 (mod 4). Uso demostrativo (M pequeño).
    def __init__(self, seed: int = 8731, p: int = 383, q: int = 503):
        # Validación de primos de Blum
        if p == q or p % 4 != 3 or q % 4 != 3:
            raise ValueError("p y q deben ser primos distintos con p≡q≡3 (mod 4).")
        self.p, self.q = int(p), int(q)
        self.M = self.p * self.q  # módulo compuesto

        # Semilla: 0 < x0 < M y coprima con M (evitar múltiplos de p o q)
        x0 = int(seed) % self.M
        if x0 == 0:
            x0 = 3
        while x0 % self.p == 0 or x0 % self.q == 0:
            x0 = (x0 + 1) % self.M
            if x0 == 0:
                x0 = 3

        # Estado inicial: X0 = x0^2 mod M (definición estándar)
        self.state = pow(x0, 2, self.M)

    def _next_bit(self) -> int:
        # Iteración cuadrática y extracción del bit menos significativo
        self.state = pow(self.state, 2, self.M)
        return self.state & 1

    def random(self, bits: int = 32) -> float:
        # Empaquetado de 'bits' LSB sucesivos en un entero y escalado a [0,1)
        x = 0
        for _ in range(int(bits)):
            x = (x << 1) | self._next_bit()
        return x / (1 << bits)

    def randint(self, low: int, high: int) -> int:
        # Entero en [low, high] vía escala de random(); posible sesgo mínimo por discretización
        return low + int(self.random() * (high - low + 1))

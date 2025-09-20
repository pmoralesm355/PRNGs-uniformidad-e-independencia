class LCG:
    # LCG — Generador Congruencial Lineal
    # Recurrencia: X_{k+1} = (a*X_k + c) mod m ; salida U = X_k / m ∈ [0,1)
    # Parámetros por defecto (32-bit): m=2^32, a=1664525, c=1013904223
    # Hull–Dobell (periodo completo ≈ m): gcd(c,m)=1; todos los primos de m dividen (a−1);
    # si 4|m entonces 4|(a−1). No criptográfico.
    # Semilla por defecto: 123456789 (reproducible).

    def __init__(self, seed: int = 123456789,
                 a: int = 1664525, c: int = 1013904223, m: int = 2**32):
        self.a = int(a)              # multiplicador
        self.c = int(c)              # incremento
        self.m = int(m)              # módulo
        self.state = int(seed) % self.m  # estado inicial X_0 ∈ [0, m-1]

    def random(self) -> float:
        # Avanza el estado y devuelve U ∈ [0,1)
        self.state = (self.a * self.state + self.c) % self.m
        return self.state / self.m

    def randint(self, low: int, high: int) -> int:
        # Entero en [low, high] vía escala de random(); posible sesgo por discretización
        return low + int(self.random() * (high - low + 1))

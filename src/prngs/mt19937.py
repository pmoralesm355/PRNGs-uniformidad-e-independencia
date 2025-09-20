class MT19937:
    """
    Mersenne Twister (MT19937)
    - Periodo: 2^19937 - 1 (no criptográfico).
    - Semilla por defecto: 5489 (canónica de referencia; reproducible).
    Constantes:
      w=32 (bits/word)  n=624 (estado)  m=397 (offset twist)  r=31 (partición)
      a=0x9908B0DF (matriz A en twist)
      u=11,d=0xFFFFFFFF ; s=7,b=0x9D2C5680 ; t=15,c=0xEFC60000 ; l=18  (tempering)
      f=1812433253 (inicialización del estado)
    """

    # parámetros MT19937
    w, n, m, r = 32, 624, 397, 31
    a = 0x9908B0DF
    u, d = 11, 0xFFFFFFFF
    s, b = 7,  0x9D2C5680
    t, c = 15, 0xEFC60000
    l = 18
    f = 1812433253

    # máscaras para unir bits altos/bajos al formar x
    lower_mask = (1 << r) - 1
    upper_mask = ((1 << w) - 1) & ~lower_mask

    def __init__(self, seed: int = 5489):
        self.MT = [0] * self.n         # buffer de estado
        self.index = self.n             # fuerza twist en primera extracción
        self.seed(seed)

    def seed(self, seed: int) -> None:
        # expansión de semilla al estado completo
        self.index = self.n
        self.MT[0] = seed & 0xFFFFFFFF
        for i in range(1, self.n):
            x = self.MT[i-1] ^ (self.MT[i-1] >> (self.w - 2))
            self.MT[i] = (self.f * x + i) & 0xFFFFFFFF

    def twist(self) -> None:
        # regeneración del bloque de 624 valores crudos
        for i in range(self.n):
            x  = (self.MT[i] & self.upper_mask) + (self.MT[(i+1) % self.n] & self.lower_mask)
            xA = x >> 1
            if x & 1:                   # si LSB=1, mezclar con A
                xA ^= self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
        self.index = 0

    def extract_number(self) -> int:
        # extracción de entero 32-bit con tempering
        if self.index >= self.n:
            self.twist()
        y = self.MT[self.index]
        y ^= (y >> self.u) & self.d
        y ^= (y << self.s) & self.b
        y ^= (y << self.t) & self.c
        y ^= (y >> self.l)
        self.index += 1
        return y & 0xFFFFFFFF

    def random(self) -> float:
        # float ∈ [0,1)
        return self.extract_number() / 2**32

    def randint(self, low: int, high: int) -> int:
        # entero en [low, high] (posible sesgo mínimo por discretización)
        return low + int(self.random() * (high - low + 1))

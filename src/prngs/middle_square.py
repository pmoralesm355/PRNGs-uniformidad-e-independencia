class MiddleSquare:
    # Middle-Square (von Neumann)
    # Recurrencia: S_{k+1} = mid_n(S_k^2) ; salida U = S_k / 10^n ∈ [0,1)
    # Limitaciones: periodos muy cortos; ciclos/0 (uso educativo).
    # Parámetros: n_digits par ≥ 4; seed normalizada a n dígitos (zfill).

    def __init__(self, seed: int = 675248, n_digits: int = 6):
        if n_digits < 4 or (n_digits % 2) != 0:
            raise ValueError("n_digits debe ser par y ≥ 4 (p.ej., 4, 6, 8).")
        self.n = int(n_digits)
        s = str(int(seed)).zfill(self.n)     # normaliza ancho
        self.state = int(s[-self.n:])        # usa últimos n dígitos

    def random(self) -> float:
        # Eleva al cuadrado y toma n dígitos centrales (padding a 2n)
        sq  = str(self.state ** 2).zfill(2 * self.n)
        mid = len(sq) // 2
        core = sq[mid - self.n // 2 : mid + self.n // 2]
        self.state = int(core)               # puede colapsar a 0 (comportamiento esperado)
        return self.state / (10 ** self.n)

    def randint(self, low: int, high: int) -> int:
        # Entero en [low, high] vía escala de random()
        return low + int(self.random() * (high - low + 1))

# PARTE 1 — PRNGs: histogramas, pruebas de hipótesis y tabla visual
# N=1000, BINS=35. Pruebas (b): χ² (uniformidad), rachas Z (independencia), ρ̂1 (lag-1).
# Comparación (c): algoritmo elegido vs random (stdlib) y secrets (OS) en una tabla.
# Salida: out/hist_*.png, out/parte1_summary.json, out/parte1_tabla.png, out/parte1_comp_<algo>.png

import os, json, math, random, secrets
import matplotlib.pyplot as plt
from typing import Dict, Any, List
from prngs import LCG, MiddleSquare, MT19937, BlumBlumShub, RANDU
from tests.utils import sample, chi_square_uniform, runs_test_independence, autocorr_lag1
from tests.plotting import save_hist

# ---------------- Configuración ----------------
OUT = os.path.join(os.path.dirname(__file__), '..', 'out')
N, BINS         = 1000, 35                    # tamaño de muestra y bins (χ²: df=34)
CHI2_CRIT_95    = 49.80                       # umbral 95% para df=34
Z_CRIT_95       = 1.96                        # |Z| crítico ~ N(0,1)
AC1_MAX         = lambda n: 2.0/math.sqrt(n)  # regla |ρ̂1| ≤ 2/√N
COMPARE_ALGO    = "LCG"                       # algoritmo elegido para (c)

# Período teórico (con orden de magnitud cuando aplica)
PERIOD_NOTE = {
    "LCG":          "≈2^32 ≈ 4.29e9 (si Hull–Dobell)",
    "MiddleSquare": "Muy corto; ciclos pequeños/colapso a 0",
    "MT19937":      "2^19937−1 (~1e6000) (enorme)",
    "BBS":          "≤λ(M)=lcm(p−1,q−1)≈95,882 (estado); bits < eso",
    "RANDU":        "≈2^29 ≈ 5.37e8; planos 3D",
    "random":       "2^19937−1 (~1e6000) (stdlib)",
    "secrets":      "CSPRNG (sin período determinista)",
}

# ------------- RNG extra (secrets) -------------
def _secrets_float():            # fracción de 52 bits ~ Unif[0,1)
    return secrets.randbits(52) / (1 << 52)
class SecretsRNG:                # adaptador .random()
    def random(self): return _secrets_float()

# ----------------- Pruebas (b) -----------------
def evaluate(xs: List[float], bins: int) -> Dict[str, Any]:
    # χ²: uniformidad 1D contra Unif[0,1)
    chi2, df = chi_square_uniform(xs, bins=bins)

    # Rachas: independencia básica alrededor de 0.5 (Wald–Wolfowitz)
    runs = runs_test_independence(xs)
    Z = runs.get("Z", float("nan"))
    p_runs = math.erfc(abs(Z)/math.sqrt(2)) if math.isfinite(Z) else float("nan")  # p≈2(1-Φ(|Z|))

    # ρ̂1: autocorrelación lag-1
    ac1 = autocorr_lag1(xs)

    return {
        "chi2": chi2, "df": df, "pass_chi2_95": (chi2 < CHI2_CRIT_95),
        "runs_R": runs.get("R"), "runs_Z": Z, "runs_p": p_runs, "pass_runs_95": (abs(Z) <= Z_CRIT_95),
        "autocorr_lag1": ac1, "pass_ac1_rule": (abs(ac1) <= AC1_MAX(len(xs))),
    }

# -------------- Tabla visual (PNG) --------------
def _row(r: Dict[str, Any]) -> List[str]:
    p = r["runs_p"]
    pstr = "<0.001" if (isinstance(p, float) and p < 1e-3) else f"{p:.3f}"
    return [
        r["name"], PERIOD_NOTE.get(r["name"], "N/D"),
        f'{r["chi2"]:.2f}', str(r["df"]), "OK" if r["pass_chi2_95"] else "FAIL",
        f'{r["runs_Z"]:.2f}', pstr, "OK" if r["pass_runs_95"] else "FAIL",
        f'{r["autocorr_lag1"]:.3f}', "OK" if r["pass_ac1_rule"] else "FAIL"
    ]

def _colors(rows: List[Dict[str,Any]], ncols: int):
    cols = []
    for r in rows:
        row = ["white"] * ncols
        row[4] = "#c8e6c9" if r["pass_chi2_95"] else "#ffcdd2"   # χ²
        row[7] = "#c8e6c9" if r["pass_runs_95"] else "#ffcdd2"   # rachas
        row[9] = "#c8e6c9" if r["pass_ac1_rule"] else "#ffcdd2"  # ρ̂1
        cols.append(row)
    return cols

def save_table_png(results: List[Dict[str,Any]], path: str, title: str):
    headers = ["PRNG","Período (teórico)","χ²","df","χ² 5%","Z(rachas)","p","Rachas 5%","ρ̂1","|ρ̂1|≤2/√N"]
    body    = [_row(r) for r in results]
    colors  = _colors(results, len(headers))

    # anchos relativos: más espacio a PRNG/Período para leer el orden de magnitud
    colw = [0.16, 0.36, 0.06, 0.05, 0.07, 0.10, 0.06, 0.10, 0.05, 0.07]

    fig_h = 0.55 * (len(body) + 2)
    fig_w = 18
    fig, ax = plt.subplots(figsize=(fig_w, fig_h)); ax.axis('off')

    tab = ax.table(cellText=body, colLabels=headers, cellColours=colors,
                   colWidths=colw, cellLoc='center', colLoc='center', loc='center')

    tab.auto_set_font_size(False); tab.set_fontsize(10); tab.scale(1.0, 1.2)
    for (r, c), cell in tab.get_celld().items():
        if r == 0:
            cell.set_text_props(fontweight='bold')
        if c in (0, 1) and r > 0:  # alinear PRNG y Período a la izquierda
            cell._loc = 'left'
            cell.get_text().set_ha('left')
        cell.get_text().set_wrap(False)

    ax.set_title(title, pad=6)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.tight_layout()
    plt.savefig(path, bbox_inches='tight', dpi=220)
    plt.close()

def save_comp_png(results: List[Dict[str,Any]], algo: str, path: str):
    keep = {algo, "random", "secrets"}
    sub  = [r for r in results if r["name"] in keep]
    headers = ["PRNG","χ² 5%","Rachas 5%","|ρ̂1|≤2/√N"]
    body = [[r["name"],
             "✓" if r["pass_chi2_95"] else "✗",
             "✓" if r["pass_runs_95"] else "✗",
             "✓" if r["pass_ac1_rule"] else "✗"] for r in sub]
    colors=[]
    for r in sub:
        row=["white"]*len(headers)
        row[1]="#c8e6c9" if r["pass_chi2_95"] else "#ffcdd2"
        row[2]="#c8e6c9" if r["pass_runs_95"] else "#ffcdd2"
        row[3]="#c8e6c9" if r["pass_ac1_rule"] else "#ffcdd2"
        colors.append(row)
    colw = [0.35, 0.22, 0.22, 0.21]
    fig, ax = plt.subplots(figsize=(9, 0.6*(len(body)+2))); ax.axis('off')
    tab = ax.table(cellText=body, colLabels=headers, cellColours=colors,
                   colWidths=colw, cellLoc='center', colLoc='center', loc='center')
    tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 1.25)
    for (r, c), cell in tab.get_celld().items():
        if r == 0: cell.set_text_props(fontweight='bold')
        if c == 0 and r > 0:
            cell._loc = 'left'; cell.get_text().set_ha('left')
    ax.set_title(f"Comparación (c): {algo} vs random vs secrets", pad=6)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.tight_layout()
    plt.savefig(path, bbox_inches='tight', dpi=220)
    plt.close()

# ------------------- Pipeline -------------------
def run_one(name: str, rng) -> Dict[str, Any]:
    # genera muestra, guarda histograma y evalúa pruebas (b)
    xs = sample(rng, n=N)
    save_hist(xs, os.path.join(OUT, f"hist_{name}.png"), bins=BINS,
              title=f"Histogram of Pseudo-random Numbers ({name})")
    base = evaluate(xs, bins=BINS)
    return {"name": name, "n": N, "bins": BINS, **base}

def main():
    os.makedirs(OUT, exist_ok=True)
    gens = [
        ("LCG",          LCG(seed=123456789)),
        ("MiddleSquare", MiddleSquare(seed=675248, n_digits=6)),
        ("MT19937",      MT19937(seed=5489)),
        ("BBS",          BlumBlumShub(seed=8731, p=383, q=503)),
        ("RANDU",        RANDU(seed=1)),
        ("random",       random.Random(42)),   # MT stdlib
        ("secrets",      SecretsRNG()),
    ]
    results = [run_one(name, rng) for name, rng in gens]

    with open(os.path.join(OUT, "parte1_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "results": results,
            "thresholds": {
                "chi2_crit_95_df34": CHI2_CRIT_95,
                "runs_Z_crit_95": Z_CRIT_95,
                "ac1_rule": f"|rho1|<=2/sqrt(N) con N={N}"
            }
        }, f, indent=2, ensure_ascii=False)

    save_table_png(results, os.path.join(OUT, "parte1_tabla.png"),
                   "Pruebas de hipótesis (χ², rachas, ρ̂1) — N=1000, BINS=35")
    save_comp_png(results, COMPARE_ALGO,
                  os.path.join(OUT, f"parte1_comp_{COMPARE_ALGO}.png"))

    print("[OK] Parte 1 → out/hist_*.png, out/parte1_summary.json, "
          "out/parte1_tabla.png, out/parte1_comp_*.png")

if __name__ == "__main__":
    main()

# Periodo → mostrado desde PERIOD_NOTE (con orden de magnitud).
# Uniformidad → chi_square_uniform + pass_chi2_95.
# Independencia → runs_test_independence (Z,p) + autocorr_lag1 (ρ̂1) y sus umbrales.

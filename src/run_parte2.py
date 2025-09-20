# PARTE 2 — Monte Carlo (X~Unif(a,b))
# Estimador: Î = (b-a)*mean(f(a+(b-a)U)), U~Unif(0,1). SE = (b-a)*sqrt(s_f^2/N).
# IC95%: Î ± 1.96*SE. Comparamos contra valores teóricos y marcamos cobertura (✓/✗).

import os, json, math, random, secrets
from montecarlo.core import f1, f2          # f1(x)=sin(pi x), f2(x)=phi(x) (N(0,1))
from prngs import LCG, MT19937

OUT, N = os.path.join(os.path.dirname(__file__), '..', 'out'), 200_000
THEORY = {"int_sin": 2.0/math.pi, "int_normal": 0.4772498680518208}

_as_secrets = lambda: secrets.randbits(52)/(1<<52)
class SecretsRNG:  # adaptador .random()
    def random(self): return _as_secrets()

def mc_integral_stats(f, a, b, rng, n=N):
    w = (b-a); s1=s2=0.0
    for _ in range(n):
        fx = f(a + w*rng.random()); s1 += fx; s2 += fx*fx
    m = s1/n; var = (s2 - n*m*m)/(n-1) if n>1 else 0.0
    est = w*m; se = w*math.sqrt(var/n); ci = (est-1.96*se, est+1.96*se)
    return est, se, ci

_relerr = lambda x,t: abs(x-t)/abs(t)
_in = lambda x,lo,hi: (lo <= x <= hi)

def run_one(name, rng):
    est1,se1,ci1 = mc_integral_stats(f1, 0.0, 1.0, rng)
    est2,se2,ci2 = mc_integral_stats(f2, 0.0, 2.0, rng)
    return {
        "rng":name,"N":N,
        "int_sin":est1,"se_sin":se1,"ci_sin":ci1,"err_sin":_relerr(est1,THEORY["int_sin"]),
        "int_normal":est2,"se_normal":se2,"ci_normal":ci2,"err_normal":_relerr(est2,THEORY["int_normal"]),
        "cover_sin":_in(THEORY["int_sin"],*ci1),"cover_normal":_in(THEORY["int_normal"],*ci2)
    }

def main():
    os.makedirs(OUT, exist_ok=True)
    gens = [("random(PyStd MT19937)", random.Random(12345)),
            ("MT19937(5489)",         MT19937(seed=5489)),
            ("LCG(123456789)",        LCG(seed=123456789)),
            ("secrets(OS)",           SecretsRNG())]
    rows = [run_one(n,g) for n,g in gens]

    print(f"[N={N}] Monte Carlo — estimación ± IC95% (err relativo, SE) y cobertura del valor teórico")
    for r in rows:
        c1 = "✓" if r["cover_sin"] else "✗"
        c2 = "✓" if r["cover_normal"] else "✗"
        print(f"- {r['rng']}")
        print(f"  ∫_0^1 sin(πx) dx  ≈ {r['int_sin']:.6f}  [{r['ci_sin'][0]:.6f}, {r['ci_sin'][1]:.6f}]"
              f"  (err {r['err_sin']:.2e}, SE {r['se_sin']:.2e})  cover {c1}")
        print(f"  ∫_0^2 φ(x) dx     ≈ {r['int_normal']:.6f}  [{r['ci_normal'][0]:.6f}, {r['ci_normal'][1]:.6f}]"
              f"  (err {r['err_normal']:.2e}, SE {r['se_normal']:.2e})  cover {c2}")

    with open(os.path.join(OUT,"parte2_montecarlo.json"),"w",encoding="utf-8") as f:
        json.dump({"N":N,"theory":THEORY,"rows":rows}, f, indent=2, ensure_ascii=False)
    print("\n[OK] Guardado en out/parte2_montecarlo.json")

if __name__ == "__main__":
    main()

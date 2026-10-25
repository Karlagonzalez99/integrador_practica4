"""Estadistica II - Pruebas de hipotesis para una media (caso 2: sigma desconocida, n>=30 -> Z con S)."""
import os
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from scipy import stats
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
SALIDA = ROOT / "Output"
SALIDA.mkdir(exist_ok=True)

url = URL.create("postgresql+psycopg", username=os.environ["PGUSER"],
                 password=os.environ["PGPASSWORD"], host=os.environ["PGHOST"],
                 port=int(os.environ.get("PGPORT", 5432)),
                 database=os.environ.get("PGDATABASE", "raw"))
engine = create_engine(url, connect_args={"sslmode": "require"})

sql = """
select v.nombre_variedad as variedad, f.clasificacion_altura as altura,
       f.region as region, l.puntaje_catacion_scaa as puntaje
from public_marts.fct_lotes_acopio l
join public_marts.dim_variedades v on v.id_variedad = l.id_variedad
join public_marts.dim_fincas f on f.id_finca = l.id_finca
where l.puntaje_catacion_scaa is not null
"""
df = pd.read_sql(sql, engine)
df["puntaje"] = pd.to_numeric(df["puntaje"])
ALFA = 0.05

PRUEBAS = [
    ("Geisha", df[df.variedad == "Geisha"]["puntaje"], 90, "derecha"),
    ("Region Madriz", df[df.region == "Madriz"]["puntaje"], 88, "izquierda"),
    ("Altura HG", df[df.altura == "Altura (HG)"]["puntaje"], 87, "dos"),
]

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
resumen = []
for ax, (nombre, x, mu0, cola) in zip(axes, PRUEBAS):
    n, xbar, s = len(x), x.mean(), x.std(ddof=1)
    z = (xbar - mu0) / (s / np.sqrt(n))
    if cola == "derecha":
        zc = stats.norm.ppf(1 - ALFA)
        rechaza = z > zc
        regla = f"Z > {zc:.3f}"
        h0, h1 = f"mu <= {mu0}", f"mu > {mu0}"
    elif cola == "izquierda":
        zc = stats.norm.ppf(1 - ALFA)
        rechaza = z < -zc
        regla = f"Z < -{zc:.3f}"
        h0, h1 = f"mu >= {mu0}", f"mu < {mu0}"
    else:
        zc = stats.norm.ppf(1 - ALFA / 2)
        rechaza = abs(z) > zc
        regla = f"Z < -{zc:.3f} o Z > {zc:.3f}"
        h0, h1 = f"mu = {mu0}", f"mu != {mu0}"
    print(f"\nPrueba: {nombre}")
    print(f"  H0: {h0}   H1: {h1}   alfa={ALFA}")
    print(f"  n={n}  media={xbar:.3f}  S={s:.3f}  Z={z:.3f}")
    print(f"  Rechazo H0 si: {regla}  ->  {'SE RECHAZA H0' if rechaza else 'NO se rechaza H0'}")
    resumen.append([nombre, h0, h1, n, round(xbar, 3), round(s, 3), round(z, 3),
                    regla, "Rechaza H0" if rechaza else "No rechaza H0"])

    xs = np.linspace(-4, 4, 400)
    ax.plot(xs, stats.norm.pdf(xs), color="black")
    if cola == "derecha":
        m = xs >= zc
        ax.fill_between(xs[m], stats.norm.pdf(xs[m]), color="tab:red", alpha=0.4)
    elif cola == "izquierda":
        m = xs <= -zc
        ax.fill_between(xs[m], stats.norm.pdf(xs[m]), color="tab:red", alpha=0.4)
    else:
        for m in (xs <= -zc, xs >= zc):
            ax.fill_between(xs[m], stats.norm.pdf(xs[m]), color="tab:red", alpha=0.4)
    ax.axvline(max(min(z, 4), -4), color="tab:blue", linestyle="--",
               label=f"Z calculado = {z:.2f}")
    ax.set_title(f"{nombre}\n{h0} vs {h1}")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_yticks([])

plt.tight_layout()
fig.savefig(SALIDA / "pruebas_hipotesis.png", dpi=150)
pd.DataFrame(resumen, columns=["prueba", "H0", "H1", "n", "media", "S", "Z",
                               "regla_rechazo", "decision"]).to_csv(
    SALIDA / "pruebas_hipotesis.csv", index=False)
print("\nGuardado en Output/: pruebas_hipotesis.png y .csv")

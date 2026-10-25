"""Estadistica II - Intervalos de confianza para el puntaje de catacion (SCAA)."""
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

url = URL.create(
    "postgresql+psycopg",
    username=os.environ["PGUSER"],
    password=os.environ["PGPASSWORD"],
    host=os.environ["PGHOST"],
    port=int(os.environ.get("PGPORT", 5432)),
    database=os.environ.get("PGDATABASE", "raw"),
)
engine = create_engine(url, connect_args={"sslmode": "require"})

sql = """
select l.id_lote,
       v.nombre_variedad as variedad,
       f.clasificacion_altura as altura,
       f.region as region,
       l.puntaje_catacion_scaa as puntaje
from public_marts.fct_lotes_acopio l
join public_marts.dim_variedades v on v.id_variedad = l.id_variedad
join public_marts.dim_fincas f on f.id_finca = l.id_finca
where l.puntaje_catacion_scaa is not null
"""
df = pd.read_sql(sql, engine)
df["puntaje"] = pd.to_numeric(df["puntaje"])
NC = 0.95


def ic_media(x, nc=NC):
    n = len(x)
    xbar = x.mean()
    s = x.std(ddof=1)
    t = stats.t.ppf(1 - (1 - nc) / 2, n - 1)
    error = t * s / np.sqrt(n)
    return n, xbar, s, t, error, xbar - error, xbar + error


def tabla_ic(col):
    filas = []
    for grupo, g in df.groupby(col):
        if len(g) < 2:
            continue
        n, xbar, s, t, e, li, ls = ic_media(g["puntaje"])
        filas.append([grupo, n, round(xbar, 2), round(s, 2), round(t, 3),
                      round(e, 3), round(li, 2), round(ls, 2)])
    tb = pd.DataFrame(filas, columns=[col, "n", "media", "S", "t",
                                      "error_maximo", "limite_inf", "limite_sup"])
    return tb.sort_values("media", ascending=False)


def grafico(tb, col, titulo, archivo):
    tb = tb.sort_values("media")
    fig, ax = plt.subplots(figsize=(8, 4 + 0.3 * len(tb)))
    ax.errorbar(tb["media"], tb[col].astype(str),
                xerr=[tb["media"] - tb["limite_inf"], tb["limite_sup"] - tb["media"]],
                fmt="o", capsize=4)
    ax.set_xlabel("Puntaje de catacion SCAA (media con IC 95%)")
    ax.set_title(titulo)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    fig.savefig(SALIDA / archivo, dpi=150)
    plt.close(fig)


for col, titulo in [("variedad", "por variedad"),
                    ("altura", "por clasificacion de altura"),
                    ("region", "por region de origen")]:
    tb = tabla_ic(col)
    print(f"\nIC 95% para el puntaje promedio {titulo}:\n")
    print(tb.to_string(index=False))
    tb.to_csv(SALIDA / f"ic_puntaje_{col}.csv", index=False)
    grafico(tb, col, f"Puntaje promedio {titulo} - Cooperativa El Volcan",
            f"ic_puntaje_{col}.png")

# Muestreo: muestra aleatoria de 30 lotes vs. parametro poblacional
mu = df["puntaje"].mean()
sigma = df["puntaje"].std(ddof=0)
m = df["puntaje"].sample(30, random_state=42)
n, xbar, s, t, e, li, ls = ic_media(m)
print(f"\nMuestra n=30: media={xbar:.2f}, S={s:.2f}, IC95%=[{li:.2f}; {ls:.2f}]")
print(f"Media poblacional ({len(df)} lotes) = {mu:.2f} -> dentro del IC: {li <= mu <= ls}")

# Tamano de muestra para error maximo E = 0.5 puntos (poblacion grande)
E = 0.5
z = stats.norm.ppf(1 - (1 - NC) / 2)
n_req = int(np.ceil((z * sigma / E) ** 2))
print(f"\nSigma={sigma:.2f}, Z={z:.3f}, E={E}: n = [(Z*sigma)/E]^2 = {n_req} lotes")
print("\nArchivos guardados en Output/")

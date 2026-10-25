"""Estadistica II - Regresion lineal simple: puntaje de catacion (Y) segun altitud (X)."""
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
select f.altitud_msnm as x, l.puntaje_catacion_scaa as y
from public_marts.fct_lotes_acopio l
join public_marts.dim_fincas f on f.id_finca = l.id_finca
where l.puntaje_catacion_scaa is not null and f.altitud_msnm is not null
"""
df = pd.read_sql(sql, engine).apply(pd.to_numeric)
x, y = df["x"].to_numpy(), df["y"].to_numpy()
n = len(x)

sx, sy = x.sum(), y.sum()
sxy, sx2 = (x * y).sum(), (x ** 2).sum()
b1 = (sxy - sx * sy / n) / (sx2 - sx ** 2 / n)
b0 = (sy - b1 * sx) / n
yhat = b0 + b1 * x
res = y - yhat
r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
r = np.sign(b1) * np.sqrt(r2)

s_e = np.sqrt((res ** 2).sum() / (n - 2))
se_b1 = s_e / np.sqrt(((x - x.mean()) ** 2).sum())
t = b1 / se_b1
tc = stats.t.ppf(1 - 0.05 / 2, n - 2)

print(f"n = {n}  (altitudes distintas: {df['x'].nunique()})")
print(f"Sum x={sx:.0f}  Sum y={sy:.1f}  Sum xy={sxy:.1f}  Sum x2={sx2:.0f}")
print(f"b1 = {b1:.5f}   b0 = {b0:.4f}")
print(f"Recta: y_hat = {b0:.4f} + {b1:.5f} x")
print(f"r = {r:.4f}   R2 = {r2:.4f}")
print(f"Prueba t pendiente: t = {t:.2f}  vs  t critico (0.025; {n-2}) = {tc:.3f}  -> "
      f"{'se rechaza H0: la altitud explica el puntaje' if abs(t) > tc else 'no se rechaza H0'}")
for alt in (1000, 1200, 1400):
    print(f"Prediccion con X={alt} msnm: y_hat = {b0 + b1 * alt:.2f} puntos")

fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
ax = axes[0]
ax.scatter(x, y, s=8, alpha=0.3)
xs = np.linspace(x.min(), x.max(), 100)
ax.plot(xs, b0 + b1 * xs, color="tab:red", label=f"y = {b0:.2f} + {b1:.4f}x\nR2 = {r2:.3f}")
ax.set_xlabel("Altitud (msnm)")
ax.set_ylabel("Puntaje SCAA")
ax.set_title("Puntaje vs altitud")
ax.legend()
axes[1].scatter(yhat, res, s=8, alpha=0.3)
axes[1].axhline(0, color="tab:red")
axes[1].set_xlabel("Valores ajustados")
axes[1].set_ylabel("Residuos")
axes[1].set_title("Residuos vs ajustados")
axes[2].hist(res, bins=30, edgecolor="white")
axes[2].set_xlabel("Residuos")
axes[2].set_title("Distribucion de residuos")
plt.tight_layout()
fig.savefig(SALIDA / "regresion_puntaje_altitud.png", dpi=150)
pd.DataFrame([[n, b0, b1, r, r2, t]], columns=["n", "b0", "b1", "r", "R2", "t_pendiente"]).to_csv(
    SALIDA / "regresion_puntaje_altitud.csv", index=False)
print("\nGuardado en Output/: regresion_puntaje_altitud.png y .csv")

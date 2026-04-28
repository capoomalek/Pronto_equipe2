import time
start_time = time.process_time()

import numpy as np
from numpy import loadtxt, linspace
from scipy.interpolate import griddata, RegularGridInterpolator
import matplotlib.pyplot as plt

# Chargement des coordonnées restituées (produites par Coord3D_objet.py)
X_mes = loadtxt('X_mes.txt')
Y_mes = loadtxt('Y_mes.txt')
Z_mes = loadtxt('Z_mes.txt')

print(f"Points restitués chargés : {len(X_mes)}")

# Chargement de l'objet réel (produit par Objet.py)
X_reel = loadtxt('X.txt')
Y_reel = loadtxt('Y.txt')
Z_reel_grid = loadtxt('Z.txt')

print(f"Objet réel : ZMaxi = {Z_reel_grid.max():.2f} mm")

# Interpolation de Z_reel aux positions (X_mes, Y_mes)
X_lin = X_reel[0, :]   # vecteur des colonnes (1ère ligne)
Y_lin = Y_reel[:, 0]   # vecteur des lignes   (1ère colonne)

interp_reel = RegularGridInterpolator(
    (Y_lin, X_lin), Z_reel_grid,
    method='linear',
    bounds_error=False,
    fill_value=np.nan
)
Z_reel = interp_reel(np.column_stack([Y_mes, X_mes]))

# Calcul de l'écart ΔZ = Z_mes - Z_reel
# On ne conserve que les points sur le bouclier (Z_reel > 0) et sans NaN
DeltaZ = Z_mes - Z_reel
masque = (~np.isnan(DeltaZ)) & (Z_reel > 0)

dZ = DeltaZ[masque]
Xv = X_mes[masque]
Yv = Y_mes[masque]

# Statistiques

print("\n--- Comparateur : écart ΔZ = Zmes - Zreel ---")
print(f"  Points valides    : {len(dZ)}")
print(f"  Écart moyen       : {dZ.mean():.3f} mm")
print(f"  Écart-type        : {dZ.std():.3f} mm")
print(f"  Écart max absolu  : {np.abs(dZ).max():.3f} mm")
print(f"  Écart min / max   : {dZ.min():.3f} / {dZ.max():.3f} mm")


xi = linspace(X_mes.min(), X_mes.max(), 500)
yi = linspace(Y_mes.min(), Y_mes.max(), 500)

Zi_dZ = griddata((Xv, Yv), dZ,
                 (xi[None, :], yi[:, None]), method='linear')

fig, ax = plt.subplots(figsize=(8, 6))

vmin = np.nanmin(Zi_dZ)
vmax = np.nanmax(Zi_dZ)

im = ax.imshow(Zi_dZ,
               extent=[xi.min(), xi.max(), yi.min(), yi.max()],
               origin='lower',
               cmap='YlOrBr',
               vmin=vmin,
               vmax=vmax,
               aspect='auto')

cbar = fig.colorbar(im, ax=ax)
cbar.set_label('ΔZ en mm')

ax.set_title('Ecart entre objet simulé et objet mesuré')
ax.set_xlabel('Xmes en mm')
ax.set_ylabel('Ymes en mm')

plt.tight_layout()
plt.savefig('Comparateur_result.png', dpi=150)
plt.show()

print(time.process_time() - start_time, "seconds")

import time
start_time = time.process_time()

import numpy as np
from numpy import loadtxt, pi, array, zeros, savetxt, linspace
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

# =============================================================================
# Chargement des fichiers générés par les scripts précédents
# =============================================================================

# Matrices de projection perspective (générées par franges_objet.py
# et franges_recepteur.py)
ME = loadtxt('ME.txt')   # 3×4  émetteur
MR = loadtxt('MR.txt')   # 3×4  récepteur

# Nombre de trames / ordre du code binaire
N = int(loadtxt('N.txt'))
P = 2**N   # nombre de franges

# Taille LCD (émetteur)
NbHE = int(loadtxt('NbHE.txt'))   # nombre de colonnes LCD

# Matrices de positions des côtés de franges
# (générées par Local_cotes_franges.py)
# Chaque matrice a la taille du récepteur zoomé (NbHRzoom × NbVRzoom)
PosiGauche = loadtxt('PosiGauche.txt')   # côté gauche : valeur = C (impair)
PosiDroite = loadtxt('PosiDroite.txt')   # côté droit  : valeur = C+1

# Coordonnées pixels du récepteur zoomé
uRzoom = loadtxt('uRzoom.txt')   # coordonnées lignes  (uR)
vRzoom = loadtxt('vRzoom.txt')   # coordonnées colonnes (vR)

print(f"N = {N}  →  P = {P} franges")
print(f"NbHE = {NbHE}")
print(f"Taille image récepteur zoom : {PosiGauche.shape}")

# =============================================================================
# §5.3  RECONSTRUCTION 3D  (Eq. 34 et 35)
#
# Eq. 34 : vEg = (NbHE / 2^N) * C + 1      (bord gauche de la frange C)
#           vEd = (NbHE / 2^N) * (C + 1)   (bord droit  de la frange C)
#
# Eq. 35 : résolution de  G · [X, Y, Z]^T = H
#
#   G = | m31R*uR - m11R   m32R*uR - m12R   m33R*uR - m13R |
#       | m31R*vR - m21R   m32R*vR - m22R   m33R*vR - m23R |
#       | m31E*vE - m21E   m32E*vE - m22E   m33E*vE - m23E |
#
#   H = | m14R - m34R*uR |
#       | m24R - m34R*vR |
#       | m24E - m34E*vE |
# =============================================================================

def reconstruct_point(uR, vR, vE):
    """
    Restitue les coordonnées 3D (X, Y, Z) d'un point de l'objet
    à partir de ses coordonnées récepteur (uR, vR) et de l'abscisse
    émetteur vE associée (bord gauche ou droit de la frange).

    Paramètres
    ----------
    uR : float  — ligne   du point sur la CCD (pixels)
    vR : float  — colonne du point sur la CCD (pixels)
    vE : float  — colonne du bord de frange sur le LCD (pixels)

    Retourne
    --------
    xyz : ndarray (3,)  — coordonnées [X, Y, Z] en mm,
          ou [nan, nan, nan] si le système est singulier.
    """
    G = np.array([
        [MR[2,0]*uR - MR[0,0],  MR[2,1]*uR - MR[0,1],  MR[2,2]*uR - MR[0,2]],
        [MR[2,0]*vR - MR[1,0],  MR[2,1]*vR - MR[1,1],  MR[2,2]*vR - MR[1,2]],
        [ME[2,0]*vE - ME[1,0],  ME[2,1]*vE - ME[1,1],  ME[2,2]*vE - ME[1,2]]
    ], dtype=float)

    H = np.array([
        MR[0,3] - MR[2,3]*uR,
        MR[1,3] - MR[2,3]*vR,
        ME[1,3] - ME[2,3]*vE
    ], dtype=float)

    try:
        return np.linalg.solve(G, H)
    except np.linalg.LinAlgError:
        return np.full(3, np.nan)


# =============================================================================
# Parcours de toutes les franges impaires C ∈ {1, 3, 5, …, 2^N - 1}
# Pour chaque frange C, les côtés gauche et droit sont repérés respectivement
# dans PosiGauche (valeur == C) et PosiDroite (valeur == C+1).
# =============================================================================

X_mes = []
Y_mes = []
Z_mes = []

NbHRzoom, NbVRzoom = PosiGauche.shape

for C in range(1, P, 2):   # franges impaires uniquement (§6.4.2)

    # Eq. 34 : abscisses LCD des bords de la frange C
    vEg = (NbHE / P) * C + 1        # bord gauche → vE = vEg
    vEd = (NbHE / P) * (C + 1)      # bord droit  → vE = vEd

    # ---- Côté gauche (PosiGauche == C) ----
    rows_g, cols_g = np.where(PosiGauche == C)
    for i in range(len(rows_g)):
        uR = float(uRzoom[rows_g[i], cols_g[i]])
        vR = float(vRzoom[rows_g[i], cols_g[i]])
        xyz = reconstruct_point(uR, vR, vEg)
        if not np.any(np.isnan(xyz)):
            X_mes.append(xyz[0])
            Y_mes.append(xyz[1])
            Z_mes.append(xyz[2])

    # ---- Côté droit (PosiDroite == C+1) ----
    rows_d, cols_d = np.where(PosiDroite == C + 1)
    for i in range(len(rows_d)):
        uR = float(uRzoom[rows_d[i], cols_d[i]])
        vR = float(vRzoom[rows_d[i], cols_d[i]])
        xyz = reconstruct_point(uR, vR, vEd)
        if not np.any(np.isnan(xyz)):
            X_mes.append(xyz[0])
            Y_mes.append(xyz[1])
            Z_mes.append(xyz[2])

X_mes = np.array(X_mes)
Y_mes = np.array(Y_mes)
Z_mes = np.array(Z_mes)

print(f"Points restitués : {len(X_mes)}")

# Sauvegarde des coordonnées restituées
savetxt('X_mes.txt', X_mes, fmt='%-7.6f')
savetxt('Y_mes.txt', Y_mes, fmt='%-7.6f')
savetxt('Z_mes.txt', Z_mes, fmt='%-7.6f')

# =============================================================================
# §6.4.3  AFFICHAGE
#
# Figure 6-10 : représentation 3D points par points
# Figure 6-11 : représentation en niveaux de gris
# =============================================================================

fig = plt.figure(figsize=(14, 6))

# ── Figure 6-10 : vue 3D points par points ───────────────────────────────────
ax1 = fig.add_subplot(121, projection='3d')
if len(X_mes) > 0:
    sc = ax1.scatter(X_mes, Y_mes, Z_mes,
                     c=Z_mes, cmap='viridis', s=1, alpha=0.6)
    fig.colorbar(sc, ax=ax1, shrink=0.5, pad=0.1, label='Zmes (mm)')
ax1.set_xlabel('Xmes (mm)')
ax1.set_ylabel('Ymes (mm)')
ax1.set_zlabel('Zmes (mm)')
ax1.set_title(f'Objet 3D restitué dans repère objet (N={N})\n'
              f'Représentation 3D points par points')

# ── Figure 6-11 : niveaux de gris (interpolation sur grille régulière) ───────
ax2 = fig.add_subplot(122)
if len(X_mes) > 0:
    xi = linspace(X_mes.min(), X_mes.max(), 600)
    yi = linspace(Y_mes.min(), Y_mes.max(), 600)
    Zi = griddata((X_mes, Y_mes), Z_mes,
                  (xi[None, :], yi[:, None]), method='linear')
    im = ax2.imshow(Zi,
                    extent=[xi.min(), xi.max(), yi.min(), yi.max()],
                    origin='lower', cmap='gray', aspect='auto')
    fig.colorbar(im, ax=ax2, label='Zmes (mm)')
ax2.set_xlabel('Xmes (mm)')
ax2.set_ylabel('Ymes (mm)')
ax2.set_title(f'Image3D - objet Zmes (mm)\n'
              f'Représentation en niveaux de gris (N={N})')

plt.tight_layout()
plt.savefig('Coord3D_Objet_result.png', dpi=150)
plt.show()

print(time.process_time() - start_time, "seconds")
import time
start_time = time.process_time()

import matplotlib.pyplot as plt
from skimage import io
import numpy as np
from numpy import loadtxt, zeros, savetxt, linspace
from scipy.interpolate import griddata

<<<<<<< HEAD
# 1. CHARGEMENT DES MATRICES ET DONNÉES

ME = loadtxt('ME_calib.txt') # Matrice Emetteur (Emetteur -> Objet)
MR = loadtxt('MR_calib.txt') # Matrice Récepteur (Récepteur -> Objet)

N = 5 
P = 2**N
NbHE = 1280 # Largeur de l'image projetée par le projecteur


PosiGauche = loadtxt('PosiGauche.txt')
PosiDroite = loadtxt('PosiDroite.txt')

=======



ME = loadtxt('ME.txt')  
MR = loadtxt('MR.txt')  


N = int(loadtxt('N.txt'))
P = 2**N   


NbHE = int(loadtxt('NbHE.txt'))   

# Matrices de positions des côtés de franges

PosiGauche = loadtxt('PosiGauche.txt')   
PosiDroite = loadtxt('PosiDroite.txt')   

# Coordonnées pixels du récepteur zoomé
uRzoom = loadtxt('uRzoom.txt')   
vRzoom = loadtxt('vRzoom.txt')   
>>>>>>> 98680d94e546950f74d75c3e925272284e6340d4

NbHR, NbVR = PosiGauche.shape

<<<<<<< HEAD
# Création automatique de la grille de coordonnées 
uR_coords, vR_coords = np.meshgrid(np.arange(NbVR), np.arange(NbHR))

print(f"Système calibré : N={N}, Résolution Caméra={NbVR}x{NbHR}")

# 2. FONCTION DE RECONSTRUCTION (Triangulation Eq. 35)

def reconstruct_point(uR, vR, vE):
    # Système G * [X, Y, Z] = H
=======


def reconstruct_point(uR, vR, vE):
    """
    Restitue les coordonnées 3D (X, Y, Z) d'un point de l'objet
    à partir de ses coordonnées récepteur (uR, vR) et de l'abscisse
    émetteur vE associée (bord gauche ou droit de la frange).

    """
>>>>>>> 98680d94e546950f74d75c3e925272284e6340d4
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

# 3. CALCUL DU NUAGE DE POINTS

<<<<<<< HEAD
X_mes, Y_mes, Z_mes = [], [], []
=======
>>>>>>> 98680d94e546950f74d75c3e925272284e6340d4

for C in range(1, P, 2):
    vEg = (NbHE / P) * C + 1
    vEd = (NbHE / P) * (C + 1)

<<<<<<< HEAD
    
=======
NbHRzoom, NbVRzoom = PosiGauche.shape

for C in range(1, P, 2):   

    # Eq. 34 : abscisses LCD des bords de la frange C
    vEg = (NbHE / P) * C + 1        
    vEd = (NbHE / P) * (C + 1) 

>>>>>>> 98680d94e546950f74d75c3e925272284e6340d4
    rows_g, cols_g = np.where(PosiGauche == C)
    for i in range(len(rows_g)):
        xyz = reconstruct_point(rows_g[i], cols_g[i], vEg)
        if not np.any(np.isnan(xyz)):
            X_mes.append(xyz[0]); Y_mes.append(xyz[1]); Z_mes.append(xyz[2])

<<<<<<< HEAD
    
=======
>>>>>>> 98680d94e546950f74d75c3e925272284e6340d4
    rows_d, cols_d = np.where(PosiDroite == C + 1)
    for i in range(len(rows_d)):
        xyz = reconstruct_point(rows_d[i], cols_d[i], vEd)
        if not np.any(np.isnan(xyz)):
            X_mes.append(xyz[0]); Y_mes.append(xyz[1]); Z_mes.append(xyz[2])

X_mes, Y_mes, Z_mes = np.array(X_mes), np.array(Y_mes), np.array(Z_mes)

# 4. AFFICHAGE ET SAUVEGARDE

fig = plt.figure(figsize=(12, 5))

<<<<<<< HEAD
# Vue 3D
ax1 = fig.add_subplot(121, projection='3d')
if len(X_mes) > 0:
    sc = ax1.scatter(X_mes, Y_mes, Z_mes, c=Z_mes, cmap='viridis', s=1)
    ax1.set_title("Restitution 3D")
    
# Vue Niveaux de gris
=======

fig = plt.figure(figsize=(14, 6))

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

>>>>>>> 98680d94e546950f74d75c3e925272284e6340d4
ax2 = fig.add_subplot(122)
if len(X_mes) > 10:
    xi = linspace(X_mes.min(), X_mes.max(), 400)
    yi = linspace(Y_mes.min(), Y_mes.max(), 400)
    Zi = griddata((X_mes, Y_mes), Z_mes, (xi[None, :], yi[:, None]), method='linear')
    ax2.imshow(Zi, extent=[xi.min(), xi.max(), yi.min(), yi.max()], cmap='gray', origin='lower')
    ax2.set_title("Carte de profondeur")

plt.show()
savetxt('Z_mes.txt', Z_mes)
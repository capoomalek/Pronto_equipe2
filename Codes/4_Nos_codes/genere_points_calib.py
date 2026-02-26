# -*- coding: utf-8 -*-
"""
Script utilitaire pour générer les fichiers de points de calibration.
Évite le pointage manuel en calculant les intersections théoriques du damier.
"""

import numpy as np

# 1. Paramètres physiques du damier sur l'objet (issus de Damier_recept.py)
LX = 995.0  # mm
LY = 622.0  # mm
p = 8       # nb carreaux horizontaux
q = 8       # nb carreaux verticaux

# 2. Calcul des coordonnées des coins internes (7x7 = 49 points)
dX = LX / p
dY = LY / q

X_corners = np.linspace(-LX/2 + dX, LX/2 - dX, p-1)
Y_corners = np.linspace(-LY/2 + dY, LY/2 - dY, q-1)

# Création de la grille 3D (Z = 0 car le damier est à plat)
X_grid, Y_grid = np.meshgrid(X_corners, Y_corners)
Z_grid = np.zeros_like(X_grid)

# On regroupe tout dans une matrice (N, 3)
pts_3d = np.column_stack((X_grid.flatten(), Y_grid.flatten(), Z_grid.flatten()))

# 3. Projection 2D sur la caméra
# On charge la matrice théorique pour simuler ce que "voit" la caméra
try:
    MR = np.loadtxt('MR.txt')
except OSError:
    print("Erreur : Fichier MR.txt introuvable. Exécutez Damier_recept.py d'abord.")
    exit(1)

pts_2d = np.zeros((len(pts_3d), 2))

# Application de la transformation perspective (coordonnées homogènes)
for i, (X, Y, Z) in enumerate(pts_3d):
    su = MR[0,0]*X + MR[0,1]*Y + MR[0,2]*Z + MR[0,3]
    sv = MR[1,0]*X + MR[1,1]*Y + MR[1,2]*Z + MR[1,3]
    s  = MR[2,0]*X + MR[2,1]*Y + MR[2,2]*Z + MR[2,3]
    
    # Division par le facteur d'échelle s
    pts_2d[i, 0] = su / s
    pts_2d[i, 1] = sv / s

# 4. Sauvegarde des fichiers finaux
np.savetxt('points_3D.txt', pts_3d, fmt='%.4f')
np.savetxt('points_2D_recepteur.txt', pts_2d, fmt='%.4f')

print("Succès ! Les fichiers points_3D.txt et points_2D_recepteur.txt ont été générés.")
print(f"Nombre de points de calibration créés : {len(pts_3d)}")
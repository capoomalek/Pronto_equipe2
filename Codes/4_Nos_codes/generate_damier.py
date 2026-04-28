# -*- coding: utf-8 -*-
"""
Générateur de Mire Damier pour l'émetteur (Projecteur)
Conforme à la Figure 7-3 du document (Eq. 48)
Résolution : 1280 x 800 (Damier Rouge/Noir avec 12 points marqués)
"""

import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. PARAMÈTRES DE LA MIRE (Tirés du PDF)
# ==========================================
NbVE = 800   # Hauteur en pixels (axe uE)
NbHE = 1280  # Largeur en pixels (axe vE)
q = 8        # Nombre de divisions verticales
p = 8        # Nombre de divisions horizontales

# ==========================================
# 2. GÉNÉRATION DU DAMIER (Équation 48)
# ==========================================
# Création des grilles de coordonnées
v, u = np.meshgrid(np.arange(NbHE), np.arange(NbVE))

# Calcul selon l'équation 48 du PDF
valeurs = np.sin(np.pi * q * u / NbVE) * np.sin(np.pi * p * v / NbHE)

# Création de l'image RGB (Rouge et Noir)
image_mire = np.zeros((NbVE, NbHE, 3), dtype=np.uint8)
image_mire[valeurs < 0] = [255, 0, 0]  # Rouge (si < 0)
image_mire[valeurs >= 0] = [0, 0, 0]   # Noir  (si >= 0)

# ==========================================
# 3. DESSIN DES MARQUEURS (Cercles bleus, Texte jaune)
# ==========================================
# Configuration de la figure Matplotlib pour sauvegarder SANS bordures blanches
fig = plt.figure(figsize=(NbHE/100, NbVE/100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis('off') # On cache les axes
ax.imshow(image_mire)

# Coordonnées des 12 points d'après le tableau (Page 37)
# uE = axe vertical (Lignes) | vE = axe horizontal (Colonnes)
pts_uE = [100, 400, 700, 100, 400, 700, 100, 400, 700,  100,  400,  700]
pts_vE = [320, 320, 320, 640, 640, 640, 960, 960, 960, 1280, 1280, 1280]

for i in range(12):
    y = pts_uE[i]
    x = pts_vE[i]
    
    # 1. Dessin du cercle bleu ciel (vide au centre)
    ax.plot(x, y, 'o', markeredgecolor='#007FFF', markerfacecolor='none', 
            markersize=14, markeredgewidth=2)
    
    # 2. Dessin du texte en jaune (légèrement décalé pour ne pas cacher la croix)
    # Décalage spécifique pour la dernière colonne afin que le texte ne sorte pas de l'image
    offset_x = 15 if x < 1280 else -60
    ax.text(x + offset_x, y - 15, f'mE{i+1}', color='yellow', fontsize=14, fontweight='bold')

# ==========================================
# 4. SAUVEGARDE ET AFFICHAGE DES COORDONNÉES
# ==========================================
nom_fichier = 'Mire_Emetteur_Damier.png'
plt.savefig(nom_fichier, dpi=100)
print(f"✅ Mire générée avec succès : {nom_fichier}")
print(f"   Dimensions : {NbHE}x{NbVE} pixels")

print("\n📍 COORDONNÉES DES POINTS DE CALIBRATION ÉMETTEUR (pts_2d_E) :")
print("---------------------------------------------------------------")
print("  Point  |  uE (Ligne)  |  vE (Colonne) ")
print("---------------------------------------------------------------")
for i in range(12):
    print(f"  mE{i+1:<2}  |     {pts_uE[i]:<6} |     {pts_vE[i]:<6}")
print("---------------------------------------------------------------")
print("Ces valeurs sont prêtes à être copiées dans votre script calib_emetteur.py ! (Rappel : z=0 et z=100 utilisent les mêmes pixels)")
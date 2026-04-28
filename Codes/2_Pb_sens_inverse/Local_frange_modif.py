"""
Created on Mon Nov 20 08:28:41 2017
MAJ octobre 2023 — seuillage adaptatif ajouté
@author: Elisabeth Lys
"""
# %%
import time
start_time = time.process_time()  # début mesure temps d'exécution

import matplotlib.pyplot as plt
from skimage import io
from skimage import filters
from skimage.morphology import disk
import numpy as np
from numpy import empty, zeros, ones, savetxt
from scipy.ndimage import gaussian_filter

# ── Chargement nombre d'images ────────────────────────────
N = 5

NbHRzoom = 1080
NbVRzoom  = 1920

# On crée la matrice IRzoom à la bonne taille
IRzoom     = zeros((NbHRzoom, NbVRzoom, N))
Posiglobal = zeros((NbHRzoom, NbVRzoom))
PosiGauche = zeros((NbHRzoom, NbVRzoom))
PosiDroite = zeros((NbHRzoom, NbVRzoom))

# ── Paramètres du seuillage adaptatif ────────────────────
# sigma_fond  : rayon du filtre gaussien pour estimer l'éclairage de fond
#               Augmenter si les franges sont larges (ex: 80-100)
#               Diminuer si l'éclairage varie très localement (ex: 30)
sigma_fond  = 50

# thresh_rel  : seuil sur l'image normalisée (valeurs autour de 1.0)
#               Augmenter (ex: 0.55) si trop de bruit détecté
#               Diminuer  (ex: 0.35) si des franges sont manquantes
thresh_rel  = 0.45

eps         = 1e-6   # évite toute division par zéro

# ── Chargement des images et binarisation adaptative ─────
for k in range(N):
    Nom = f'IRZoom{str(k + 1)}.bmp'

    img = io.imread(Nom)

    # Extraction du canal en float64
    if img.ndim == 3:
        canal = img[:, :, 0].astype(np.float64)
    else:
        canal = img.astype(np.float64)

    # Estimation du fond (éclairage basse fréquence)
    # Le filtre gaussien large lisse les franges et ne garde
    # que la variation lente de luminosité dans la scène
    fond = gaussian_filter(canal, sigma=sigma_fond)
    fond = np.clip(fond, eps, None)   # sécurité : évite fond = 0

    # Normalisation locale : supprime la non-uniformité d'éclairage
    # Dans une zone sombre, fond est bas ET les franges sont basses,
    # donc leur rapport reste ~constant partout dans l'image
    canal_norm = canal / fond         # valeurs autour de 1.0 sur fond
                                      # les franges brillantes donnent > 1

    # Seuillage relatif → binaire 0 / 1
    IRzoom[:, :, k] = (canal_norm > thresh_rel).astype(np.float64)

# Libération mémoire
Nom  = None
fond = None

# ── Localisation de la frange C ───────────────────────────

# Initialisation des variables LClogic et LC
LC_num   = empty((NbHRzoom, NbVRzoom))
LClogic  = ones((NbHRzoom, NbVRzoom), dtype=bool)
LC       = zeros((NbHRzoom, NbVRzoom))

for C in range(1, 2**N + 1, 2):

    # Numéro en base binaire de la frange à localiser
    Cbin = np.binary_repr(C, N)

    # Transformation en liste d'entiers pour accès élément par élément
    tabCbin = list(map(int, Cbin))

    # Localisation de la frange C impaire :
    # on cherche les pixels dont le code binaire (sur les N images)
    # correspond exactement à tabCbin
    LClogic = IRzoom[:, :, 0] == tabCbin[0]
    for l in range(1, N):
        LClogic = LClogic & (IRzoom[:, :, l] == tabCbin[l])

    # Matrice de localisation numérique (True → 1, False → 0)
    LC = LClogic * 1
    del LClogic

    # Filtrage médian : nettoie les petites imperfections résiduelles
    # disk(5) = élément structurant circulaire de rayon 5 px
    LC = filters.median(np.uint8(LC), disk(5))

    # Extraction des bords gauche et droit de chaque frange, ligne par ligne
    for i in range(NbHRzoom):
        p0 = np.nonzero(LC[i, :] == 1)[0]
        if len(p0) > 0:
            aG = p0[0]    # premier pixel allumé → bord gauche de la frange
            aD = p0[-1]   # dernier pixel allumé  → bord droit de la frange

            # Positions globales (bord G = C impair, bord D = C+1 pair)
            Posiglobal[i, aG] = C
            Posiglobal[i, aD] = C + 1

            # Positions gauche et droite séparées
            PosiGauche[i, aG] = C
            PosiDroite[i, aD] = C + 1

# ── Enregistrement des matrices de positions ─────────────
savetxt('PosiGauche.txt', PosiGauche, fmt='%-7.0f')
savetxt('PosiDroite.txt', PosiDroite, fmt='%-7.0f')
savetxt('Posiglobal.txt', Posiglobal, fmt='%-7.0f')
savetxt('LC_num.txt',     LC_num,     fmt='%-7.0f')

# ── Inversion de contraste pour l'affichage ───────────────
InvPosiglobal = 1. - Posiglobal

# ── Enregistrement de l'image des côtés de franges ───────
couleur_cotes = np.asarray([255, 255, 255])   # blanc intensité maximale
B = zeros((NbHRzoom, NbVRzoom, 3))
A = 'Cotes_franges.bmp'

B[:, :, 0] = couleur_cotes[0] * InvPosiglobal
B[:, :, 1] = couleur_cotes[1] * InvPosiglobal
B[:, :, 2] = couleur_cotes[2] * InvPosiglobal
B = B.astype(np.uint8)
io.imsave(A, B)

# ── Affichages ────────────────────────────────────────────
plt.figure()
plt.imshow(PosiGauche, cmap=plt.get_cmap('gray'))
plt.title('Position Gauche')

plt.figure()
plt.imshow(PosiDroite, cmap=plt.get_cmap('gray'))
plt.title('Position Droite')

plt.figure()
plt.imshow(Posiglobal, cmap=plt.get_cmap('gray'))
plt.title('Position Globale')

# Affichage de l'image enregistrée des côtés de franges
plt.figure()
plt.imshow(B[:, :, 1], cmap=plt.get_cmap('gray'))
plt.title('Image des cotés des franges')
plt.xlabel('vRzoom pixels')
plt.ylabel('uRzoom pixels')

print(time.process_time() - start_time, "seconds")
# %%
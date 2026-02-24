import numpy as np

def calcul_coordonnees_3D():
    print("1. Chargement des matrices de calibration...")
    ME = np.loadtxt('ME.txt')
    MR = np.loadtxt('MR.txt')
    
    print("2. Chargement des axes et des données de franges...")
    uR_axe = np.loadtxt('uRzoomvect.txt') # 1500 pixels
    vR_axe = np.loadtxt('vRzoomvect.txt') # 1080 pixels
    
    # On charge le fichier avec les positions de l'émetteur
    # Vous pouvez changer pour 'posiglobal.txt' si vous voulez combiner droite/gauche
    vE_matrice = np.loadtxt('Posiglobal.txt') 
    
    print("3. Création de la grille et application du masque...")
    # Création de la grille 2D (1080x1500) pour la caméra
    U, V = np.meshgrid(uR_axe, vR_axe)
    
    # --- LE MASQUE DE FILTRAGE ---
    # On ne garde QUE les pixels où une frange a été détectée (vE > 0)
    masque_valide = vE_matrice > 0
    
    # Extraction des points valides uniquement (aplatit automatiquement en vecteurs 1D)
    uR_valide = U[masque_valide]
    vR_valide = V[masque_valide]
    vE_valide = vE_matrice[masque_valide]
    
    N_points_valides = len(uR_valide)
    print(f"-> {N_points_valides} points utiles trouvés sur les 1 620 000 pixels !")
    print("4. Résolution du système d'équations...")

    # Initialisation de G (N_points, 3, 3) et H (N_points, 3)
    G = np.zeros((N_points_valides, 3, 3))
    H = np.zeros((N_points_valides, 3))
    
    # Remplissage de la matrice G
    G[:, 0, 0] = MR[2, 0] * uR_valide - MR[0, 0]
    G[:, 0, 1] = MR[2, 1] * uR_valide - MR[0, 1]
    G[:, 0, 2] = MR[2, 2] * uR_valide - MR[0, 2]
    
    G[:, 1, 0] = MR[2, 0] * vR_valide - MR[1, 0]
    G[:, 1, 1] = MR[2, 1] * vR_valide - MR[1, 1]
    G[:, 1, 2] = MR[2, 2] * vR_valide - MR[1, 2]
    
    G[:, 2, 0] = ME[2, 0] * vE_valide - ME[1, 0]
    G[:, 2, 1] = ME[2, 1] * vE_valide - ME[1, 1]
    G[:, 2, 2] = ME[2, 2] * vE_valide - ME[1, 2]

    # Remplissage du vecteur H
    H[:, 0] = MR[0, 3] - MR[2, 3] * uR_valide
    H[:, 1] = MR[1, 3] - MR[2, 3] * vR_valide
    H[:, 2] = ME[1, 3] - ME[2, 3] * vE_valide

    # Résolution
    try:
        # L'astuce est ici : on ajoute une dimension avec np.newaxis
        # H passe de (25902, 3) à (25902, 3, 1)
        P = np.linalg.solve(G, H[..., np.newaxis])
    except np.linalg.LinAlgError:
        print("Erreur : Impossible de résoudre le système pour certains points.")
        return

    print("5. Reconstitution des images 3D et sauvegarde...")
    # On crée des matrices vides (remplies de "Not a Number") de la taille de l'image (1080x1500)
    X_complet = np.full(vE_matrice.shape, np.nan)
    Y_complet = np.full(vE_matrice.shape, np.nan)
    Z_complet = np.full(vE_matrice.shape, np.nan)

    # P est maintenant de dimension (N, 3, 1), on va donc lire P[:, 0, 0]
    X_complet[masque_valide] = P[:, 0, 0]
    Y_complet[masque_valide] = P[:, 1, 0]
    Z_complet[masque_valide] = P[:, 2, 0]

    # Sauvegarde
    np.savetxt('X_obj.txt', X_complet, fmt='%.6f', delimiter='\t')
    np.savetxt('Y_obj.txt', Y_complet, fmt='%.6f', delimiter='\t')
    np.savetxt('Z_obj.txt', Z_complet, fmt='%.6f', delimiter='\t')
    
    print("Succès ! Fichiers générés avec le fond ignoré.")

if __name__ == '__main__':
    calcul_coordonnees_3D()
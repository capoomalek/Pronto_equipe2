import numpy as np
import matplotlib.pyplot as plt

def calcul_et_affichage_3D():
    print("1. Chargement des matrices de calibration...")
    ME = np.loadtxt('ME.txt')
    MR = np.loadtxt('MR.txt')
    
    # --- LA BONNE MÉTHODE (Eq. 36) ---
    # Normalisation des matrices (on divise par le coefficient m34, situé en [2, 3])
    MEN = ME / ME[2, 3]
    MRN = MR / MR[2, 3]
    
    print("2. Chargement des axes et des données de franges...")
    # L'axe appelé "uR_axe" fait 1500 pixels (Horizontal) et "vR_axe" fait 1080 pixels (Vertical)
    Axe_H = np.loadtxt('urzoomvect.txt') 
    Axe_V = np.loadtxt('vrzoomvect.txt') 
    vE_matrice = np.loadtxt('Posiglobal.txt') 
    
    print("3. Création de la grille et application des corrections...")
    Grille_H, Grille_V = np.meshgrid(Axe_H, Axe_V)
    
    # On ne garde que les pixels où une frange a été détectée (vE > 0)
    masque_valide = vE_matrice > 0
    
    # --- LES CORRECTIONS GEOMETRIQUES SONT ICI ---
    OFFSET_CAMERA = 230      # Recentrage du zoom horizontal (1920 - 1500) / 2
    FACTEUR_PROJECTEUR = 40  # Conversion du numéro de frange en pixel LCD (1280 pixels / 32 franges)
    
    # D'après la théorie du PDF : uR est l'axe VERTICAL et vR est l'axe HORIZONTAL
    uR_valide = Grille_V[masque_valide] 
    vR_valide = Grille_H[masque_valide] + OFFSET_CAMERA
    vE_valide = vE_matrice[masque_valide] * FACTEUR_PROJECTEUR
    
    N_points = len(uR_valide)
    print(f"-> {N_points} points utiles isolés pour le calcul.")
    print("4. Résolution du système d'équations (Eq. 36)...")

    # Initialisation de GN et HN
    GN = np.zeros((N_points, 3, 3))
    HN = np.zeros((N_points, 3))
    
    # Remplissage de la matrice GN (Eq. 36)
    GN[:, 0, 0] = MRN[2, 0] * uR_valide - MRN[0, 0]
    GN[:, 0, 1] = MRN[2, 1] * uR_valide - MRN[0, 1]
    GN[:, 0, 2] = MRN[2, 2] * uR_valide - MRN[0, 2]
    
    GN[:, 1, 0] = MRN[2, 0] * vR_valide - MRN[1, 0]
    GN[:, 1, 1] = MRN[2, 1] * vR_valide - MRN[1, 1]
    GN[:, 1, 2] = MRN[2, 2] * vR_valide - MRN[1, 2]
    
    GN[:, 2, 0] = MEN[2, 0] * vE_valide - MEN[1, 0]
    GN[:, 2, 1] = MEN[2, 1] * vE_valide - MEN[1, 1]
    GN[:, 2, 2] = MEN[2, 2] * vE_valide - MEN[1, 2]

    # Remplissage du vecteur HN (Eq. 36)
    HN[:, 0] = MRN[0, 3] - uR_valide
    HN[:, 1] = MRN[1, 3] - vR_valide
    HN[:, 2] = MEN[1, 3] - vE_valide

    # On transforme HN pour autoriser le calcul matriciel par lot avec NumPy
    HN = HN[..., np.newaxis]

    # Résolution GN * P = HN
    try:
        P = np.linalg.solve(GN, HN)
    except np.linalg.LinAlgError:
        print("Erreur : Impossible de résoudre le système (Matrice singulière).")
        return

    print("5. Reconstitution de l'image 3D et sauvegarde...")
    X_complet = np.full(vE_matrice.shape, np.nan)
    Y_complet = np.full(vE_matrice.shape, np.nan)
    Z_complet = np.full(vE_matrice.shape, np.nan)

    # Extraction des coordonnées pour la sauvegarde
    X_complet[masque_valide] = P[:, 0, 0]
    Y_complet[masque_valide] = P[:, 1, 0]
    Z_complet[masque_valide] = P[:, 2, 0]

    np.savetxt('X_obj.txt', X_complet, fmt='%.6f', delimiter='\t')
    np.savetxt('Y_obj.txt', Y_complet, fmt='%.6f', delimiter='\t')
    np.savetxt('Z_obj.txt', Z_complet, fmt='%.6f', delimiter='\t')
    
    print("Succès ! Fichiers générés. Lancement de la vue 3D...")

    # ==========================================
    # 6. AFFICHAGE 3D INTERACTIF
    # ==========================================
    
    # On récupère directement les listes de points calculés pour l'affichage
    X_objet = P[:, 0, 0]
    Y_objet = P[:, 1, 0]
    Z_objet = P[:, 2, 0]

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    # Dessin du nuage (coloré selon Z)
    nuage = ax.scatter(X_objet, Y_objet, Z_objet, color='steelblue', s=1.3)
    

    ax.set_xlabel('Axe X (mm)')
    ax.set_ylabel('Axe Y (mm)')
    ax.set_zlabel('Axe Z (mm)')
    ax.set_title("Reconstruction 3D de l'objet")

    # ASTUCE 1 : Forcer les vraies proportions physiques (évite l'effet plat)
    ax.set_box_aspect((np.ptp(X_objet), np.ptp(Y_objet), np.ptp(Z_objet)))

    # ASTUCE 2 : Orienter la caméra initiale pour bien voir le relief
    ax.view_init(elev=35, azim=-45)

    plt.show()

if __name__ == '__main__':
    calcul_et_affichage_3D()
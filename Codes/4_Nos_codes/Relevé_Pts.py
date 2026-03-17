import matplotlib.pyplot as plt
from skimage import io
import numpy as np

# --- 1. Remplace par le nom de TA photo ---
nom_image = 'photo_damier.jpg' 

try:
    image = io.imread(nom_image)
except FileNotFoundError:
    print(f"Erreur : L'image '{nom_image}' est introuvable. Mets la bonne photo dans le dossier !")
    exit()

# --- 2. Affichage interactif ---
plt.figure(figsize=(10, 8))
plt.imshow(image)
plt.title("CLIC GAUCHE = Ajouter un point | CLIC DROIT = Annuler le dernier | ENTRÉE = Terminer")

print("La fenêtre va s'ouvrir. Clique sur tes points DANS L'ORDRE.")
print("Appuie sur la touche 'Entrée' de ton clavier quand tu as fini.")

# ginput permet de cliquer sur l'image et de récupérer les (u, v)
# n=-1 permet de cliquer autant de fois que tu veux. timeout=0 désactive le chronomètre.
points_cliques = plt.ginput(n=-1, timeout=0) 
plt.close()

# --- 3. Formatage pour ton code de calibration ---
if points_cliques:
    print("\n" + "="*50)
    print("🎯 SUPER ! Voici ton code prêt à être copié-collé dans calib_recepteur.py :")
    print("="*50 + "\n")
    
    print("pts_2d = np.array([")
    for u, v in points_cliques:
        # On arrondit à 1 chiffre après la virgule pour que ce soit propre
        print(f"    [{u:.1f}, {v:.1f}],")
    print("], dtype=float)")
    
    # Bonus : Sauvegarde dans un fichier texte au cas où
    np.savetxt('mes_points_cliques.txt', points_cliques, fmt='%.1f')
    print("\n(Ces points ont aussi été sauvegardés dans 'mes_points_cliques.txt')")
else:
    print("\nTu n'as cliqué sur aucun point !")
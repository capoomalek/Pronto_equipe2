import numpy as np
import matplotlib.pyplot as plt

def visualiser_3D():
    print("Chargement des fichiers X_obj.txt, Y_obj.txt, Z_obj.txt...")
    X = np.loadtxt('X_obj.txt')
    Y = np.loadtxt('Y_obj.txt')
    Z = np.loadtxt('Z_obj.txt')

    print("Préparation du nuage de points...")
    # 1. On aplatit les matrices en listes 1D
    X_flat = X.flatten()
    Y_flat = Y.flatten()
    Z_flat = Z.flatten()

    # 2. Le masque magique : on repère toutes les cases qui NE SONT PAS des "nan"
    masque_valide = ~np.isnan(Z_flat)

    # 3. On extrait uniquement les points de l'objet (les ~25 900 points)
    X_objet = X_flat[masque_valide]
    Y_objet = Y_flat[masque_valide]
    Z_objet = Z_flat[masque_valide]

    print(f"Affichage interactif de {len(Z_objet)} points en cours...")

    # 4. Création de la fenêtre 3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 5. Dessin du nuage de points (Scatter plot)
    # s=1 : taille des points (très fins)
    # c=Z_objet : colore les points selon leur profondeur Z (magnifique effet visuel)
    # cmap='viridis' : palette de couleurs allant du violet (profond) au jaune (proche)
    nuage = ax.scatter(X_objet, Y_objet, Z_objet, c=Z_objet, cmap='viridis', s=1)

    # Ajout d'une échelle de couleurs sur le côté
    barre_couleur = fig.colorbar(nuage, ax=ax, shrink=0.5, aspect=10)
    barre_couleur.set_label('Profondeur Z (mm)')

    # Légendes des axes
    ax.set_xlabel('Axe X (mm)')
    ax.set_ylabel('Axe Y (mm)')
    ax.set_zlabel('Axe Z (mm)')
    ax.set_title("Reconstruction 3D de l'objet")

    
    # ax.invert_zaxis() 

    # Rendu final
    plt.show()

if __name__ == '__main__':
    visualiser_3D()
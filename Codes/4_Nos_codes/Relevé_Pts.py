import matplotlib.pyplot as plt
from skimage import io
import numpy as np

# --- CONFIGURATION ---
nom_image = 'photo_damier.bmp'
Z_plan = 0  # Mettre 0 ou 100 selon la photo

labels_points = ['M1 (haut-gauche)', 'M2 (milieu-gauche)', 'M3 (bas-gauche)',
                 'M4 (haut-centre)',  'M5 (centre)',        'M6 (bas-centre)',
                 'M7 (haut-droite)', 'M8 (milieu-droite)', 'M9 (bas-droite)']

# Coordonnées 3D correspondantes (à adapter si votre mire a des dimensions différentes)
pts_3d_ref = np.array([
    [-497.5,  234, Z_plan],
    [-497.5,    0, Z_plan],
    [-497.5, -234, Z_plan],
    [     0,  311, Z_plan],
    [     0,    0, Z_plan],
    [     0, -311, Z_plan],
    [ 497.5,  234, Z_plan],
    [ 497.5,    0, Z_plan],
    [ 497.5, -234, Z_plan],
])

# --- CHARGEMENT IMAGE ---
image = io.imread(nom_image)
fig, ax = plt.subplots(figsize=(14, 9))
ax.imshow(image)

points_cliques = []
markers = []

def on_click(event):
    if event.inaxes != ax:
        return
    if event.button == 1:  # clic gauche
        idx = len(points_cliques)
        if idx >= 9:
            print("9 points déjà cliqués ! Appuie sur Entrée pour terminer.")
            return
        u, v = event.xdata, event.ydata
        points_cliques.append([u, v])
        # Affiche le marqueur et le label sur l'image
        m = ax.plot(u, v, 'r+', markersize=15, markeredgewidth=2)[0]
        t = ax.text(u+10, v-10, labels_points[idx], color='yellow',
                    fontsize=9, fontweight='bold')
        markers.append((m, t))
        ax.set_title(f"Point {idx+1}/9 cliqué : {labels_points[idx]} → ({u:.1f}, {v:.1f})\n"
                     f"Prochain : {labels_points[idx+1] if idx < 8 else 'TERMINÉ — appuie sur Entrée'}",
                     color='white')
        fig.canvas.draw()
        print(f"  ✓ {labels_points[idx]} : u={u:.1f}, v={v:.1f}")

    elif event.button == 3:  # clic droit = annuler dernier
        if points_cliques:
            points_cliques.pop()
            m, t = markers.pop()
            m.remove()
            t.remove()
            idx = len(points_cliques)
            ax.set_title(f"Annulé. Cliquez maintenant : {labels_points[idx]}", color='orange')
            fig.canvas.draw()
            print(f"  ✗ Dernier point annulé.")

def on_key(event):
    if event.key == 'enter':
        plt.close()

fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('key_press_event', on_key)

ax.set_facecolor('black')
fig.patch.set_facecolor('#1e1e1e')
ax.set_title(f"Cliquez sur : {labels_points[0]}", color='white', fontsize=11)
print("\nOrdre de clic attendu :")
for i, l in enumerate(labels_points):
    print(f"  {i+1}. {l}")
print("\nClic GAUCHE = pointer | Clic DROIT = annuler | ENTRÉE = valider\n")
plt.tight_layout()
plt.show()

# --- RÉSULTATS ---
if len(points_cliques) == 9:
    pts_2d = np.array(points_cliques)
    print("\n" + "="*55)
    print("✅ pts_2d pour Z =", Z_plan, "mm :")
    print("pts_2d = np.array([")
    for p in pts_2d:
        print(f"    [{p[0]:.1f}, {p[1]:.1f}],")
    print("], dtype=float)")
    np.savetxt(f'pts_2d_Z{Z_plan}.txt', pts_2d, fmt='%.1f')
    print(f"\nSauvegardé dans pts_2d_Z{Z_plan}.txt")

    # Vérification visuelle : affiche les paires 3D/2D
    print("\nVérification des correspondances 3D ↔ 2D :")
    print(f"{'Point':<6} {'X':>8} {'Y':>8} {'Z':>6}  |  {'uR':>8} {'vR':>8}")
    print("-" * 50)
    for i, (p3, p2) in enumerate(zip(pts_3d_ref, pts_2d)):
        print(f"M{i+1:<5} {p3[0]:>8.1f} {p3[1]:>8.1f} {p3[2]:>6.0f}  |  {p2[0]:>8.1f} {p2[1]:>8.1f}")
else:
    print(f"\n⚠️  Attention : {len(points_cliques)}/9 points cliqués. Recommencez.")
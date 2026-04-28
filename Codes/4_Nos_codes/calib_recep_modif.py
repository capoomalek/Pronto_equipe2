# -*- coding: utf-8 -*-
"""
CALIBRATION RECEPTEUR - Tout en un
1. Clic sur la photo → coordonnées pixels (uR, vR)
2. Saisie des coordonnées réelles (X, Y, Z) en mm
3. Calibration automatique → MRNmes + paramètres
"""

import numpy as np
from numpy.linalg import lstsq, norm
from scipy.optimize import fmin
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from skimage import io
import time

# ============================================================
#  PARAMÈTRES À MODIFIER
# ============================================================
NOM_IMAGE   = 'damier1.png'   # nom de ta photo
NB_POINTS   = 9                    # points par plan (min 6)
NB_PLANS    = 2                    # nombre de hauteurs Z (1 ou 2)
T3R_MES     = 1210.656             # distance O→récepteur en mm (à mesurer)
# ============================================================


# ============================================================
#  FONCTIONS DE CALIBRATION (Sécurisées mathématiquement)
# ============================================================

def calibration_faugeras_toscani(coords_3d, coords_2d):
    N = coords_3d.shape[0]
    A = np.zeros((2*N, 11))
    B = np.zeros((2*N, 1))
    for i in range(N):
        X, Y, Z = coords_3d[i]
        u, v    = coords_2d[i]
        A[2*i,   0:3]  = [X, Y, Z];  A[2*i,   3]     = 1
        A[2*i,   8:11] = [-u*X, -u*Y, -u*Z];  B[2*i,   0] = u
        A[2*i+1, 4:7]  = [X, Y, Z];  A[2*i+1, 7]     = 1
        A[2*i+1, 8:11] = [-v*X, -v*Y, -v*Z];  B[2*i+1, 0] = v
    x, _, _, _ = lstsq(A, B, rcond=None)
    
    M = np.zeros((3, 4))
    M[0,:] = [x[0,0], x[1,0], x[2,0], x[3,0]]
    M[1,:] = [x[4,0], x[5,0], x[6,0], x[7,0]]
    M[2,:] = [x[8,0], x[9,0], x[10,0], 1.0]
    return M

def extraction_parametres(M):
    rho  = 1.0 / norm(M[2, 0:3])
    u0   = (rho**2) * np.dot(M[0,0:3], M[2,0:3])
    v0   = (rho**2) * np.dot(M[1,0:3], M[2,0:3])
    
    # Sécurisation avec np.abs() pour absorber les imprécisions de clic pixel
    au   = -np.sqrt(np.abs((rho**2)*np.dot(M[0,0:3],M[0,0:3]) - u0**2))
    av   =  np.sqrt(np.abs((rho**2)*np.dot(M[1,0:3],M[1,0:3]) - v0**2))
    
    r3   = rho * M[2,0:3]
    r1   = (rho*M[0,0:3] - u0*r3) / au
    r2   = (rho*M[1,0:3] - v0*r3) / av
    R    = np.array([r1, r2, r3])
    
    t3   = rho * M[2,3]
    t1   = (rho*M[0,3] - u0*t3) / au
    t2   = (rho*M[1,3] - v0*t3) / av
    return u0, v0, au, av, R, t1, t2, t3

def matrice_rotation(angles):
    phi, theta, psi = angles
    phi_r, theta_r, psi_r = np.radians(phi), np.radians(theta), np.radians(psi)
    
    Rx = np.array([[1,0,0],[0,np.cos(phi_r),-np.sin(phi_r)],[0,np.sin(phi_r),np.cos(phi_r)]])
    Ry = np.array([[np.cos(theta_r),0,np.sin(theta_r)],[0,1,0],[-np.sin(theta_r),0,np.cos(theta_r)]])
    Rz = np.array([[np.cos(psi_r),-np.sin(psi_r),0],[np.sin(psi_r),np.cos(psi_r),0],[0,0,1]])
    
    return Rz @ Ry @ Rx

def cout_angles(angles, R_cible):
    return norm(matrice_rotation(angles) - R_cible)


# ============================================================
#  ÉTAPE 1 : SAISIE DES COORDONNÉES 3D RÉELLES
# ============================================================

def saisir_coordonnees_3d(nb_points, nb_plans):
    print("\n" + "="*60)
    print("  ÉTAPE 1 — Saisie des coordonnées 3D réelles")
    print("="*60)
    print(f"Entrez les coordonnées de {nb_points * nb_plans} points.")
    print("Format : X Y Z  (séparés par des espaces, en mm)")
    print("Exemple : -497.5 234 0")
    print("(Appuyez sur Entrée après chaque point)\n")

    pts_3d = []

    for plan in range(nb_plans):
        print(f"--- Plan {plan+1}/{nb_plans} ---")
        for i in range(nb_points):
            while True:
                try:
                    entree = input(f"  Point {plan*nb_points + i + 1:>2} "
                                   f"(plan {plan+1}, pt {i+1}) "
                                   f"[X Y Z] : ").strip()
                    valeurs = [float(v) for v in entree.split()]
                    if len(valeurs) != 3:
                        print("    ⚠️  Entrez exactement 3 valeurs : X Y Z")
                        continue
                    pts_3d.append(valeurs)
                    print(f"    ✓ X={valeurs[0]:.1f}, Y={valeurs[1]:.1f}, Z={valeurs[2]:.1f}")
                    break
                except ValueError:
                    print("    ⚠️  Valeurs invalides, recommencez.")
        print()

    return np.array(pts_3d, dtype=float)


# ============================================================
#  ÉTAPE 2 : CLIC SUR LA PHOTO → COORDONNÉES PIXELS
# ============================================================

def cliquer_points_photo(nom_image, pts_3d, nb_points, nb_plans):
    print("\n" + "="*60)
    print("  ÉTAPE 2 — Relevé des pixels sur la photo")
    print("="*60)

    try:
        image = io.imread(nom_image)
    except FileNotFoundError:
        print(f"❌ Image '{nom_image}' introuvable !")
        return None

    n_total = nb_points * nb_plans
    pts_2d  = []
    markers = []

    # Couleurs par plan pour distinguer visuellement
    couleurs_plan = ['red', 'lime', 'cyan', 'orange', 'magenta']

    fig, ax = plt.subplots(figsize=(16, 10))
    ax.imshow(image, cmap='gray' if image.ndim == 2 else None)
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('black')

    # Légende des plans
    legendes = [mpatches.Patch(color=couleurs_plan[p],
                               label=f'Plan {p+1} (Z={pts_3d[p*nb_points, 2]:.0f} mm)')
                for p in range(nb_plans)]
    ax.legend(handles=legendes, loc='upper right',
              facecolor='#333', labelcolor='white', fontsize=10)

    def update_titre():
        idx = len(pts_2d)
        if idx >= n_total:
            ax.set_title("✅ Tous les points cliqués ! Appuyez sur Entrée pour valider.",
                         color='lime', fontsize=12, fontweight='bold')
        else:
            plan_idx = idx // nb_points
            pt_idx   = idx  % nb_points
            X, Y, Z  = pts_3d[idx]
            couleur  = couleurs_plan[plan_idx % len(couleurs_plan)]
            ax.set_title(
                f"Cliquez sur le point {idx+1}/{n_total}  —  "
                f"Plan {plan_idx+1} | Point {pt_idx+1}  —  "
                f"X={X:.1f}  Y={Y:.1f}  Z={Z:.0f} mm\n"
                f"Clic GAUCHE = pointer | Clic DROIT = annuler dernier",
                color=couleur, fontsize=11)
        fig.canvas.draw()

    update_titre()

    def on_click(event):
        if event.inaxes != ax:
            return

        if event.button == 1:    # clic gauche → ajouter
            idx = len(pts_2d)
            if idx >= n_total:
                print("Tous les points sont relevés ! Appuyez sur Entrée.")
                return

            u, v     = event.xdata, event.ydata
            plan_idx = idx // nb_points
            couleur  = couleurs_plan[plan_idx % len(couleurs_plan)]
            X, Y, Z  = pts_3d[idx]

            pts_2d.append([u, v])

            # Affichage sur l'image
            m = ax.plot(u, v, '+', color=couleur,
                        markersize=18, markeredgewidth=2)[0]
            t = ax.text(u+10, v-10,
                        f"{idx+1}\n({X:.0f},{Y:.0f},{Z:.0f})",
                        color='yellow', fontsize=8, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2',
                                  facecolor='black', alpha=0.6))
            markers.append((m, t))
            update_titre()
            print(f"  ✓ Pt {idx+1:>2} : pixel=({u:.0f},{v:.0f})  "
                  f"↔  3D=({X:.1f},{Y:.1f},{Z:.0f})")

        elif event.button == 3:  # clic droit → annuler dernier
            if not pts_2d:
                return
            pts_2d.pop()
            m, t = markers.pop()
            m.remove(); t.remove()
            update_titre()
            idx = len(pts_2d)
            print(f"  ✗ Annulé. Revenez sur le point {idx+1} "
                  f"(3D={pts_3d[idx]})")

    def on_key(event):
        if event.key == 'enter':
            plt.close()

    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('key_press_event',    on_key)
    plt.tight_layout()
    plt.show()

    if len(pts_2d) != n_total:
        print(f"\n⚠️  Incomplet : {len(pts_2d)}/{n_total} points. Abandon.")
        return None

    return np.array(pts_2d, dtype=float)


# ============================================================
#  ÉTAPE 3 : VÉRIFICATION VISUELLE AVANT CALIBRATION
# ============================================================

def verifier_correspondances(pts_3d, pts_2d):
    print("\n" + "="*60)
    print("  ÉTAPE 3 — Vérification des correspondances")
    print("="*60)
    print(f"{'#':<3} {'X':>8} {'Y':>8} {'Z':>6}  │  {'uR':>7} {'vR':>7}")
    print("─"*45)
    for i in range(len(pts_3d)):
        print(f"{i+1:<3} {pts_3d[i,0]:>8.1f} {pts_3d[i,1]:>8.1f} "
              f"{pts_3d[i,2]:>6.0f}  │  "
              f"{pts_2d[i,0]:>7.1f} {pts_2d[i,1]:>7.1f}")

    print("\nCes correspondances sont-elles correctes ?")
    rep = input("  Tapez 'o' pour continuer, 'n' pour recommencer : ").strip().lower()
    return rep == 'o'


# ============================================================
#  ÉTAPE 4 : CALIBRATION + AFFICHAGE RÉSULTATS
# ============================================================

def lancer_calibration(pts_3d, pts_2d, t3r):
    print("\n" + "="*60)
    print("  ÉTAPE 4 — Calibration")
    print("="*60)
    t0 = time.process_time()

    # Calcul matrice normalisée
    MRNmes = calibration_faugeras_toscani(pts_3d, pts_2d)

    # Extraction paramètres
    u0, v0, au, av, R, t1, t2, t3 = extraction_parametres(MRNmes)

    # Angles d'Euler par optimisation
    angles_init   = [-90, -160, 0]
    angles_optim  = fmin(cout_angles, angles_init, args=(R,), disp=False)
    phi, theta, psi = angles_optim

    dt = time.process_time() - t0

    # Affichage
    print(f"\n  Durée : {dt:.3f} s\n")
    print("  ┌─ MRNmes ─────────────────────────────────────────┐")
    for row in MRNmes:
        print("  │  " + "  ".join(f"{v:>12.6e}" for v in row) + "  │")
    print("  └───────────────────────────────────────────────────┘")

    print(f"""
  Paramètres intrinsèques :
    u0    = {u0:.4f}  px
    v0    = {v0:.4f}  px
    αu    = {au:.4f}  px
    αv    = {av:.4f}  px

  Paramètres extrinsèques :
    t1    = {t1:.4f}  mm
    t2    = {t2:.4f}  mm
    t3    = {t3r:.3f}   mm  (valeur mesurée imposée)

  Matrice de rotation R :
    {R[0]}
    {R[1]}
    {R[2]}

  Angles d'Euler (optimisation fmin) :
    φ     = {phi:.4f} °
    θ     = {theta:.4f} °
    ψ     = {psi:.4f} °
""")

    # Erreur de reprojection (qualité de la calibration)
    erreurs = []
    for i in range(len(pts_3d)):
        XYZ1 = np.append(pts_3d[i], 1.0)
        proj  = MRNmes @ XYZ1
        u_rep = proj[0] / proj[2]
        v_rep = proj[1] / proj[2]
        err   = np.sqrt((u_rep - pts_2d[i,0])**2 + (v_rep - pts_2d[i,1])**2)
        erreurs.append(err)

    print(f"  Erreur de reprojection (qualité calibration) :")
    print(f"    Moyenne : {np.mean(erreurs):.2f} px")
    print(f"    Max     : {np.max(erreurs):.2f} px")
    print(f"    → Bon si < 2 px\n")

    return MRNmes


# ============================================================
#  PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    print("\n" + "█"*60)
    print("  CALIBRATION RÉCEPTEUR — Script tout-en-un")
    print("█"*60)

    # --- Étape 1 : coordonnées 3D ---
    pts_3d = saisir_coordonnees_3d(NB_POINTS, NB_PLANS)

    # --- Étape 2 : clic sur photo ---
    pts_2d = cliquer_points_photo(NOM_IMAGE, pts_3d, NB_POINTS, NB_PLANS)
    if pts_2d is None:
        exit()

    # --- Étape 3 : vérification ---
    if not verifier_correspondances(pts_3d, pts_2d):
        print("Recommencez le script.")
        exit()

    # --- Étape 4 : calibration ---
    MRNmes = lancer_calibration(pts_3d, pts_2d, T3R_MES)

    # --- Sauvegarde ---
    np.savetxt('MR.txt',      MRNmes,  fmt='%-7.9f')
    np.savetxt('pts_2d.txt',  pts_2d,  fmt='%.1f')
    np.savetxt('pts_3d.txt',  pts_3d,  fmt='%.1f')

    print("  Fichiers sauvegardés : MR.txt, pts_2d.txt, pts_3d.txt")
    print("\n" + "█"*60)
    print("  ✅  Calibration terminée !")
    print("█"*60 + "\n")
# -*- coding: utf-8 -*-
"""
Calibration de l'émetteur (Projecteur) - Avec VOS données expérimentales à 9 points/plan.
La matrice MRNmes reste celle du PDF, et les points 2D_R ont été formatés en [Ligne, Colonne].
"""

import time
import numpy as np
from scipy.optimize import fmin

def calculer_points_3d_exacts(MRN, pts_2d_R, Z_valeurs):
    """Calcule les points 3D exacts via l'Eq. 49 pour éviter les erreurs d'arrondi des tableaux."""
    N = len(pts_2d_R)
    pts_3d = np.zeros((N, 3))
    
    for i in range(N):
        uR, vR = pts_2d_R[i]
        Z = Z_valeurs[i]

        # Matrice V (2x2) de l'Eq 49
        V = np.array([
            [MRN[2, 0] * uR - MRN[0, 0], MRN[2, 1] * uR - MRN[0, 1]],
            [MRN[2, 0] * vR - MRN[1, 0], MRN[2, 1] * vR - MRN[1, 1]]
        ])
        
        # Vecteur W (2x1) de l'Eq 49 (rappel : m34NR = 1)
        W = np.array([
            (MRN[0, 2] - MRN[2, 2] * uR) * Z - uR + MRN[0, 3],
            (MRN[1, 2] - MRN[2, 2] * vR) * Z - vR + MRN[1, 3]
        ])

        XY = np.linalg.solve(V, W)
        pts_3d[i] = [XY[0], XY[1], Z]
        
    return pts_3d

def calibration_faugeras_toscani(coords_3d, coords_2d):
    """Calcule la matrice de projection normalisée MENmes (3x4)."""
    N = coords_3d.shape[0]
    A = np.zeros((2 * N, 11))
    B = np.zeros((2 * N, 1))

    for i in range(N):
        X, Y, Z = coords_3d[i]
        u, v = coords_2d[i]

        A[2 * i, 0:3] = [X, Y, Z]
        A[2 * i, 3] = 1
        A[2 * i, 8:11] = [-u * X, -u * Y, -u * Z]
        B[2 * i, 0] = u

        A[2 * i + 1, 4:7] = [X, Y, Z]
        A[2 * i + 1, 7] = 1
        A[2 * i + 1, 8:11] = [-v * X, -v * Y, -v * Z]
        B[2 * i + 1, 0] = v

    x, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)

    M = np.zeros((3, 4))
    M[0, :] = [x[0, 0], x[1, 0], x[2, 0], x[3, 0]]
    M[1, :] = [x[4, 0], x[5, 0], x[6, 0], x[7, 0]]
    M[2, :] = [x[8, 0], x[9, 0], x[10, 0], 1.0]

    return M

def extraction_parametres(M):
    """Extrait les paramètres de la matrice."""
    rho = 1.0 / np.linalg.norm(M[2, 0:3])

    u0 = (rho**2) * np.dot(M[0, 0:3], M[2, 0:3])
    v0 = (rho**2) * np.dot(M[1, 0:3], M[2, 0:3])

    alphau = -np.sqrt(np.abs((rho**2) * np.dot(M[0, 0:3], M[0, 0:3]) - u0**2))
    alphav = np.sqrt(np.abs((rho**2) * np.dot(M[1, 0:3], M[1, 0:3]) - v0**2))

    r3 = rho * M[2, 0:3]
    r1 = (rho * M[0, 0:3] - u0 * r3) / alphau
    r2 = (rho * M[1, 0:3] - v0 * r3) / alphav
    R = np.array([r1, r2, r3])

    t3 = rho * M[2, 3]
    t1 = (rho * M[0, 3] - u0 * t3) / alphau
    t2 = (rho * M[1, 3] - v0 * t3) / alphav

    return u0, v0, alphau, alphav, R, t1, t2, t3

def matrice_rotation_theorique(angles):
    """Génère la matrice de rotation avec la convention Z-Y-X du document."""
    phi, theta, psi = angles
    phi_r, theta_r, psi_r = np.radians(phi), np.radians(theta), np.radians(psi)
    
    # Assignation des angles aux bons axes selon la page 13 du PDF
    Rz = np.array([[np.cos(phi_r), -np.sin(phi_r), 0], [np.sin(phi_r), np.cos(phi_r), 0], [0, 0, 1]])
    Ry = np.array([[np.cos(theta_r), 0, np.sin(theta_r)], [0, 1, 0], [-np.sin(theta_r), 0, np.cos(theta_r)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(psi_r), -np.sin(psi_r)], [0, np.sin(psi_r), np.cos(psi_r)]])
    
    return Rz @ Ry @ Rx

def fonction_cout_angles(angles, R_cible):
    """Évalue l'écart (norme de Frobenius)."""
    R_calc = matrice_rotation_theorique(angles)
    return np.linalg.norm(R_calc - R_cible)

if __name__ == "__main__":
    start_time = time.process_time()
    
    # ---------------------------------------------------------------------
    # 1. DONNÉES EXACTES
    # ---------------------------------------------------------------------
    
    # La matrice du récepteur extraite du PDF (Page 35) conservée selon votre choix
    MRNmes = np.array([
        [ 1.56492678e-01, -1.36595739e+00, -4.21571050e-01,  5.39765839e+02],
        [ 1.56427595e+00,  5.29628396e-03, -2.77337063e-01,  9.57792527e+02],
        [ 2.89486548e-04,  5.69774502e-06, -7.85623485e-04,  1.00000000e+00]
    ])
    
    # VOS Points 2D mRj (Récepteur) lus sur la caméra (18 points)
    # Formatés en [uR (Ligne/Y), vR (Colonne/X)] pour correspondre à la matrice MRNmes
    pts_2d_R = np.array([
        # --- PLAN Z = 0 ---
        [278.4, 782.1],  [544.0, 786.1],  [809.6, 793.1],
        [295.4, 1011.8], [539.0, 1013.8], [781.6, 1020.8],
        [309.4, 1204.5], [534.0, 1207.5], [757.7, 1213.5],
        # --- PLAN Z = 100 ---
        [330.3, 908.9],  [542.0, 912.9],  [756.7, 918.9],
        [343.3, 1083.7], [539.0, 1088.7], [734.7, 1092.7],
        [357.3, 1227.4], [536.0, 1230.4], [714.7, 1236.4]
    ], dtype=float)

    # Points 2D mEj de la mire projetée (9 points * 2 plans = 18 points)
    # Formatés en [uE (Ligne), vE (Colonne)]
    pts_2d_E = np.array([
        # --- PLAN Z = 0 ---
        [100, 320], [400, 320], [700, 320],
        [100, 640], [400, 640], [700, 640],
        [100, 960], [400, 960], [700, 960],
        # --- PLAN Z = 100 ---
        [100, 320], [400, 320], [700, 320],
        [100, 640], [400, 640], [700, 640],
        [100, 960], [400, 960], [700, 960]
    ], dtype=float)

    # 9 points à Z=0 et 9 points à Z=100
    Z_valeurs = np.array([0]*9 + [100]*9)

    # RECALCUL MATHÉMATIQUE EXACT DES POINTS 3D (Équation 49)
    pts_3d_exacts = calculer_points_3d_exacts(MRNmes, pts_2d_R, Z_valeurs)

    # ---------------------------------------------------------------------
    # 2. CALCUL MATRICE NORMALISÉE (MENmes)
    # ---------------------------------------------------------------------
    MENmes = calibration_faugeras_toscani(pts_3d_exacts, pts_2d_E)
    
    print(f"Calib_emetteur.py ({time.process_time() - start_time:.3f} s)\n")
    print("-" * 60)
    print(" MENmes =")
    print(MENmes)
    print("-" * 60)

    # ---------------------------------------------------------------------
    # 3. EXTRACTION DES PARAMÈTRES ET MISE À L'ÉCHELLE
    # ---------------------------------------------------------------------
    t3Emes_doc = 1472.3 

    u0Emes, v0Emes, alphauEmes, alphavEmes, REmes, t1Emes, t2Emes, t3Emes_calc = extraction_parametres(MENmes)

    print("\n" + "-" * 60)
    print("   PARAMÈTRES INTRINSÈQUES ET EXTRINSÈQUES")
    print(f"   u0Emes     =  {u0Emes}")
    print(f"   v0Emes     =  {v0Emes}")
    print(f"   alphauEmes =  {alphauEmes}")
    print(f"   alphavEmes =  {alphavEmes}")
    print("   REmes      =\n", REmes)
    print(f"   t1Emes     =  {t1Emes}")
    print(f"   t2Emes     =  {t2Emes}")
    print(f"   t3Emes     =  {t3Emes_doc}  (Valeur imposée)")
    print("-" * 60)

    # ---------------------------------------------------------------------
    # 4. RÉSOLUTION NUMÉRIQUE DES ANGLES D'EULER
    # ---------------------------------------------------------------------
    angles_initiaux = [-90, 160, 0]
    
    angles_optimises = fmin(fonction_cout_angles, angles_initiaux, args=(REmes,), disp=False)
    phiEmes, thetaEmes, psiEmes = angles_optimises

    print("\n" + "-" * 60)
    print(f"   phiEmes   =  {phiEmes} °")
    print(f"   thetaEmes =  {thetaEmes} °")
    print(f"   psiEmes   =  {psiEmes} °")
    print("-" * 60)
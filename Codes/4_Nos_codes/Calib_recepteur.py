# -*- coding: utf-8 -*-
"""
Calibration du récepteur (Caméra) - Ajusté selon le cahier des charges.
Intègre la matrice normalisée, le facteur d'échelle t3Rmes, et l'optimisation des angles (fmin).
"""

import time
import numpy as np
from scipy.optimize import fmin

def calibration_faugeras_toscani(coords_3d, coords_2d):
    """Calcule la matrice de projection normalisée MRNmes (3x4)."""
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
    """Extrait les paramètres de la matrice mise à l'échelle."""
    # Le facteur d'échelle est directement géré par la norme de la 3eme ligne
    rho = 1.0 / np.linalg.norm(M[2, 0:3])

    u0 = (rho**2) * np.dot(M[0, 0:3], M[2, 0:3])
    v0 = (rho**2) * np.dot(M[1, 0:3], M[2, 0:3])

    alphau = -np.sqrt((rho**2) * np.dot(M[0, 0:3], M[0, 0:3]) - u0**2)
    alphav = np.sqrt((rho**2) * np.dot(M[1, 0:3], M[1, 0:3]) - v0**2)

    r3 = rho * M[2, 0:3]
    r1 = (rho * M[0, 0:3] - u0 * r3) / alphau
    r2 = (rho * M[1, 0:3] - v0 * r3) / alphav
    R = np.array([r1, r2, r3])

    t3 = rho * M[2, 3]
    t1 = (rho * M[0, 3] - u0 * t3) / alphau
    t2 = (rho * M[1, 3] - v0 * t3) / alphav

    return u0, v0, alphau, alphav, R, t1, t2, t3

def matrice_rotation_theorique(angles):
    """Génère une matrice de rotation 3D à partir des angles d'Euler en degrés."""
    phi, theta, psi = angles
    phi_r, theta_r, psi_r = np.radians(phi), np.radians(theta), np.radians(psi)
    
    # Matrices de rotation élémentaires (Convention classique)
    Rx = np.array([[1, 0, 0], [0, np.cos(phi_r), -np.sin(phi_r)], [0, np.sin(phi_r), np.cos(phi_r)]])
    Ry = np.array([[np.cos(theta_r), 0, np.sin(theta_r)], [0, 1, 0], [-np.sin(theta_r), 0, np.cos(theta_r)]])
    Rz = np.array([[np.cos(psi_r), -np.sin(psi_r), 0], [np.sin(psi_r), np.cos(psi_r), 0], [0, 0, 1]])
    
    return Rz @ Ry @ Rx

def fonction_cout_angles(angles, R_cible):
    """Évalue l'écart (norme de Frobenius) entre la rotation calculée et la rotation visée (Eq. 47)."""
    R_calc = matrice_rotation_theorique(angles)
    return np.linalg.norm(R_calc - R_cible)

if __name__ == "__main__":
    start_time = time.process_time()
    
    # ---------------------------------------------------------------------
    # 1. DONNÉES DE CALIBRATION
    # ---------------------------------------------------------------------
    
    # Tableau des 18 points 2D (issus de l'image 'Figure 7-2')
    pts_2d = np.array([
        [165, 209], [539, 209], [913, 209],
        [120, 959], [539, 959], [967, 959],
        [257, 1517], [539, 1517], [822, 1517],
        [127, 195], [539, 195], [951, 195],
        [85, 1010], [539, 1010], [1005, 1010],
        [236, 1603], [539, 1603], [843, 1603]
    ], dtype=float)

    # Tableau des 18 points 3D (issus de l'image 'Figure 7-1')
    pts_3d = np.array([
        [-497.5,  234,   0], [-497.5,    0,   0], [-497.5, -234,   0],
        [     0,  311,   0], [     0,    0,   0], [     0, -311,   0],
        [ 497.5,  234,   0], [ 497.5,    0,   0], [ 497.5, -234,   0],
        [-497.5,  234, 100], [-497.5,    0, 100], [-497.5, -234, 100],
        [     0,  311, 100], [     0,    0, 100], [     0, -311, 100],
        [ 497.5,  234, 100], [ 497.5,    0, 100], [ 497.5, -234, 100]
    ], dtype=float)

    # ---------------------------------------------------------------------
    # 2. CALCUL MATRICE NORMALISÉE (MRNmes)
    # ---------------------------------------------------------------------
    MRNmes = calibration_faugeras_toscani(pts_3d, pts_2d)
    
    print(f"Calib_recepteur.py ({time.process_time() - start_time:.3f}s)\n")
    print("-" * 60)
    print(" MRNmes =")
    print(MRNmes)
    print("-" * 60)

    # ---------------------------------------------------------------------
    # 3. MISE À L'ÉCHELLE (Eq. 46) ET EXTRACTION DES PARAMÈTRES
    # ---------------------------------------------------------------------
    # D'après ton document, la valeur mesurée est :
    t3Rmes_doc = 1210.656 
    
    # Eq 46 : MRmes = t3Rmes * MRNmes
    MRmes = t3Rmes_doc * MRNmes 
    
    u0Rmes, v0Rmes, alphauRmes, alphavRmes, RRmes, t1Rmes, t2Rmes, t3Rmes = extraction_parametres(MRNmes)

    print("\n" + "-" * 60)
    print(f"   u0Rmes =  {u0Rmes}")
    print(f"   v0Rmes =  {v0Rmes}")
    print(f"   alphauRmes =  {alphauRmes}")
    print(f"   alphavRmes =  {alphavRmes}")
    print("   RRmes =")
    print(RRmes)
    print(f"   t1Rmes =  {t1Rmes}")
    print(f"   t2Rmes =  {t2Rmes}")
    print(f"   t3Rmes =  {t3Rmes_doc}  (Valeur imposée/mesurée)")
    print("-" * 60)

    # ---------------------------------------------------------------------
    # 4. RÉSOLUTION NUMÉRIQUE DES ANGLES D'EULER (Eq. 47)
    # ---------------------------------------------------------------------
    # Valeurs d'initialisation (proches des valeurs théoriques de simulation)
    angles_initiaux = [-90, -160, 0]
    
    # Optimisation fmin de Python
    angles_optimises = fmin(fonction_cout_angles, angles_initiaux, args=(RRmes,), disp=False)
    phiRmes, thetaRmes, psiRmes = angles_optimises

    print("\n" + "-" * 60)
    print(f"   phiRmes   =  {phiRmes} °")
    print(f"   thetaRmes =  {thetaRmes} °")
    print(f"   psiRmes   =  {psiRmes} °")
    print("-" * 60)
# -*- coding: utf-8 -*-
"""
Calibration de l'émetteur (Projecteur) par la méthode de Faugeras-Toscani.
Utilise les n = 24 points de calibration (Z=0 et Z=100) issus du TP.
"""

import time
import numpy as np
from scipy.optimize import fmin

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

if __name__ == "__main__":
    start_time = time.process_time()
    
    # --- 1. DONNÉES DE CALIBRATION ÉMETTEUR ---
    
    # Points 2D LCD (uEj, vEj en pixels) - Répétés pour Z=0 et Z=100
    pts_2d_base = [
        [100, 320], [400, 320], [700, 320],
        [100, 640], [400, 640], [700, 640],
        [100, 960], [400, 960], [700, 960],
        [100, 1280], [400, 1280], [700, 1280]
    ]
    pts_2d = np.array(pts_2d_base + pts_2d_base, dtype=float)

    # Points 3D (Xj, Yj, Zj en mm) issus du calcul par Eq. 49
    pts_3d = np.array([
        # Plan Z = 0
        [-259.9, 228.1,   0], [-259.9,  -0.9,   0], [-259.9, -230.0,   0],
        [   0.9, 215.9,   0], [   0.9, -0.94,   0], [   0.9, -216.8,   0],
        [ 232.7, 203.7,   0], [ 232.7, -0.95,   0], [ 232.7, -205.6,   0],
        [ 440.0, 193.4,   0], [ 440.0, -0.95,   0], [ 440.0, -195.0,   0],
        # Plan Z = 100
        [-204.5, 212.1, 100], [-204.5, -0.94, 100], [-204.5, -213.1, 100],
        [  37.5, 199.9, 100], [  37.5, -0.95, 100], [  37.5, -200.9, 100],
        [ 252.4, 189.2, 100], [ 252.4, -0.94, 100], [ 252.4, -190.6, 100],
        [ 444.7, 179.3, 100], [ 444.7, -0.95, 100], [ 444.7, -181.2, 100]
    ], dtype=float)

    # --- 2. CALCUL MATRICE NORMALISÉE (MENmes) ---
    MENmes = calibration_faugeras_toscani(pts_3d, pts_2d)
    
    print(f"Calib_emetteur.py ({time.process_time() - start_time:.3f} s)\n")
    print("-" * 60)
    print(" MENmes =")
    print(MENmes)
    print("-" * 60)

    # --- 3. EXTRACTION DES PARAMÈTRES ---
    u0Emes, v0Emes, alphauEmes, alphavEmes, REmes, t1Emes, t2Emes, t3Emes = extraction_parametres(MENmes)

    print("\n" + "-" * 60)
    print("   PARAMÈTRES INTRINSÈQUES ET EXTRINSÈQUES (Base)")
    print(f"   u0Emes     =  {u0Emes:.4f}")
    print(f"   v0Emes     =  {v0Emes:.4f}")
    print(f"   alphauEmes =  {alphauEmes:.4f}")
    print(f"   alphavEmes =  {alphavEmes:.4f}")
    print("   REmes      =")
    print(REmes)
    print(f"   t1Emes     =  {t1Emes:.4f}")
    print(f"   t2Emes     =  {t2Emes:.4f}")
    print(f"   t3Emes     =  {t3Emes:.4f}")
    print("-" * 60)

    # --- 4. SAUVEGARDE DE LA MATRICE ---
    np.savetxt('ME_calib.txt', MENmes, fmt='%-7.9f')
    print("\nMatrice de calibration enregistrée sous 'ME_calib.txt'.")
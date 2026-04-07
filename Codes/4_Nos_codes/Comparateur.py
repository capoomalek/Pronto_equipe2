import time
start_time = time.process_time()

import numpy as np
from numpy import loadtxt, pi, array, zeros, savetxt, linspace
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

X_mes = loadtxt('X_mes.txt')
Y_mes = loadtxt('Y_mes.txt')
Z_mes = loadtxt('Z_mes.txt')

X_simule = loadtxt('X.txt')
Y_simule = loadtxt('Y.txt')
Z_simule = loadtxt('Z.txt')

delta_X = X_mes - X_simule
delta_Y = Y_mes - Y_simule
delta_Z = Z_mes - Z_simule

# Affichage des erreurs de restitution


print(time.process_time() - start_time, "seconds")
plt.savefig('Comparateur_Erreurs.png', dpi=150)
plt.show()
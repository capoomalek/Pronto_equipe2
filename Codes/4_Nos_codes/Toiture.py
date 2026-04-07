# -*- coding: utf-8 -*-

import time
start_time = time.process_time() # début mesure temps d'éxecusion

# On importe le module numpy qui permet de faire du calcul numérique
#import numpy as np
from numpy import meshgrid, sqrt, linspace, savetxt
# On importe le module matplotlib qui permet de générer des graphiques 2D et 3D
import matplotlib.pyplot as plt


#************************************************************************
#*********** Création de l'objet toiture dans repère Objet (O,X,Y,Z) ***
#************************************************************************
#Nb pixel Objet (échantillonnage objet)
NbHO = 1280
NbVO = 800

#Coordonnées matricielles des pts M de l'objet
[X,Y] = meshgrid(linspace(-600,600,NbHO),linspace(-400,400,NbVO))

Z = 0*X


P1 = (Y >= 0) & (Y <= 200) & (X >= -Y - 100) & (X <= Y + 100)

P2 = (Y<X-100) & (Y>-X+100) & (X<300)

P3 = (Y <= 0) & (Y >= -200) & (Y <= -X + 100) & (Y <= X + 100)

P4 = (X >= -300) & (Y-X-100 >= 0) & (Y+X+100 <= 0)



Z1 = 75 - 75*Y/200
Z[P1] = Z1[P1]

Z2 = (225/2)*(1 - X/300)
Z[P2] = Z2[P2]

Z3 = 75/200*Y + 75
Z[P3] = Z3[P3]

Z4 = 225*(1 + X/300)/2
Z[P4] = Z4[P4]


    


#Enregistrement des coordonnées matricelles objet
savetxt('X_toiture.txt', X, fmt='%-7.6f')   
savetxt('Y_toiture.txt', Y, fmt='%-7.6f')
savetxt('Z_toiture.txt', Z, fmt='%-7.6f')  


#************************************************************************
#************************ Affichage de l'objet  *************************
#************************************************************************

z_min, z_max = 0, abs(Z).max()
plt.figure()
plt.pcolor(X,Y,Z, cmap='gray', vmin=z_min, vmax=z_max)
plt.title('Z (mm) - Objet toiture simulé')
# set the limits of the plot to the limits of the data
plt.axis([X.min(), X.max(), Y.min(), Y.max()])
plt.colorbar()
plt.savefig("Toiture1.png")
print(time.process_time() - start_time, "seconds")  # fin mesure temps d'éxecusion
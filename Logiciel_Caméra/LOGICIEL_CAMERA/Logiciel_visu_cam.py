import sys, os

import cv2
import time
from datetime import datetime

from PySide6.QtCore import Slot, QSize
from PySide6.QtGui import QIcon, QAction, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QPushButton, QComboBox
from ThemeMenu import ThemeMenu


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# style_path = resource_path("resources\\ac_style.txt")

"""
App configuration
"""
__title__="LOGITECHApp"
__version__="v0.1"
__icon__=resource_path("resources/icons/webcam_grd.png")

class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualisation Webcam LOGITECH")
        self.setWindowIcon(QIcon("ressources/icons/webcam.png"))
        self.resize(800, 50)

        self.createActions()
        self.createMenuBar()
        self.createToolBar()

        self.statusBar = self.statusBar()
        self.statusBar.showMessage(self.windowTitle())   # Définition du message initial


    def createActions(self):
        # Menu Files  ------------
        self.actExit = QAction(QIcon("ressources/icons/exit.png"), "Exit", self)
        self.actExit.setShortcut("Alt+F4")
        self.actExit.setStatusTip("Sortir du logiciel")
        # La méthode close est directement fournie par la classe QMainWindow.
        self.actExit.triggered.connect(self.close)

        # Menu Camera ------------
        self.actParam = QAction(QIcon("ressources/icons/settings.png"), "Paramètres", self)
        self.actParam.setShortcut("Alt+P")
        self.actParam.setStatusTip("Paramètres de la webcam")
        self.actParam.setEnabled(False)
        # self.actParam.triggered.connect(self.menuParameter)

        self.actSave = QAction(QIcon("ressources/icons/save.png"), "&Save", self)
        self.actSave.setShortcut("Ctrl+S")
        self.actSave.setStatusTip("Sauvegarder une image de la webcam")
        self.actSave.setEnabled(False)
        # self.actSave.triggered.connect(self.menuSave)

    def createMenuBar(self):
        menuBar = self.menuBar()
        file = menuBar.addMenu("&File")
        file.addAction(self.actExit)

        camera = menuBar.addMenu("&Camera")
        camera.addAction(self.actParam)
        camera.addAction(self.actSave)

        themeMenu = ThemeMenu()
        menuBar.addMenu(themeMenu)

    def createToolBar(self):
        toolBar = self.addToolBar("File toolbar")
        toolBar.setFloatable(False)
        toolBar.setMovable(False)
        toolBar.addAction(self.actExit)

        #On créé la barre d'outils pour la caméra
        self.bottomBar = QToolBar("Caméra")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.bottomBar)
        self.bottomBar.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea | Qt.ToolBarArea.BottomToolBarArea)

        # Ajout d'un widget quelconque dans la barre d'outils.
        self.comboBox = QComboBox()
        self.comboBox.addItems(["-","0", "1"]) #, "2","3"
        # self.comboBox.setIconSize(QSize(64,32))
        self.comboBox.setStatusTip("Choisir un canal de connexion de la webcam")
        # self.comboBox.activated.connect(self.chooseCamera)
        self.bottomBar.addWidget(self.comboBox)

        self.buttonOk = QPushButton(QIcon("ressources/icons/yes.png"), "",self)
        # self.buttonOk.setIconSize(QSize(32, 32))
        self.buttonOk.clicked.connect(self.chooseCamera)
        self.bottomBar.addWidget(self.buttonOk)
        self.buttonOk.setStatusTip("Valider le choix de la caméra")

        self. bottomBar.addSeparator()

        self.buttonRun = QPushButton(QIcon("ressources/icons/webcam-64x64.png"), "",self) #
        self.buttonRun.setIconSize(QSize(32,32))
        self.bottomBar.addWidget(self.buttonRun)
        self.buttonRun.setEnabled(False)
        self.buttonRun.setStatusTip("Ouvrir la caméra")

        self.buttonStop = QPushButton(QIcon("ressources/icons/no_webcam-64x64.png"),"",self) # close_camera
        self.buttonStop.setIconSize(QSize(32,32))
        self.bottomBar.addWidget(self.buttonStop)
        self.buttonStop.setEnabled(False)
        self.buttonStop.setStatusTip("Stopper la caméra")

        # self.bottomBar.setIconSize(QSize(64,32))
        self.bottomBar.addAction(self.actParam)
        self.bottomBar.addAction(self.actSave)

        # On demande l'instanciation de la barre de status
        self.statusBar().showMessage("Barre outils Caméra")

    @Slot()
    def chooseCamera(self):
        # On récupère la valeur du menu déroulant et on la transforme en int
        ctext = self.comboBox.currentText()
        print("Vous avez sélectionné : " + ctext)

        # on modifie l'état des bouton de la barre d'outil
        self.cameraDevice = int(ctext)
        self.comboBox.setEnabled(False)
        self.buttonOk.setEnabled(False)
        self.buttonRun.setEnabled(True)
        self.buttonRun.clicked.connect(self.runCamera)
    @Slot()
    def runCamera(self):
        time1 = time.time()
        self.counter = 1

        # On règle l'état des boutons
        self.actExit.setEnabled(False)
        self.buttonRun.setEnabled(False)
        self.actParam.setEnabled(True)
        self.actParam.triggered.connect(self.menuParameter)
        self.actSave.setEnabled(True)
        self.actSave.triggered.connect(self.menuSave)
        self.buttonStop.setEnabled(True)
        self.buttonStop.clicked.connect(self.stopCamera)


        print("On ouvre la caméra", str(self.cameraDevice))
        self.cap = cv2.VideoCapture(self.cameraDevice, cv2.CAP_DSHOW)  #, cv2.CAP_DSHOW
        if not self.cap.isOpened():
            print("Impossible d'ouvrir la caméra")
            exit()

        """
        0. CV_CAP_PROP_POS_MSEC Position actuelle du fichier vidéo en millisecondes.
        1. CV_CAP_PROP_POS_FRAMES Index basé sur 0 de l'image à décoder/self.capturer ensuite.
        2. CV_CAP_PROP_POS_AVI_RATIO Position relative du fichier vidéo
        3. CV_CAP_PROP_FRAME_WIDTH Largeur des images dans le flux vidéo.
        4. CV_CAP_PROP_FRAME_HEIGHT Hauteur des images dans le flux vidéo.
        5. CV_CAP_PROP_FPS Fréquence d'images.
        6. CV_CAP_PROP_FOURCC Code à 4 caractères du codec.
        7. CV_CAP_PROP_FRAME_COUNT Nombre d'images dans le fichier vidéo.
        8. CV_CAP_PROP_FORMAT Format des objets Mat renvoyés par retrieve() .
        9. CV_CAP_PROP_MODE Valeur spécifique au backend indiquant le mode de self.capture actuel.
        10. CV_CAP_PROP_BRIGHTNESS Luminosité de l'image (uniquement pour les caméras).
        11. CV_CAP_PROP_CONTRAST Contraste de l'image (uniquement pour les caméras).
        12. CV_CAP_PROP_SATURATION Saturation de l'image (uniquement pour les caméras).
        13. CV_CAP_PROP_HUE Teinte de l'image (uniquement pour les caméras).
        14. CV_CAP_PROP_GAIN Gain de l'image (uniquement pour les caméras).
        15. CV_CAP_PROP_EXPOSURE Exposition (uniquement pour les caméras).
        16. CV_CAP_PROP_CONVERT_RGB Indicateurs booléens indiquant si les images doivent être converties en RVB.
        17. CV_CAP_PROP_WHITE_BALANCE Actuellement non pris en charge.
        18. CV_CAP_PROP_RECTIFICATION Drapeau de rectification pour les caméras stéréo (note : uniquement pris en charge par le backend DC1394 v 2.x actuellement).
        """

        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)
        self.cap.set(cv2.CAP_PROP_CONTRAST, 128)
        self.cap.set(cv2.CAP_PROP_SATURATION, 128)
        self.cap.set(cv2.CAP_PROP_SHARPNESS, 128)
        self.cap.set(cv2.CAP_PROP_GAMMA, 2)  # Menu non accéssible avec cette caméra
        self.cap.set(cv2.CAP_PROP_BACKLIGHT, 0)
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        self.cap.set(cv2.CAP_PROP_TEMPERATURE, 2900)
        self.cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 4000)  # 3502
        self.cap.set(cv2.CAP_PROP_GAIN, 0)
        self.cap.set(cv2.CAP_PROP_ZOOM, 100)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.cap.set(cv2.CAP_PROP_FOCUS, 41)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 2)  # Exposition par défaut 2
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -5)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        # self.cap.set(cv2.CAP_PROP_SETTINGS, 1)  # Ouverture  (1 )  de la boite de dialogue paramètre de la camera

        time2 = time.time()
        print('\n' 'Temps de mise en route : ' + f'{round(time2 - time1, 2)}' + ' s''\n')
        print('-' * 40)
        print('\n' 'Démarrage - Affichage des valeurs par défaut ...')
        # Affichage dans la console des valeurs par défaut de la caméra
        print('Luminosité : ' + f'{self.cap.get(cv2.CAP_PROP_BRIGHTNESS)}')
        print('Contraste : ' + f'{self.cap.get(cv2.CAP_PROP_CONTRAST)}')
        print('Saturation : ' + f'{self.cap.get(cv2.CAP_PROP_SATURATION)}')
        print('Netteté : ' + f'{self.cap.get(cv2.CAP_PROP_SHARPNESS)}')
        # print('Correction Gamma : ' + f'{self.cap.get(cv2.CAP_PROP_GAMMA)}') # Valeur = -1 le menu n'est pas accessible
        print('AUTO_WB: ' + f'{self.cap.get(cv2.CAP_PROP_AUTO_WB)}')
        # print('Température : ' + f'{self.cap.get(cv2.CAP_PROP_TEMPERATURE)}')
        # print('Température - Balance des Blancs : ' + f'{self.cap.get(cv2.CAP_PROP_WB_TEMPERATURE)}') #WBTemp
        print('Rétro-éclairage : ' + f'{self.cap.get(cv2.CAP_PROP_BACKLIGHT)}')  # Backlight
        print('Gain : ' + f'{self.cap.get(cv2.CAP_PROP_GAIN)}')
        print('Zoom : ' + f'{self.cap.get(cv2.CAP_PROP_ZOOM)}')
        print('Autofocus : ' + f'{self.cap.get(cv2.CAP_PROP_AUTOFOCUS)}')
        print('Focus : ' + f'{self.cap.get(cv2.CAP_PROP_FOCUS)}')
        print('Exposition auto : ' + f'{self.cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)}')  # auto_exposure
        print('Exposition : ' + f'{self.cap.get(cv2.CAP_PROP_EXPOSURE)}')
        self.stop = False
        while self.stop == False:
            ret, self.frame = self.cap.read()
            if ret:
                cv2.imshow("image", self.frame)

                if cv2.waitKey(1) == ord('q'):
                    break

    @Slot()
    def stopCamera(self):
        # On modifie l'état de la variable stop pour sortir de la boucle while
        self.stop = True
        self.cap.release()
        cv2.destroyAllWindows()
        print("on arrête la caméra")
        self.comboBox.setEnabled(True)
        self.buttonOk.setEnabled(True)

        self.buttonStop.setEnabled(False)
        self.actParam.setEnabled(False)
        self.actSave.setEnabled(False)
        self.actExit.setEnabled(True)




    @Slot()
    def menuParameter(self):
        print("On ouvre le menu paramètre")
        self.cap.set(cv2.CAP_PROP_SETTINGS, 1)

    @Slot()
    def menuSave(self):
        image_name = ".\Save_images\Image_{}.bmp".format(self.counter)
        cv2.imwrite(image_name, self.frame)  #
        print("{} enregistrée !".format(image_name))
        self.counter += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    myWindow = MyWindow()#__title__+__version__
    myWindow.show()
    app.quit()
    sys.exit(app.exec())
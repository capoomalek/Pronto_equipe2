import os
import platform

from PySide6.QtCore import QFile, QTextStream, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QStyleFactory, QApplication


class ThemeMenu(QMenu):

    def __init__(self, text="&Themes", parent=None):
        super().__init__(text, parent)

        # On liste les fichiers d'extension .qss présents dans le dossier qss.
        styleSheets = [file for file in os.listdir("./ressources/qss") if file.endswith(".qss")]
        # On trie la liste sans tenir compte de la casse.
        styleSheets.sort(key=lambda file: file.lower())
        # Pour chaque fichier trouvé, on crée l'action associée.
        for styleSheet in styleSheets:
            self.addAction(self.createThemeAction(styleSheet.replace(".qss", "")))

        if len(styleSheets) > 0:
            self.addSeparator()

        # On récupère le theme de démarrage
        app = QApplication.instance()
        currentTheme = app.style().name()

        actFusion = QAction("&Fusion theme", self)
        actFusion.setStatusTip("Fusion theme")
        actFusion.setData("Fusion")
        actFusion.triggered.connect(self.changeTheme)
        actFusion.setCheckable(True)
        actFusion.setChecked(currentTheme == "fusion")
        self.addAction(actFusion)

        actWindows = QAction("&Windows theme", self)
        actWindows.setStatusTip("Windows theme")
        actWindows.setData("Windows")
        actWindows.triggered.connect(self.changeTheme)
        actWindows.setCheckable(True)
        actWindows.setChecked(currentTheme == "windows")
        self.addAction(actWindows)

        if platform.system() == "Windows":
            actWindowsVista = QAction("Windows &Vista theme", self)
            actWindowsVista.setStatusTip("Windows theme")
            actWindowsVista.setData("WindowsVista")
            actWindowsVista.triggered.connect(self.changeTheme)
            actWindowsVista.setCheckable(True)
            actWindowsVista.setChecked(currentTheme == "windowsvista")
            self.addAction(actWindowsVista)

    def createThemeAction(self, themeName):
        action = QAction(f"{themeName} theme", self)
        action.setStatusTip(f"{themeName} theme")
        action.setData(f"qss/{themeName}.qss")
        action.triggered.connect(self.changeStyleSheet)
        action.setCheckable(True)
        return action

    def checkSelectedAction(self):
        for action in self.actions():
            if action != self.sender():
                action.setChecked(False)

    @Slot()
    def changeStyleSheet(self):
        self.checkSelectedAction()
        qssFileName = self.sender().data()
        app = QApplication.instance()
        file = QFile(qssFileName)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyle(None)
        app.setStyleSheet(stream.readAll())
        file.close()
        print(f"{qssFileName} applied")

    @Slot()
    def changeTheme(self):
        self.checkSelectedAction()
        themeName = self.sender().data()
        app = QApplication.instance()
        app.setStyleSheet(None)
        app.setStyle(QStyleFactory.create(themeName))
        print(f"{themeName} style applied")
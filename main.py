# pip install pyqt6
# pip install pyautogui
# pip install keyboard

from PyQt6.QtWidgets import QApplication
from ui import MainWidget

if __name__ == '__main__':
    app = QApplication([])
    wgt = MainWidget()
    wgt.show()
    app.exec()
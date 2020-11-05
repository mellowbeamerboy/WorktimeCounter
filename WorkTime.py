from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton
import sys

class win(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('WorkTime')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = win()
    mw.show()
    sys.exit(app.exec_())
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime
import sys, os, json

class Front(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Work Time Counter')
        self.zero = '00:00:00'
        self.saved = True
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.initUI()

        # initialize backend object of the application
        self.engine = Back()

        self.initHistoryManagement()
        self.historyWindow = HistoryTable()
        self.connectHistoryWindowMethods()

    def initUI(self):
        # counter
        self.count = 0

        # create flag
        self.flag = False

        # time label
        self.label = QLabel(self)

        # set text to label
        self.label.setText(self.zero)
        self.label.setFont(QFont('Arial', 25))
        self.label.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(self.label, 0, 0, 1, 3)

        # create pushbuttons
        self.start = QPushButton("Start", self)
        self.start.pressed.connect(self.startCount)
        self.grid.addWidget(self.start, 1, 0)

        self.pause = QPushButton("Pause", self)
        self.pause.pressed.connect(self.pauseCount)
        self.grid.addWidget(self.pause, 1, 1)

        self.reset = QPushButton("Reset", self)
        self.reset.pressed.connect(self.resetWarning)
        self.grid.addWidget(self.reset, 1, 2)

        # create timer object
        self.timer = QTimer(self)

        # add action to the timer
        self.timer.timeout.connect(self.showTime)

        # set the update period
        self.timer.start(1000)

    def closeEvent(self, event):
        close = QMessageBox()
        if self.flag:
            close.setText('Your timer is still running!\nAre you sure you want to exit without saving?')
        elif not self.saved:
            close.setText('You didn\'t save your working time!\nAre you sure you want to exit without saving?')
        else:
            close.setText("Are you sure you want to exit?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def showTime(self):
        if self.flag:
            self.count += 1
        text = self.formatIntoTime(self.count)
        self.label.setText(text)
    
    def formatIntoTime(self, secs):
        if secs == 0:
            return self.zero
        h = int((secs - secs % 3600) / 3600)
        secs -= h * 3600
        m = int((secs - secs % 60) / 60)
        s = secs - m * 60

        HH = str(h) if h >= 10 else f'0{h}'
        MM = str(m) if m >= 10 else f'0{m}'
        SS = str(s) if s >= 10 else f'0{s}'

        return f'{HH}:{MM}:{SS}'

    def startCount(self):
        self.flag = True
        self.saved = False

    def pauseCount(self):
        self.flag = False

    def resetWarning(self):
        if not self.saved:
            msg = QMessageBox()
            msg.setText('You didn\'t save your working time. Are you sure you want to reset?')
            msg.setStandardButtons(msg.Yes|msg.No)
            msg = msg.exec()
            if msg == QMessageBox.Yes:
                self.resetCount()
            else:
                return
        else:
            self.resetCount()

    def resetCount(self):
        self.flag = False
        self.saved = True
        self.count = 0
        self.label.setText(self.zero)

    def initHistoryManagement(self):
        self.Save = QPushButton('Save', self)
        self.Save.clicked.connect(self.saveCurrentWorkTime)
        self.grid.addWidget(self.Save, 2, 0, 1, 3)

        self.History = QPushButton('History', self)
        self.History.clicked.connect(self.showHistory)
        self.grid.addWidget(self.History, 3,0, 1, 3)

    def showHistory(self):
        data = self.engine.whData['History']
        rows = len(data)
        self.historyWindow.tableWidget.setRowCount(rows)
        for i, row in enumerate(data):
            for j, col in enumerate(row.keys()):
                item = QTableWidgetItem(row.get(col))
                self.historyWindow.tableWidget.setItem(i, j, item)
        self.historyWindow.tableWidget.resizeColumnsToContents()
        # self.historyWindow.resize(self.historyWindow.tableWidget.size())
        self.historyWindow.show()
    
    def saveCurrentWorkTime(self):
        if self.label.text() != self.zero:
            self.pauseCount()
            comment, ok = QInputDialog.getText(self, 'Comment', 'Leave a comment (optional): ')
            if ok:
                self.engine.whData['History'].append({
                    'Date': str(datetime.now().date()),
                    'Time worked': self.label.text(),
                    'Comment': comment
                })
                self.engine.saveData()
                self.resetCount()
                self.saved = True
                qm = QMessageBox
                qm.information(QWidget(), '', 'Saved!')

    def connectHistoryWindowMethods(self):
        self.historyWindow.deleteSelectedButt.clicked.connect(self.deleteSelected)
        self.historyWindow.saveChangesButt.clicked.connect(self.saveChanges)

    def deleteSelected(self):
        selected = self.historyWindow.tableWidget.currentRow()
        if selected >= 0 and self.historyWindow.tableWidget.isEnabled():
            qm = QMessageBox
            ret = qm.question(QWidget(), '', 'Are you sure you want to delete selected rows?', qm.Yes, qm.No)
            if ret == qm.Yes:
                self.historyWindow.tableWidget.removeRow(selected)
                qm.information(QWidget(), '', 'Remember to save changes!')

    def saveChanges(self):
        qm = QMessageBox
        ret = qm.question(QWidget(), '', 'Are you sure you want to save these changes?', qm.Yes, qm.No)
        if ret == qm.Yes:
            data = {}
            data['History'] = []
            headers = ('Date', 'Time worked', 'Comment')
            for row in range(self.historyWindow.tableWidget.rowCount()):
                data['History'].append({})
                for col in range(self.historyWindow.tableWidget.columnCount()):
                    key = headers[col]
                    val = self.historyWindow.tableWidget.item(row, col).text()
                    data['History'][row][key] = val
            self.engine.whData = data
            self.engine.saveData()
            qm.information(QWidget(), '', 'Saved')
        


class HistoryTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 700, 500)
        self.setWindowTitle('History')
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.tableWidget.setHorizontalHeaderLabels(('Date','Time worked','Comment'))
        self.tableWidget.setEnabled(False)
        self.initButtons()

    def initButtons(self):
        self.toggleEditButt = QPushButton('Activate / Deactivate for making changes', self)
        self.toggleEditButt.clicked.connect(self.toggleEdit)
        self.layout.addWidget(self.toggleEditButt)
        self.deleteSelectedButt = QPushButton('Delete selected')
        self.layout.addWidget(self.deleteSelectedButt)
        self.saveChangesButt = QPushButton('Save changes')
        self.layout.addWidget(self.saveChangesButt)

    def toggleEdit(self):
        self.tableWidget.setEnabled(False) if self.tableWidget.isEnabled() else self.tableWidget.setEnabled(True)

class Back():
    def __init__(self):
        self.cwd = os.getcwd() # /home/maciej/Documents/PythonProjects/WorkTime
        self.whPath = os.path.join(self.cwd, 'MyWorkHistory.txt')
        self.whData = self.loadData()
        self.saveData()

    def loadData(self):        
        dataExists = os.path.isfile(self.whPath)
        if dataExists:
            with open(self.whPath) as json_file:
                data = json.load(json_file)
            return data
        else:
            data = {}
            data['History'] = []
            return data

    def saveData(self):
        with open(self.whPath, 'w') as outfile:
            json.dump(self.whData, outfile, sort_keys=False, indent=4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = Front()
    mw.show()
    sys.exit(app.exec_())
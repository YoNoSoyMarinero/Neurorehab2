from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QPushButton,QSpinBox, QGridLayout, QWidget, QComboBox, QLabel
from pyqtgraph import PlotWidget, plot
from EEGSerialCommunication import EEGSerialCommunication
import pyqtgraph as pg
import numpy as np
import sys
import os
from random import randint

class MainWindow(QtWidgets.QMainWindow):

    def set_time_settings(self):
        spinbox_value = self.signal_length.value() if self.signal_length.value() > 0 else 5
        self.eeg_x = list(np.linspace(0.0, spinbox_value, num=spinbox_value*160))
        self.eeg_y = [0 for _ in range(spinbox_value*160)]

        self.movement_x = list(np.linspace(0.0, spinbox_value, num=spinbox_value*160))
        self.movement_y = [0 for _ in range(spinbox_value*160)]

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.eeg_x = list(np.linspace(0.0, 5.0, num=800))
        self.eeg_y = [0 for _ in range(800)]

        self.movement_x = list(np.linspace(0.0, 5.0, num=800))
        self.movement_y = [0 for _ in range(800)]
        self.plot = False

        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        self.pen = pg.mkPen(color=(199,36,177),width= 2)

        self.ser_port = EEGSerialCommunication()
        self.ser_port.turn_simulator_on()
        self.ser_port.turn_channel()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("EEG app")
        self.setStyleSheet("background-color: black;")
        self.layout = QGridLayout()

        self.graphWidgetEEG = pg.PlotWidget()        
        self.graphWidgetEEG.setBackground('k')
        self.graphWidgetEEG.setMaximumSize(600, 200)
        self.graphWidgetEEG.setMinimumSize(600, 200)
        self.graphWidgetEEG.getAxis('left').setPen('b')
        self.graphWidgetEEG.getAxis('bottom').setPen('b')
        

        self.graphWidgetMovement = pg.PlotWidget()
        self.graphWidgetMovement.setBackground('k')
        self.graphWidgetMovement.setMaximumSize(600, 200)
        self.graphWidgetMovement.setMinimumSize(600, 200)
        self.graphWidgetMovement.getAxis('left').setPen('b')
        self.graphWidgetMovement.getAxis('bottom').setPen('b')

        self.set_setting_button = QPushButton("Set time")
        self.set_setting_button.setMaximumSize(100, 40)
        self.set_setting_button.setMinimumSize(100, 40)
        self.set_setting_button.setStyleSheet("QPushButton {background-color : rgb(57, 255, 20)}")
        self.set_setting_button.clicked.connect(self.set_time_settings)

        self.button = QPushButton('Start')
        self.button.setToolTip("This is a start\stop button")
        self.button.setMaximumSize(100, 40)
        self.button.setMinimumSize(100, 40)
        self.button.setStyleSheet(f"""
        QPushButton {
            "{background-color : rgb(210,39,48)}" if self.plot else "{background-color : rgb(77, 77, 255)}"
        }
        QPushButton:hover {
            "{background-color : rgb(230, 59, 68)}" if self.plot else "{background-color : rgb(97,97,255)}"
        }
    """)
        self.button.clicked.connect(self.start_stop)
        self.button.setFont(QtGui.QFont('Times', 10))

        

        self.combox = QComboBox()
        self.combox.setStyleSheet("""QComboBox QAbstractItemView {
                                    background: rgb(77, 77, 255);
                                    selection-background-color: blue;
                                    }
                                    QComboBox {
                                    background: rgb(77, 77, 255);
                                    }""")
        self.combox.setMaximumSize(100, 40)
        self.combox.setMinimumSize(100, 40)
        for i in range(24):
            self.combox.addItem("CH" + str(i + 1))

        self.combox.setCurrentIndex(0)


        self.length_label = QLabel("Singal display time")
        self.length_label.setStyleSheet("color: rgb(77, 77, 255)")
        self.length_label.resize(100, 40)
        self.signal_length = QSpinBox()
        self.signal_length.resize(100, 40)
        self.signal_length.setStyleSheet("color: rgb(77, 77, 255)")


        self.layout.addWidget(self.button, 0, 1)
        self.layout.addWidget(self.graphWidgetEEG, 0, 0)
        self.layout.addWidget(self.graphWidgetMovement, 1, 0)
        self.layout.addWidget(self.combox, 0, 2)
        self.layout.addWidget(self.length_label, 0, 3)
        self.layout.addWidget(self.signal_length, 0, 4)
        self.layout.addWidget(self.set_setting_button, 0, 5)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)


        self.data_line_eeg =  self.graphWidgetEEG.plot(self.eeg_x, self.eeg_y, pen = self.pen)
        self.data_line_movement = self.graphWidgetMovement.plot(self.movement_x, self.movement_y, pen = self.pen)


    def start_stop(self):
        self.plot = not self.plot
        self.button.setText("Stop" if self.plot else "Start")
        self.button.setStyleSheet(f"""
        QPushButton {
            "{background-color : rgb(210,39,48)}" if self.plot else "{background-color : rgb(77, 77, 255)}"
        }
        QPushButton:hover {
            "{background-color : rgb(240, 69, 78)}" if self.plot else "{background-color : rgb(107,107,255)}"
        }
    """)

    def update_plot_data(self):
        
        if self.plot:
            self.set_setting_button.setDisabled(True)
            current_row = self.ser_port.read_line()
            if not current_row:
                return
            self.eeg_x = self.eeg_x[1:]
            self.eeg_x.append(self.eeg_x[-1] + 0.00625)

            self.movement_x = self.movement_x[1:]
            self.movement_x.append(self.movement_x[-1] + 0.00625)

            self.eeg_y = self.eeg_y[1:]
            self.eeg_y.append(current_row[self.combox.currentIndex()])

            self.movement_y = self.movement_y[1:]
            self.movement_y.append(current_row[-1])


            self.data_line_eeg.setData(self.eeg_x, self.eeg_y)
            self.data_line_movement.setData(self.movement_x, self.movement_y)
        else:
            self.set_setting_button.setDisabled(False)
            pass

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
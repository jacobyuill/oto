import sys
from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QHBoxLayout, QComboBox, QWidget,
    QPushButton, QCheckBox, QVBoxLayout, QLineEdit
)
from PySide6.QtCore import QProcess
from PySide6.QtGui import QIcon, QCloseEvent

app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("logo.svg"))
        self.setWindowTitle("oto")

        self.button = QPushButton("Start")
        self.button.setFixedSize(200, 50)
        self.tremolo_cb = QCheckBox("Tremolo")

        # Create checkbox and line edit
        self.volume_label = QLabel("Volume:")
        self.volume_le = QLineEdit("")
        self.volume_le.setFixedSize(30, 30)

        # Add to layout to place both CB and LE on same "y axis"
        self.volume_h_layout = QHBoxLayout()
        self.volume_h_layout.addWidget(self.volume_label)
        self.volume_h_layout.addWidget(self.volume_le)

        self.noisecolor_label = QLabel("Noise Color:")
        self.noisecolor_combo = QComboBox()
        self.noisecolor_combo.addItems(["White", "Brown", "Pink"])

        self.noisecolor_h_layout = QHBoxLayout()
        self.noisecolor_h_layout.addWidget(self.noisecolor_label)
        self.noisecolor_h_layout.addWidget(self.noisecolor_combo)

        self.noise = "brownnoise"
        self.noisecolor_combo.currentTextChanged.connect(self.set_color)

        # QVBoxLayout needed to stack checkboxes and buttons vertically
        self.layout = QVBoxLayout()

        # Stack everything up
        self.layout.addLayout(self.noisecolor_h_layout)
        self.layout.addLayout(self.volume_h_layout)
        self.layout.addWidget(self.tremolo_cb)
        self.layout.addWidget(self.button)
        self.is_enabled = True

        self.volume_le.editingFinished.connect(self.set_volume)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.button.clicked.connect(self.exec_cmd)
        self.process = None
        self.volume = "0.2"

    def closeEvent(self, event: QCloseEvent):
        if self.process is not None:
            self.process.kill()
            self.process = None
        super().closeEvent(event)

    def toggle_menu(self):
        self.is_enabled = not self.is_enabled
        self.tremolo_cb.setEnabled(self.is_enabled)
        self.volume_label.setEnabled(self.is_enabled)
        self.volume_le.setEnabled(self.is_enabled)
        self.noisecolor_combo.setEnabled(self.is_enabled)
        self.noisecolor_label.setEnabled(self.is_enabled)

    def set_color(self, text):
        color_dict = {
            "White": "whitenoise",
            "Brown": "brownnoise",
            "Pink": "pinknoise",
        }
        self.noise = color_dict.get(text, "brownnoise")
        print(text, "selected")

    def set_volume(self):
        self.volume = self.volume_le.text()
        if float(self.volume) > 1.0:
            self.volume = "1"

    def exec_cmd(self):
        if self.process is not None:
            self.process.kill()
            self.process = None
            self.button.setText("Start")
            # re-enable checkboxes
            self.toggle_menu()
        else:
            self.toggle_menu()
            self.process = QProcess(self)
            program = "sox"
            args = [
                "-q", "-c", "2", "-r", "32000", "-n", "-d", "-D",
                "synth", "12:00:00", self.noise, "vol", self.volume
            ]
            if self.tremolo_cb.isChecked():
                args += ["tremolo", "0.0625", "50"]
                print("Tremolo checked")
            self.process.start(program, args)
            self.button.setText("Stop")

def main():
    window = MainWindow()
    window.show()
    app.exec()

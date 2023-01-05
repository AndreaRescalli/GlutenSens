from loguru import logger

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QTextEdit
)
from PyQt5 import QtCore


"""!
@brief Macro to avoid emission of append_signal.

This ensures not to access some deleted objects when trying to display
logs on window, if the user has closed the application.
N.B: This has to be global or it will not work [probably due to multi-threading].
"""
KILL = False



##################
# LOGGER SIGNALS #
##################
class LoggerSignals(QtCore.QObject):
    """!
    @brief Class that defines the signals available to the logger display class.

    Available signals (with respective inputs) are:
        - append_signal:
            str --> text to be displayed
    """
    append_signal = QtCore.pyqtSignal(str)



########################
# LOGGER DISPLAY CLASS #
########################
class LoggerDisplay(QtCore.QObject):
    """!
    @brief Class that is in charge of displaying logger messages on GUI.

    N.B: Has to be a QObject since a simple QTextEdit cannot work with 
    multiple threads (and the logger is active in multiple threads).
    {QObject::connect: Cannot queue arguments of type 'QTextCursor'
    (Make sure 'QTextCursor' is registered using qRegisterMetaType().) 
    would be displayed on terminal otherwise}.
    """
    def __init__(self):
        """!
        @brief Init LoggerDisplay.
        """
        super(QtCore.QObject, self).__init__()

        self.signals = LoggerSignals()

        self.txt_window = QTextEdit()
        self.txt_window.setReadOnly(True)
        logger.add(
            self.appendMessage, 
            format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {name} | {message}"
        )


    def appendMessage(self, text):
        """!
        @brief Send signal to MainWindow for updating the display.

        Using signals is necessary when working with multiple threads (and
        the logger is active in multiple threads).
        """
        global KILL
        if not KILL:
            self.signals.append_signal.emit(text)



###################################
# POTENTIOMETER CALIBRATION CLASS #
###################################
class PotCalDialog(QDialog):
    """!
    @brief Display potentiometer values.
    """
    def __init__(self, parent=None):
        """!
        @brief Init PotCalDialog.
        """
        super().__init__(parent)

        self.setWindowTitle("Calibration")
        
        # Info label
        self.label = QLabel("Adjust potentiometer value. Click 'OK' to confirm, 'Cancel' to quit")

        # Display window
        self.txt_window = QTextEdit()
        self.txt_window.setReadOnly(True)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.txt_window)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
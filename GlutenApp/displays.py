from loguru import logger

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QTextEdit
)
from PyQt5 import QtCore


KILL = False
"""
Macro to avoid emission of append_signal.

This ensures not to access some deleted objects when trying to display
logs on window, if the user has closed the application. 
"""




##################
# LOGGER SIGNALS #
##################
class LoggerSignals(QtCore.QObject):
    """
    Class that defines the signals available to a :py:meth:`LoggerDisplay` object.
    """
    #: Text *(str)* to be displayed.
    append_signal = QtCore.pyqtSignal(str)



########################
# LOGGER DISPLAY CLASS #
########################
class LoggerDisplay(QtCore.QObject):
    """
    Class that is in charge of displaying logger messages on GUI.

    .. note::
        Has to be a *QObject* because a *QTextEdit* cannot work with 
        multiple threads (the logger is active in multiple threads)::

            QObject::connect: Cannot queue arguments of type 'QTextCursor'
            (Make sure 'QTextCursor' is registered using qRegisterMetaType(). 

        would be generated otherwise.
    """
    def __init__(self):
        """
        Init a logger display.
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
        """
        This method sends a signal to ``MainWindow`` to update the display.

        :param text: Text to be displayed.
        :type text: str
        """
        global KILL
        if not KILL:
            self.signals.append_signal.emit(text)
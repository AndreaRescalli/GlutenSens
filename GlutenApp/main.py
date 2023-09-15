import sys
import time
import os

from datetime import datetime

from logging import DEBUG
from loguru import logger

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QProgressBar,
    QComboBox,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox
)

import serial_workers as wrk
import tab_graph as grp
import displays
import csv_exporter



#################
# LOGGER CONFIG #
#################
"""
Configuring the logger to print messages on terminal(s)
"""
logger.configure(handlers=[{"sink": sys.stderr, "level": "WARNING"}]) # avoids printing all but warnings and higher on terminal
file_name = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
logger.add(
    os.path.join('Logs',file_name+'.log'), 
    format="{time:DD-MM-YYYY HH:mm:ss:SSS} | {level} | {name} | {line} | {message}", 
    level=DEBUG,
    backtrace=True, 
    enqueue=True,
    rotation="5 MB", 
    retention="2 days"
)



###############
# MAIN WINDOW #
###############
class MainWindow(QMainWindow):
    """
    Main window of GlutenApp. All the widgets and operations are managed inside here.
    """

    def __init__(self):
        """
        Init a main window.
        """
        # Parallel thread for progress bar
        self.bar_worker = wrk.BarWorker()
        # Parallel thread for serial port scan
        self.scan_worker = wrk.ScanWorker()
        # Parallel thread for serial port reading
        self.read_worker = wrk.ReadWorker(None)

        super(MainWindow, self).__init__()

        # Title and geometry
        self.setWindowTitle("GlutenSense")
        width = 1000
        height = 800
        self.setMinimumSize(width, height)
        
        # Thread handler
        self.threadpool = QtCore.QThreadPool()

        self.serialscan()
        self.initUI()



    #####################
    # GRAPHIC INTERFACE #
    #####################
    def initUI(self):
        """
        This method sets up the graphical interface structure.
        """

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Searching for target device...")
        self.progress_bar = QProgressBar()
        self.status_bar.addWidget(self.status_label,1)
        self.status_bar.addWidget(self.progress_bar,1)

        # Menu bar
        menu = self.menuBar()
        self.file_menu = menu.addMenu("&File")
        self.option_menu = menu.addMenu("&Options")

        # Toolbar
            # File toolbar
        self.file_toolbar = QToolBar("File toolbar")
                # Cannot be moved
        self.file_toolbar.setMovable(False)
        self.file_toolbar.setFloatable(False)
                # Cannot be hidden
        self.file_toolbar.toggleViewAction().setEnabled(False)
        self.file_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.addToolBar(self.file_toolbar)
                # ID for csv file
        self.file_toolbar.addSeparator()
        self.file_toolbar.addWidget(QLabel("CSV ID: "))
        self.id_txt = QLineEdit(
            maxLength=10,
            textEdited=self.change_csv_id
        )
        self.id_txt.setFixedWidth(80)
        self.id_txt.setPlaceholderText("max 10 char")
        self.file_toolbar.addWidget(self.id_txt)
                # Icon for data export to csv
        self.file_toolbar.addSeparator()
        self.csv_export_icon = QAction(QtGui.QIcon('Icons/script-excel.png'), "Export .csv")
        self.csv_export_icon.setCheckable(True)
        self.csv_export_icon.triggered.connect(self.doExportcsv)
        self.csv_export_icon.setShortcut(QtGui.QKeySequence("Ctrl+e"))
        self.file_toolbar.addAction(self.csv_export_icon)
        self.file_toolbar.addSeparator()
        self.file_menu.addAction(self.csv_export_icon)
            # Option toolbar
        self.opt_toolbar = QToolBar("Option toolbar")
                # Cannot be moved
        self.opt_toolbar.setMovable(False)
        self.opt_toolbar.setFloatable(False)
                # Cannot be hidden
        self.opt_toolbar.toggleViewAction().setEnabled(False)
        self.opt_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.addToolBar(self.opt_toolbar)

        # Graph's tab panel
        self.graph_tab = grp.MyTabWidget()
        self.graph_tab.setDisabled(True)

        # Serial interface
            # Button to start R measurement with PSoC readout circuit
        self.res_stream_btn = QPushButton(
            text="Start measure",
            checkable=True,
            toggled=self.psoc_res_measure_start
        )
        self.res_stream_btn.setDisabled(True)
            # Button to stop any data streaming
        self.stop_stream_btn = QPushButton(
            text="STOP",
            checkable=True,
            toggled=self.stop_data_stream
        )
        self.stop_stream_btn.setDisabled(True)
            # User input line
        self.input_txt = QLineEdit()
        self.input_txt.setDisabled(True)
        self.send_btn = QPushButton(
            text="Send",
            clicked=self.send_input
        )
        self.clear_btn = QPushButton(
            text="Clear",
            clicked=self.graph_tab.output_window.clear
        )
        self.send_btn.setDisabled(True)
        self.clear_btn.setDisabled(True)

        # Logger display
        self.logger_interface = displays.LoggerDisplay()
        self.logger_interface.signals.append_signal.connect(self.update_log_window)
        self.logger_txt = displays.LoggerDisplay().txt_window
                
        # layout
        streaming_hlay = QHBoxLayout()
        streaming_hlay.addWidget(self.res_stream_btn)
        streaming_hlay.addWidget(self.stop_stream_btn)
        input_hlay = QHBoxLayout()
        input_hlay.addWidget(self.input_txt)
        input_hlay.addWidget(self.send_btn)
        input_hlay.addWidget(self.clear_btn)
        serial_port_hlay = QVBoxLayout()
        serial_port_hlay.addWidget(self.conn_btn,1)
        serial_port_hlay.addWidget(self.com_list_widget)
        logger_and_serial = QHBoxLayout()
        logger_and_serial.addWidget(self.logger_txt,5)
        logger_and_serial.addLayout(serial_port_hlay,1)
        vlay = QVBoxLayout()
        vlay.addLayout(streaming_hlay)
        vlay.addLayout(input_hlay)
        vlay.addWidget(self.graph_tab,10)
        vlay.addLayout(logger_and_serial,2)
        widget = QWidget()
        widget.setLayout(vlay)
        self.setCentralWidget(widget)



    ####################
    # SERIAL INTERFACE #
    ####################
    def serialscan(self):
        """
        This method performs an automatic connection with target device.

        Scans all the available ports with a device
        connected to them, then searches across them for the target device.
        If found, the GUI connects to it, otherwise an error will be generated.
        """
        self.port_text = ""
        # Combo box to hold ports list
        self.com_list_widget = QComboBox()
        self.com_list_widget.currentTextChanged.connect(self.port_changed)
        
        # Connect-to-port button
        self.conn_btn = QPushButton(
            text=("Connect to port {}".format(self.port_text)), 
            checkable=True,
            toggled=self.on_toggled
        )
        if not wrk.CONNECTION_STATUS:
            self.com_list_widget.setDisabled(True)
            self.conn_btn.setDisabled(True)

        # Setup scan worker (already defined)
        self.scan_worker.signals.error.connect(self.scanworker_error)
        self.scan_worker.signals.device.connect(self.update_port_list)
        # Execute the worker
        self.threadpool.start(self.scan_worker)

        # Setup progress bar worker (already defined)
        self.bar_worker.signals.progress.connect(self.update_progress)
        self.bar_worker.signals.finished.connect(self.check_progress)
        # Execute the worker
        self.threadpool.start(self.bar_worker)


    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        """
        This method enables connection and disconnection from selected serial port.

        :param checked: State of the ``conn_btn``.
        :type checked: bool
        """
        if checked:
            # Setup reading worker
            self.read_worker = wrk.ReadWorker(self.port_text) # needs to be re defined
            self.read_worker.is_streaming = True
            self.read_worker.signals.data.connect(self.handle_data)
            self.read_worker.signals.status.connect(self.check_serialport_status)
            # Execute the worker
            self.threadpool.start(self.read_worker)
        else:
            # Stop streaming
            self.read_worker.is_streaming = False
            # Kill thread
            self.read_worker.is_killed = True
            # Disable all the widgets
            self.com_list_widget.setDisabled(False) # enable the possibility to change port
            self.res_stream_btn.setDisabled(True)
            self.input_txt.setDisabled(True)
            self.stop_stream_btn.setDisabled(True)
            self.send_btn.setDisabled(True)
            self.clear_btn.setDisabled(True)
            self.graph_tab.setDisabled(True)
            self.conn_btn.setText(
                "Connect to port {}".format(self.port_text)
            )


    @QtCore.pyqtSlot(bool)
    def psoc_res_measure_start(self, checked):
        """
        This method starts resistance measurement using PSoC readout circuit.

        :param checked: State of the ``res_stream_btn``.
        :type checked: bool
        """
        if checked:
            self.read_worker.send(wrk.PSOC_RES_CMD)
            logger.info("PSoC resistance measurement started")
            self.res_stream_btn.setDisabled(True)
            self.stop_stream_btn.setChecked(False)
            self.graph_tab.clear_plot_btn.setDisabled(True)
            #self.start = time.time()


    @QtCore.pyqtSlot(bool)
    def stop_data_stream(self, checked):
        """
        This method stops measurement and, if enabled, exports data to csv file.

        .. note:: 
            This function does **not** set ``is_streaming`` to ``False``, neither kills the 
            ``read_woker`` thread. This operation is performed only by :py:meth:`on_toggle`.

        :param checked: State of the ``stop_stream_btn``.
        :type checked: bool
        """
        if checked:
            self.read_worker.send(wrk.STOP_STREAM_CMD)
            logger.info("Measurement stopped")
            if self.res_stream_btn.isChecked():
                csv_exporter.export_psoc_res_data()

            #self.stop = time.time()
            #t = self.stop-self.start
            #logger.info("time: {}, samples: {}".format(t, len(csv_exporter.PSoC_res_dict['Resistance'])))

            # Reset the dictionaries
            csv_exporter.PSoC_res_dict.update({
                'Resistance': []
            })
            
            self.res_stream_btn.setChecked(False)
            self.res_stream_btn.setDisabled(False)
            self.graph_tab.clear_plot_btn.setDisabled(False)
            

    def send_input(self):
        """
        This method sends user typed text to the connected device.
        """
        self.read_worker.send(self.input_txt.text())



    #######################
    # SCAN WORKER SIGNALS #
    #######################
    def scanworker_error(self, text):
        """
        This method handles errors generated when no target device is found on any port. 
        Adjusts status bar label and COM port list.

        :param text: Error string to be printed on console.
        :type text: str
        """
        self.status_label.setText("Searching for target device...")
        self.com_list_widget.clear()

        if "setup" in text:
            # Device was found, but connection failed.. automatically re-start the search
            self.scan_worker.device_found = False

            
    def update_port_list(self, port):
        """
        This method updates serial ports list widget based on active ones.

        :param port: Port name to which a device is connected.
        :type port: str
        """
        if self.com_list_widget.findText(port) == -1: # avoids duplicates
            self.com_list_widget.addItems([port])
        self.com_list_widget.setCurrentText(port)



    ######################
    # BAR WORKER SIGNALS #
    ######################
    def update_progress(self, progress):
        """
        This method updates the progress bar during the initial search-for-target-devide phase.

        :param progress: Progress quantification from 0 to 100% to be visualized on screen.
        :type progress: int

        .. note:: 
            The percentage is time based, not event-related. The only event that
            has an impact on the percentage displayed is the connection with the
            target device, upon which 100% will be displayed.
        """
        self.progress_bar.setValue(progress)


    def check_progress(self):
        """
        This method operates on the progress bar depending on the status of the 
        search-for-target-devide and connection phases.
        """
        if wrk.CONNECTION_STATUS != wrk.DEVICE_CONN:
            # Setup progress bar worker
            self.bar_worker = wrk.BarWorker() # needs to be re defined
            self.bar_worker.signals.progress.connect(self.update_progress)
            self.bar_worker.signals.finished.connect(self.check_progress)
            # Execute the worker
            self.threadpool.start(self.bar_worker)
        else:
            # Remove widgets from status bar
            time.sleep(0.5)
            self.status_bar.removeWidget(self.progress_bar)
            self.status_bar.removeWidget(self.status_label)
            # Enable the interface and set status tips (not done before to avoid hiding the progress bar)
            self.conn_btn.setDisabled(False)
            self.conn_btn.setChecked(True)
            self.id_txt.setStatusTip("Insert identifier for .csv file. Max 5 char allowed")
            self.csv_export_icon.setStatusTip("Enable/Disable .csv export")
            self.res_stream_btn.setStatusTip("Start resistance measurement with PSoC readout circuit")
            self.stop_stream_btn.setStatusTip("Stop any active streaming")
            self.input_txt.setStatusTip("User input to be sent to target device")
            self.send_btn.setStatusTip("Send user input to target device")
            self.clear_btn.setStatusTip("Clear 'Reading...' tab history")
            self.logger_txt.setStatusTip("Logging information display")
            self.com_list_widget.setStatusTip("List of eligible ports")
            self.conn_btn.setStatusTip("Connect/Disconnect from serial port")

            logger.success("GUI connected with device on port {}.".format(self.com_list_widget.currentText()))



    #######################
    # READ WORKER SIGNALS #
    #######################
    def handle_data(self, packet_type, data):
        """
        This method updates the output window and the plot; it also updates the dictionary in which the 
        resistance values, measured by the instrument and transmitted to the host machine, are stored.
        
        :param packet_type: Identifier of the type of data that have been received.
        :type packet_type: str
        :param data: The actual data being received.
        :type data: list
        """
        if packet_type != "Reset info":
            # Reset info is handled differently
            for i in range(0, len(data)):
                self.graph_tab.output_window.append(str(data[i]))
                self.graph_tab.output_window.moveCursor(QtGui.QTextCursor.End)

        if packet_type == "Reset info":
            # Reset stream buttons to relfect device status (not streaming)
            self.res_stream_btn.setChecked(False)
            self.res_stream_btn.setDisabled(False)
            self.stop_stream_btn.setChecked(False)
            # Clear plots
            self.graph_tab.clear_plot(1, self.graph_tab.psoc_r_graph) # 1 is just random to account for state parameter
        elif packet_type == "PSoC res measurement":
            # Update plot and dict
            self.graph_tab.update_plot(data[0], self.graph_tab.x_psoc_r, self.graph_tab.y_psoc_r, self.graph_tab.psoc_rLoad_line)
            csv_exporter.PSoC_res_dict['Resistance'].append(data[0])



    def check_serialport_status(self, port_name, status):
        """
        This method handles the status of the connection to serial port phase.

        :param port_name: Port name to which a connection is being estabilished.
        :type port_name: str
        :param status: Paramenter representing the status of the connection (0 - error during opening, 1 - success, 2 - error during reading).
        :type status: int
        """
        if status == 0:
            self.conn_btn.setChecked(False)
            self.read_worker.is_streaming = False
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning")
            dlg.setText("Failed to open port {}. Please check the connection and try again.".format(port_name))
            dlg.setStandardButtons(QMessageBox.Ok)
            dlg.setIcon(QMessageBox.Warning)
            button = dlg.exec_()
        elif status == 1:
            # Clear user line and output window tab
            self.graph_tab.output_window.clear()
            self.input_txt.clear()
            # Enable all the widgets on the interface
            self.com_list_widget.setDisabled(True) # disable the possibility to change COM port when already connected
            self.res_stream_btn.setDisabled(False)
            self.input_txt.setDisabled(False)
            self.stop_stream_btn.setDisabled(False)
            self.send_btn.setDisabled(False)
            self.clear_btn.setDisabled(False)
            self.graph_tab.setDisabled(False)
            self.conn_btn.setText(
                "Disconnect from port {}".format(port_name)
            )
        elif status == 2:
            self.conn_btn.setChecked(False)
            # This error is generated upon device disconnection from port, so the device
            # has to be reconnected --> will be reset --> it won't stream once reset
            # --> we can set streaming buttons as default to not confuse the user
            self.stop_stream_btn.setChecked(False)
            self.res_stream_btn.setChecked(False)
            self.read_worker.is_streaming = False
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning")
            dlg.setText("Cannot communicate with port {}. Please check the connection and try again.".format(port_name))
            dlg.setStandardButtons(QMessageBox.Ok)
            dlg.setIcon(QMessageBox.Warning)
            button = dlg.exec_()


    ###############
    #  UTILITIES  #
    ###############
    def port_changed(self):
        """
        This method updates ``conn_btn`` label based on selected port.
        """
        self.port_text = self.com_list_widget.currentText()
        self.conn_btn.setText("Connect to port {}".format(self.port_text))


    def exitHandler(self):
        """
        This method kills every possible running thread upon exiting application.

        .. note::
            Due to the time it takes to scan each single port, if prematurely
            interupted the ``scan_worker`` thread may raise a ``RuntimeError`` in the terminal,
            but its functions that use a serial port are designed to also close said port, hence
            after very few seconds (necessary to terminate the operations) the app can 
            be run again without any problem.
        """
        displays.KILL = True # avoids printing to a not-anymore-existing widget
        self.scan_worker.is_killed = True
        self.bar_worker.is_killed = True
        self.read_worker.is_streaming = False
        self.read_worker.is_killed = True


    def update_log_window(self, text):
        """
        This method updates the logger display.

        :param text: Text to be displayed.
        :type text: str
        """
        self.logger_txt.append(text)
        self.logger_txt.moveCursor(QtGui.QTextCursor.End)


    @QtCore.pyqtSlot(str)
    def change_csv_id(self, id):
        """
        This method updates the csv identifier according to user input.

        :param id: ID typed by the user inside corresponding box.
        :type id: str
        """
        csv_exporter.id = id.replace(' ','-') # avoid spaces in the id


    def doExportcsv(self, checked):
        """
        This method enables csv export of received data.
        """
        if checked:
            logger.info("Data export to .csv file enabled")
            csv_exporter.EXPORT = True
        else:
            logger.info("Data export to .csv file disabled")
            csv_exporter.EXPORT = False



#############
#  RUN APP  #
#############
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.aboutToQuit.connect(w.exitHandler)
    w.show()
    sys.exit(app.exec_())



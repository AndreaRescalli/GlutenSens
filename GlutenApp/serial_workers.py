import time

import struct

import math

from loguru import logger

from PyQt5.QtCore import (
    QObject, 
    QRunnable, 
    pyqtSignal, 
    pyqtSlot
)

import serial
import serial.tools.list_ports



##############
#  COMMANDS  #
##############
CONN_REQUEST_CMD = 'c'
"""
Command to find target device.
"""

PSOC_RES_CMD = 'm'
"""
Command to initiate PSoC resistance measurement.
"""

STOP_STREAM_CMD = 's'
"""
Command to stop data streaming.
"""

RESET_CMD = 'r'
"""
Command to retrieve information such as sampling frequency.
"""



##############
#  SETTINGS  #
##############
BAUDRATE = 115200
"""
Baudrate of serial port.
"""



##############
#   MACROS   #
##############
    # --------------- CONNECTION
DEVICE_NOT_CONN = False    
"""
Target device not connected.
"""

DEVICE_CONN = True
"""
Target device connected.
"""

CONNECTION_STATUS = DEVICE_NOT_CONN
"""
Variable that holds the status of the connection between GUI and target device.
"""

CONNECTING = 0
"""
Attempting to connect to a port.
"""

DEV_NOT_FOUND = 1
"""
Target device NOT found on a port.
"""

DEV_FOUND = 2
"""
Target device found on a port.
"""

DEV_CONN = 3
"""
Connection with target device estabilished.
"""

    # --------------- DATA STREAM
HEADER_PSOC_R_MEAS = 0x0A    
"""
Header byte for incoming PSoC resistance measurements data.
"""

HEADER_RESET = 0x00
"""
Header byte for reset info.
"""

TAIL_MEAS_PACKETS = 0xFF
"""
Tail byte for incoming measurements data.
"""

TAIL_RESET = 0x0F
"""
Tail byte for reset info.
"""

PSOC_RES_SAMPLE_RATE = 10 # hardcoded but also retrieved upon connection to be sure
"""
PSoC resistance measurement display rate in Hz. 
Hardcoded but also retrieved upon connection to be sure.
"""



################
# SCAN_SIGNALS #
################
class ScanWorkerSignals(QObject):
    """
    Class that defines the signals available to a :py:meth:`ScanWorker` object.
    """
    #: Error *(str)* to be printed on console.
    error = pyqtSignal(str)
    #: Port name *(str)* to which a Cypress device is connected.
    device = pyqtSignal(str)



###############
# SCAN_WORKER #
###############
class ScanWorker(QRunnable):
    """
    Main class for serial scan: searches for target device.
    """
    def __init__(self):
        """
        Init a scan worker.
        """
        self.is_killed = False
        super().__init__()
        # Init port, params and signals
        self.ser = serial.Serial()
        self.port = None
        self.baudrate = None
        self.signals = ScanWorkerSignals()


    @pyqtSlot()
    def run(self):
        """
        This method scans the active serial ports to search for target device.
        """
        logger.trace("Serial ports scan thread initiated.")
        global CONNECTION_STATUS
        self.device_found = False
        while (not self.device_found):
            if self.is_killed:
                logger.warning("App closed while scan was running.")
                return
            psoc_ports = [
                p.name
                for p in serial.tools.list_ports.comports()
                # The following option will speed-up the research but if the PC does not
                # recognize the device as 'Cypress' due to driver's issues, it will not
                # be able to find the device.
                #if 'Cypress' in p.manufacturer 
            ]
            if not psoc_ports:
                logger.critical("No Cypress device connected to any port. Please check your connections and try again.")
                self.signals.error.emit("No Cypress device connected to any port. Please check your connections and try again.")
                time.sleep(2) # allows for user reaction
            for port in psoc_ports:
                self.signals.device.emit(port)
                self.device_found = self.check_device(port)
                if (self.device_found):
                    self.port = port
                    self.baudrate = BAUDRATE
                    logger.debug("Target device found on port {}.".format(self.port))
                    time.sleep(1)
                    try:
                        self.ser = serial.Serial(
                            port=self.port, baudrate=self.baudrate, write_timeout=0, timeout=2)
                        if (self.ser.is_open):
                            self.ser.close()
                            CONNECTION_STATUS = DEVICE_CONN 
                            logger.debug("Connected to target device on port {}.".format(self.port))                       
                            break
                    except serial.SerialException:
                        self.signals.error.emit("Error during setup of port {}.".format(self.port))
                        logger.exception("Error during setup of port {}.".format(self.port))
                else:
                    logger.warning("No target device found on port {}.".format(port))
                    time.sleep(1)


    def check_device(self, port):
        """
        This method checks whether the current port has target device connected to it.

        :param port: Name of the port to be checked.
        :type port: str
        :returns: ``True`` or ``False`` based on whether the target device has been found on that port.
        :rtype: bool
        """
        logger.debug("Checking port {}.".format(port))
        try:
            time.sleep(0.5) # allows for connection of device when scan is already running.
                            # without this small delay the connection still happens but an
                            # error due to an initial opening failure is shown on terminal
            ser = serial.Serial(port=port, baudrate=BAUDRATE,
                                write_timeout=0, timeout=2)
            if (ser.is_open):
                try:
                    ser.write(CONN_REQUEST_CMD.encode('utf-8'))
                    logger.debug("Connection character {} written on port {}.".format(CONN_REQUEST_CMD, port))
                    time.sleep(1)
                    line = ''
                    while (ser.in_waiting > 0):
                        line += ser.read().decode('utf-8', errors='replace')
                    if ('$$$' in line):
                        ser.close()
                        time.sleep(2)
                        return True
                except:
                    logger.critical("Could not write connection character {} on port {}.".format(CONN_REQUEST_CMD, port))
        except serial.SerialException:
            logger.exception("Error during setup of port {}.".format(port))
            return False
        except ValueError:
            logger.exception("Error during setup of port {}.".format(port))
            return False
        return False



###############
# BAR_SIGNALS #
###############
class BarWorkerSignals(QObject):
    """
    Class that defines the signals available to a :py:meth:`BarWorker` object.
    """
    #: Progress *(int)* percentage to be displayed on application's status bar.
    progress = pyqtSignal(int)
    #: Signal emitted when progress bar is at 100%.
    finished = pyqtSignal()



##############
# BAR_WORKER #
##############
class BarWorker(QRunnable):
    """
    Main class for progress bar update.
    """
    def __init__(self):
        """
        Init a bar worker.
        """
        self.is_killed = False
        super().__init__()
        self.signals = BarWorkerSignals()


    @pyqtSlot()
    def run(self):
        """
        This method computes the percentage progress with which the progress bar will be updated.

        .. note:: 
            The percentage is time based, not event-related. The only event that
            has an impact on the percentage displayed is the connection with the
            target device, upon which 100% will be displayed.
        """
        logger.trace("Progress bar thread initiated.")
        global CONNECTION_STATUS
        total_n = 1000
        for n in range(total_n):
            if self.is_killed:
                logger.warning("App closed while scan was running.")
                return
            progress_pc = int(100*float(n+1)/total_n) # 0to100 as int
            if CONNECTION_STATUS != DEVICE_CONN:
                self.signals.progress.emit(progress_pc)
            else:
                self.signals.progress.emit(100)
                break
            time.sleep(0.01)

        self.signals.finished.emit()
                            


################
# READ_SIGNALS #
################
class ReadWorkerSignals(QObject):
    """
    Class that defines the signals available to a :py:meth:`ReadWorker` object.
    """
    #: Contains the type of data *(str)* and the actual data *(list)* received.
    data = pyqtSignal(str, list)
    #: Error *(str)* to be printed on console. 
    error = pyqtSignal(str)
    #: Contains the name of the COM port being used *(str)* and the status *(int)* of its connection (0 - error during opening, 1 - success, 2 - reading error).
    status = pyqtSignal(str, int)



###############
# READ_WORKER #
###############
class ReadWorker(QRunnable):
    """
    Main class for serial reading tasks.
    """
    def __init__(self, serial_port_name):
        """
        Init a read worker.
        """
        self.is_streaming = False
        self.is_killed = False
        self.read_state = 0
        self.packet_type = ""
        super().__init__()
        self.signals = ReadWorkerSignals()
        self.port = serial.Serial()
        self.port_name = serial_port_name


    @pyqtSlot()
    def run(self):
        """
        This method estabilishes a connection with desired serial port and collects incoming data.
        """
        logger.trace("Reading thread initiated.")
        global PSOC_RES_SAMPLE_RATE
        try:
            self.port = serial.Serial(port=self.port_name, baudrate=BAUDRATE,
                                    write_timeout=0, timeout=2)                
            if self.port.is_open:
                self.signals.status.emit(self.port_name, 1)
                logger.info("Succesfully connected to port {}.".format(self.port_name))
                self.port.write(RESET_CMD.encode('utf-8'))
        except serial.SerialException:
            self.signals.status.emit(self.port_name, 0)
            logger.exception("Error during setup of port {}.".format(self.port_name))

        while(self.is_streaming):
            try:
                if self.port.in_waiting > 0:
                    if self.read_state == 0:
                        header = self.port.read(1)
                        # Header byte
                        header = struct.unpack('B', header)[0]
                        if (header == HEADER_PSOC_R_MEAS  or
                            header == HEADER_RESET        or
                            header == 0x11):
                            self.read_state = 1
                            if (header == HEADER_PSOC_R_MEAS):
                                self.packet_type = "PSoC res measurement"
                            elif (header == HEADER_RESET):
                                self.packet_type = "Reset info"
                                logger.debug("Device reset.")
                            elif (header == 0x11):
                                self.packet_type = "Test"
                                logger.debug("Test.")
                    elif self.read_state == 1:
                        if self.packet_type == "PSoC res measurement":
                            res_raw = self.port.read(6)
                            res_raw = struct.unpack('6B', res_raw) # Data bytes
                            self.read_state = 2
                        elif self.packet_type == "Reset info":
                            info_raw = self.port.read(1)
                            # Data bytes
                            info_raw = struct.unpack('B', info_raw)[0]
                            self.read_state = 2
                        elif self.packet_type == "Test":
                            u_raw = self.port.read(4)
                            u_raw = struct.unpack('f', u_raw)[0] # Data bytes
                            self.read_state = 2
                    elif self.read_state == 2:
                        if self.packet_type == "PSoC res measurement":
                            psoc_r_tail = self.port.read(1)
                            # Tail byte
                            psoc_r_tail = struct.unpack('B', psoc_r_tail)[0]
                            if (psoc_r_tail == TAIL_MEAS_PACKETS):
                                # Handle data only if tail packet is correct
                                res = self.get_data(res_raw)
                                self.signals.data.emit(self.packet_type,[res])
                                self.read_state = 0
                        elif self.packet_type == "Reset info":
                            info_tail = self.port.read(1)
                            # Tail byte
                            info_tail = struct.unpack('B', info_tail)[0]
                            if (info_tail == TAIL_RESET):
                                PSOC_RES_SAMPLE_RATE = info_raw
                                logger.info("PSoC res sample rate changed to {} Hz.".format(PSOC_RES_SAMPLE_RATE))
                                self.signals.data.emit(self.packet_type,[0])
                                self.read_state = 0
                        elif self.packet_type == "Test":
                            test_tail = self.port.read(1)
                            # Tail byte
                            test_tail = struct.unpack('B', test_tail)[0]
                            if (test_tail == 0x0F):
                                # Handle data only if tail packet is correct
                                u = self.truncate(u_raw, 3)
                                self.signals.data.emit(self.packet_type,[u])
                                self.read_state = 0                               
                #time.sleep(0.001)
            except serial.SerialException:
                self.signals.status.emit(self.port_name, 2)
                logger.exception("Cannot communicate with port {}. Please check the connection and try again.".format(self.port_name))

        if self.is_killed:
                self.port.close()
                logger.info("Serial port {} closed.".format(self.port_name))
                return


    def send(self, char):
        """
        This method sends a single character on serial port.

        :param char: Character to be sent.
        :type char: char
        """
        try:
            self.port.write(char.encode('utf-8'))
            logger.debug("Written {} on port {}.".format(char, self.port_name))
        except:
            logger.exception("Could not write {} on port {}.".format(char, self.port_name))


    def truncate(self, number, digits) -> float:
        """
        This method is used to truncate the reconstructed float after 3 decimals.
        This is necessay because floating point precision of Python is higher than C, and if a 3 decimal float
        is sent to the GUI, once reconstructed it will have a lot more decimals, NOT PART OF THE ORIGINAL SIGNAL.

        :param number: Number to be truncated.
        :type char: float
        :param digits: Number of digits to maintain.
        :type digits: int

        :returns: Truncated number of desired decimal precision.
        :rtype: float
        """
        # Improve accuracy with floating point operations, to avoid truncate(16.4, 2) = 16.39 or truncate(-1.13, 2) = -1.12
        nbDecimals = len(str(number).split('.')[1]) 
        if nbDecimals <= digits:
            return number
        stepper = 10.0 ** digits
        return math.trunc(stepper * number) / stepper


    def get_data(self, data_raw):
        """
        This method reconstructs the measured resistance value from the 6 bytes received.

        :param data_raw: Array of 6 bytes containing resistance data to be reconstructed.
        :type data_raw: int

        :returns: Reconstructed value of resistance.
        :rtype: float

        .. note::
            The first 4 bytes of data_raw encodes the integer value, in Ohm:

            0. (0x???????? >> 24) & 0xFF
            1. (0x???????? >> 16) & 0xFF
            2. (0x???????? >> 8)  & 0xFF
            3. (0x????????)       & 0xFF

            The last 2 bytes encodes the decimal part as an integer.
            To get the decimal value they need to be divided by 1000.

            4. (0x???? >> 8)      & 0xFF
            5. (0x????)           & 0xFF

        """
        data_int = data_raw[0] << 24 | data_raw[1] << 16 | data_raw[2] << 8 | data_raw[3]
        data_dec = data_raw[4] << 8 | data_raw[5]
        data_final = round((data_int + data_dec/1000), 3)
        return data_final
import time

import struct

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
"""!
@brief Command to find target device.
"""
CONN_REQUEST_CMD = 'c'

"""!
@brief Command to initiate PSoC R measurement.
"""
PSOC_RES_CMD = 'm'

"""!
@brief Command to stop data streaming.
"""
STOP_STREAM_CMD = 's'

"""!
@brief Command to retrieve info.
"""
RESET_CMD = 'r'



##############
#  SETTINGS  #
##############
"""!
@brief Baudrate of serial port.
"""
BAUDRATE = 115200



##############
#   MACROS   #
##############
    # --------------- CONNECTION
"""!
@brief Target device not connected.
"""
DEVICE_NOT_CONN = False

"""!
@brief Target device connected.
"""
DEVICE_CONN = True

"""!
@brief Variable that holds the status of the connection between GUI and target device.
"""
CONNECTION_STATUS = DEVICE_NOT_CONN

"""!
@brief Attempting to connect to a port.
"""
CONNECTING = 0

"""!
@brief Target device NOT found on a port.
"""
DEV_NOT_FOUND = 1

"""!
@brief Target device found on a port.
"""
DEV_FOUND = 2

"""!
@brief Connection with target device estabilished.
"""
DEV_CONN = 3

    # --------------- DATA STREAM
"""!
@brief Header byte for incoming PSoC resistance measurements data.
"""
HEADER_PSOC_R_MEAS = 0x0A

"""!
@brief Header byte for reset info.
"""
HEADER_RESET = 0x00


"""!
@brief Tail byte for incoming capacitance measurements data.
"""
TAIL_MEAS_PACKETS = 0xFF

"""!
@brief Tail byte for reset info.
"""
TAIL_RESET = 0x0F

"""!
@brief PSoC resistance measurement display rate in Hz.
"""
PSOC_RES_SAMPLE_RATE = 40 # for now is default, should be retrieved upon connection



################
# SCAN_SIGNALS #
################
class ScanWorkerSignals(QObject):
    """!
    @brief Class that defines the signals available to a scanworker.

    Available signals (with respective inputs) are:
        - error:
            str --> error string to be printed on console
        - device:
            str --> port name to which a Cypress device is connected
    """
    error = pyqtSignal(str)
    device = pyqtSignal(str)



###############
# SCAN_WORKER #
###############
class ScanWorker(QRunnable):
    """!
    @brief Main class for serial scan: searches for target device.
    """
    def __init__(self):
        """!
        @brief Init worker.
        """
        self.is_killed = False
        super().__init__()
        # init port, params and signals
        self.ser = serial.Serial()
        self.port = None
        self.baudrate = None
        self.signals = ScanWorkerSignals()


    @pyqtSlot()
    def run(self):
        """!
        @brief Scan the serial ports to search for target device.
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
                # the following option will speed-up the research but if the PC does not
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
        """!
        @brief Check whether the current port has target device connected to it.
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
    """!
    @brief Class that defines the signals available to a barworker.

    Available signals (with respective inputs) are:
        - progress:
            int --> progress complete, from 0-100
        - finished
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal()



##############
# BAR_WORKER #
##############
class BarWorker(QRunnable):
    """!
    @brief Main class for progress bar update.
    """
    def __init__(self):
        """!
        @brief Init worker.
        """
        self.is_killed = False
        super().__init__()
        self.signals = BarWorkerSignals()


    @pyqtSlot()
    def run(self):
        """!
        @brief Compute the 0 to 100 %.
        
        The percentage is time based, not event related. The only event that
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
    """!
    @brief Class that defines the signals available to a readworker.

    Available signals (with respective inputs) are:
        - data:
            list  --> data to be printed on console and plotted
            str   --> packet type
        - error:
            str --> error string to be printed on console
        - status:
            str --> port name
            int --> macro representing the state (0 - error during opening, 1 - success, 2 - reading error)
    """
    data = pyqtSignal(str, list)
    error = pyqtSignal(str)
    status = pyqtSignal(str, int)



###############
# READ_WORKER #
###############
class ReadWorker(QRunnable):
    """!
    @brief Main class for serial reading tasks.
    """
    def __init__(self, serial_port_name):
        """!
        @brief Init worker.
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
        """!
        @brief Estabilish connection with desired serial port and collect data.
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
                            header == HEADER_RESET):
                            self.read_state = 1
                            if (header == HEADER_PSOC_R_MEAS):
                                self.packet_type = "PSoC res measurement"
                            elif (header == HEADER_RESET):
                                self.packet_type = "Reset info"
                                logger.debug("Device reset.")
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
                #time.sleep(0.001)
            except serial.SerialException:
                self.signals.status.emit(self.port_name, 2)
                logger.exception("Cannot communicate with port {}. Please check the connection and try again.".format(self.port_name))

        if self.is_killed:
                self.port.close()
                logger.info("Serial port {} closed.".format(self.port_name))
                return


    def send(self, char):
        """!
        @brief Basic function to send a single char on serial port.
        """
        try:
            self.port.write(char.encode('utf-8'))
            logger.debug("Written {} on port {}.".format(char, self.port_name))
        except:
            logger.exception("Could not write {} on port {}.".format(char, self.port_name))


    def get_data(self, data_raw):
        """!
        @brief Retrieve capacitance or resistance value measured from 6 bytes.

        data_raw has the following structure:
            The first 4 bytes encodes for the integer value, in pF or Ohm
            - [0]: (0x???????? >> 24) & 0xFF
            - [1]: (0x???????? >> 16) & 0xFF
            - [2]: (0x???????? >> 8)  & 0xFF
            - [3]: (0x????????)       & 0xFF
            The last two bytes encodes for the decimal part as an int16.
            To get the decimal value they need to be divided by 1000.
            - [4]: (0x???? >> 8)      & 0xFF
            - [5]: (0x????)           & 0xFF

        """
        data_int = data_raw[0] << 24 | data_raw[1] << 16 | data_raw[2] << 8 | data_raw[3]
        data_dec = data_raw[4] << 8 | data_raw[5]
        data_final = round((data_int + data_dec/1000), 3)
        return data_final
from PyQt5.QtWidgets import (
    QWidget, 
    QTabWidget, 
    QVBoxLayout,  
    QTextEdit
)

import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from pyqtgraph.functions import SI_PREFIXES_ASCII

import serial_workers as wrk



##############
# TAB WIDGET #
##############
class MyTabWidget(QWidget):
    def __init__(self):
        """!
        @brief Init MyTabWidget.
        """
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout()
  
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300, 200)
  
        # Add tabs
        self.tabs.addTab(self.tab1, "Reading...")
        self.tabs.addTab(self.tab2, "PSoC-R")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.output_window = QTextEdit(readOnly=True)
        self.tab1.layout.addWidget(self.output_window)
        self.tab1.setLayout(self.tab1.layout)

        # Create fourth tab
        self.tab2.layout = QVBoxLayout(self)
        self.psoc_r_graph = PlotWidget()
        self.tab2.layout.addWidget(self.psoc_r_graph)
        self.tab2.setLayout(self.tab2.layout)

        # Plot settings
            # Axes
        self.n_seconds = 30 # Number of seconds to display
        self.x_psoc_r, self.y_psoc_r, self.y_psoc_pot = self.define_axes(wrk.PSOC_RES_SAMPLE_RATE)
            # Add grid
        self.psoc_r_graph.showGrid(x=True, y=True)
            # Set background color
        self.psoc_r_graph.setBackground('w')
            # Add title
        self.psoc_r_graph.setTitle("Resistance measurements using PSoC readout circuit")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.psoc_r_graph.setLabel('left', 'Resistance [Ohm]', **styles)
        self.psoc_r_graph.setLabel('bottom', 'Time [s]', **styles)
            # Add legend
        self.psoc_r_graph.addLegend()

        # Plot data
        self.psoc_rLoad_line = self.plot(self.psoc_r_graph, self.x_psoc_r, self.y_psoc_r, 'Load', 'r')

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


    def plot(self, graph, x, y, curve_name, color):
        """!
        @brief Draw graph.
        """
        pen = pg.mkPen(color=color)
        line = graph.plot(x, y, name=curve_name, pen=pen)
        return line

  
    def update_plot(self, data, x_array, y_array, plot_line):
        """!
        @brief Update graph line with new data received.
        """
        # Update y values
        y_array.append(y_array.pop(0))
        y_array[-1] = data

        # Update plot with new values
        plot_line.setData(x_array, y_array)


    def clear_plot(self, graph):
        """!
        @brief Clear graph to account for sample rate changes.

        To always visualize seconds along the x axis while accounting for possible
        changes in the sample rate induced by the user, there is the need to re-
        compute the x axis whenever this happens, and update the corresponding plot.
        """
        if graph == self.psoc_r_graph:
            # Re-define axes
            self.x_psoc_r, self.y_psoc_r, self.y_psoc_pot = self.define_axes(wrk.PSOC_RES_SAMPLE_RATE)
            # Adjust lines
            self.psoc_rLoad_line.setData(self.x_psoc_r, self.y_psoc_r)


    def define_axes(self, sample_rate):
        """!
        @brief Define the x axis (and init y to 0) according to sample rate.

        The dependency on the sample rate is needed to adjust from sample per
        seconds to seconds (which is the units displayed on the x axis)
        """
        n_points = self.n_seconds * sample_rate # Number of points to plot

        time_between_points = (self.n_seconds)/float(n_points)
        x_axis = [x for x in range(-n_points, 0)]
        for j in range(n_points):
            x_axis[j] = -self.n_seconds + j * time_between_points
        y_axis = [0 for y in range(-n_points, 0)]

        if sample_rate == wrk.PSOC_RES_SAMPLE_RATE:
            y_axis_2 = [0 for y in range(-n_points, 0)]
            return x_axis, y_axis,y_axis_2
        else:
            return x_axis, y_axis     
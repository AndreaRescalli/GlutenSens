from PyQt5.QtWidgets import (
    QWidget, 
    QPushButton,
    QTabWidget, 
    QVBoxLayout,  
    QTextEdit
)

import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from pyqtgraph.functions import SI_PREFIXES_ASCII

from loguru import logger

import serial_workers as wrk



##############
# TAB WIDGET #
##############
class MyTabWidget(QWidget):
    """
    This class holds the tabs shown at the center of the application. The first tab hosts an
    output window on which numeric data will be printed, whereas the second tab hosts the data plot.
    """
    def __init__(self):
        """
        Init a tab widget.
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

        # Create second tab
        self.tab2.layout = QVBoxLayout(self)
        self.psoc_r_graph = PlotWidget()
        self.clear_plot_btn = QPushButton(
            text="Clear plot",
        )
        self.clear_plot_btn.clicked.connect(lambda state,plot=self.psoc_r_graph: self.clear_plot(state, plot))
        self.tab2.layout.addWidget(self.clear_plot_btn)
        self.tab2.layout.addWidget(self.psoc_r_graph)
        self.tab2.setLayout(self.tab2.layout)

        # Plot settings
            # Axes
        self.n_seconds = 30 # Number of seconds to display
        self.x_psoc_r, self.y_psoc_r = self.define_axes(wrk.PSOC_RES_SAMPLE_RATE)
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
        """
        This method overwrites the existing ``.plot`` method for a graph to offer flexibility in multiple-curves plots 
        and multiple plots scenarios.

        :param graph: Plot on which the user wants to draw.
        :type graph: PlotWidget
        :param x: Array of data to be shown on x-axis.
        :type x: double
        :param y: Array of data to be plotted.
        :type y: double
        :param curve_name: Name of the curve to be plotted. Will be shown in the legend.
        :type curve_name: str
        :param color: Color of the curve.
        :type color: str

        :returns: An object representing the plotted curve. It can be manipulated to update the plot without the need 
            to re-draw it. 
        """
        pen = pg.mkPen(color=color)
        line = graph.plot(x, y, name=curve_name, pen=pen)
        return line

  
    def update_plot(self, data, x_array, y_array, plot_line):
        """
        This method updates the plot curve with new data received.

        :param data: New data to update the plot with.
        :type data: double
        :param x: Array of data to be shown on x-axis.
        :type x: double
        :param y: Array of data to be plotted.
        :type y: double
        :param plot_line: Plot curve that needs to be updated with the new data.
        """
        # Update y values
        y_array.append(y_array.pop(0))
        y_array[-1] = data

        # Update plot with new values
        plot_line.setData(x_array, y_array)


    def clear_plot(self, state, graph):
        """
        This method clears the plot.

        :param state: Dummy variable. It holds the state of the ``clear_plot_btn`` when clicked but it is not used.
        :type state: int
        :param graph: Plot that needs to be cleared.
        :type graph: PlotWidget
        """
        if graph == self.psoc_r_graph:
            # Re-define axes
            self.x_psoc_r, self.y_psoc_r = self.define_axes(wrk.PSOC_RES_SAMPLE_RATE)
            # Adjust lines
            self.psoc_rLoad_line.setData(self.x_psoc_r, self.y_psoc_r)
            logger.debug("Plot cleared.")


    def define_axes(self, sample_rate):
        """
        This method defines the x axis (and init y axis to 0) according to a given sample rate.
        The dependency on the sample rate is needed to adjust from sample per
        seconds to seconds (which is the units displayed on the x axis).

        :param sample_rate: The sample rate of the acquired data.
        :type sample_rate: int

        :returns: The two axes in the form of two arrays.
        :rtype: tuple
        """
        # Number of points to plot
        n_points = self.n_seconds * sample_rate 

        time_between_points = (self.n_seconds)/float(n_points)
        x_axis = [x for x in range(-n_points, 0)]
        for j in range(n_points):
            x_axis[j] = -self.n_seconds + j * time_between_points
        y_axis = [0 for y in range(-n_points, 0)]

        return x_axis, y_axis     
import glob
import sys
import numpy as np
import planet_utils.planet as pl
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import (
    QDialog,
    QApplication,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
)

from PyQt5.QtWidgets import (
    QFileDialog,
    QLineEdit,
    QWidget,
    QPushButton,
    QApplication,
    QVBoxLayout,
    QLabel,
    QGraphicsView,
    QGraphicsPixmapItem,
    QGraphicsScene,
)

from matplotlib.patches import Rectangle
from matplotlib.figure import Figure

from planet_utils.planet_training_dataset_gui import *


class Window(QDialog):
    def __init__(self, planet_file_name, coords, output_folder, parent=None):
        super(Window, self).__init__(parent)
        self.planet_file_name = planet_file_name
        self.coords = coords
        self.output_folder = output_folder
        self.figure = plt.figure(figsize=(10, 18))

        self.canvas = FigureCanvas(self.figure)
        self.plot()

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.button1 = self.create_button(button_name="Aerosols")
        self.button2 = self.create_button(button_name="Clouds")
        self.button3 = self.create_button(button_name="Vegetation")
        self.button4 = self.create_button(button_name="Urban")

        self.button_write_coords = QPushButton(
            "WRITE COORDS TO TRAINING TEXT FILE")
        self.button_write_coords.clicked.connect(self.write_coords)
        self.button_write_coords.setStyleSheet(
            "background-color : rgb(0, 255, 0); font-size:20px"
        )

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.button_write_coords)
        layout.addWidget(self.canvas)

        buttons_layout = QHBoxLayout()
        [
            buttons_layout.addWidget(button)
            for button in (self.button1, self.button2, self.button3, self.button4)
        ]
        layout.addLayout(buttons_layout)

        buttons_layout.setContentsMargins(20, 20, 20, 20)
        buttons_layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.setLayout(layout)

    def create_button(self, button_name="Sample"):
        button_var = QPushButton(button_name)
        button_var.clicked.connect(self.onClicked)
        button_var.country = button_name
        button_var.setStyleSheet(
            "background-color : rgb(255, 0, 0); font-size:20px")
        return button_var

    def onClicked(self):
        #global coords, class_ids, cid, value_to_print
        global class_ids, cid, value_to_print
        radioButton = self.sender()
        [
            button.setStyleSheet(
                "background-color : rgb(255, 0, 0); font-size:20px")
            for button in (self.button1, self.button2, self.button3, self.button4)
        ]
        if radioButton.isEnabled():
            radioButton.setStyleSheet(
                "background-color : rgb(0, 255, 0); font-size:20px"
            )
            print("Selection is %s" % (radioButton.country))
            value_to_print = radioButton.country
            self.ax.figure.canvas.mpl_connect(
                "button_press_event", self.on_press)
            self.ax.figure.canvas.mpl_connect(
                "button_release_event", self.on_release)
            # self.ax.figure.canvas.mpl_connect('scroll_event', self.zoom_fun)

    def zoom_fun(self, event):
        print("HAVING FUN==========================")
        base_scale = 1.2
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * 0.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * 0.5
        xdata = event.xdata
        ydata = event.ydata
        if event.button == "up":
            scale_factor = 1 / base_scale
        elif event.button == "down":
            scale_factor = base_scale
        else:
            scale_factor = 1
            print(event.button)
        self.ax.set_xlim(
            [xdata - cur_xrange * scale_factor, xdata + cur_xrange * scale_factor]
        )
        self.ax.set_ylim(
            [ydata - cur_yrange * scale_factor, ydata + cur_yrange * scale_factor]
        )
        plt.draw()

    def on_press(self, event):
        print(
            "{} | x: {} and y: {}".format(
                value_to_print, np.round(event.xdata), np.round(event.ydata)
            )
        )
        self.x0 = event.xdata
        self.y0 = event.ydata
        self.lock = True
        ix, iy = event.xdata, event.ydata
        self.coords.append((ix, iy, value_to_print,))
        self.ax.figure.canvas.mpl_connect("motion_notify_event", self.on_move)

    def on_release(self, event):
        self.x1 = event.xdata
        self.y1 = event.ydata

        self.ax.add_patch(
            Rectangle(
                (self.x0, self.y0),
                self.x1 - self.x0,
                self.y1 - self.y0,
                facecolor="b",
                edgecolor="r",
                alpha=0.3,
            )
        )
        self.moving_rect.set_alpha(0.3)

        self.ax.figure.canvas.draw()
        self.lock = False
        ix, iy = event.xdata, event.ydata
        self.coords.append((ix, iy, value_to_print,))

    def on_move(self, event):
        self.x2 = event.xdata
        self.y2 = event.ydata
        if self.lock is True:
            self.moving_rect.set_width(self.x2 - self.x0)
            self.moving_rect.set_height(self.y2 - self.y0)
            self.moving_rect.set_xy((self.x0, self.y0))
            self.ax.figure.canvas.draw()
        else:
            None

    def plot(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.planet_reflectance = plot_planet_rgb(
            self.ax, self.planet_file_name)

        self.moving_rect = Rectangle(
            (0, 0), 1, 1, facecolor="b", edgecolor="r", alpha=0.3
        )
        self.ax.add_patch(self.moving_rect)
        self.canvas.draw()

    def write_coords(self, event):
        print("====================== WRITING COORDS ===================!")
        coords_text_output = coords_to_text(
            self.coords,
            reflectance=self.planet_reflectance,
            planet_filename=self.planet_file_name,
            output_filename=self.output_folder
            + self.planet_file_name.split("/")[-1].split(".")[0]
            + ".train_coords",
            reset=True,
        )

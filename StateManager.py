from tkinter import StringVar
import cv2
from PIL import Image
from PIL.ImageTk import PhotoImage
from struct import unpack
import numpy as np
from matplotlib import pyplot as plt
from utils import \
    generate_grayscale, \
    generate_law_gamma, \
    generate_bw, \
    generate_negative, \
    salt_and_pepper, \
    open_image
from copy import deepcopy


# Custom subject class that triggers the update method of classes when variables are changed
class Subject:
    def __init__(self):
        self._observers = []

    # Notifies all listeners to the state changes
    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.notify(self)

    # Adds a new listener
    def subscribe(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    # Removes a listener
    def unsubscribe(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass


# Stores all the states that are shared among all the classes
class StateManager(Subject):
    def __init__(self):
        Subject.__init__(self)
        # All private properties are states that notify listeners that their values had changed

        # Current image displayed
        self._curr_img: Image = None

        # Default image without the filters
        self._default_img: Image = None

        # All image headers (if the file is PCX)
        self._img_headers = {}

        # All channel histograms of the current image
        self._histograms = ()

        # All filtered versions of the image
        self._filters = {}

        # All color channels
        self.channel_images = ()

        # Current histogram displayed
        self.hist_displayed = "red"

        # Booleans that help isolate which state had changed
        self.hist_changed = False
        self.headers_changed = False
        self.filters_changed = False
        self.img_changed = False

        # Status text displayed at the bottom of the window
        self.status = StringVar()
        self.status.set("Application started.")

    @property
    def img_headers(self):
        return self._img_headers

    @property
    def histograms(self):
        return self._histograms

    @property
    def filters(self):
        return self._filters

    @property
    def curr_img(self):
        return self._curr_img

    @property
    # Convert to cv2 instead of a Pillow Image Type
    def curr_cv2_img(self):
        np_array = np.array(self._curr_img)
        return cv2.cvtColor(np_array, cv2.COLOR_RGB2BGR)

    @property
    def default_img(self):
        return self._default_img

    @property
    # Convert to cv2 instead of a Pillow Image Type
    def default_cv2_img(self):
        if self._default_img is None:
            return None
        np_array = np.array(self._default_img)
        return cv2.cvtColor(np_array, cv2.COLOR_RGB2BGR)

    @img_headers.setter
    # Update the image headers then notify listeners
    def img_headers(self, img_headers: dict):
        self._img_headers = img_headers
        self.hist_changed = False
        self.filters_changed = False
        self.img_changed = False
        self.headers_changed = True
        self.notify()

    @histograms.setter
    # Update the histograms then notify listeners
    def histograms(self, histograms: tuple):
        self._histograms = histograms
        self.headers_changed = False
        self.filters_changed = False
        self.img_changed = False
        self.hist_changed = True
        self.notify()

    @filters.setter
    # Update the filters then notify listeners
    def filters(self, filters: dict):
        self._filters = filters
        self.headers_changed = False
        self.hist_changed = False
        self.img_changed = False
        self.filters_changed = True
        self.notify()

    @curr_img.setter
    # Update the current image then notify listeners
    def curr_img(self, img: Image):
        self._curr_img = img
        self.headers_changed = False
        self.hist_changed = False
        self.filters_changed = False
        self.img_changed = True
        self.notify()

    @default_img.setter
    # Update the default image then notify listeners
    def default_img(self, img: Image):
        self._default_img = img
        self.headers_changed = False
        self.hist_changed = False
        self.filters_changed = False
        self.img_changed = True
        self.notify()

    # Guide 3
    # Generates a histogram for every channel and its corresponding color channel
    def generate_histogram(self, screen_size):
        channel_img_list = []
        channel_histogram_list = []
        channel_list = {"red": [0, 1], "green": [0, 2], "blue": [1, 2]}

        # Algo for channels
        for channel_name in channel_list:
            channel = deepcopy(self.curr_cv2_img)
            channel[:, :, channel_list[channel_name][0]] = 0
            channel[:, :, channel_list[channel_name][1]] = 0

            # read image from folder and converts it to RGB because cv2.cvtColor returns BGR
            channel = cv2.cvtColor(channel, cv2.COLOR_BGR2RGB)
            channel_img = Image.fromarray(channel)
            channel_img.thumbnail(screen_size, Image.LANCZOS)
            channel_img_list.append(PhotoImage(channel_img))

            # get sum and make 1d array
            channel_image_values = channel.sum(axis=2).ravel()
            bars, bins = np.histogram(channel_image_values, range(257))

            # Generate the plot and convert it to image
            fig = plt.figure()
            plt.hist(channel_image_values, bins, color=channel_name)
            fig.canvas.draw()
            img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
            img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            img = Image.fromarray(img)
            img.thumbnail(screen_size, Image.LANCZOS)
            channel_histogram_list.append(PhotoImage(img))

        plt.close()
        # Change the current channel images and histograms then notify the listeners
        self.channel_images = tuple(channel_img_list)
        self.histograms = tuple(channel_histogram_list)

    # Read .PCX header files - Guide 2
    def read_pcx_header(self, file):

        img_headers = {}

        # opens the file and reads it as binary
        with open(file, 'rb') as pcx:
            # Unpacking binary header file depending on the size
            img_headers['manufacturer'] = unpack('B', pcx.read(1))[0]
            img_headers['version'] = unpack('B', pcx.read(1))[0]
            img_headers['encoding '] = unpack('B', pcx.read(1))[0]
            img_headers['bpp'] = unpack('B', pcx.read(1))[0]
            img_headers['dimensions'] = (unpack('H', pcx.read(2))[0],
                                         unpack('H', pcx.read(2))[0],
                                         unpack('H', pcx.read(2))[0],
                                         unpack('H', pcx.read(2))[0])
            img_headers['hdpi'] = unpack('H', pcx.read(2))[0]
            img_headers['vdpi'] = unpack('H', pcx.read(2))[0]

            pcx.seek(65, 0)
            img_headers['ncp'] = unpack('B', pcx.read(1))[0]

            img_headers['bpl'] = unpack('H', pcx.read(2))[0]
            img_headers['palette_info'] = unpack('H', pcx.read(2))[0]
            img_headers['hss'] = unpack('H', pcx.read(2))[0]
            img_headers['vss'] = unpack('H', pcx.read(2))[0]
        self.img_headers = img_headers

    # Generate all image filters
    def generate_all_filters(self):
        # read image from folder and converts it to RGB because cv2.cvtColor returns BGR
        cv2_image = cv2.cvtColor(self.curr_cv2_img, cv2.COLOR_BGR2GRAY)
        png_image = deepcopy(self.curr_img)
        # Generate the grayscale
        grayscale = generate_grayscale(png_image)

        self.filters = {
            # Default image
            "Default": PhotoImage(self.default_img),

            # convert to grayscale
            "Grayscale": PhotoImage(deepcopy(grayscale)),

            # salt and pepper
            "Salt and Pepper": salt_and_pepper(deepcopy(cv2_image)),

            # negative for the colored image
            "Colored Negative": generate_negative(deepcopy(png_image)),

            # negative for the grayscale image
            "Grayscale Negative": generate_negative(deepcopy(grayscale)),

            # black and white
            "Black and White": generate_bw(deepcopy(cv2_image)),

            # power law gamma
            "Low Gamma": generate_law_gamma(self.curr_cv2_img),
        }

    # Opens an image and properly formats it
    def process_image(self):
        try:

            # Open file dialog
            image_path = open_image()

            image = Image.open(image_path)

            # Set image to state manager
            image_name = image_path.split("/")[-1]

            # Display headers if .pcx image
            if image.format == "PCX":
                self.read_pcx_header(image_path)

            # Convert image to PNG for channels algo and save to same folder as this file
            if image.info.get("transparency", None) is not None:
                png_image = image.convert("RGBA")
            else:
                png_image = image.convert("RGB")

            # Set the current image and notify listeners
            self.curr_img = png_image
            self.default_img = png_image
            self.status.set(f"{image_name} opened.")
            self.status.set("Generating filters...")
            self.generate_all_filters()

            self.status.set("Generated filters")

        except AttributeError:
            # Display error on failure
            pass

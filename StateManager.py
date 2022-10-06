from tkinter import Frame, Listbox, StringVar
import cv2
from PIL import Image, ImageTk
from struct import unpack
import numpy as np
from matplotlib import pyplot as plt


# Custom subject class that triggers the update method of classes when variables are changed
class Subject:
    def __init__(self):
        self._observers = []

    def update(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)

    def subscribe(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass


# Stores variables and their states, if a specific variable/state changes then other classes are notified
class StateManager(Subject):
    def __init__(self):
        Subject.__init__(self)
        self._image: Image = None
        self._img_path = ""
        self._img_headers = {}
        self._histograms = ()
        self.channel_images = ()
        self.red = None

        self.hist_displayed = "red"

        self.status = StringVar()
        self.status.set("Application started.")

    @property
    def image(self):
        return self._image

    @property
    def img_path(self):
        return self._img_path

    @property
    def img_headers(self):
        return self._img_headers

    @property
    def histograms(self):
        return self._histograms

    @image.setter
    def image(self, image: Image):
        self._image = image

    @img_path.setter
    def img_path(self, img_path):
        self._img_path = img_path

    @img_headers.setter
    def img_headers(self, img_headers):
        self._img_headers = img_headers
        self.update()

    @histograms.setter
    def histograms(self, histograms: tuple):
        self._histograms = histograms
        self.update()

    # Generates a histogram for every channel and its corresponding color channel
    def generate_histogram(self, screen_size):
        # Algo for channels
        red_channel = cv2.imread('./assets/pic.png')
        red_channel[:, :, 0] = 0
        red_channel[:, :, 1] = 0
        cv2.imwrite('./assets/red_channel.png', red_channel)
        red_channel_img = Image.open('./assets/red_channel.png')
        red_channel_img.thumbnail(screen_size, Image.LANCZOS)
        red_channel_img = ImageTk.PhotoImage(red_channel_img)

        green_channel = cv2.imread('./assets/pic.png')
        green_channel[:, :, 0] = 0
        green_channel[:, :, 2] = 0
        cv2.imwrite('./assets/green_channel.png', green_channel)
        green_channel_img = Image.open('./assets/green_channel.png')
        green_channel_img.thumbnail(screen_size, Image.LANCZOS)
        green_channel_img = ImageTk.PhotoImage(green_channel_img)

        blue_channel = cv2.imread('./assets/pic.png')
        blue_channel[:, :, 1] = 0
        blue_channel[:, :, 2] = 0
        cv2.imwrite('./assets/blue_channel.png', blue_channel)
        blue_channel_img = Image.open('./assets/blue_channel.png')
        blue_channel_img.thumbnail(screen_size, Image.LANCZOS)
        blue_channel_img = ImageTk.PhotoImage(blue_channel_img)

        self.channel_images = (red_channel_img, green_channel_img, blue_channel_img)

        # read image from folder and converts it to RGB because cv2.cvtColor returns BGR
        # reads red picture; if you want green/blue, change file name
        gen_red_image = cv2.cvtColor(red_channel, cv2.COLOR_BGR2RGB)
        gen_green_image = cv2.cvtColor(green_channel, cv2.COLOR_BGR2RGB)
        gen_blue_image = cv2.cvtColor(blue_channel, cv2.COLOR_BGR2RGB)

        # get sum and make 1d array
        red_image_values = gen_red_image.sum(axis=2).ravel()
        bars, bins = np.histogram(red_image_values, range(257))

        plt.figure()
        plt.hist(red_image_values, bins, color="red")
        plt.savefig("./assets/red_hist.png")
        red_img = Image.open("./assets/red_hist.png")
        red_img.thumbnail(screen_size, Image.LANCZOS)
        red_channel = ImageTk.PhotoImage(red_img)
        self.red = red_channel

        green_image_values = gen_green_image.sum(axis=2).ravel()
        bars, bins = np.histogram(gen_green_image, range(257))

        plt.figure()
        plt.hist(green_image_values, bins, color="green")
        plt.savefig("./assets/green_hist.png")
        green_img = Image.open("./assets/green_hist.png")
        green_img.thumbnail(screen_size, Image.LANCZOS)
        green_channel = ImageTk.PhotoImage(green_img)

        blue_image_values = gen_blue_image.sum(axis=2).ravel()
        bars, bins = np.histogram(gen_blue_image, range(257))

        plt.figure()
        plt.hist(blue_image_values, bins, color="blue")
        plt.savefig("./assets/blue_hist.png")
        blue_img = Image.open("./assets/blue_hist.png")
        blue_img.thumbnail(screen_size, Image.LANCZOS)
        blue_channel = ImageTk.PhotoImage(blue_img)

        self.histograms = (red_channel, green_channel, blue_channel)

    # Read .PCX header files
    def read_pcx_header(self, file):
        img_headers = {}
        with open(file, 'rb') as pcx:
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

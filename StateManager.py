from tkinter import StringVar
from tkinter.ttk import Notebook
import cv2
from PIL import Image
from PIL.ImageTk import PhotoImage
from struct import unpack
import numpy as np
from matplotlib import pyplot as plt
from ImageFrame import ImageFrame
from utils import \
    generate_grayscale, \
    generate_negative_grayscale, \
    generate_low_gamma, \
    generate_bw, \
    generate_colored_negative, \
    salt_and_pepper


# Custom subject class that triggers the update method of classes when variables are changed
class Subject:
    def __init__(self):
        self._observers = []

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.notify(self)

    def subscribe(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass


class StateManager(Subject):
    def __init__(self, notebook: Notebook):
        Subject.__init__(self)
        self._notebook = notebook
        # self._frame_list: list[ImageFrame] = []
        self._frame_dict: dict = {}
        self._tab_count = 0

        self._img_header_dict: dict = {}
        self._histograms_dict: dict = {}
        self._filters_dict: dict = {}
        self._img_headers = {}
        self._histograms = ()
        self._filters = {}
        self.channel_images = ()

        self.hist_displayed = "red"
        self.hist_changed = False
        self.headers_changed = False
        self.filters_changed = False

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

    @img_headers.setter
    def img_headers(self, img_headers: dict):
        self._img_headers = img_headers
        curr_tab_name = self._notebook.tab(self._notebook.select(), "text")
        if self._img_header_dict[curr_tab_name] != img_headers:
            self._img_header_dict[curr_tab_name] = img_headers
        self.hist_changed = False
        self.filters_changed = False
        self.headers_changed = True
        self.notify()

    @histograms.setter
    def histograms(self, histograms: tuple):
        self._histograms = histograms
        curr_tab_name = self._notebook.tab(self._notebook.select(), "text")
        if self._histograms_dict[curr_tab_name] != histograms:
            self._histograms_dict[curr_tab_name] = histograms
        self.headers_changed = False
        self.filters_changed = False
        self.hist_changed = True
        self.notify()

    @filters.setter
    def filters(self, filters: dict):
        self._filters = filters
        curr_tab_name = self._notebook.tab(self._notebook.select(), "text")
        if self._filters_dict[curr_tab_name] != filters:
            self._filters_dict[curr_tab_name] = filters
        self.headers_changed = False
        self.hist_changed = False
        self.filters_changed = True
        self.notify()

    # Add new tabs to image frame
    def add_tab(self, name="New File"):
        try:
            if self._tab_count == 1:
                frame: ImageFrame = self.get_current_tab()
                # frame: ImageFrame = self._frame_list[self._notebook.index(self._notebook.select())]
                if not frame.image_frame.winfo_ismapped():
                    frame.image_frame = frame.create_frame()
                    return
            elif self._tab_count == 6:
                self.status.set("Maximum of 6 tabs is allowed.")
                return
            # TODO: add loading screen
            image_frame = ImageFrame(self)

            self._tab_count += 1
            if name == "New File":
                name = f"{name} {self._tab_count}"

            self._notebook.add(image_frame.image_frame, text=name)
            # self._frame_list.append(image_frame)
            self._frame_dict[name] = image_frame
            self._histograms_dict[name] = {}
            self._img_header_dict[name] = {}
            self._filters_dict[name] = {}
            self.status.set("New tab created.")
        except IndexError:
            raise

    # Remove current image tab
    def remove_current_tab(self):
        try:
            frame_name = self._notebook.tab(self._notebook.select(), "text")
            if self._tab_count == 1:
                # self._frame_list[self._notebook.index(self._notebook.select())].image_frame.grid_forget()
                self._frame_dict[frame_name].image_frame.grid_forget()
                return
            self._frame_dict.pop(frame_name)
            self._histograms_dict.pop(frame_name)
            self._img_header_dict.pop(frame_name)
            self._filters_dict.pop(frame_name)
            self._notebook.forget(
                self._notebook.index(self._notebook.select()))
            self._tab_count -= 1
        except IndexError:
            raise

    # Return an instance of the current notebook instance
    def get_notebook_instance(self) -> Notebook:
        return self._notebook

    # Get notebook dimensions
    def get_tab_dimensions(self):
        return self._notebook.winfo_reqwidth(), self._notebook.winfo_reqwidth()

    # Get instance of current tab
    def get_current_tab(self):
        return self._frame_dict[self._notebook.tab(self._notebook.select(), "text")]

    # Changes the UI based on the current tab
    def change_tab(self, event):
        try:
            curr_frame_name: ImageFrame = event.widget.tab(
                self._notebook.select(), "text")
            self.img_headers = self._img_header_dict[curr_frame_name]
            self.histograms = self._histograms_dict[curr_frame_name]
            self.filters = self._filters_dict[curr_frame_name]
        except KeyError:
            self.status.set("KeyError in changing tabs.")

    # Renames the current tab in the stored dictionary
    def rename_current_tab(self, name: str):
        old_key = self._notebook.tab(self._notebook.select(), "text")
        self._frame_dict[name] = self._frame_dict.pop(old_key)
        self._histograms_dict[name] = self._histograms_dict.pop(old_key)
        self._img_header_dict[name] = self._img_header_dict.pop(old_key)
        self._filters_dict[name] = self._filters_dict.pop(old_key)
        self._notebook.tab("current", text=name)

    # Generates a histogram for every channel and its corresponding color channel
    def generate_histogram(self, screen_size):
        # TODO: Add loading screen
        # Algo for channels
        red_channel = cv2.imread('./assets/pic.png')
        red_channel[:, :, 0] = 0
        red_channel[:, :, 1] = 0
        cv2.imwrite('./assets/red_channel.png', red_channel)
        red_channel_img = Image.open('./assets/red_channel.png')
        red_channel_img.thumbnail(screen_size, Image.LANCZOS)
        red_channel_img = PhotoImage(red_channel_img)

        green_channel = cv2.imread('./assets/pic.png')
        green_channel[:, :, 0] = 0
        green_channel[:, :, 2] = 0
        cv2.imwrite('./assets/green_channel.png', green_channel)
        green_channel_img = Image.open('./assets/green_channel.png')
        green_channel_img.thumbnail(screen_size, Image.LANCZOS)
        green_channel_img = PhotoImage(green_channel_img)

        blue_channel = cv2.imread('./assets/pic.png')
        blue_channel[:, :, 1] = 0
        blue_channel[:, :, 2] = 0
        cv2.imwrite('./assets/blue_channel.png', blue_channel)
        blue_channel_img = Image.open('./assets/blue_channel.png')
        blue_channel_img.thumbnail(screen_size, Image.LANCZOS)
        blue_channel_img = PhotoImage(blue_channel_img)

        self.channel_images = (
            red_channel_img, green_channel_img, blue_channel_img)

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
        red_channel = PhotoImage(red_img)

        green_image_values = gen_green_image.sum(axis=2).ravel()
        bars, bins = np.histogram(gen_green_image, range(257))

        plt.figure()
        plt.hist(green_image_values, bins, color="green")
        plt.savefig("./assets/green_hist.png")
        green_img = Image.open("./assets/green_hist.png")
        green_img.thumbnail(screen_size, Image.LANCZOS)
        green_channel = PhotoImage(green_img)

        blue_image_values = gen_blue_image.sum(axis=2).ravel()
        bars, bins = np.histogram(gen_blue_image, range(257))

        plt.figure()
        plt.hist(blue_image_values, bins, color="blue")
        plt.savefig("./assets/blue_hist.png")
        blue_img = Image.open("./assets/blue_hist.png")
        blue_img.thumbnail(screen_size, Image.LANCZOS)
        blue_channel = PhotoImage(blue_img)

        self.histograms = (red_channel, green_channel, blue_channel)

    # Read .PCX header files
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
    def generate_all_filters(self, png_image):
        cv2_image = cv2.imread('./assets/pic.png', 0)
        grayscale_pil, grayscale_np = generate_grayscale(png_image)

        self.filters = {
            # convert to grayscale
            "Grayscale": PhotoImage(grayscale_pil),

            # salt and pepper
            "Salt and Pepper": salt_and_pepper(cv2_image),

            # negative for the colored image
            "Colored Negative": generate_colored_negative(png_image),

            # negative for the grayscale image
            "Grayscale Negative": generate_negative_grayscale(grayscale_pil),

            # black and white
            "Black and White": generate_bw(),

            # power law gamma
            "Low Gamma": generate_low_gamma(),
        }

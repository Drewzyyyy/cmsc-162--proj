from random import random
from tkinter import StringVar
from tkinter.ttk import Notebook
import cv2
from PIL import Image, ImageFilter
from PIL.ImageTk import PhotoImage
from struct import unpack
import numpy as np
from matplotlib import pyplot as plt
from ImageFrame import ImageFrame
import random


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


# Stores variables and their states, if a specific variable/state changes then other classes are notified
def generate_colored_negative(png_image):
    negative_img_colored = png_image

    for i in range(negative_img_colored.size[0] - 1):
        for j in range(negative_img_colored.size[1] - 1):

            color_of_pixel = negative_img_colored.getpixel((i, j))

            if type(color_of_pixel) == tuple:
                red = 256 - color_of_pixel[0]
                green = 256 - color_of_pixel[1]
                blue = 256 - color_of_pixel[2]

                negative_img_colored.putpixel((i, j), (red, green, blue))
            else:
                # for grayscale
                color_of_pixel = 256 - color_of_pixel
                negative_img_colored.putpixel((i, j), color_of_pixel)

    negative_img_colored.save('./assets/colored-negative.png')
    return PhotoImage(negative_img_colored)


# Generate a black and white image based on the image uploaded
def generate_bw(threshold: int = 127):
    grayscale_copy = cv2.imread('./assets/grayscale.png')

    (thresh, b_and_white) = cv2.threshold(
        grayscale_copy, threshold, 255, cv2.THRESH_BINARY)
    cv2.imwrite('./assets/b_and_w.png', b_and_white)
    return PhotoImage(Image.open('./assets/b_and_w.png'))


# Generate an image with low gamma filter based on the image uploaded
def generate_low_gamma(gamma_const: float = 0.4):
    gamma_copy_img = cv2.imread('./assets/pic.png')

    gamma = np.array(255 * (gamma_copy_img / 255)
                     ** gamma_const, dtype='uint8')
    cv2.imwrite('./assets/gamma.png', gamma)
    return PhotoImage(Image.open('./assets/gamma.png'))


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

        self.curr_grayscale: Image = None

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
        # print(self._notebook.tab(self._notebook.select(), "text"))
        return self._frame_dict[self._notebook.tab(self._notebook.select(), "text")]
        # return self._frame_list[self._notebook.index(self._notebook.select())]

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

    # Generate all image filters
    def generate_all_filters(self, png_image):
        # self.threading_queue = Queue(5)

        # convert to grayscale
        grayscale = self.generate_grayscale(png_image)

        # negative for the colored image
        colored_negative = generate_colored_negative(png_image)

        # negative for the grayscale image
        colored_grayscale = self.generate_negative_grayscale()

        # black and white
        b_w = generate_bw()

        # power law gamma
        low_gamma = generate_low_gamma()

        self.filters = {
            "Grayscale": grayscale,
            "Colored Negative": colored_negative,
            "Grayscale Negative": colored_grayscale,
            "Black and White": b_w,
            "Low Gamma": low_gamma,
        }

        # salt and pepper
        salt_and_pepper = self.salt_and_pepper()

        # average
        average = self.generate_averaging_filter()

        # median
        median = self.median_filtering()

        # high pass
        high_pass = self.highpass_laplacian()

        # unsharp mask
        unmasked = self.unsharp_masking()

        # highboost
        highboost = self.highboost()

        # sobel
        img_sobel = self.gradient_sobel()

        # Generate an image with a grayscale filter
    def generate_grayscale(self, png_image):
        grayscale = np.asarray(png_image)
        grayscale = grayscale.astype('float')

        red = grayscale[:, :, 0]
        green = grayscale[:, :, 1]
        blue = grayscale[:, :, 2]

        grayscale_img = 0.2989 * red + 0.5870 * green + 0.1140 * blue

        grayscale_img = Image.fromarray(np.uint8(grayscale_img))

        grayscale_img.save('./assets/grayscale.png')
        self.curr_grayscale = grayscale_img
        res = PhotoImage(grayscale_img)
        return res

    # Generate a negative of the image grayscale
    def generate_negative_grayscale(self):
        negative_img_grayscale = self.curr_grayscale

        for i in range(negative_img_grayscale.size[0] - 1):
            for j in range(negative_img_grayscale.size[1] - 1):

                color_of_pixel = negative_img_grayscale.getpixel((i, j))

                if type(color_of_pixel) == tuple:
                    red = 256 - color_of_pixel[0]
                    green = 256 - color_of_pixel[1]
                    blue = 256 - color_of_pixel[2]

                    negative_img_grayscale.putpixel((i, j), (red, green, blue))
                else:
                    # for grayscale
                    color_of_pixel = 256 - color_of_pixel
                    negative_img_grayscale.putpixel((i, j), color_of_pixel)

        negative_img_grayscale.save('./assets/grayscale-negative.png')
        return PhotoImage(Image.open('./assets/grayscale-negative.png'))

    def generate_averaging_filter(self):
        temp_img = cv2.imread('./assets/pic.png', 0)

        a, b = temp_img.shape  # rows & columns

        mask = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
        mask = mask/16

        new_img = np.zeros([a, b])

        for i in range(1, a-1):
            for j in range(1, b-1):
                tmp = temp_img[i-1, j-1]*mask[0, 0]+temp_img[i-1, j]*mask[0, 1]+temp_img[i-1, j+1]*mask[0, 2]+temp_img[i, j-1]*mask[1, 0]+temp_img[i,j]*mask[1, 1]+temp_img[i, j+1]*mask[1, 2]+temp_img[i+1, j-1]*mask[2, 0]+temp_img[i+1, j]*mask[2, 1]+temp_img[i+1, j+1]*mask[2, 2]
                # print(tmp)
                new_img[i, j] = tmp

        new_img = new_img.astype(np.uint8)
        cv2.imwrite('./assets/average.png', new_img)
        cv2.imshow('averaging filter', new_img)

    # DREW: toggle to apply filter on salt and pepper image or purely grayscale lang for average, median
    def salt_and_pepper(self):
        temp_img = cv2.imread('./assets/pic.png', 0)

        rows, cols = temp_img.shape

        num_pix = random.randint(300, 10000)

        # Change to white
        for i in range(num_pix):
            y = random.randint(0, rows-1)
            x = random.randint(0, cols-1)
            temp_img[y][x] = 255

        # Change to black
        num_pix = random.randint(300, 10000)
        for i in range(num_pix):
            y = random.randint(0, rows-1)
            x = random.randint(0, cols-1)
            temp_img[y][x] = 0

        cv2.imwrite('./assets/salt_and_pepper.png', temp_img)
        cv2.imshow('salt and pepper', temp_img)

    def median_filtering(self):
        image = cv2.imread('./assets/pic.png', 0)
        a, b = image.shape  # rows & columns

        new_img = np.zeros([a, b])

        for i in range(1, a-1):
            for j in range(1, b-1):
                tmp = [image[i-1, j-1],
                       image[i-1, j],
                       image[i-1, j+1],
                       image[i, j-1],
                       image[i, j],
                       image[i, j+1],
                       image[i+1, j-1],
                       image[i+1, j],
                       image[i+1, j+1]]

                tmp = sorted(tmp)
                new_img[i, j] = tmp[4]

        new_img = new_img.astype(np.uint8)
        cv2.imwrite('./assets/median.png', new_img)
        cv2.imshow('median', new_img)

    # Spatial domain laplacian
    def highpass_laplacian(self):
        image = cv2.imread('./assets/pic.png', 0)

        filt = np.array([[0, 1, 0],
                         [1, -4, 1],
                         [0, 1, 0]])

        filtered_img = cv2.filter2D(src=image, ddepth=-1, kernel=filt)

        filt2 = image + (-1*filtered_img)

        clip = np.array(np.clip(filt2, 0, 255), dtype='uint8')

        cv2.imwrite('./assets/highpass.png', clip)

        cv2.imshow('highpass', clip)

    def unsharp_masking(self):
        img = cv2.imread('./assets/pic.png', 0)
        img = img / 255

        blurred_img = cv2.GaussianBlur(img, (31, 31), cv2.BORDER_DEFAULT)

        mask = img - blurred_img
        final = img + mask
        final = np.clip(final, 0, 255)

        cv2.imshow('unsharp masking', final)

    def highboost(self):
        img = cv2.imread('./assets/pic.png', 0)
        img = img / 255

        blurred_img = cv2.GaussianBlur(img, (31, 31), cv2.BORDER_DEFAULT)

        mask = img - blurred_img
        amplify_param = 5
        final = img + amplify_param*mask
        final = np.clip(final, 0, 255)

        cv2.imshow('highboost', final)

    def gradient_sobel(self):
        img = cv2.imread('./assets/pic.png', 0)

        x_sobel = np.array(([[-1, -2, -1],
                             [0, 0, 0],
                             [1, 2, 1]]))

        y_sobel = np.array(([[-1, 0, 1],
                             [-2, 0, 2],
                             [-1, 0, 1]]))

        x = cv2.filter2D(src=img, ddepth=-1, kernel=x_sobel)
        y = cv2.filter2D(src=img, ddepth=-1, kernel=y_sobel)
        sum = np.array(x + y, dtype='uint8')
        # clarify w/ jc if this is clipped + background???

        cv2.imshow('sobel', sum)

import tkinter
from tkinter import Frame, \
    StringVar, \
    Button, \
    Label
from PIL import Image, ImageTk
from utils import open_image
import numpy as np
import cv2
from threading import Thread
from queue import Queue


# Frame that displays the image
class ImageFrame:
    def __init__(self, state_manager):
        # Root Window
        self.parent = state_manager.get_notebook_instance()
        self.parent.update_idletasks()

        self.state_manager = state_manager

        self.image: Image = None
        self.grayscale: Image = None
        self.img_path = ""

        self.threading_queue: Queue | None = None

        # COLORS
        self.frame_background = "#748cab"

        # Set Screen Size
        self.window_dimensions = state_manager.get_tab_dimensions()

        # Instantiate frame
        self.image_frame = self.create_frame()

        # Instantiate instructions
        self.instructions_text = StringVar()
        self.instructions_text.set("Select an image to view.")
        self.instructions = Button(self.image_frame, textvariable=self.instructions_text, font="Calibri",
                                   command=self.display_image)
        self.instructions.place(relx=0.5, rely=0.5, anchor="center")

    def create_frame(self):
        frame = Frame(self.parent,
                      width=self.window_dimensions[0],
                      height=self.window_dimensions[1],
                      bg=self.frame_background)
        frame.grid(column=0, row=0, pady=10, padx=10)
        frame.grid_propagate(False)
        return frame

    def generate_grayscale(self):
        grayscale = np.asarray(self.image).astype('float')

        red = grayscale[:, 0]
        green = grayscale[:, 1]
        blue = grayscale[:, 2]

        grayscale_img = 0.2989 * red + 0.5870 * green + 0.1140 * blue

        grayscale_img = Image.fromarray(np.uint8(grayscale_img))

        grayscale_img.save('./assets/grayscale.png')
        self.grayscale = grayscale
        self.threading_queue.put(grayscale_img)

    def generate_colored_negative(self):
        negative_img_colored = self.image

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

        self.threading_queue.put(negative_img_colored)

    def generate_negative_grayscale(self):
        negative_img_grayscale = Image.open('./assets/grayscale.png')

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

        self.threading_queue.put(negative_img_grayscale)

    def generate_bw(self):
        grayscale_copy = cv2.imread('./assets/grayscale.png')

        threshold = 127  # user-adjusted; gagawan ng slider

        (thresh, b_and_white) = cv2.threshold(grayscale_copy, threshold, 255, cv2.THRESH_BINARY)
        cv2.imwrite('./assets/b_and_w.png', b_and_white)
        self.threading_queue.put(b_and_white)

    def generate_low_gamma(self):
        gamma_copy_img = cv2.imread('./assets/pic.png')

        gamma_const = 0.4  # gagawan ng slider

        gamma = np.array(255 * (gamma_copy_img / 255) ** gamma_const, dtype='uint8')
        cv2.imwrite('./assets/gamma.png', gamma)
        self.threading_queue.put(gamma)

    # Open Image in File Folders
    def display_image(self):
        try:
            # Open file dialog
            image_path = open_image()
            image = Image.open(image_path)

            # Set image to state manager
            self.image = image
            self.img_path = image_path
            image_name = image_path.split("/")[-1]
            self.state_manager.rename_current_tab(image_name)

            # Display headers if .pcx image
            if image.format == "PCX":
                self.state_manager.read_pcx_header(image_path)

            # Convert image to PNG for channels algo and save to same folder as this file
            png_image = image.convert("RGB")
            png_image.save('./assets/pic.png')

            # Set image sizes of histograms
            right_frame_size: tuple = (int((self.parent.winfo_width() * 0.5)),
                                       int(self.parent.winfo_height() * 0.4))
            self.state_manager.generate_histogram(right_frame_size)

            # Resize image
            image.thumbnail(self.window_dimensions, Image.LANCZOS)
            image = ImageTk.PhotoImage(image)

            self.threading_queue = Queue(5)

            # convert to grayscale
            grayscale_thread = Thread(target=self.generate_grayscale, args=())

            # negative for the colored image
            colored_negative_thread = Thread(target=self.generate_colored_negative, args=())

            # negative for the grayscale image
            grayscale_negative_thread = Thread(target=self.generate_negative_grayscale, args=())

            # black and white
            bw_thread = Thread(target=self.generate_bw, args=())

            # power law gamma
            low_gamma_thread = Thread(target=self.generate_low_gamma, args=())

            grayscale_thread.start()
            low_gamma_thread.start()
            colored_negative_thread.start()
            grayscale_thread.join()
            grayscale_negative_thread.start()
            bw_thread.start()
            low_gamma_thread.join()
            colored_negative_thread.join()
            grayscale_negative_thread.join()
            bw_thread.join()

            filters_results = []
            while not self.threading_queue.empty():
                filters_results.append(self.threading_queue.get())

            self.state_manager.filters = {
                "Grayscale": filters_results[0],
                "Low Gamma": filters_results[1],
                "Colored Negative": filters_results[2],
                "Grayscale Negative": filters_results[3],
                "Black and White": filters_results[4]
            }

        except AttributeError:
            # Display error on failure
            self.instructions_text.set("Image upload failed.")
            self.state_manager.status.set("Image upload failed.")

        else:

            # Destroy instructions label
            self.instructions.destroy()

            # If child image exists then destroy it
            for widget in self.image_frame.winfo_children():
                widget.destroy()

            # Display image config
            image_name = image_path.split("/")[-1]

            self.state_manager.status.set(f"{image_name} opened.")

            # Display image in place of the instructions
            image_label = Label(self.image_frame, image=image, width=self.window_dimensions[0],
                                height=self.window_dimensions[1])
            image_label.image = image
            image_label.place(relx=0.5, rely=0.5, anchor="center")

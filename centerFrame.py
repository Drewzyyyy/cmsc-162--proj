from tkinter import Frame, \
    StringVar, \
    Button, \
    Label
from PIL import Image, ImageTk
from utils import open_image
from StateManager import StateManager
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2


# Frame that displays the image
class CenterFrame:
    def __init__(self, parent, state_manager: StateManager):
        # Root Window
        self.parent = parent
        self.parent.update()

        self.state_manager: StateManager = state_manager

        # COLORS
        frame_background = "#748cab"

        # Set Screen Size
        self.window_dimensions = (
            self.parent.winfo_width() * 0.7,
            self.parent.winfo_height() * 0.9)

        # Instantiate frame
        self.center_frame = Frame(self.parent,
                                  width=self.window_dimensions[0],
                                  height=self.window_dimensions[1],
                                  bg=frame_background)
        self.center_frame.grid(column=0, rowspan=2, pady=10, padx=10)
        self.center_frame.grid_propagate(False)

        # Instantiate instructions
        self.instructions_text = StringVar()
        self.instructions_text.set("Select an image to view.")
        self.instructions = Button(self.center_frame, textvariable=self.instructions_text, font="Calibri",
                                   command=self.display_image)
        self.instructions.place(relx=0.5, rely=0.5, anchor="center")

    # Open Image in File Folders
    def display_image(self):
        try:
            # Open file dialog
            image_path = open_image()
            image = Image.open(image_path)
            
            # Set image to state manager
            self.state_manager.image = image
            self.state_manager.image_path = image_path

            # Display headers if .pcx image
            if image.format == "PCX":
                self.state_manager.read_pcx_header(image_path)

            # Convert image to PNG for channels algo and save to same folder as this file
            png_image = image.convert("RGB")
            png_image.save('./assets/pic.png')

            # Set image sizes of histograms
            right_frame_size: tuple = (int((self.parent.winfo_width() * 0.3) - 50),
                                       int(self.parent.winfo_height() * 0.32))
            self.state_manager.generate_histogram(right_frame_size)

            # Resize image
            image.thumbnail(self.window_dimensions, Image.LANCZOS)
            image = ImageTk.PhotoImage(image)

        except AttributeError:
            # Display error on failure
            self.instructions_text.set("Image upload failed.")
            self.state_manager.status.set("Image upload failed.")

        else:
            # convert to grayscale
            grayscale = np.asarray(Image.open('./assets/pic.png'))
            grayscale = grayscale.astype('float')

            r = grayscale[:,:,0]
            g = grayscale[:,:,1]
            b = grayscale[:,:,2]

            grayscale_img = 0.2989*r + 0.5870*g + 0.1140*b
            
            grayscale_img = Image.fromarray(np.uint8(grayscale_img))
            grayscale_img.show()
            grayscale_img.save('./assets/grayscale.png')

            # negative for the colored image
            negative_img_colored = Image.open('./assets/pic.png')

            for i in range(negative_img_colored.size[0]-1):
                for j in range(negative_img_colored.size[1]-1):

                    color_of_pixel = negative_img_colored.getpixel((i,j))

                    if type(color_of_pixel) == tuple:
                        red = 256 - color_of_pixel[0]
                        green = 256 - color_of_pixel[1]
                        blue = 256 - color_of_pixel[2]

                        negative_img_colored.putpixel((i,j), (red, green, blue))
                    else:
                        # for grayscale
                        color_of_pixel = 256 - color_of_pixel
                        negative_img_colored.putpixel((i,j), color_of_pixel)

            negative_img_colored.show()

            #negative for the grayscale image
            negative_img_grayscale = Image.open('./assets/grayscale.png')

            for i in range(negative_img_grayscale.size[0]-1):
                for j in range(negative_img_grayscale.size[1]-1):

                    color_of_pixel = negative_img_grayscale.getpixel((i,j))

                    if type(color_of_pixel) == tuple:
                        red = 256 - color_of_pixel[0]
                        green = 256 - color_of_pixel[1]
                        blue = 256 - color_of_pixel[2]

                        negative_img_grayscale.putpixel((i,j), (red, green, blue))
                    else:
                        # for grayscale
                        color_of_pixel = 256 - color_of_pixel
                        negative_img_grayscale.putpixel((i,j), color_of_pixel)

            negative_img_grayscale.show()

            
            

            self.state_manager.image = grayscale_img
            self.state_manager.image_path = './assets/grayscale.png'


            # Destroy instructions label
            self.instructions.destroy()

            # If child image exists then destroy it
            for widget in self.center_frame.winfo_children():
                widget.destroy()

            # Display image config
            image_name = image_path.split("/")[-1]

            self.state_manager.status.set(f"{image_name} opened.")

            # Display image in place of the instructions
            image_label = Label(self.center_frame, image=image, width=self.window_dimensions[0],
                                height=self.window_dimensions[1])
            image_label.image = image
            image_label.grid(column=0, row=0)

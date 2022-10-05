from tkinter import Frame, \
    StringVar, \
    Label, \
    Button
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import cv2
from PIL import Image, ImageTk
from utils import open_image, read_pcx_header
import numpy as np


# Frame that displays the image
class CenterFrame:
    def __init__(self, parent, right_frame):
        # Root Window
        self.parent = parent
        self.parent.update()

        print(f"{self.parent.winfo_width()} x {self.parent.winfo_height()}")

        # Set Screen Size
        self.max_screen_dimensions = (self.parent.winfo_width() * 0.8, self.parent.winfo_height() * 0.8)

        # Instance of right frame (metadata frame)
        self.right_frame = right_frame

        # Instantiate frame
        self.center_frame = Frame(self.parent, width=self.max_screen_dimensions[0],
                                  height=self.max_screen_dimensions[1],
                                  bg='white')
        self.center_frame.grid(column=0, row=0, pady=10, padx=10)
        self.center_frame.grid_columnconfigure(0, minsize=self.max_screen_dimensions[0])
        self.center_frame.grid_rowconfigure(0, minsize=self.max_screen_dimensions[1])

        # Instantiate instructions
        self.instructions_text = StringVar()
        self.instructions_text.set("Select an image to view.")
        self.instructions = Button(self.center_frame, textvariable=self.instructions_text, font="Calibri",
                                   command=self.display_image)
        self.instructions.grid(column=0, row=0)

    # Open Image in File Folders
    def display_image(self):
        try:
            image, filename = open_image()

            if image.format == "PCX":
                pcx_headers = read_pcx_header(filename)
                self.right_frame.insert_headers(pcx_headers)

            else:
                self.right_frame.remove_headers()

            # Convert image to PNG for channels algo and save to same folder as this file
            pngImage = image.convert("RGB")
            pngImage.save('pic.png')

            # Resize image
            image.thumbnail(self.max_screen_dimensions, Image.LANCZOS)
            image = ImageTk.PhotoImage(image)

        except AttributeError:
            # Display error on failure
            self.instructions_text.set("Image upload failed.")

        else:
            # Destroy instructions label
            self.instructions.destroy()

            # If child image exists then destroy it
            for widget in self.center_frame.winfo_children():
                widget.destroy()

            # Algo for channels
            blue_channel = cv2.imread('pic.png')
            blue_channel[:,:,1] = 0
            blue_channel[:,:,2] = 0
            cv2.imwrite('blue_pic.png', blue_channel)

            green_channel = cv2.imread('pic.png')
            green_channel[:,:,0] = 0
            green_channel[:,:,2] = 0
            cv2.imwrite('green_pic.png', green_channel)

            red_channel = cv2.imread('pic.png')
            red_channel[:,:,0] = 0
            red_channel[:,:,1] = 0
            cv2.imwrite('red_pic.png', red_channel)

            # read image from folder and converts it to RGB because cv2.cvtColor returns BGR
            # reads red picture; if you want green/blue, change file name
            genImage = cv2.imread('red_pic.png')
            genImage = cv2.cvtColor(genImage, cv2.COLOR_BGR2RGB)

            # get sum and make 1d array
            image_values = genImage.sum(axis=2).ravel()
            bars, bins = np.histogram(image_values, range(257))

            # Histograms
            histogram = Figure(figsize= (5, 5), dpi=100)
            plot = histogram.add_subplot(111)
            
            # Draw plot and show in window
            plot.hist(image_values, bins=bins,color='r')
            plot.legend(["Red Channel"])
            can = FigureCanvasTkAgg(histogram, master=self.center_frame)
            can.draw()
            can.get_tk_widget().grid(column=1, row=0)


            # open image and convert to tk to display
            image_open = Image.open('red_pic.png')
            img_to_tk = ImageTk.PhotoImage(image_open)


            # Display image config
            Label(self.center_frame, text=f"File opened: {filename}", bg="grey").grid(column=0, row=1, sticky="SW")

            # Display image in place of the instructions
            image_label = Label(self.center_frame, image=image, width=self.max_screen_dimensions[0],
                                height=self.max_screen_dimensions[1])
            image_label.image = image
            image_label.grid(column=0, row=0)

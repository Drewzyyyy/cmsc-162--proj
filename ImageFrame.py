import tkinter
from tkinter import Frame, \
    StringVar, \
    Button, \
    Label
from PIL import Image, ImageTk
from utils import open_image
import numpy as np
import cv2


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
            if image.info.get("transparency", None) is not None:
                png_image = image.convert("RGBA")
            else:
                png_image = image.convert("RGB")
            png_image.save('./assets/pic.png')

            # Set image sizes of histograms
            right_frame_size: tuple = (int((self.parent.winfo_width() * 0.5)),
                                       int(self.parent.winfo_height() * 0.4))
            self.state_manager.generate_histogram(right_frame_size)

            # Resize image
            image.thumbnail(self.window_dimensions, Image.LANCZOS)
            image = ImageTk.PhotoImage(image)

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

            self.state_manager.generate_all_filters(png_image)

        except AttributeError:
            # Display error on failure
            self.instructions_text.set("Image upload failed.")
            self.state_manager.status.set("Image upload failed.")

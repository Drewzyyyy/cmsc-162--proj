from tkinter import Frame, \
    StringVar, \
    Button, \
    Label
from PIL import Image, ImageTk
from utils import open_image
from StateManager import StateManager
import numpy as np


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

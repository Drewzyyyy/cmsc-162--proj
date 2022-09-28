from tkinter import Frame, \
    StringVar, \
    Label
from PIL import Image, ImageTk
from utils import open_image, read_pcx_header

# Constants
MAX_IMAGE_DIMENSIONS = (1440, 810)


# Frame that displays the image
class CenterFrame:
    def __init__(self, parent, right_frame):
        # Root Window
        self.parent = parent

        # Instance of right frame (metadata frame)
        self.right_frame = right_frame

        # Instantiate frame
        self.center_frame = Frame(self.parent, width=1080, height=1080, bg='white')
        self.center_frame.grid(column=0, row=0, pady=10, padx=10)
        self.center_frame.grid_columnconfigure(0, minsize=MAX_IMAGE_DIMENSIONS[0])
        self.center_frame.grid_rowconfigure(0, minsize=950)

        # Instantiate instructions
        self.instructions_text = StringVar()
        self.instructions_text.set("Select an image to view.")
        self.instructions = Label(self.center_frame, textvariable=self.instructions_text, font="Calibri",
                                  width=150, height=50)
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

            # Resize image
            image.thumbnail(MAX_IMAGE_DIMENSIONS, Image.LANCZOS)
            image_dimensions = image.size
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

            # Display image config
            Label(self.center_frame, text=f"File opened: {filename}", bg="grey").grid(column=0, row=1, sticky="SW")

            # Display image in place of the instructions
            image_label = Label(self.center_frame, image=image, width=image_dimensions[0], height=image_dimensions[1])
            image_label.image = image
            image_label.grid(column=0, row=0)

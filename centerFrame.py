from tkinter import Frame, \
    StringVar, \
    Label, \
    Button
from PIL import Image, ImageTk
from utils import open_image, read_pcx_header


# Frame that displays the image
class CenterFrame:
    def __init__(self, parent, right_frame):
        # Root Window
        self.parent = parent

        # Set Screen Size
        self.max_screen_dimensions = (self.parent.winfo_screenwidth() * 0.39, self.parent.winfo_screenheight() * 0.88)
        self.max_image_dimensions = (self.parent.winfo_screenwidth() * 0.78, self.parent.winfo_screenheight() * 0.78)

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

            # Resize image
            image.thumbnail(self.max_image_dimensions, Image.LANCZOS)
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
            image_label = Label(self.center_frame, image=image, width=self.max_screen_dimensions[0],
                                height=self.max_screen_dimensions[1])
            image_label.image = image
            image_label.grid(column=0, row=0)

from tkinter import Frame, \
    StringVar, \
    Button, \
    Label
from PIL import Image
from PIL.ImageTk import PhotoImage


# Frame that displays the image
class ImageFrame(Frame):
    def __init__(self, parent, state_manager):
        self.state_manager = state_manager

        # Root Window
        self.parent = parent
        self.parent.update_idletasks()

        parent_dimensions = (
            int(parent.winfo_width() * 0.7),
            int(parent.winfo_height() * 0.92)
        )

        Frame.__init__(self,
                       master=parent,
                       width=parent_dimensions[0],
                       height=parent_dimensions[1],
                       relief="raised")

        # COLORS
        self.frame_background = "#748cab"

        # Set Screen Size
        self.window_dimensions = (self.winfo_reqwidth(), self.winfo_reqwidth())

        # Instantiate instructions
        self.instructions_text = StringVar()
        self.instructions_text.set("Select an image to view.")
        self.instructions = Button(self, textvariable=self.instructions_text, font="Calibri",
                                   command=self.state_manager.process_image)
        self.instructions.place(relx=0.5, rely=0.5, anchor="center")

        self.grid(column=0, row=0, pady=10, padx=10)
        self.grid_propagate(False)

    # Triggered when specific variables are changed in the state manager
    def notify(self, states):
        if states.img_changed and states.curr_img is not None:
            self.display_image(states.curr_img)
            self.parent.update_idletasks()

    # Open Image in File Folders
    def display_image(self, image):
        try:
            self.state_manager.status.set(value="Formatting image...")
            if isinstance(image, PhotoImage):
                image_tk = image
            else:
                # Set image sizes of histograms
                right_frame_size: tuple = (int(self.parent.winfo_width() * 0.5),
                                           int(self.parent.winfo_height() * 0.4))
                self.state_manager.generate_histogram(right_frame_size)
                self.state_manager.status.set(value="Generating Histograms...")

                # Resize image
                image.thumbnail(self.window_dimensions, Image.LANCZOS)
                image_tk = PhotoImage(image)

                # Destroy instructions label
                self.instructions.destroy()

                # If child image exists then destroy it
                for widget in self.winfo_children():
                    widget.destroy()

            # Display image in place of the instructions
            image_label = Label(self, image=image_tk, width=self.window_dimensions[0],
                                height=self.window_dimensions[1])
            image_label.image = image_tk
            self.state_manager.status.set(value="Placing Photo...")
            image_label.place(relx=0.5, rely=0.5, anchor="center")

        except AttributeError:
            # Display error on failure
            self.instructions_text.set("Image upload failed.")
            self.state_manager.status.set("Image upload failed.")
            raise

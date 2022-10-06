from tkinter import LabelFrame, Listbox, Label, Frame
from StateManager import StateManager
from PIL import ImageTk


# Frame that displays the metadata/headers
class RightFrame:
    def __init__(self, parent):
        # Root Window
        self.parent = parent
        self.parent.update()

        # Histograms
        self.red_channel_hist: ImageTk.PhotoImage or None = None
        self.green_channel_hist: ImageTk.PhotoImage or None = None
        self.blue_channel_hist: ImageTk.PhotoImage or None = None

        # Channel images
        self.red_channel_img: ImageTk.PhotoImage or None = None
        self.green_channel_img: ImageTk.PhotoImage or None = None
        self.blue_channel_img: ImageTk.PhotoImage or None = None

        # Colors
        self.frame_background = "#3e5c76"
        self.text_color = "#f0ebd8"

        # Constants
        self.window_dimensions = (
            (self.parent.winfo_width() * 0.3) - 50,
            self.parent.winfo_height())

        # Instantiate upper right frame
        self.upper_right_frame = LabelFrame(self.parent,
                                            width=self.window_dimensions[0],
                                            height=self.window_dimensions[1] * 0.3,
                                            bg=self.frame_background,
                                            fg=self.text_color,
                                            relief="raised",
                                            text="Image Metadata")
        self.upper_right_frame.grid(column=1, row=0, pady=5, padx=10, ipadx=1, ipady=1)
        self.upper_right_frame.grid_propagate(False)
        self.upper_right_frame.update()

        # Instantiate lower right frame
        self.lower_right_frame = Frame(self.parent,
                                       width=self.window_dimensions[0],
                                       height=self.window_dimensions[1] * 0.58,
                                       bg=self.frame_background,
                                       relief="raised")
        self.lower_right_frame.grid(column=1, row=1)
        self.lower_right_frame.grid_propagate(False)
        self.lower_right_frame.update()

        # Contains the list of header metadata
        self.header_list: Listbox = Listbox(self.upper_right_frame,
                                            width=int(self.upper_right_frame.winfo_reqwidth() - 20),
                                            height=int(self.upper_right_frame.winfo_reqheight()))
        self.header_list.grid(column=0, row=0)

        # Instantiate histogram and channel image
        self.histogram: Label = Label(self.lower_right_frame)
        self.channel_img: Label = Label(self.lower_right_frame)

        # Instantiate histogram frame label
        self.histogram_label = Label(self.lower_right_frame,
                                     text="Histogram",
                                     bg=self.frame_background,
                                     fg=self.text_color,
                                     width=int(self.lower_right_frame.winfo_reqwidth() * 0.13),
                                     height=(int(self.lower_right_frame.winfo_reqheight() * 0.0025)))
        self.histogram_label.grid(column=0, row=0)
        self.histogram_label.grid_propagate(False)

    # Triggered when specific variables are changed in the state manager
    def update(self, states: StateManager):
        try:
            # Display the header metadata
            if states.img_headers:
                self.display_header(states.img_headers)

            # Store the histograms and channel images then display default red channel
            if states.histograms:
                self.red_channel_hist = states.histograms[0]
                self.green_channel_hist = states.histograms[1]
                self.blue_channel_hist = states.histograms[2]

                self.red_channel_img = states.channel_images[0]
                self.green_channel_img = states.channel_images[1]
                self.blue_channel_img = states.channel_images[2]
                self.display_histogram()

        except ValueError:
            raise

    # Display the image headers to the screen
    def display_header(self, img_headers):
        try:
            self.header_list.delete(0, "end")
            for idx, header in enumerate(img_headers):
                if idx == 0:
                    self.header_list.insert(idx, f"{header.capitalize()}: Zshoft .pcx({img_headers[header]})")
                else:
                    self.header_list.insert(idx, f"{header.capitalize()}: {img_headers[header]}")
            self.header_list.grid(column=0, row=0)
        except ValueError:
            raise

    # Display the histograms based on the color channel provided
    def display_histogram(self, color_channel="red"):
        # Remove histogram and channel image from the screen to add new ones
        self.histogram.grid_forget()
        self.channel_img.grid_forget()

        if color_channel == "red":
            self.histogram = Label(self.lower_right_frame,
                                   image=self.red_channel_hist,
                                   bg=self.frame_background,
                                   width=int(self.upper_right_frame.winfo_reqwidth()),
                                   height=int(self.upper_right_frame.winfo_reqheight()))
            self.histogram.image = self.red_channel_hist
            self.channel_img = Label(self.lower_right_frame,
                                     image=self.red_channel_img,
                                     bg=self.frame_background,
                                     width=int(self.upper_right_frame.winfo_reqwidth()),
                                     height=int(self.upper_right_frame.winfo_reqheight()))
            self.channel_img.image = self.red_channel_img

        elif color_channel == "green":
            self.histogram = Label(self.lower_right_frame,
                                   image=self.green_channel_hist,
                                   bg=self.frame_background,
                                   width=int(self.upper_right_frame.winfo_reqwidth()),
                                   height=int(self.upper_right_frame.winfo_reqheight()))
            self.histogram.image = self.green_channel_hist
            self.channel_img = Label(self.lower_right_frame,
                                     image=self.green_channel_img,
                                     bg=self.frame_background,
                                     width=int(self.upper_right_frame.winfo_reqwidth()),
                                     height=int(self.upper_right_frame.winfo_reqheight()))
            self.channel_img.image = self.green_channel_img

        elif color_channel == "blue":
            self.histogram = Label(self.lower_right_frame,
                                   image=self.blue_channel_hist,
                                   bg=self.frame_background,
                                   width=int(self.upper_right_frame.winfo_reqwidth()),
                                   height=int(self.upper_right_frame.winfo_reqheight()))
            self.histogram.image = self.blue_channel_hist
            self.channel_img = Label(self.lower_right_frame,
                                     image=self.blue_channel_img,
                                     bg=self.frame_background,
                                     width=int(self.upper_right_frame.winfo_reqwidth()),
                                     height=int(self.upper_right_frame.winfo_reqheight()))
            self.channel_img.image = self.blue_channel_img

        # After choosing display them on the screen
        self.histogram.grid(column=0, row=1, padx=0, pady=0)
        self.channel_img.grid(column=0, row=2, padx=0, pady=0)

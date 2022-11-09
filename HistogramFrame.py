from tkinter import Frame, Label, OptionMenu, StringVar
from PIL.ImageTk import PhotoImage


# Generates the Frame for displaying the histogram
class HistogramFrame(Frame):
    def __init__(self, parent, config: dict):
        # Specific config values for dimensions and background color
        self.config = config
        self.parent = parent

        Frame.__init__(self,
                       master=self.parent,
                       width=self.config["width"],
                       height=self.config["height"],
                       bg=self.config["bg"],
                       relief="raised")
        self.grid(column=0, row=0)
        self.grid_propagate(False)
        self.update_idletasks()

        # All possible channels
        self.values = ["Red", "Green", "Blue"]

        # Stores the current chosen channel
        self.var = StringVar(value=self.values[0])

        self.channel_options = OptionMenu(self,
                                          self.var,
                                          *self.values,
                                          command=self.set_images)

        self.channel_histograms: dict = {"Red": None, "Green": None, "Blue": None}
        self.channel_images: dict = {"Red": None, "Green": None, "Blue": None}

        # Instantiate histogram and channel images
        self.histogram: Label = Label(self)
        self.channel_img: Label = Label(self)

    # Triggered when specific variables are changed in the state manager
    def notify(self, states):
        try:
            # Store the histograms and channel images then display default red channel
            if states.hist_changed:
                if not states.histograms:
                    self.histogram.grid_forget()
                    self.channel_img.grid_forget()
                    self.channel_options.grid_forget()
                    return

                # Iterate through every key, or channel name, then store each value
                for idx, channel in enumerate(self.channel_histograms):
                    self.channel_histograms[channel] = states.histograms[idx]
                    self.channel_images[channel] = states.channel_images[idx]

                self.set_images("Red")

        except ValueError:
            raise

    # Set the images and histogram to be displayed
    def set_images(self, color_channel):
        # Synchronize the current chosen channel
        if color_channel != self.var.get():
            self.var.set(color_channel)

        self.channel_options.grid(column=0, row=0, sticky="NSEW")

        # Remove histogram and channel image from the screen to add new ones
        self.histogram.grid_forget()
        self.channel_img.grid_forget()

        # Set the channel image and histogram based on the color channel
        hist_img = self.channel_histograms[color_channel]
        channel_img = self.channel_images[color_channel]

        # Set the histogram
        self.histogram = Label(self,
                               image=hist_img,
                               bg=self.config["bg"],
                               width=self.winfo_reqwidth(),
                               height=int(self.winfo_reqheight() * 0.4))
        self.histogram.image = hist_img

        # Set the channel color image
        self.channel_img = Label(self,
                                 image=channel_img,
                                 bg=self.config["bg"],
                                 width=self.winfo_reqwidth(),
                                 height=int(self.winfo_reqheight() * 0.4))
        self.channel_img.image = channel_img

        # After choosing display them on the screen
        self.histogram.grid(column=0, row=1, padx=0, pady=0)
        self.channel_img.grid(column=0, row=2, padx=0, pady=0)

from tkinter import Frame, Label, OptionMenu, StringVar
from tkinter.ttk import Notebook
from PIL.ImageTk import PhotoImage


class HistogramFrame(Frame):
    def __init__(self, parent: Notebook, config: dict):
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

        self.values = ["Red", "Green", "Blue"]
        self.var = StringVar(value=self.values[0])

        self.channel_options = OptionMenu(self,
                                          self.var,
                                          *self.values,
                                          command=self.set_images)

        # Histograms
        self.red_channel_hist: PhotoImage or None = None
        self.green_channel_hist: PhotoImage or None = None
        self.blue_channel_hist: PhotoImage or None = None

        # Channel images
        self.red_channel_img: PhotoImage or None = None
        self.green_channel_img: PhotoImage or None = None
        self.blue_channel_img: PhotoImage or None = None

        # Instantiate histogram and channel image
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

                self.red_channel_hist = states.histograms[0]
                self.green_channel_hist = states.histograms[1]
                self.blue_channel_hist = states.histograms[2]

                self.red_channel_img = states.channel_images[0]
                self.green_channel_img = states.channel_images[1]
                self.blue_channel_img = states.channel_images[2]
                self.set_images("Red")

        except ValueError:
            raise

    def set_images(self, color_channel):
        if color_channel != self.var.get():
            self.var.set(color_channel)

        self.channel_options.grid(column=0, row=0, sticky="NSEW")
        # Remove histogram and channel image from the screen to add new ones
        self.histogram.grid_forget()
        self.channel_img.grid_forget()

        hist_img: PhotoImage
        channel_img: PhotoImage

        if color_channel == "Red":
            hist_img = self.red_channel_hist
            channel_img = self.red_channel_img

        elif color_channel == "Green":
            hist_img = self.green_channel_hist
            channel_img = self.green_channel_img

        else:
            hist_img = self.blue_channel_hist
            channel_img = self.blue_channel_img

        self.histogram = Label(self,
                               image=hist_img,
                               bg=self.config["bg"],
                               width=self.winfo_reqwidth(),
                               height=int(self.winfo_reqheight() * 0.4))
        self.histogram.image = hist_img
        self.channel_img = Label(self,
                                 image=channel_img,
                                 bg=self.config["bg"],
                                 width=self.winfo_reqwidth(),
                                 height=int(self.winfo_reqheight() * 0.4))
        self.channel_img.image = channel_img

        # After choosing display them on the screen
        self.histogram.grid(column=0, row=1, padx=0, pady=0)
        self.channel_img.grid(column=0, row=2, padx=0, pady=0)

from tkinter import Menu
from functools import partial
from utils import add_watermark, open_bit_plane_window


# Generates the window menu
class Menus(Menu):
    def __init__(self, parent, state_manager, metadata_frame):
        super(Menus, self).__init__(parent,
                                    background="grey",
                                    foreground="black",
                                    activebackground="white",
                                    activeforeground="black")

        self.metadata_frame = metadata_frame

        # Flag for enabling settings that are disabled at init
        self.__are_filters_disabled = True

        # Menubar tabs
        file = Menu(self, tearoff=0)
        file.add_command(label="Open", command=state_manager.process_image)
        file.add_separator()
        file.add_command(label="Exit", command=parent.quit)
        self.add_cascade(label="File", menu=file)

        # Edit menu
        self.edit = Menu(self, tearoff=0)
        self.edit.add_command(label="Show Bit Planes",
                              command=partial(open_bit_plane_window, parent),
                              state="disabled")
        self.edit.add_command(label="Add Watermark",
                              command=partial(add_watermark, parent),
                              state="disabled")
        self.add_cascade(label="Edit", menu=self.edit)

        # Changes the color channel
        change_channel = Menu(self, tearoff=0)

        # Channels tabs
        self.channels = Menu(change_channel, tearoff=0)
        change_channel.add_cascade(label="Change Channel", menu=self.channels)
        self.channels.add_command(label="RED",
                                  command=partial(self.metadata_frame.histogram_frame.set_images, "Red"),
                                  state="disabled")
        self.channels.add_command(label="GREEN",
                                  command=partial(self.metadata_frame.histogram_frame.set_images, "Green"),
                                  state="disabled")
        self.channels.add_command(label="BLUE",
                                  command=partial(self.metadata_frame.histogram_frame.set_images, "Blue"),
                                  state="disabled")
        self.add_cascade(label="Channels", menu=change_channel)

        # List of available filters
        self.main_filters = ["Grayscale",
                             "Salt and Pepper",
                             "Colored Negative",
                             "Grayscale Negative",
                             "Black and White",
                             "Low Gamma"]
        self.sub_filters = ["Default",
                            "Low Pass Average",
                            "Low Pass Median",
                            "High Pass Laplacian",
                            "Unsharping Mask",
                            "Highboost Amp Parameter=5",
                            "Gradient Sobel Average",
                            "Gradient Sobel X",
                            "Gradient Sobel Y"]

        # Changes the filter used
        self.filters = Menu(self, tearoff=0)

        # Grayscale and Salt and Pepper submenus
        grayscale = Menu(change_channel, tearoff=0)
        salt_and_pepper = Menu(change_channel, tearoff=0)

        # All available commands for changing the filter
        self.filters.add_command(label="Default",
                                 command=partial(self.metadata_frame.filters_frame.set_main_filter_image, "Default"),
                                 state="disabled")
        self.filters.add_separator()

        # Generate menus based on listed filters
        for main_filter in self.main_filters:
            # Generate sub-filters for grayscale and salt and pepper
            if main_filter == "Grayscale":
                self.filters.add_cascade(label=main_filter,
                                         menu=grayscale,
                                         state="disabled")
                for sub_filter in self.sub_filters:
                    grayscale.add_command(label=sub_filter,
                                          command=partial(self.set_subfilter, True, sub_filter))
            elif main_filter == "Salt and Pepper":
                self.filters.add_cascade(label="Salt and Pepper",
                                         menu=salt_and_pepper,
                                         state="disabled")
                for sub_filter in self.sub_filters:
                    salt_and_pepper.add_command(label=sub_filter,
                                                command=partial(self.set_subfilter, False, sub_filter))
            else:
                self.filters.add_command(label=main_filter,
                                         command=partial(self.metadata_frame.filters_frame.set_main_filter_image,
                                                         main_filter),
                                         state="disabled")
        self.add_cascade(label="Filters", menu=self.filters)

        self.process = Menu(self, tearoff=0)
        self.degradation = Menu(self, tearoff=0)
        self.restoration = Menu(self, tearoff=0)
        self.compression = Menu(self, tearoff=0)

        self.process.add_cascade(label="Degradation",
                                 menu=self.degradation,
                                 state="disabled")
        self.degradation.add_command(label="Salt",
                                     command=partial(state_manager.open_image_in_new_window, parent, 'Salt'))
        self.degradation.add_command(label="Pepper",
                                     command=partial(state_manager.open_image_in_new_window, parent, 'Pepper'))
        self.degradation.add_command(label="Salt and Pepper",
                                     command=partial(state_manager.open_image_in_new_window, parent, 'Salt and Pepper'))

        self.process.add_cascade(label="Restoration",
                                 menu=self.restoration,
                                 state="disabled")
        self.restoration.add_command(label="Contraharmonic Filter",
                                     command=partial(state_manager.open_image_in_new_window, parent, 'Contraharmonic'))
        self.restoration.add_command(label="Order-Statistics Filter",
                                     command=partial(state_manager.open_image_in_new_window, parent, 'Median'))

        self.process.add_cascade(label="Compression",
                                 menu=self.compression,
                                 state="disabled")
        self.compression.add_command(label="Run Length Encoding - Grayscale",
                                     command=partial(state_manager.open_image_in_new_window, parent,
                                                     'Run Length - Grayscale'))
        self.compression.add_command(label="Run Length Encoding - Colored",
                                     command=partial(state_manager.open_image_in_new_window, parent,
                                                     'Run Length - Colored'))

        self.add_cascade(label="Process", menu=self.process)

    # Triggered when image has been uploaded
    def notify(self, states):
        # Enable all previously disabled menus on init
        if states.img_changed and self.__are_filters_disabled:
            # Enable all channels
            self.channels.entryconfig("RED", state="normal")
            self.channels.entryconfig("GREEN", state="normal")
            self.channels.entryconfig("BLUE", state="normal")

            # Enable all filters
            for main_filter in self.main_filters:
                self.filters.entryconfig(main_filter, state="normal")
            self.filters.entryconfig("Default", state="normal")
            self.process.entryconfig("Degradation", state="normal")
            self.process.entryconfig("Restoration", state="normal")
            self.process.entryconfig("Compression", state="normal")
            self.edit.entryconfig("Show Bit Planes", state="normal")
            self.edit.entryconfig("Add Watermark", state="normal")
            self.__are_filters_disabled = False
            states.unsubscribe(self)

    # Updates the sub-filter on the image
    def set_subfilter(self, is_grayscale, subfilter):
        if is_grayscale:
            main_filter = "Grayscale"
        else:
            main_filter = "Salt and Pepper"
        # First set the image filter as grayscale or salt and pepper
        self.metadata_frame.filters_frame.set_main_filter_image(main_filter)

        if subfilter == "default":
            return
        self.metadata_frame.filters_frame.set_subfilter_image(subfilter)

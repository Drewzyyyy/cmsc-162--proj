from tkinter import Frame, StringVar, OptionMenu, Label, IntVar, Scale, DoubleVar
from tkinter.ttk import Notebook
from utils import generate_low_gamma, generate_bw, generate_more_filters


# Frame tab that stores the filters the image is applied to
class FiltersFrame(Frame):
    def __init__(self, parent: Notebook, config: dict):
        Frame.__init__(self,
                       master=parent,
                       width=config["width"],
                       height=config["height"],
                       bg=config["bg"],
                       relief="raised")
        self.grid(column=0, row=0)
        self.grid_propagate(False)
        self.update_idletasks()

        self.values: list = ["None"]
        self.more_filter_values: list = ["None"]
        self.current_filter = StringVar(value=self.values[0])
        self.current_more_filter = StringVar(value=self.more_filter_values[0])

        self.filter_options: OptionMenu = self.create_option_menu()
        self.more_filters: OptionMenu | None = None

        self.filters: dict = {}
        self.grayscale_filters: dict = {}
        self.salt_and_pepper_filters: dict = {}
        self.filtered_image = Label(self)

        self.filter_label = Label(self)
        self.filter_scale_val: IntVar | DoubleVar | None = None
        self.filter_scale = Scale(self)

    # Triggered when specific variables are changed in the state manager
    def notify(self, states):
        try:
            if states.filters_changed:
                if not states.filters:
                    self.filter_options.grid_forget()
                    self.filtered_image.grid_forget()
                    self.filter_label.grid_forget()
                    self.filter_scale.grid_forget()
                    self.filters = {}
                    self.grayscale_filters = {}
                    self.salt_and_pepper_filters = {}
                    if self.more_filters is not None:
                        self.more_filters.grid_forget()
                    return
                self.filters = states.filters.copy()
                self.values = [*self.filters.keys()]
                self.filter_options = self.create_option_menu(self.values)
                self.grayscale_filters = generate_more_filters('Grayscale')
                self.salt_and_pepper_filters = generate_more_filters('Salt and Pepper')
                self.update_idletasks()
                self.set_image("Grayscale")
        except ValueError:
            raise

    # Create OptionMenu
    def create_option_menu(self, values=None, for_gray=False):

        if values is None:
            values = ["None"]

        if for_gray:
            return OptionMenu(self,
                              self.current_more_filter,
                              *values,
                              command=self.set_filter_image)

        return OptionMenu(self,
                          self.current_filter,
                          *values,
                          command=self.set_image)

    def set_filter_image(self, image_filter):
        if image_filter == "None":
            value = self.current_filter.get()
            self.filtered_image = Label(self,
                                        image=self.filters[value],
                                        width=self.winfo_reqwidth(),
                                        height=int(self.winfo_reqheight() * 0.4))
            self.filtered_image.image = self.filters[value]

            self.filtered_image.grid(column=0, row=1)
            self.filtered_image.grid_propagate(False)

            return
        else:
            self.filtered_image.grid_forget()
            filter_dict: dict = self.grayscale_filters.copy() if self.current_filter.get() == 'Grayscale' else \
                self.salt_and_pepper_filters.copy()
            self.filtered_image = Label(self,
                                        image=filter_dict[image_filter],
                                        width=self.winfo_reqwidth(),
                                        height=int(self.winfo_reqheight() * 0.4))
            self.filtered_image.image = filter_dict[image_filter]
            self.filter_label = Label(self,
                                      text="More Filters")
            self.current_more_filter.set(image_filter)
        self.filtered_image.grid(column=0, row=1)
        self.filtered_image.grid_propagate(False)

    # Set the filtered image displayed on screen
    def set_image(self, image_filter):
        self.filter_options.grid(column=0, row=0, sticky="nsew")
        self.filtered_image.grid_forget()
        self.filter_label.grid_forget()
        self.filter_scale.grid_forget()
        if self.more_filters is not None:
            self.more_filters.grid_forget()
        self.filtered_image = Label(self,
                                    image=self.filters[image_filter],
                                    width=self.winfo_reqwidth(),
                                    height=int(self.winfo_reqheight() * 0.4))
        self.filtered_image.image = self.filters[image_filter]

        if image_filter == "Low Gamma":
            self.filter_label = Label(self,
                                      text="Gamma Const")
            self.filter_scale = Scale(self,
                                      from_=0,
                                      to=100,
                                      resolution=0.01,
                                      orient="horizontal",
                                      length=self.winfo_reqwidth(),
                                      command=self.update_filter)
            self.filter_scale_val = DoubleVar(value=0.4)
            self.filter_scale.set(self.filter_scale_val.get())
            self.filter_label.grid(column=0, row=2, sticky="nsew")
            self.filter_scale.grid(column=0, row=3)
        elif image_filter == "Black and White":
            self.filter_label = Label(self,
                                      text="Threshold")
            self.filter_scale = Scale(self,
                                      from_=0,
                                      to=255,
                                      resolution=1,
                                      orient="horizontal",
                                      length=self.winfo_reqwidth(),
                                      command=self.update_filter)
            self.filter_scale_val = IntVar(value=127)
            self.filter_scale.set(self.filter_scale_val.get())
            self.filter_label.grid(column=0, row=2, sticky="nsew")
            self.filter_scale.grid(column=0, row=3)
        elif image_filter == "Grayscale" or image_filter == "Salt and Pepper":
            values: dict = self.grayscale_filters if image_filter == "Grayscale" else self.salt_and_pepper_filters
            keys = [*values.keys()]
            self.current_more_filter.set("None")
            self.more_filters = self.create_option_menu(keys, True)
            self.more_filters.grid(column=0, row=2, sticky="nsew")

        self.current_filter.set(image_filter)
        self.filtered_image.grid(column=0, row=1)
        self.filtered_image.grid_propagate(False)

    # Update filtered image based on the scale value
    def update_filter(self, value):
        self.filter_scale_val.set(value)
        curr_filter = self.current_filter.get()
        if curr_filter == "Low Gamma":
            self.filters["Low Gamma"] = generate_low_gamma(self.filter_scale_val.get())
        else:
            self.filters["Black and White"] = generate_bw(self.filter_scale_val.get())
        self.filtered_image = Label(self,
                                    image=self.filters[curr_filter],
                                    width=self.winfo_reqwidth(),
                                    height=int(self.winfo_reqheight() * 0.4))
        self.filtered_image.image = self.filters[curr_filter]
        self.filtered_image.grid(column=0, row=1)
        self.filtered_image.grid_propagate(False)

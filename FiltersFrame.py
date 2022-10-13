from tkinter import Frame, StringVar, OptionMenu, Label, IntVar, Scale, DoubleVar
from tkinter.ttk import Notebook
from StateManager import generate_bw, generate_low_gamma


# Frame tab that stores the filters the image is applied to
class FiltersFrame(Frame):
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

        self.values = ["Grayscale",
                       "Grayscale Negative",
                       "Black and White",
                       "Colored Negative",
                       "Low Gamma"]
        self.current_filter = StringVar(value=self.values[0])

        self.filter_options = OptionMenu(self,
                                         self.current_filter,
                                         *self.values,
                                         command=self.set_image)

        self.filters: dict = {}
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
                    return
                self.filters = states.filters.copy()
                self.set_image("Grayscale")
        except ValueError:
            raise

    # Set the filtered image displayed on screen
    def set_image(self, image_filter):
        self.filter_options.grid(column=0, row=0, sticky="nsew")
        self.filtered_image.grid_forget()
        self.filter_label.grid_forget()
        self.filter_scale.grid_forget()
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
                                      to=1,
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

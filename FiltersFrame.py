from tkinter import Frame, StringVar, OptionMenu, Label
from tkinter.ttk import Notebook
from PIL.ImageTk import PhotoImage


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
        self.var = StringVar(value=self.values[0])

        self.filter_options = OptionMenu(self,
                                         self.var,
                                         *self.values,
                                         command=self.set_image)

        self.filters: dict = {}
        self.filtered_image = Label(self)

    # Triggered when specific variables are changed in the state manager
    def notify(self, states):
        try:
            if states.filters_changed:
                if not states.filters:
                    self.filter_options.grid_forget()
                    self.filtered_image.grid_forget()
                    return
                print("hello")
                print(states.filters)
                self.filters = states.filters.copy()
                self.set_image("Grayscale")
        except ValueError:
            raise

    def set_image(self, image_filter):
        self.filter_options.grid(column=0, row=0)
        self.filtered_image.grid_forget()
        self.filtered_image = Label(self,
                                    image=self.filters[image_filter],
                                    width=self.winfo_reqwidth(),
                                    height=int(self.winfo_reqheight() * 0.4))
        self.filtered_image.image = self.filters[image_filter]

        self.filtered_image.grid(column=0, row=1)
        self.filtered_image.grid_propagate(False)

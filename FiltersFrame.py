from tkinter import Frame, StringVar, OptionMenu, Label, IntVar, Scale, DoubleVar
from utils import generate_low_gamma, generate_bw, generate_more_filters
import cv2
from numpy import array, uint8


# Frame tab that stores the filters the image is applied to
class FiltersFrame(Frame):
    def __init__(self, parent, config: dict):
        Frame.__init__(self,
                       master=parent,
                       width=config["width"],
                       height=config["height"],
                       bg=config["bg"],
                       relief="raised")
        self.grid(column=0, row=0)
        self.grid_propagate(False)
        self.update_idletasks()

        # Stores all main filter names
        self.main_filters: list = ["None"]

        # Stores all sub-filter names for grayscale and salt and pepper
        self.sub_filters: list = ["None"]

        # Stores the current main and sub filters used
        self.current_main_filter = StringVar(value=self.main_filters[0])
        self.current_sub_filter = StringVar(value=self.sub_filters[0])

        # Instance of the OptionMenu for the main and sub filters
        self.main_filter_options: OptionMenu = self.create_option_menu()
        self.sub_filters_options: OptionMenu | None = None

        # Stores all pre-filtered images based on the main filters
        self.filters: dict = {}
        
        # Stores all pre-filtered images based on grayscale or salt and pepper 
        self.grayscale_filters: dict = {}
        self.salt_and_pepper_filters: dict = {}
        
        # Label that displays the image on-screen
        self.filtered_image = Label(self)

        # Text label
        self.filter_label = Label(self)
        
        # Slider for black and white and low pass images
        self.filter_scale = Scale(self)
        self.filter_scale_val: IntVar | DoubleVar | None = None

        # Copy of the state manager instance for updating the current image on screen
        self.states = None
        
        # Copy of the non PhotoImage type of the current image without filters
        self.default_img = None

    # Triggered when specific variables are changed in the state manager
    def notify(self, states):
        try:
            if states.filters_changed:
                # Checker if filters were not passed
                if not states.filters:
                    self.main_filter_options.grid_forget()
                    self.filtered_image.grid_forget()
                    self.filter_label.grid_forget()
                    self.filter_scale.grid_forget()
                    self.filters = {}
                    self.grayscale_filters = {}
                    self.salt_and_pepper_filters = {}
                    if self.sub_filters_options is not None:
                        self.sub_filters_options.grid_forget()
                    return
                
                # Create a deepcopy of the filtered images
                self.filters = states.filters.copy()
                
                # Copies the names of all filters generated
                self.main_filters = [*self.filters.keys()]
                self.main_filter_options = self.create_option_menu(self.main_filters)
                
                # Generate the grayscale and salt and pepper filtered images
                self.grayscale_filters = generate_more_filters('Grayscale')
                self.salt_and_pepper_filters = generate_more_filters('Salt and Pepper')
                self.update_idletasks()
                self.set_main_filter_image("Default")
            
            # Get a copy of the state manager and the default image
            if self.states is None:
                self.states = states
            if self.default_img is None:
                self.default_img = states.default_cv2_img
        except ValueError:
            raise

    # Create OptionMenu
    def create_option_menu(self, values=None, for_gray=False):

        if values is None:
            values = ["None"]

        # If the option menu if for the grayscale
        if for_gray:
            return OptionMenu(self,
                              self.current_sub_filter,
                              *values,
                              command=self.set_subfilter_image)

        # Else create an option menu for the salt and pepper filter
        return OptionMenu(self,
                          self.current_main_filter,
                          *values,
                          command=self.set_main_filter_image)

    # Updates the preview image and main image to the chosen subfilter
    def set_subfilter_image(self, image_filter):
        # Get the chosen main filter value
        chosen_filter = self.current_main_filter.get()

        # Temporarily forget the filtered image
        self.filtered_image.grid_forget()
        # If default then display the default grayscale or salt and pepper image
        if image_filter == "Default":
            self.filtered_image = Label(self,
                                        image=self.filters[chosen_filter],
                                        width=self.winfo_reqwidth(),
                                        height=int(self.winfo_reqheight() * 0.4))
            self.filtered_image.image = self.filters[chosen_filter]
            self.states.curr_img = self.filters[chosen_filter]

            self.filtered_image.grid(column=0, row=1)
            self.filtered_image.grid_propagate(False)
            return
        # Else display the filtered image based on the filter for the grayscale or salt and pepper
        else:
            # Ternary operation for using a deepcopy of the grayscale or salt and pepper filtered images
            filter_dict: dict = self.grayscale_filters.copy() if chosen_filter == 'Grayscale' else \
                self.salt_and_pepper_filters.copy()
            self.filtered_image = Label(self,
                                        image=filter_dict[image_filter],
                                        width=self.winfo_reqwidth(),
                                        height=int(self.winfo_reqheight() * 0.4))
            self.filtered_image.image = filter_dict[image_filter]
            self.states.curr_img = filter_dict[image_filter]
            self.filter_label = Label(self,
                                      text="More Filters")
            self.current_sub_filter.set(image_filter)
        self.filtered_image.grid(column=0, row=1)
        self.filtered_image.grid_propagate(False)

    # Set the filtered image based on the main filter
    def set_main_filter_image(self, image_filter):
        # Place the OptionsMenu
        self.main_filter_options.grid(column=0, row=0, sticky="nsew")

        # Forget the other UI Elements to be replaced
        self.filtered_image.grid_forget()
        self.filter_label.grid_forget()
        self.filter_scale.grid_forget()

        # Forget the sub-filters OptionsMenu if it was chosen
        if self.sub_filters_options is not None:
            self.sub_filters_options.grid_forget()

        # Set the preview image to the chosen filter
        self.filtered_image = Label(self,
                                    image=self.filters[image_filter],
                                    width=self.winfo_reqwidth(),
                                    height=int(self.winfo_reqheight() * 0.4))
        self.filtered_image.image = self.filters[image_filter]

        # Set the main image to the chosen filter
        self.states.curr_img = self.filters[image_filter]

        if image_filter == "Low Gamma":
            # Create a slider to change the gamma constant
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
            # Create a slider to change the threshold
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
            # Ternary operation for using a deepcopy of the grayscale or salt and pepper filtered images
            values: dict = self.grayscale_filters if image_filter == "Grayscale" else self.salt_and_pepper_filters
            keys = [*values.keys()]
            self.current_sub_filter.set("None")

            # Create the option menu along with all possible sub filters
            self.sub_filters_options = self.create_option_menu(keys, True)
            self.sub_filters_options.grid(column=0, row=2, sticky="nsew")

        self.current_main_filter.set(image_filter)
        self.filtered_image.grid(column=0, row=1)
        self.filtered_image.grid_propagate(False)

    # Update filtered image based on the slider value
    def update_filter(self, value):
        # Get the current slider value
        self.filter_scale_val.set(value)

        # Get the current filter used (Black and White or Low Gamma)
        curr_filter = self.current_main_filter.get()
        if curr_filter == "Low Gamma":
            # If Low Gamma generate a new image with the chosen gamma constant
            self.filters["Low Gamma"] = generate_low_gamma(self.default_img, self.filter_scale_val.get())
        else:
            # Else if Black and White generate a new image with the chosen threshold value
            cv2_image = cv2.cvtColor(self.default_img, cv2.COLOR_BGR2GRAY)
            self.filters["Black and White"] = generate_bw(cv2_image, self.filter_scale_val.get())

        # Place the value on screen
        self.filtered_image = Label(self,
                                    image=self.filters[curr_filter],
                                    width=self.winfo_reqwidth(),
                                    height=int(self.winfo_reqheight() * 0.4))
        self.filtered_image.image = self.filters[curr_filter]
        self.states.curr_img = self.filters[curr_filter]
        self.filtered_image.grid(column=0, row=1)
        self.filtered_image.grid_propagate(False)

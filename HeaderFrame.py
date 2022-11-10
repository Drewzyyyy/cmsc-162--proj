from tkinter import Frame, Listbox


# Generates the frame for storing the list of image headers
class HeaderFrame(Frame):
    def __init__(self, parent, config: dict):
        # Specific config values for dimensions and background color
        self.config = config
        self.parent = parent

        Frame.__init__(self,
                       master=self.parent,
                       width=self.config["width"],
                       height=self.config["height"],
                       bg=self.config["bg"])
        self.grid(column=0, row=0)
        self.grid_propagate(False)
        self.update_idletasks()

        # Contains the list of header metadata
        self.header_list: Listbox = Listbox(self,
                                            width=int(self.config["width"] - 20),
                                            height=self.config["height"])
        self.header_list.grid(column=0, row=0)

    # Triggered when specific variables are changed in the state manager
    def notify(self, states):
        try:
            # Display the header metadata
            if states.headers_changed:
                if not states.img_headers:
                    self.header_list.delete(0, "end")
                    return
                self.display_header(states.img_headers)

        except ValueError:
            raise

    # Display the headers to the screen
    def display_header(self, img_headers):
        try:
            header_list = self.header_list
            header_list.delete(0, "end")
            for idx, header in enumerate(img_headers):
                if idx == 0:
                    header_list.insert(idx, f"{header.capitalize()}: Zshoft .pcx({img_headers[header]})")
                else:
                    header_list.insert(idx, f"{header.capitalize()}: {img_headers[header]}")
            header_list.grid(column=0, row=0)
        except ValueError:
            raise

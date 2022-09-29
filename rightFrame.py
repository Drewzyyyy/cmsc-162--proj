from tkinter import LabelFrame, Listbox


# Frame that displays the metadata/headers
class RightFrame:
    def __init__(self, parent):
        # Root Window
        self.parent = parent
        self.parent.update()

        # Constants
        window_dimensions = (400, self.parent.winfo_height())

        # Instantiate frame
        self.right_frame = LabelFrame(self.parent, width=window_dimensions[0], height=window_dimensions[1], bg="grey",
                                      borderwidth=2, relief="raised",
                                      text="Image Header Metadata")
        self.right_frame.grid(column=1, row=0, pady=10, padx=10, ipadx=5, ipady=5)

        # Boolean to allow frame to be seen in the screen
        self.show_right_frame = True

        # Contains the list of header metadata
        self.header_list = Listbox(self.right_frame, height=45, width=40)
        self.header_list.grid(column=0, row=0)

    # Add the headers to be displayed in the screen
    def insert_headers(self, img_headers):
        for idx, header in enumerate(img_headers):
            if idx == 0:
                self.header_list.insert(idx, f"{header.capitalize()}: Zshoft .pcx({img_headers[header]})")
            else:    
                self.header_list.insert(idx, f"{header.capitalize()}: {img_headers[header]}")

    # Remove the headers from the list on screen
    def remove_headers(self):
        self.header_list.delete(0, "end")

    # Shows or hides the right frame/metadata frame from the screen
    def display_headers(self):
        if self.show_right_frame:
            self.right_frame.grid_forget()
        else:
            self.right_frame.grid(column=1, row=0, pady=10, padx=10, ipadx=5, ipady=5)

        self.show_right_frame = not self.show_right_frame
        return self.show_right_frame

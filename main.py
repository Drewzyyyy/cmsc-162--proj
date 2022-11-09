from tkinter import Tk, \
    PhotoImage, \
    Label
from sys import platform
from MetadataFrame import MetadataFrame
from StateManager import StateManager
from ImageFrame import ImageFrame
from Menus import Menus

if __name__ == "__main__":
    # Window Config
    root = Tk()
    root.title('Cola PhotoEditor')

    # Setting window to zoomed is platform dependent
    if platform == "linux" or platform == "linux2":
        root.attributes("-zoomed", True)
    else:
        root.state("zoomed")
    root_icon = PhotoImage(file='assets/logo.png')
    root.iconphoto(False, root_icon)

    # Color Scheme
    BACKGROUND_COLOR = "#1d2d44"
    BLACK_LABEL_COLOR = "#0d1321"
    WHITE_LABEL_COLOR = "#f0ebd8"

    # Initialize State Manager
    state_manager = StateManager()

    # Set image tabs
    image_frame = ImageFrame(root, state_manager)
    root.update_idletasks()

    # Set metadata frame
    metadata_frame = MetadataFrame(root)
    root.update_idletasks()

    # These frames listen for changes
    state_manager.subscribe(image_frame)
    state_manager.subscribe(metadata_frame.header_frame)
    state_manager.subscribe(metadata_frame.histogram_frame)
    state_manager.subscribe(metadata_frame.filters_frame)
    root.update_idletasks()

    # Status bar below
    status_bar = Label(root, textvariable=state_manager.status, bg=BLACK_LABEL_COLOR, fg=WHITE_LABEL_COLOR)
    status_bar.grid(columnspan=2, row=2, sticky="NSEW", padx=10)

    # Instantiate Menus
    menubar = Menus(root, state_manager, metadata_frame)

    # Menubar listens for any changes
    state_manager.subscribe(menubar)

    # Runs the window
    root.config(menu=menubar, bg=BACKGROUND_COLOR)
    root.mainloop()

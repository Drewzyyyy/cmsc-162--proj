from tkinter import Tk, \
    PhotoImage, \
    Menu, \
    Label
from functools import partial
from sys import platform
from centerFrame import CenterFrame
from rightFrame import RightFrame
from StateManager import StateManager

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

    # Set frame
    center_frame = CenterFrame(root, state_manager)
    right_frame = RightFrame(root)

    # When specific variables are changed, subscribed classes are informed
    state_manager.subscribe(right_frame)
    root.update()

    # Status bar below
    status_bar = Label(root, textvariable=state_manager.status, bg=BLACK_LABEL_COLOR, fg=WHITE_LABEL_COLOR)
    status_bar.grid(columnspan=2, row=2, sticky="NSEW", padx=10)

    # Set Menubar
    menubar = Menu(root, background="grey", foreground="black", activebackground="white", activeforeground="black")

    # Menubar tabs
    file = Menu(menubar, tearoff=0)
    file.add_command(label="New")
    file.add_command(label="Open", command=center_frame.display_image)
    file.add_separator()
    file.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file)

    # Changes the color channel
    edit = Menu(menubar, tearoff=0)
    screen_reso = Menu(edit, tearoff=0)
    edit.add_cascade(label="Change Channel", menu=screen_reso)
    screen_reso.add_command(label="RED", command=partial(right_frame.display_histogram, "red"))
    screen_reso.add_command(label="GREEN", command=partial(right_frame.display_histogram, "green"))
    screen_reso.add_command(label="BLUE", command=partial(right_frame.display_histogram, "blue"))
    menubar.add_cascade(label="Edit", menu=edit)

    # Runs the window
    root.config(menu=menubar, bg=BACKGROUND_COLOR)
    root.mainloop()

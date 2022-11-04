from tkinter import Tk, \
    PhotoImage, \
    Menu, \
    Label
from tkinter.ttk import Notebook
from functools import partial
from sys import platform
from MetadataFrame import MetadataFrame
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

    # Set image tabs
    root.update_idletasks()
    notebook = Notebook(root, width=int(root.winfo_width() * 0.7), height=int(root.winfo_height() * 0.9))

    # Initialize State Manager
    state_manager = StateManager(notebook)
    notebook.bind('<<NotebookTabChanged>>', state_manager.change_tab)

    # Set image frame
    state_manager.add_tab()
    notebook.grid(column=0, rowspan=2, pady=10, padx=10)
    notebook.grid_propagate(False)
    notebook.update_idletasks()

    # Set metadata frame
    metadata_frame = MetadataFrame(root)
    root.update_idletasks()

    state_manager.subscribe(metadata_frame.header_frame)
    state_manager.subscribe(metadata_frame.histogram_frame)
    state_manager.subscribe(metadata_frame.filters_frame)
    root.update_idletasks()

    # Status bar below
    status_bar = Label(root, textvariable=state_manager.status, bg=BLACK_LABEL_COLOR, fg=WHITE_LABEL_COLOR)
    status_bar.grid(columnspan=2, row=2, sticky="NSEW", padx=10)

    # Set Menubar
    menubar = Menu(root, background="grey", foreground="black", activebackground="white", activeforeground="black")

    # Menubar tabs
    file = Menu(menubar, tearoff=0)
    file.add_command(label="New", command=state_manager.add_tab)
    file.add_command(label="Open", command=state_manager.get_current_tab().display_image)
    file.add_separator()
    file.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file)

    # Changes the color channel
    edit = Menu(menubar, tearoff=0)

    screen_reso = Menu(edit, tearoff=0)
    edit.add_cascade(label="Change Channel", menu=screen_reso)
    screen_reso.add_command(label="RED", command=partial(metadata_frame.histogram_frame.set_images, "Red"))
    screen_reso.add_command(label="GREEN", command=partial(metadata_frame.histogram_frame.set_images, "Green"))
    screen_reso.add_command(label="BLUE", command=partial(metadata_frame.histogram_frame.set_images, "Blue"))

    remove_tab = Menu(edit, tearoff=0)
    edit.add_cascade(label="Remove tab", menu=remove_tab)
    remove_tab.add_command(label="Current tab", command=state_manager.remove_current_tab)
    remove_tab.add_separator()
    menubar.add_cascade(label="Edit", menu=edit)

    # Runs the window
    root.config(menu=menubar, bg=BACKGROUND_COLOR)
    root.mainloop()

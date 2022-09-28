from tkinter import Tk, \
    PhotoImage, \
    Menu
from centerFrame import CenterFrame
from rightFrame import RightFrame


if __name__ == "__main__":
    # Window Config
    root = Tk()
    root.title('Cola PhotoEditor')
    root.attributes('-zoomed', True)
    root_icon = PhotoImage(file='assets/logo.png')
    root.iconphoto(False, root_icon)

    # Set frame
    right_frame = RightFrame(root)
    center_frame = CenterFrame(root, right_frame)

    # Set Menubar
    menubar = Menu(root, background="grey", foreground="black", activebackground="white", activeforeground="black")

    # Menubar tabs
    file = Menu(menubar, tearoff=0)
    file.add_command(label="New")
    file.add_command(label="Open", command=center_frame.display_image)
    file.add_command(label="Save")
    file.add_command(label="Save as")
    file.add_separator()
    file.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file)

    edit = Menu(menubar, tearoff=0)
    edit.add_command(label="View headers", command=right_frame.display_headers)
    menubar.add_cascade(label="Edit", menu=edit)

    # Runs the window
    root.config(menu=menubar, bg="#263D42")
    root.mainloop()

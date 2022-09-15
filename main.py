import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Window Config
root = tk.Tk()
root.title('Cola PhotoEditor')
root_icon = tk.PhotoImage(file='logo.png')
root.iconphoto(False, root_icon)


# Open Image in File Folders
def open_image():
    try:
        # Open folder
        filename = filedialog.askopenfilename(parent=root, title='Select File',
                                              filetypes=(("JPEGs", "*.jpg"), ("PNGs", "*.png"), ("all files", "*.*")))
        image = Image.open(filename)

        # Resize image
        resized_image = image.resize((240, 240))
        image = ImageTk.PhotoImage(resized_image)

    except AttributeError:
        # Display error on failure
        instructions_text.set("Image upload failed.")

    else:
        # Destroy instructions label
        instructions.destroy()

        # Display image in place of the instructions
        image_label = tk.Label(image=image, width=250, height=250)
        image_label.image = image
        image_label.grid(columnspan=3, column=0, row=1)


# Set canvas
canvas = tk.Canvas(root, height=700, width=700, bg="#263D42")
canvas.grid(columnspan=3, rowspan=3)

frame = tk.Frame(root, bg="white")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

# Instructions
instructions_text = tk.StringVar()
instructions_text.set("Select an image to view.")
instructions = tk.Label(root, textvariable=instructions_text, font="Calibri")
instructions.grid(columnspan=3, column=0, row=1)

# Browse btn
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text,
                       fg="white", bg="#263D42",
                       command=open_image)
browse_text.set("Browse")
browse_btn.grid(column=1, row=2)

# Runs the window
root.mainloop()

from tkinter import filedialog


# Open local image
def open_image():
    try:
        # Open folder
        return filedialog.askopenfilename(title='Select File',
                                          filetypes=(
                                              ("JPEGs", "*.jpg"), ("PNGs", "*.png"),
                                              ("all files", "*.*")))
    except AttributeError:
        raise AttributeError("Image upload failed.")

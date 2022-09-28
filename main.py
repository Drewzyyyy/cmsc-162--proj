import struct
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import sys

# Window Config
root = tk.Tk()
root.title('Cola PhotoEditor')
root_icon = tk.PhotoImage(file='logo.png')
root.iconphoto(False, root_icon)

# Open Image in File Folders
def open_image():
    try:
        # Open folder
        filename = filedialog.askopenfilename(parent=root, title='Select File', filetypes=(("JPEGs", "*.jpg"), ("PNGs", "*.png"), ("all files", "*.*")))
        image = Image.open(filename)

        # UNPACKING HEADER FILE

        # Manufacturer
        with open(f'{filename}', 'rb') as pcx:
            manufacturer = struct.unpack('B', pcx.read(1))[0]

        # Version
            version = struct.unpack('B', pcx.read(1))[0]
        
        # Encoding
            encoding = struct.unpack('B', pcx.read(1))[0]
        
        # Bits per Pixel
            bpp = struct.unpack('B', pcx.read(1))[0]

        # Window - xmin
            window_xmin = struct.unpack('H', pcx.read(2))[0]
        
        # Window - ymin
            window_ymin = struct.unpack('H', pcx.read(2))[0]
            
        # Window - xmax
            window_xmax = struct.unpack('H', pcx.read(2))[0]
            
        # Window - ymax
            window_ymax = struct.unpack('H', pcx.read(2))[0]
            
        # hdpi
            hdpi = struct.unpack('H', pcx.read(2))[0]
            
        # vdpi
            vdpi = struct.unpack('H', pcx.read(2))[0]
                    
        # number of color planes
            pcx.seek(65,0)
            ncp = struct.unpack('B', pcx.read(1))[0]
                    
        # bytes per line
            bpl = struct.unpack('H', pcx.read(2))[0]
            
        # palette info
            palette_info = struct.unpack('H', pcx.read(2))[0]
            
        # horizontal screen size
            hss = struct.unpack('H', pcx.read(2))[0]
            
        # vertical screen size
            vss = struct.unpack('H', pcx.read(2))[0]
            
        # Printing all header values in terminal
        # print('Zshoft .pcx(', manufacturer, ')')
        # print(version)
        # print(encoding)
        # print(bpp)
        # print(window_xmin, window_ymin, window_xmax, window_ymax)
        # print(hdpi)
        # print(vdpi)
        # print(ncp)
        # print(bpl)
        # print(palette_info)
        # print(hss)
        # print(vss)

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
browse_btn = tk.Button(root, textvariable=browse_text, command=open_image)
browse_text.set("Browse")
browse_btn.grid(column=1, row=2)

# Runs the window
root.mainloop()

from tkinter import filedialog
from struct import unpack
from PIL import Image


# Read .PCX header files
def read_pcx_header(file):
    pcx_headers = {}
    with open(file, 'rb') as pcx:
        pcx_headers['manufacturer'] = unpack('B', pcx.read(1))[0]
        pcx_headers['version'] = unpack('B', pcx.read(1))[0]
        pcx_headers['encoding '] = unpack('B', pcx.read(1))[0]
        pcx_headers['bpp'] = unpack('B', pcx.read(1))[0]
        pcx_headers['dimensions'] = (unpack('H', pcx.read(2))[0],
                                     unpack('H', pcx.read(2))[0],
                                     unpack('H', pcx.read(2))[0],
                                     unpack('H', pcx.read(2))[0])
        pcx_headers['hdpi'] = unpack('H', pcx.read(2))[0]
        pcx_headers['vdpi'] = unpack('H', pcx.read(2))[0]

        pcx.seek(65, 0)
        pcx_headers['ncp'] = unpack('B', pcx.read(1))[0]

        pcx_headers['bpl'] = unpack('H', pcx.read(2))[0]
        pcx_headers['palette_info'] = unpack('H', pcx.read(2))[0]
        pcx_headers['hss'] = unpack('H', pcx.read(2))[0]
        pcx_headers['vss'] = unpack('H', pcx.read(2))[0]
    return pcx_headers


# Open local image
def open_image():
    try:
        # Open folder
        filename: filedialog = filedialog.askopenfilename(title='Select File',
                                                          filetypes=(
                                                              ("JPEGs", "*.jpg"), ("PNGs", "*.png"),
                                                              ("all files", "*.*")))
        return Image.open(filename), filename
    except AttributeError:
        raise AttributeError("Image upload failed.")

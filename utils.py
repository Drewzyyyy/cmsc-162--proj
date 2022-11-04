from tkinter import filedialog
from PIL import Image
from PIL.ImageTk import PhotoImage
import cv2
import numpy as np
from random import randint
from copy import deepcopy


# Open local image
def open_image():
    try:
        # Open folder
        return filedialog.askopenfilename(title='Select File',
                                          filetypes=(
                                              ("PCXs", "*.pcx"), ("JPEGs", "*.jpg"), ("PNGs", "*.png"),
                                              ("all files", "*.*")))
    except AttributeError:
        raise AttributeError("Image upload failed.")


def get_imagetk(image):
    if type(image) == np.ndarray:
        image = Image.fromarray(image)
    return PhotoImage(image)


# Generate an image with a grayscale filter
def generate_grayscale(png_image):
    png_image = np.asarray(png_image)
    grayscale = png_image.astype('float')

    red = grayscale[:, :, 0]
    green = grayscale[:, :, 1]
    blue = grayscale[:, :, 2]

    grayscale_img = 0.2989 * red + 0.5870 * green + 0.1140 * blue

    grayscale_img = Image.fromarray(np.uint8(grayscale_img))

    grayscale_img.save('./assets/grayscale.png')

    return grayscale_img, np.uint8(grayscale_img)


def generate_colored_negative(negative_img_colored):
    for i in range(negative_img_colored.size[0] - 1):
        for j in range(negative_img_colored.size[1] - 1):

            color_of_pixel = negative_img_colored.getpixel((i, j))

            if type(color_of_pixel) == tuple:
                red = 256 - color_of_pixel[0]
                green = 256 - color_of_pixel[1]
                blue = 256 - color_of_pixel[2]

                negative_img_colored.putpixel((i, j), (red, green, blue))
            else:
                # for grayscale
                color_of_pixel = 256 - color_of_pixel
                negative_img_colored.putpixel((i, j), color_of_pixel)

    print('nega good')
    return get_imagetk(negative_img_colored)


# Generate a negative of the image grayscale
def generate_negative_grayscale(grayscale_img):
    for i in range(grayscale_img.size[0] - 1):
        for j in range(grayscale_img.size[1] - 1):

            color_of_pixel = grayscale_img.getpixel((i, j))

            if type(color_of_pixel) == tuple:
                red = 256 - color_of_pixel[0]
                green = 256 - color_of_pixel[1]
                blue = 256 - color_of_pixel[2]

                grayscale_img.putpixel((i, j), (red, green, blue))
            else:
                # for grayscale
                color_of_pixel = 256 - color_of_pixel
                grayscale_img.putpixel((i, j), color_of_pixel)

    print('nega grayscale good')
    return get_imagetk(grayscale_img)


# Generate a black and white image based on the image uploaded
def generate_bw(threshold: int = 127):
    png_img = cv2.imread('./assets/grayscale.png')
    (thresh, b_and_white) = cv2.threshold(
        png_img, threshold, 255, cv2.THRESH_BINARY)
    return get_imagetk(b_and_white)


# Generate an image with low gamma filter based on the image uploaded
def generate_low_gamma(gamma_const: float = 0.4):
    img = cv2.imread('./assets/pic.png')
    gamma = np.array(255 * (img / 255)
                     ** gamma_const, dtype='uint8')
    return get_imagetk(gamma)


# DREW: toggle to apply filter on salt and pepper image or purely grayscale lang for average, median
def salt_and_pepper(img):
    rows, cols = img.shape

    num_pix = randint(300, 10000)

    # Change to white
    for i in range(num_pix):
        y = randint(0, rows - 1)
        x = randint(0, cols - 1)
        img[y][x] = 255

    # Change to black
    num_pix = randint(300, 10000)
    for i in range(num_pix):
        y = randint(0, rows - 1)
        x = randint(0, cols - 1)
        img[y][x] = 0

    cv2.imwrite('./assets/salt_and_pepper.png', img)
    return get_imagetk(img)


def generate_averaging_filter(img):
    rows, cols = img.shape  # rows & columns

    mask = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
    mask = mask / 16

    new_img = np.zeros([rows, cols])

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            new_img[i, j] = img[i - 1, j - 1] * mask[0, 0] + img[i - 1, j] * mask[0, 1] + img[i - 1, j + 1] * mask[
                0, 2] + img[i, j - 1] * mask[1, 0] + img[i, j] * mask[1, 1] + img[i, j + 1] * mask[
                                1, 2] + img[i + 1, j - 1] * mask[2, 0] + img[i + 1, j] * mask[2, 1] + img[
                                i + 1, j + 1] * mask[2, 2]

    new_img = new_img.astype(np.uint8)
    print('ave filt good')
    return get_imagetk(new_img)


def median_filtering(img):
    rows, cols = img.shape  # rows & columns

    new_img = np.zeros([rows, cols])

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            tmp = [img[i - 1, j - 1],
                   img[i - 1, j],
                   img[i - 1, j + 1],
                   img[i, j - 1],
                   img[i, j],
                   img[i, j + 1],
                   img[i + 1, j - 1],
                   img[i + 1, j],
                   img[i + 1, j + 1]]

            tmp = sorted(tmp)
            new_img[i, j] = tmp[4]

    new_img = new_img.astype(np.uint8)
    print('medi filt good')
    return get_imagetk(new_img)


# Spatial domain laplacian
def highpass_laplacian(img):
    filter_data = np.array([[0, 1, 0],
                            [1, -4, 1],
                            [0, 1, 0]])

    filtered_img = cv2.filter2D(src=img, ddepth=-1, kernel=filter_data)

    filter_data2 = img + (-1 * filtered_img)

    clip = np.array(np.clip(filter_data2, 0, 255), dtype='uint8')

    print('lap good')
    return get_imagetk(clip)


def unsharp_masking(img):
    img = (img / 255)
    blurred_img = cv2.GaussianBlur(img, (31, 31), cv2.BORDER_DEFAULT)

    mask = img - blurred_img
    final = img + mask

    final = np.clip(final, 0, 255)
    final = cv2.normalize(final, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    final = final.astype('uint8')

    print('unsharp good')
    return get_imagetk(final)


def highboost(img):
    img = img / 255

    blurred_img = cv2.GaussianBlur(img, (31, 31), cv2.BORDER_DEFAULT)

    mask = img - blurred_img
    amplify_param = 5
    final = img + amplify_param * mask
    final = np.clip(final, 0, 255)
    final = cv2.normalize(final, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    final = final.astype('uint8')

    print('highboost good')
    return get_imagetk(final)


def gradient_sobel(img):
    row, col = np.shape(img)
    final_img = np.zeros(shape=(row, col))
    x_grad = np.zeros(shape=(row, col))
    y_grad = np.zeros(shape=(row, col))

    y_sobel = np.array(([[-1, -2, -1],
                         [0, 0, 0],
                         [1, 2, 1]]))

    x_sobel = np.array(([[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]]))

    for i in range(row - 2):
        for j in range(col - 2):
            x_partial = np.sum(np.multiply(x_sobel, img[i:i + 3, j:j + 3]))  # compute partial derivative of x
            y_partial = np.sum(np.multiply(y_sobel, img[i:i + 3, j:j + 3]))  # compute partial derivative of y
            x_grad[i + 1, j + 1] = x_partial
            y_grad[i + 1, j + 1] = y_partial
            final_img[i + 1, j + 1] = np.sqrt(x_partial ** 2 + y_partial ** 2)

    print('sobel good')
    return get_imagetk(final_img), get_imagetk(x_grad), get_imagetk(y_grad)


def generate_more_filters(base_image):
    if base_image == 'Grayscale':
        base_image = 'pic'
    else:
        base_image = 'salt_and_pepper'
    cv2_image = cv2.imread(f'./assets/{base_image}.png', 0)
    sobel_ave, sobel_x, sobel_y = gradient_sobel(cv2_image)

    return {
        "None": None,
        # average
        "Low Pass Average": generate_averaging_filter(deepcopy(cv2_image)),

        # median
        "Low Pass Median": median_filtering(deepcopy(cv2_image)),

        # high pass
        "High Pass Laplacian": highpass_laplacian(deepcopy(cv2_image)),

        # un-sharp mask
        "Unsharping Mask": unsharp_masking(deepcopy(cv2_image)),

        # high boost
        "Highboost Filtering": highboost(deepcopy(cv2_image)),

        # Sobel
        "Gradient Sobel Average": sobel_ave,
        "Gradient Sobel X": sobel_x,
        "Gradient Sobel Y": sobel_y,
    }

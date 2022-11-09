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
    png_image = np.asarray(png_image) # RGB array
    grayscale = png_image.astype('float') # convert to float

    # Splits into three arrays of red, green, and blue 
    red = grayscale[:, :, 0]
    green = grayscale[:, :, 1]
    blue = grayscale[:, :, 2]

    # Transformation function to convert RGB to greyscale
    grayscale_img = 0.2989 * red + 0.5870 * green + 0.1140 * blue

    # Converts to image
    grayscale_img = Image.fromarray(np.uint8(grayscale_img))

    grayscale_img.save('./assets/grayscale.png')

    return grayscale_img, np.uint8(grayscale_img)

# Generates the colored negative of an image
# As a parameter, it getes the colored image to convert.
def generate_colored_negative(negative_img_colored):
    for i in range(negative_img_colored.size[0] - 1):
        for j in range(negative_img_colored.size[1] - 1):
            
            # Gets the current pixel
            color_of_pixel = negative_img_colored.getpixel((i, j))

            # Checks if it is an RGB pixel
            if type(color_of_pixel) == tuple:
                # Conversion to negative
                red = 256 - color_of_pixel[0]
                green = 256 - color_of_pixel[1]
                blue = 256 - color_of_pixel[2]
                
                # Replaces the pixel of the image with the negative pixel
                negative_img_colored.putpixel((i, j), (red, green, blue))
            else:
                # for grayscale
                color_of_pixel = 256 - color_of_pixel
                negative_img_colored.putpixel((i, j), color_of_pixel)

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

    return get_imagetk(grayscale_img)


# Generate a black and white image based on the image uploaded
# Gets the user input regarding the manual threshold as a parameter
def generate_bw(threshold: int = 127):
    png_img = cv2.imread('./assets/grayscale.png')

    # When the pixel value is < threshold, it will be set to 0. If pixel value is > threshold, it will be set to 255
    # Produces the b&w image
    (thresh, b_and_white) = cv2.threshold(
        png_img, threshold, 255, cv2.THRESH_BINARY)
    return get_imagetk(b_and_white)


# Generate an image with law gamma filter based on the image uploaded
# Gets the user input regarding the gamma constant/value as a parameter
def generate_law_gamma(gamma_const: float = 0.4):
    img = cv2.imread('./assets/pic.png')

    # converts image to gamma filter using the gamma value the user selected
    gamma = np.array(255 * (img / 255)
                     ** gamma_const, dtype='uint8')
    return get_imagetk(gamma)

# Generates image w/ salt and pepper noise
# Gets the image as a parameter
def salt_and_pepper(img):
    rows, cols = img.shape
    
    # Randomly generates random number of pixels to be affected by the salt and pepper noise
    num_pix = randint(300, 10000)

    # Change to white
    for i in range(num_pix):
        # choose random coordinates
        y = randint(0, rows - 1) 
        x = randint(0, cols - 1)
        img[y][x] = 255 # turn random pixel to white

    # Change to black
    num_pix = randint(300, 10000) # Randomly generates random number of pixels to be affected by the salt and pepper noise
    for i in range(num_pix):
        # choose random coordinates
        y = randint(0, rows - 1)
        x = randint(0, cols - 1)
        img[y][x] = 0 # turn random pixel to black

    cv2.imwrite('./assets/salt_and_pepper.png', img)
    return get_imagetk(img)

# Generates image w/ averaging filter
# Gets the image as a parameter
def generate_averaging_filter(img):
    rows, cols = img.shape  # gets nos. of rows & columns

    # Weighted average mask
    mask = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
    mask = mask / 16 # normalization

    # Creates new array for new image w/ filter
    new_img = np.zeros([rows, cols])

    # Applies filter to the image by using the weighted average mask for every pixel
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            new_img[i, j] = img[i - 1, j - 1] * mask[0, 0] + img[i - 1, j] * mask[0, 1] + img[i - 1, j + 1] * mask[
                0, 2] + img[i, j - 1] * mask[1, 0] + img[i, j] * mask[1, 1] + img[i, j + 1] * mask[
                                1, 2] + img[i + 1, j - 1] * mask[2, 0] + img[i + 1, j] * mask[2, 1] + img[
                                i + 1, j + 1] * mask[2, 2]

    new_img = new_img.astype(np.uint8)
    return get_imagetk(new_img)

# Generates image w/ median filter
# Gets the image as a parameter
def median_filtering(img):
    rows, cols = img.shape  # rows & columns

    # Creates new array for new image w/ filter
    new_img = np.zeros([rows, cols])

    # Applies filter to the image by computing the median and substituting the median for the center pixel
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

            tmp = sorted(tmp) # sorts the values
            new_img[i, j] = tmp[4] # replaces pixel with the median of the tmp array

    new_img = new_img.astype(np.uint8)
    return get_imagetk(new_img)

# Generates image w/ spatial domain laplacian highpass filter
# Gets the image as a parameter
def highpass_laplacian(img):
    # Kernel for the laplacian filter
    filter_data = np.array([[0, 1, 0],
                            [1, -4, 1],
                            [0, 1, 0]])

    # Applies the kernel to the image, resulting in a laplacian image
    filtered_img = cv2.filter2D(src=img, ddepth=-1, kernel=filter_data)

    # Formula used in the book
    # Original image is added to the product of the constant and the filtered image
    # The constant used is -1 because the center of the kernel is negative
    filter_data2 = img + (-1 * filtered_img)

    clip = np.array(np.clip(filter_data2, 0, 255), dtype='uint8')

    return get_imagetk(clip)

# Generates image w/ unsharp masking filter
# Gets the image as a parameter
def unsharp_masking(img):
    img = (img / 255) # normalization
    blurred_img = cv2.GaussianBlur(img, (31, 31), cv2.BORDER_DEFAULT) # blurring the image

    # Subtracting blurred image from the original
    mask = img - blurred_img  
    final = img + mask # adds mask/filter for unsharp masking to the original image

    final = np.clip(final, 0, 255)
    final = cv2.normalize(final, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    final = final.astype('uint8')

    return get_imagetk(final)

# Generates image w/ highboost filter
# Gets the image as a parameter
def highboost(img):
    img = img / 255

    blurred_img = cv2.GaussianBlur(img, (31, 31), cv2.BORDER_DEFAULT) # blurring the image

    # Subtracting blurred image from the original
    mask = img - blurred_img
    amplify_param = 5 # amplification parameter
    # adds the product of the mask/filter and amplification parameter to the original image for highboost filtering
    final = img + amplify_param * mask 
    final = np.clip(final, 0, 255)
    final = cv2.normalize(final, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    final = final.astype('uint8')

    return get_imagetk(final)

# Generates image w/ sobel gradient
# Gets the image as a parameter
def gradient_sobel(img):
    row, col = np.shape(img) # Gets nos. of rows and columns
    final_img = np.zeros(shape=(row, col)) # Initializes new array for the final image
    x_grad = np.zeros(shape=(row, col)) # Initializes new array for sobel x-gradient
    y_grad = np.zeros(shape=(row, col)) # Initializes new array for sobel y-gradient

    # Sobel y-gradient mask
    y_sobel = np.array(([[-1, -2, -1],
                         [0, 0, 0],
                         [1, 2, 1]]))

    # Sobel x-gradient mask
    x_sobel = np.array(([[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]]))

    # Apply the mask to the image using the formula
    for i in range(row - 2):
        for j in range(col - 2):
            x_partial = np.sum(np.multiply(x_sobel, img[i:i + 3, j:j + 3]))  # compute partial derivative of x
            y_partial = np.sum(np.multiply(y_sobel, img[i:i + 3, j:j + 3]))  # compute partial derivative of y
            x_grad[i + 1, j + 1] = x_partial # sobel x-gradient
            y_grad[i + 1, j + 1] = y_partial # sobel y-gradient
            final_img[i + 1, j + 1] = np.sqrt(x_partial ** 2 + y_partial ** 2) # combines the x and y gradient to the image

    return get_imagetk(final_img), get_imagetk(x_grad), get_imagetk(y_grad)


def generate_more_filters(base_image):
    if base_image == 'Grayscale':
        base_image = 'pic'
    else:
        base_image = 'salt_and_pepper'
    cv2_image = cv2.imread(f'./assets/{base_image}.png', 0)
    sobel_ave, sobel_x, sobel_y = gradient_sobel(deepcopy(cv2_image))

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

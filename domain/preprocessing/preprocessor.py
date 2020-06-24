import cv2
import numpy as np

def add_padding(bordersize, image):
    row, col = image.shape[:2]
    bottom = image[row-2:row, 0:col]
    mean = cv2.mean(bottom)[0]
    return cv2.copyMakeBorder(
        image,
        top=bordersize,
        bottom=bordersize,
        left=bordersize,
        right=bordersize,
        borderType=cv2.BORDER_CONSTANT,
        value=[mean, mean, mean]
    )

def preprocess(image_path, write_directory):
    image = cv2.imread(image_path)
    image = add_padding(bordersize=300, image=image)
    cv2.imwrite(write_directory + "/preprocessed.png", image)

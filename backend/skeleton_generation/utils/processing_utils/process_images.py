import cv2 as cv
import numpy as np
import base64

def get_pixel_coordinates(image, scale_x, scale_y):
    non_zero_indices = np.nonzero(np.any(image != [255, 255, 255], axis=-1))
    scaled_coords = zip(non_zero_indices[1] * scale_x, non_zero_indices[0] * scale_y)
    return list(scaled_coords)

def process_image(image):
    
    target_height = image.shape[0]

    aspect_ratio = image.shape[1] / image.shape[0]
    target_width = int(target_height * aspect_ratio)

    scale_x = target_width / image.shape[1]
    scale_y = target_height / image.shape[0]

    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray_image, threshold1=30, threshold2=100)

    kernel = np.ones((5, 5), np.uint8)

    closed = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel)

    contours, _ = cv.findContours(closed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    white_image = np.ones_like(image) * 255

    # Draw blue contours on the white image
    cv.drawContours(white_image, contours, -1, (255, 0, 0), 1)

    # Now, we'll convert this image to a base64 string
    _, buffer = cv.imencode(".png", white_image)
    outline_img_base64 = base64.b64encode(buffer.tobytes()).decode("utf-8")

    coordinates = get_pixel_coordinates(white_image, scale_x, scale_y)
    height = edges.shape[0]
    contour_strings = [
        "{:.7e} {:.7e}".format(float(point[0][0]), float(height - point[0][1]))
        for contour in contours
        for point in contour
    ]

    output = {
        "coordinates": coordinates,
        "contour_strings": contour_strings,
        "outline_img_base64": outline_img_base64,
    }
    return output
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np


def get_pixel_coordinates(image, scale_x, scale_y):
    coords = []
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            if np.any(image[y, x] != [255, 255, 255]):
                coords.append((x * scale_x, y * scale_y))
    return coords


# Define the target height
target_height = 200

# Directory with images
images_directory = "M-to-PY_Skel/original"

# Loop over all files in the directory
for filename in os.listdir(images_directory):
    if not filename.endswith(".txt"):  # Check file extension
        # Load the image
        image_path = os.path.join(images_directory, filename)
        image = cv2.imread(image_path)

        aspect_ratio = image.shape[1] / image.shape[0]
        target_width = int(target_height * aspect_ratio)

        # Calculate scale factors for x and y coordinates
        scale_x = target_width / image.shape[1]
        scale_y = target_height / image.shape[0]

        # Resize the image while keeping the aspect ratio
        resized_image = cv2.resize(image, (target_width, target_height))

        # Convert the image to grayscale
        gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

        # Apply edge detection
        edges = cv2.Canny(gray_image, threshold1=30, threshold2=100)

        # Find contours
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Create a white image with the same dimensions as the resized image
        white_image = np.ones_like(resized_image) * 255

        # Draw blue contours on the white image
        cv2.drawContours(white_image, contours, -1, (255, 0, 0), 1)

        # Now we use matplotlib to plot the image and add axes.
        plt.figure(figsize=(5, 5))

        # Set up axes
        plt.axis([0, target_width, target_height, 0])

        # Display the image
        plt.imshow(cv2.cvtColor(white_image, cv2.COLOR_BGR2RGB))

        # Get the coordinates of all non-white pixels in the image
        coordinates = get_pixel_coordinates(white_image, scale_x, scale_y)

        # Define the output text file path
        output_txt_path = image_path.rsplit(".", 1)[0] + ".txt"

        # Save the coordinates to a text file
        with open(output_txt_path, "w") as f:
            height = edges.shape[0]
            for contour in contours:
                for point in contour:
                    f.write(
                        "{:.7e} {:.7e}\n".format(
                            float(point[0][0]), float(height - point[0][1])
                        )
                    )

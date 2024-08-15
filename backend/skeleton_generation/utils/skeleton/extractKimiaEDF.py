import base64
from io import BytesIO
import cv2 as cv

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from skeleton_generation.utils.skeleton.BlumMedialAxis import BlumMedialAxis


def generate_skeleton(contour_strings, target_width, target_height):

    # Convert contour_strings into numpy array
    rough = np.array([list(map(float, s.split())) for s in contour_strings])

    boundary = rough[:, 0] + 1j * rough[:, 1]
    bma = BlumMedialAxis(boundary)

    fig = bma.plot_with_edges()

    plt.axis('equal')
    plt.axis('off')
    plt.grid(False)
    plt.xlim(0, target_width)  # Set x-axis limits based on target width
    plt.ylim(0, target_height)  # Set y-axis limits based on target height

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.set_size_inches((target_width/100), (target_height/100))

    # Create buffer
    buf = BytesIO()

    # Save figure to buffer in PNG format
    plt.savefig(buf, format="png")
    buf.seek(0)
    
    # Read the buffer into a NumPy array
    img_array = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    
    # Convert the NumPy array to an OpenCV image (BGR format)
    img = cv.imdecode(img_array, cv.IMREAD_COLOR)
    
    plt.close()

    return img
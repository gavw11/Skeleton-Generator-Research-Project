import cv2 as cv
import numpy as np

def remove_white_background(image):
    # Convert image to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Apply threshold to get mask of white background
    _, mask = cv.threshold(gray, 240, 255, cv.THRESH_BINARY)

    # Invert mask
    mask_inv = cv.bitwise_not(mask)

    # Apply mask to get image with transparent background
    img_with_transparent_bg = cv.bitwise_and(image, image, mask=mask_inv)

    # Add alpha channel
    b_channel, g_channel, r_channel, a_channel = cv.split(img_with_transparent_bg)
    alpha_channel = mask_inv
    img_with_alpha = cv.merge((b_channel, g_channel, r_channel, alpha_channel))

    return img_with_alpha

def overlay_images(im0, im1):
    # Create a blank alpha channel with ones (fully opaque)
    alpha_channel = np.ones((im0.shape[0], im0.shape[1]), dtype=np.uint8) * 255

    # Merge BGR channels with the alpha channel
    im0 = cv.merge((im0, alpha_channel))


    # Check if images were loaded successfully
    if im0 is None or im1 is None:
        print(f"Error: Failed to load one of the images")
        return

    # Ensure im1 has alpha channel if it doesn't have one
    if im1.shape[2] == 3:
        im1 = cv.cvtColor(im1, cv.COLOR_BGR2BGRA)

    # Remove white background from im1
    im1_processed = remove_white_background(im1)

    # Ensure im0 and im1_processed have the same dimensions
    if im0.shape[:2] != im1_processed.shape[:2]:
        im1_processed = cv.resize(im1_processed, (im0.shape[1], im0.shape[0]))


    
    # Check dimensions explicitly
    if im0.shape != im1_processed.shape:
        print(f"Error: Dimensions do not match - im0: {im0.shape}, im1_processed: {im1_processed.shape}")
        return None

    # Check types
    if im0.dtype != im1_processed.dtype:
        print(f"Error: Types do not match - im0: {im0.dtype}, im1_processed: {im1_processed.dtype}")
        return None

    # Blend images using alpha blending
    blended_image = np.empty_like(im0)

    cv.addWeighted(im1_processed, 1, im0, 1, 0, blended_image)

    return blended_image


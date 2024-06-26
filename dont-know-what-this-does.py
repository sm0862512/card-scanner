import cv2
import numpy as np
import subprocess
import time

def is_contour_inside(contour1, contour2):
    """Check if contour1 is inside contour2."""
    point = tuple(float(coord) for coord in contour1[0][0])
    return cv2.pointPolygonTest(contour2, point, False) > 0

# Open the camera
cap = cv2.VideoCapture(0)

# Set the frame width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)  # Replace with your camera's max width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)  # Replace with your camera's max height

# Check if the camera is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open camera")

# Initialize the timer
start_time = None
timer_threshold = 5  # Set the timer threshold to 5 seconds

while True:
    # Capture a frame
    ret, img = cap.read()

    # Check if the frame is captured correctly
    if not ret or img is None:
        raise IOError("Cannot capture frame")

    # Apply the image processing steps
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (13,13), 0)
    edges = cv2.Canny(blur, 50, 150)
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out contours that are inside other contours
    outer_contours = [contour for i, contour in enumerate(contours) if not any(is_contour_inside(contour, other_contour) for j, other_contour in enumerate(contours) if i != j)]

    if outer_contours:
        # Find the largest contour
        largest_contour = max(outer_contours, key=cv2.contourArea)

        # Start the timer if it's not started
        if start_time is None:
            start_time = time.time()

        # Check if the timer has reached the threshold
        if time.time() - start_time >= timer_threshold:
            # Use minimum area rectangle to approximate the contour
            rect = cv2.minAreaRect(largest_contour)
            box = cv2.boxPoints(rect)
            box = np.intp(box)  # Use np.intp instead of np.int0 to avoid deprecation warning

            # Draw a box around the card
            cv2.drawContours(img, [box], 0, (0, 255, 0), 2)

            # Crop and save the image of the box
            x, y, w, h = cv2.boundingRect(largest_contour)
            cropped_img = img[y:y+h, x:x+w]
            cv2.imwrite('largest_box.jpg', cropped_img)

            # Run the command and exit
            cv2.destroyAllWindows()
            subprocess.run(["python", "photo.py"])


    else:
        # Reset the timer if the largest contour is not found
        start_time = None

    # Display the original frame
    cv2.imshow("Original", img)
    cv2.resizeWindow("Original", 1800, 1000)  # Resize the window to 640x480

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
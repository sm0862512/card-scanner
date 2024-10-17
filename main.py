import cv2  # OpenCV library for image processing
import numpy as np  # Library for numerical operations
import subprocess  # Library to run subprocesses
import time  # Library to handle time-related tasks
from multiprocessing import Queue  # Library to handle multiprocessing queues

def is_contour_inside(contour1, contour2):
    """Check if contour1 is inside contour2."""
    # Get a point from contour1
    point = tuple(float(coord) for coord in contour1[0][0])
    # Check if the point is inside contour2
    return cv2.pointPolygonTest(contour2, point, False) > 0

def main(status_queue):
    # Try different camera indices to find an available camera
    for index in range(5):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Camera opened successfully with index {index}")
            break
        cap.release()
    else:
        raise IOError("Cannot open camera. Please check if the camera is connected and accessible.")

    # Set the frame width and height
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)  # Replace with your camera's max width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)  # Replace with your camera's max height

    # Initialize the timer
    start_time = None
    timer_threshold = 5  # Set the timer threshold to 5 seconds
    scanned_cards = 0  # Counter for scanned cards

    while True:
        # Capture a frame from the camera
        ret, img = cap.read()

        # Check if the frame is captured correctly
        if not ret or img is None:
            raise IOError("Cannot capture frame. Please check if the camera is working properly.")

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur to the grayscale image
        blur = cv2.GaussianBlur(gray, (13, 13), 0)
        # Detect edges in the blurred image
        edges = cv2.Canny(blur, 50, 150)
        # Create a kernel for dilation
        kernel = np.ones((5, 5), np.uint8)
        # Dilate the edges to make them more pronounced
        dilated = cv2.dilate(edges, kernel, iterations=2)
        # Find contours in the dilated image
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
                cropped_img = img[y:y + h, x:x + w]
                cv2.imwrite('Magic-Card.png', cropped_img)

                # Update the scanned cards count
                scanned_cards += 1
                status_queue.put(scanned_cards)

                # Run the command to execute `photo.py` and exit
                cv2.destroyAllWindows()
                subprocess.run(["python", "photo.py"])
                break
        else:
            # Reset the timer if the largest contour is not found
            start_time = None

        # Display the original frame with the green box
        if outer_contours:
            rect = cv2.minAreaRect(largest_contour)
            box = cv2.boxPoints(rect)
            box = np.intp(box)
            cv2.drawContours(img, [box], 0, (0, 255, 0), 2)

        cv2.imshow("Original", img)
        cv2.resizeWindow("Original", 1800, 1000)  # Resize the window to 1800x1000

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    status_queue = Queue()  # Create a queue to share status between processes
    main(status_queue)  # Run the main function
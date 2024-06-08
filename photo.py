import cv2 as cv
import os
from tqdm import tqdm
from multiprocessing import Pool

def calculate_good_matches(args):
    filename, target_dir = args
    # Load the query image
    query_img = cv.imread('img.jpg', cv.IMREAD_GRAYSCALE)

    # Load the current image
    current_img = cv.imread(os.path.join(target_dir, filename), cv.IMREAD_GRAYSCALE)

    # Check if images are loaded correctly
    if query_img is None or current_img is None:
        #print(f"Error: Image {filename} not loaded correctly.")
        return filename, 0

    # Resize the query image
    query_img = cv.resize(query_img, (100, 100))

    # Resize the current image
    current_img = cv.resize(current_img, (100, 100))

    # Convert images to grayscale if they are not
    if len(query_img.shape) == 3:
        query_img = cv.cvtColor(query_img, cv.COLOR_BGR2GRAY)
    if len(current_img.shape) == 3:
        current_img = cv.cvtColor(current_img, cv.COLOR_BGR2GRAY)

    # Initiate SIFT detector
    sift = cv.SIFT_create()

    # Find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(query_img, None)
    kp2, des2 = sift.detectAndCompute(current_img, None)

    # Check if descriptors are computed correctly
    if des1 is None or des2 is None:
        #print(f"Error: Descriptors for image {filename} not computed correctly.")
        return filename, 0

    # BFMatcher with default params
    bf = cv.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])

    return filename, len(good)

if __name__ == '__main__':
    # Directory with the target images
    #target_dir = 'images/'
    target_dir = r'E:\magic things\full-download'

    # Variables to keep track of the best match
    best_match = None
    max_good_matches = 0
    best_match_percentage = 0

    # Create a multiprocessing Pool
    with Pool() as p:
        # Loop over all images in the target directory
        for filename in tqdm(os.listdir(target_dir)):
            # Process each image individually
            filename, num_good_matches = p.apply(calculate_good_matches, args=((filename, target_dir),))
            # If this image is a better match than the current best match, update the best match
            if num_good_matches > max_good_matches:
                max_good_matches = num_good_matches
                best_match = filename
                best_match_percentage = match_percentage

    # Print the best match
    print(f"The best match is: {best_match}")
    print(f"Match percentage: {best_match_percentage}%")
    print(f"Number of good matches: {max_good_matches}")

    # Load the query image
    query_img = cv.imread('largest_box.jpg')

    # Load the best match
    best_match_img = cv.imread(os.path.join(target_dir, best_match))

    # Display the images
    query_img = cv.resize(query_img, (500, 500))
    cv.imshow('Query Image', query_img)
    cv.imshow('Best Match', best_match_img)
    cv.waitKey(0)
    cv.destroyAllWindows()
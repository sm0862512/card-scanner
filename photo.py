import sqlite3  # Library to interact with SQLite databases
import cv2 as cv  # OpenCV library for image processing
import os  # Library for interacting with the operating system
import requests  # Library to make HTTP requests
from tqdm import tqdm  # Library to show progress bars
from multiprocessing import Pool  # Library to handle parallel processing

def query_database(name):
    # Connect to the SQLite database
    conn = sqlite3.connect('AllPrintings.sqlite')
    # Create a cursor to execute SQL commands
    c = conn.cursor()
    # Execute the query to find the card with the given UUID
    c.execute("SELECT * FROM cardidentifiers WHERE uuid=?", (name,))
    # Fetch all the results from the query
    results = c.fetchall()
    # Close the connection to the database
    conn.close()
    # Return the results
    return results

def calculate_good_matches(args):
    filename, target_dir = args

    # Load the query image (the image we are trying to match)
    query_img = cv.imread('Magic-Card.png', cv.IMREAD_GRAYSCALE)
    # Load the current image from the target directory
    current_img = cv.imread(os.path.join(target_dir, filename), cv.IMREAD_GRAYSCALE)

    # Check if images are loaded correctly
    if query_img is None or current_img is None:
        return filename, 0, 0

    # Resize both images to 100x100 pixels
    query_img = cv.resize(query_img, (100, 100))
    current_img = cv.resize(current_img, (100, 100))

    # Convert images to grayscale if they are not already
    if len(query_img.shape) == 3:
        query_img = cv.cvtColor(query_img, cv.COLOR_BGR2GRAY)
    if len(current_img.shape) == 3:
        current_img = cv.cvtColor(current_img, cv.COLOR_BGR2GRAY)

    # Initiate SIFT detector to find keypoints and descriptors
    sift = cv.SIFT_create()
    kp1, des1 = sift.detectAndCompute(query_img, None)
    kp2, des2 = sift.detectAndCompute(current_img, None)

    # Check if descriptors are computed correctly
    if des1 is None or des2 is None:
        return filename, 0, 0

    # Use BFMatcher to match descriptors
    bf = cv.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    # Calculate total number of matches
    total_matches = len(matches)

    # Apply ratio test to find good matches
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])

    # Calculate match percentage
    match_percentage = (len(good) / total_matches) * 100

    return filename, len(good), match_percentage

if __name__ == '__main__':
    # Directory with the images to be matched
    target_dir = 'images/'
    # Variables to keep track of the best match
    best_match = None
    max_good_matches = 0
    best_match_percentage = 0

    # Create a multiprocessing Pool to process images in parallel
    with Pool() as p:
        # Loop over all images in the target directory
        for filename in tqdm(os.listdir(target_dir)):
            # Process each image individually
            filename, num_good_matches, match_percentage = p.apply(calculate_good_matches, args=((filename, target_dir),))
            # If this image is a better match than the current best match, update the best match
            if num_good_matches > max_good_matches:
                max_good_matches = num_good_matches
                best_match = filename
                best_match_percentage = match_percentage

    # Print the best match details
    print(f"The best match is: {best_match}")
    print(f"Match percentage: {best_match_percentage}%")
    print(f"Number of good matches: {max_good_matches}")

    # Load the query image
    query_img = cv.imread('Magic-Card.png')
    # Load the best match image
    best_match_img = cv.imread(os.path.join(target_dir, best_match))

    # Extract the name of the best match image (without extension)
    name, extension = os.path.splitext(best_match)
    # Query the database for additional information about the card
    results = query_database(name)

    # Print the UUID of the best match card
    print(results[0][15])
    # Make an HTTP request to the Scryfall API to get the card's URL
    apiurl = requests.get('https://api.scryfall.com/cards/' + results[0][15])
    # Print the URL of the card
    print(apiurl.json()['scryfall_uri'])
    # Open the card's URL in the default web browser
    os.system(f'start {apiurl.json()['scryfall_uri']}')

    # Resize the query image for display
    query_img = cv.resize(query_img, (500, 500))
    # Display the query image and the best match image (commented out)
    # cv.imshow('Query Image', query_img)
    # cv.imshow('Best Match', best_match_img)
    cv.waitKey(0)
    cv.destroyAllWindows()
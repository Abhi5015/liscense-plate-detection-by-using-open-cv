import os
import cv2
import imutils
import pytesseract

# Ensure Tesseract OCR is correctly set up
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Read the image file
image_path = 'Car Images/100.jpg'
image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(f"Image not found at the specified path: {image_path}")

# Resize the image - change width to 500
image = imutils.resize(image, width=500)

# Display the original image
cv2.imshow("Original Image", image)
cv2.waitKey(0)

# RGB to Gray scale conversion
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow("1 - Grayscale Conversion", gray)
cv2.waitKey(0)

# Noise removal with iterative bilateral filter (removes noise while preserving edges)
gray = cv2.bilateralFilter(gray, 11, 17, 17)
cv2.imshow("2 - Bilateral Filter", gray)
cv2.waitKey(0)

# Find Edges of the grayscale image
edged = cv2.Canny(gray, 170, 200)
cv2.imshow("3 - Canny Edges", edged)
cv2.waitKey(0)

# Find contours based on Edges
cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# Create copy of original image to draw all contours
img1 = image.copy()
cv2.drawContours(img1, cnts, -1, (0, 255, 0), 3)
cv2.imshow("4- All Contours", img1)
cv2.waitKey(0)

# Sort contours based on their area keeping minimum required area as '30' (anything smaller than this will not be considered)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
NumberPlateCnt = None  # we currently have no Number plate contour

# Top 30 Contours
img2 = image.copy()
cv2.drawContours(img2, cnts, -1, (0, 255, 0), 3)
cv2.imshow("5- Top 30 Contours", img2)
cv2.waitKey(0)

# Ensure directory for cropped images exists
cropped_dir = 'Cropped Images-Text'
if not os.path.exists(cropped_dir):
    os.makedirs(cropped_dir)

# Loop over our contours to find the best possible approximate contour of number plate
count = 0
idx = 7
for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    # Select the contour with 4 corners
    if len(approx) == 4:
        NumberPlateCnt = approx  # This is our approx Number Plate Contour

        # Crop those contours and store it in Cropped Images folder
        x, y, w, h = cv2.boundingRect(c)  # This will find out co-ord for plate
        new_img = gray[y:y + h, x:x + w]  # Create new image
        cv2.imwrite(os.path.join(cropped_dir, str(idx) + '.png'), new_img)  # Store new image
        idx += 1

        break

# Drawing the selected contour on the original image
cv2.drawContours(image, [NumberPlateCnt], -1, (0, 255, 0), 3)
cv2.imshow("Final Image With Number Plate Detected", image)
cv2.waitKey(0)

# Load the cropped image
cropped_img_path = os.path.join(cropped_dir, '7.png')
cropped_img = cv2.imread(cropped_img_path)
if cropped_img is None:
    raise FileNotFoundError(f"Cropped image not found at the specified path: {cropped_img_path}")

cv2.imshow("Cropped Image ", cropped_img)
cv2.waitKey(0)

# Use Tesseract to convert image into string
text = pytesseract.image_to_string(cropped_img_path, lang='eng')
print("Number is :", text)

cv2.waitKey(0)  # Wait for user input before closing the images displayed
cv2.destroyAllWindows()

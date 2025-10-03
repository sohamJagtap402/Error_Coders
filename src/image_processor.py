import cv2
import numpy as np
from pdf2image import convert_from_path

def get_image_from_upload(file_path):
    """Handles PDF or image input and returns a high-quality OpenCV image."""
    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path, 300) # 300 DPI for quality
        if not images:
            raise ValueError("Could not convert PDF. The file might be corrupt or empty.")
        return cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
    else:
        image = cv2.imread(file_path)
        if image is None:
            raise FileNotFoundError(f"Could not read the image file at: {file_path}")
        return image

def preprocess_for_ocr(image_region):
    """
    Applies an aggressive filter pipeline to an image region to maximize OCR accuracy.
    This is the key to achieving high-quality text extraction.
    """
    if image_region is None or image_region.size == 0:
        return None # Return None if the input is invalid to prevent crashes
    
    # Convert to grayscale, which is standard for most OCR
    gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
    
    # Apply a sharpening filter to make text edges more distinct
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(gray, -1, sharpen_kernel)
    
    # Use Otsu's thresholding to create a clean, high-contrast black and white image
    _, thresh = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh
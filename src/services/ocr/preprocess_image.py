import cv2
import numpy as np


def deskew(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )

    return rotated


def preprocess_image(image_path: str) -> cv2.typing.MatLike:

    # Step by step image preprocessor:
    # 1. Load the image
    # 2. Resize the image
    # 3. Apply Denoising
    # 4. ApplyThresholding

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    deskewed_img = img  # deskew(img)
    resized_img = cv2.resize(
        deskewed_img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC
    )
    denoised_img = cv2.fastNlMeansDenoising(resized_img, None, 30, 7, 21)
    _, thresholded_img = cv2.threshold(
        denoised_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return thresholded_img

import cv2
import numpy as np

lower_hsv = np.array([[[138, 57, 190]]], dtype=np.uint8)
upper_hsv = np.array([[[177, 255, 255]]], dtype=np.uint8)

lower_bgr = cv2.cvtColor(lower_hsv, cv2.COLOR_HSV2BGR)[0][0]
upper_bgr = cv2.cvtColor(upper_hsv, cv2.COLOR_HSV2BGR)[0][0]

print(lower_bgr, upper_bgr)
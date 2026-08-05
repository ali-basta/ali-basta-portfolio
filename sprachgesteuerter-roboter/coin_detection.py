"""
Object detection: coins and target boxes.

Coins are found as circles via a Canny edge map feeding a Hough transform, then
classified by the mean colour inside the detected circle. Boxes are found as
large coloured blobs across the full frame.

The HSV thresholds below were tuned empirically for the specific camera and
lighting rig used in the lab. They are the part of this pipeline most likely to
need retuning on different hardware.
"""

import cv2
import numpy as np

MIN_RADIUS = 18
MAX_RADIUS = 40
MIN_DIST = 80
MIN_BOX_AREA = 200


def detect_circles(frame):
    """Detect coin-sized circles. Returns an array of (x, y, r) in pixels."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    gray = cv2.GaussianBlur(gray, (5, 5), 1.2)

    # Running Hough on an explicit edge map proved more selective here than
    # letting HoughCircles derive edges itself.
    edges = cv2.Canny(gray, 60, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    circles = cv2.HoughCircles(
        edges, cv2.HOUGH_GRADIENT,
        dp=1.4, minDist=MIN_DIST, param1=180, param2=50,
        minRadius=MIN_RADIUS, maxRadius=MAX_RADIUS,
    )
    if circles is None:
        return []
    return np.uint16(np.around(circles[0, :]))


def mean_color_in_circle(frame, x, y, r):
    """Mean BGR inside a circle, blurred first for a more stable HSV reading."""
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (x, y), r, 255, -1)
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    return tuple(map(int, cv2.mean(blurred, mask=mask)[:3]))


def classify_color(bgr):
    """Classify a BGR value as red / orange / green / blue, else 'unknown'.

    Red wraps around the hue circle, so it needs two ranges. The second red band
    catches darker reds whose hue drifts towards orange under this lighting.
    """
    h, s, v = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]

    if (h <= 6 or h >= 170) and s >= 30 and v >= 25:
        return "red"
    if 17 <= h <= 21 and s >= 60 and v < 80:
        return "red"
    if 7 <= h <= 17 and s >= 60 and v >= 90:
        return "orange"
    if 35 <= h <= 95 and s >= 25 and v >= 45:
        return "green"
    if 85 <= h <= 140 and s >= 30 and v >= 40:
        return "blue"

    return "unknown"


def detect_coins(frame, tf, pixels_to_plate):
    """Detect coins and return them with plate coordinates in millimetres.

    `tf` is a transform from plate_transform.compute_plate_transform().
    """
    results = []
    for x, y, r in detect_circles(frame):
        color = classify_color(mean_color_in_circle(frame, int(x), int(y), int(r)))
        if color == "unknown":
            continue
        x_mm, y_mm = pixels_to_plate(float(x), float(y), tf)
        results.append({
            "color": color,
            "radius_px": int(r),
            "u": int(x), "v": int(y),
            "x_mm": round(x_mm, 2), "y_mm": round(y_mm, 2),
        })
    return results


def select_detections(detections, amount, order):
    """Pick `amount` detections in the requested order.

    `amount` is an int or "all"; `order` is one of the VALID_ORDERS tokens
    produced by the command parser, or None to keep detection order.
    """
    sort_keys = {
        "left_to_right":  lambda d: d["x_mm"],
        "right_to_left":  lambda d: -d["x_mm"],
        "top_to_bottom":  lambda d: d["y_mm"],
        "bottom_to_top":  lambda d: -d["y_mm"],
        "largest_first":  lambda d: -d["radius_px"],
        "smallest_first": lambda d: d["radius_px"],
    }

    ordered = sorted(detections, key=sort_keys[order]) if order in sort_keys else list(detections)
    if amount == "all":
        return ordered
    return ordered[:int(amount)]

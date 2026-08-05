"""
Plate coordinate transform.

Converts camera pixel coordinates into millimetre coordinates on the work plate.

Two orange markers are fixed at known positions on the plate and act as the
reference frame. Detecting them in every frame gives a similarity transform
(rotation + uniform scale + translation) from image space to plate space, so the
camera does not need to be mounted in a fixed, precisely known pose: if it is
nudged or re-aimed, the transform simply resolves to new values on the next frame.

The robot's own frame was calibrated once onto this plate frame, which means the
rest of the pipeline works in a single set of coordinates and no runtime
conversion between camera and robot frames is needed.
"""

import math

import cv2
import numpy as np

# Position of the lower marker relative to the upper one (origin).
# World axes: X to the right, Y downwards.
PLATE_DX_MM = 340.0
PLATE_DY_MM = 340.0
PLATE_WIDTH_MM = 340.0
PLATE_HEIGHT_MM = 340.0

ORANGE_LOWER = np.array([5, 150, 150], np.uint8)
ORANGE_UPPER = np.array([25, 255, 255], np.uint8)


def detect_reference_markers(frame):
    """Locate the two orange corner markers in a full frame.

    Returns {"top": (u, v), "bottom": (u, v)} in pixels, or None if fewer than
    two orange blobs are found.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, ORANGE_LOWER, ORANGE_UPPER)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) < 2:
        return None

    # Keep the two largest blobs and take their centroids.
    centers = []
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:2]:
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue
        centers.append((moments["m10"] / moments["m00"],
                        moments["m01"] / moments["m00"]))

    if len(centers) != 2:
        return None

    centers.sort(key=lambda p: p[1])  # smaller v = higher in the image
    return {"top": centers[0], "bottom": centers[1]}


def compute_plate_transform(ref_points):
    """Derive a similarity transform from the two reference markers.

    The vector between the markers is known in millimetres (PLATE_DX/DY_MM) and
    measured in pixels, which fixes scale and rotation; the upper marker fixes
    the origin. Returns None if the two points coincide.
    """
    u_a, v_a = ref_points["top"]
    u_b, v_b = ref_points["bottom"]

    du_img, dv_img = u_b - u_a, v_b - v_a
    dist_img = math.hypot(du_img, dv_img)
    if dist_img < 1e-6:
        return None

    dist_plate = math.hypot(PLATE_DX_MM, PLATE_DY_MM)
    rotation = math.atan2(PLATE_DY_MM, PLATE_DX_MM) - math.atan2(dv_img, du_img)

    return {
        "u0": u_a,
        "v0": v_a,
        "scale": dist_plate / dist_img,   # mm per pixel
        "cos": math.cos(rotation),
        "sin": math.sin(rotation),
    }


def pixels_to_plate(u, v, tf):
    """Convert pixel coordinates to plate millimetres.

    Origin is the centre of the upper orange marker.
    """
    du = u - tf["u0"]
    dv = v - tf["v0"]

    du_rot = du * tf["cos"] - dv * tf["sin"]
    dv_rot = du * tf["sin"] + dv * tf["cos"]

    return du_rot * tf["scale"], dv_rot * tf["scale"]


def inside_plate_mm(u, v, tf, margin_mm=0.0):
    """Check whether a pixel falls inside the plate. Returns (inside, x_mm, y_mm)."""
    x_mm, y_mm = pixels_to_plate(u, v, tf)
    inside = (-margin_mm <= x_mm <= PLATE_WIDTH_MM + margin_mm
              and -margin_mm <= y_mm <= PLATE_HEIGHT_MM + margin_mm)
    return inside, x_mm, y_mm

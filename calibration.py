"""
Calibration module for detecting ArUco markers and calculating scale.
"""
import cv2
import numpy as np
from PIL import Image


def detect_aruco_marker(image_path, marker_size_cm=10.0, debug=False):
    """
    Detect ArUco marker in an image and calculate pixels per cm.

    Args:
        image_path: Path to the image file
        marker_size_cm: Real-world size of the marker in cm
        debug: If True, save debug visualization

    Returns:
        tuple: (pixels_per_cm, marker_corners, marker_id) or (None, None, None) if not found
    """
    # Load image
    img_pil = Image.open(image_path)
    img_array = np.array(img_pil.convert('RGB'))
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Initialize ArUco detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # Detect markers
    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is None or len(ids) == 0:
        print("  WARNING: No ArUco marker detected in image")
        print("  Make sure:")
        print("    1. The marker is visible and in focus")
        print("    2. The marker is well-lit")
        print("    3. The marker is not occluded or damaged")
        return None, None, None

    # Use the first detected marker
    marker_id = ids[0][0]
    marker_corners = corners[0][0]

    # Calculate marker size in pixels (average of all four sides)
    def distance(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    side_lengths = [
        distance(marker_corners[0], marker_corners[1]),  # Top
        distance(marker_corners[1], marker_corners[2]),  # Right
        distance(marker_corners[2], marker_corners[3]),  # Bottom
        distance(marker_corners[3], marker_corners[0])   # Left
    ]

    avg_side_length_px = np.mean(side_lengths)
    pixels_per_cm = avg_side_length_px / marker_size_cm

    print(f"  Detected ArUco marker ID: {marker_id}")
    print(f"  Marker size in image: {avg_side_length_px:.1f} pixels")
    print(f"  Calibrated scale: {pixels_per_cm:.2f} pixels/cm")

    # Optional: Save debug visualization
    if debug:
        debug_img = img_cv.copy()
        cv2.aruco.drawDetectedMarkers(debug_img, corners, ids)

        # Add text with calibration info
        text = f"ID:{marker_id} | {pixels_per_cm:.2f} px/cm"
        cv2.putText(debug_img, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Convert back to PIL for saving
        debug_img_rgb = cv2.cvtColor(debug_img, cv2.COLOR_BGR2RGB)
        debug_pil = Image.fromarray(debug_img_rgb)

        debug_path = str(image_path).replace('.', '_debug.')
        debug_pil.save(debug_path)
        print(f"  Debug image saved: {debug_path}")

    return pixels_per_cm, marker_corners, marker_id


def calibrated_cm_to_pixels(cm, pixels_per_cm):
    """
    Convert cm to pixels using calibrated scale.

    Args:
        cm: Distance in centimeters
        pixels_per_cm: Calibration factor from detect_aruco_marker()

    Returns:
        int: Distance in pixels
    """
    return int(cm * pixels_per_cm)


def verify_calibration(image_path, marker_size_cm=10.0):
    """
    Test calibration detection on an image.

    Args:
        image_path: Path to the image file
        marker_size_cm: Real-world size of the marker in cm
    """
    print(f"\nTesting calibration on: {image_path}")
    print(f"Expected marker size: {marker_size_cm} cm")

    result = detect_aruco_marker(image_path, marker_size_cm, debug=True)

    if result[0] is not None:
        pixels_per_cm, corners, marker_id = result
        print(f"\nCalibration successful!")
        print(f"  Marker ID: {marker_id}")
        print(f"  Scale factor: {pixels_per_cm:.2f} pixels/cm")
        print(f"\nExample conversions:")
        print(f"  1 cm = {calibrated_cm_to_pixels(1, pixels_per_cm)} pixels")
        print(f"  5 cm = {calibrated_cm_to_pixels(5, pixels_per_cm)} pixels")
        print(f"  10 cm = {calibrated_cm_to_pixels(10, pixels_per_cm)} pixels")
        return True
    else:
        print("\nCalibration failed - no marker detected")
        return False


if __name__ == '__main__':
    # Test mode - run calibration on an image
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python calibration.py <image_path> [marker_size_cm]")
        print("Example: python calibration.py images/test.png 10")
        sys.exit(1)

    image_path = Path(sys.argv[1])
    marker_size = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)

    verify_calibration(image_path, marker_size)

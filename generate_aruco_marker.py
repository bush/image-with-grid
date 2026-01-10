#!/usr/bin/env python3
"""
Generate ArUco marker for calibration purposes.
This marker should be printed and placed in photos for accurate grid calibration.
"""
import cv2
import numpy as np
from pathlib import Path
import argparse


def generate_aruco_marker(marker_id=0, marker_size_cm=10, dpi=300):
    """
    Generate an ArUco marker image for printing.

    Args:
        marker_id: ID of the marker (0-1023 for 6x6 markers)
        marker_size_cm: Desired printed size in centimeters
        dpi: Print resolution
    """
    # Use 6x6 dictionary (DICT_6X6_250 has 250 markers)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

    # Calculate pixel size based on desired cm and DPI
    # Convert cm to inches, then to pixels
    marker_size_inches = marker_size_cm / 2.54
    marker_size_pixels = int(marker_size_inches * dpi)

    # Generate the marker
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_pixels)

    # Create output with white border for better detection
    border_size = int(marker_size_pixels * 0.2)  # 20% border
    total_size = marker_size_pixels + 2 * border_size
    output_img = np.ones((total_size, total_size), dtype=np.uint8) * 255
    output_img[border_size:border_size+marker_size_pixels,
               border_size:border_size+marker_size_pixels] = marker_img

    return output_img, marker_size_pixels, total_size


def main():
    parser = argparse.ArgumentParser(
        description='Generate ArUco calibration marker for printing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 10cm marker (default)
  python generate_aruco_marker.py

  # Generate 5cm marker
  python generate_aruco_marker.py --size 5

  # Generate marker with specific ID
  python generate_aruco_marker.py --id 42 --size 15

Instructions:
  1. Run this script to generate a marker image
  2. Print the generated PNG file at 100% scale (no scaling!)
  3. Measure the printed marker to verify it's the correct size
  4. Place the marker in your photos for calibration
  5. Use --calibrate-size flag in add_grid.py with the marker size
        """)

    parser.add_argument('--id', type=int, default=0,
                        help='Marker ID (0-249, default: 0)')
    parser.add_argument('--size', type=float, default=10.0,
                        help='Marker size in cm (default: 10.0)')
    parser.add_argument('--dpi', type=int, default=300,
                        help='Print resolution DPI (default: 300)')
    parser.add_argument('--output', type=str, default='aruco_marker.png',
                        help='Output filename (default: aruco_marker.png)')

    args = parser.parse_args()

    if args.id < 0 or args.id >= 250:
        print("ERROR: Marker ID must be between 0 and 249")
        exit(1)

    print(f"Generating ArUco marker...")
    print(f"  Marker ID: {args.id}")
    print(f"  Target size: {args.size} cm")
    print(f"  DPI: {args.dpi}")

    marker_img, marker_px, total_px = generate_aruco_marker(
        args.id, args.size, args.dpi
    )

    # Save the image with DPI metadata
    output_path = Path(args.output)
    # OpenCV doesn't support DPI metadata directly, so use PIL
    from PIL import Image
    pil_img = Image.fromarray(marker_img)
    pil_img.save(output_path, dpi=(args.dpi, args.dpi))

    print(f"\nMarker generated successfully!")
    print(f"  Saved to: {output_path}")
    print(f"  Marker size: {marker_px}x{marker_px} pixels")
    print(f"  Total size (with border): {total_px}x{total_px} pixels")
    print(f"\nIMPORTANT:")
    print(f"  1. Print this image at 100% scale (no 'fit to page')")
    print(f"  2. Verify the printed marker measures {args.size} cm")
    print(f"  3. If size is incorrect, adjust DPI and regenerate")
    print(f"  4. Use --calibrate-size {args.size} when running add_grid.py")


if __name__ == '__main__':
    main()

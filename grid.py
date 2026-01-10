#!/usr/bin/env python3
"""
Experimental grid script with automatic calibration using ArUco markers.
Detects calibration marker in image and adjusts grid to true dimensions.
"""
from PIL import Image, ImageDraw, ImageFont
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from calibration import detect_aruco_marker, calibrated_cm_to_pixels


def add_calibrated_grid_to_image(img_path, output_path, marker_size_cm=10.0,
                                  grid_spacing_cm=1.0, line_color=(0, 0, 0),
                                  line_width=2, weight=None, debug=False):
    """
    Add grid lines to an image using ArUco marker calibration.

    Args:
        img_path: Path to input image
        output_path: Path to save output image
        marker_size_cm: Real-world size of the ArUco marker in cm
        grid_spacing_cm: Desired grid spacing in real-world cm
        line_color: RGB tuple for line color
        line_width: Line width in pixels
        weight: Optional weight text to display
        debug: Save debug visualization showing detected marker
    """
    print(f"\nProcessing: {img_path.name}")

    # Step 1: Detect ArUco marker and get calibration
    pixels_per_cm, marker_corners, marker_id = detect_aruco_marker(
        img_path, marker_size_cm, debug=debug
    )

    if pixels_per_cm is None:
        print("  SKIPPED: Could not detect calibration marker")
        return False

    # Step 2: Calculate grid spacing in pixels using calibrated scale
    grid_spacing_px = calibrated_cm_to_pixels(grid_spacing_cm, pixels_per_cm)
    print(f"  Grid spacing: {grid_spacing_cm} cm = {grid_spacing_px} pixels (calibrated)")

    # Step 3: Open image and draw grid
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    # Get DPI if available (for saving)
    dpi = img.info.get('dpi', (72, 72))[0]

    # Load fonts
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        timestamp_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
    except:
        font = ImageFont.load_default()
        timestamp_font = ImageFont.load_default()

    # Draw vertical lines and x-axis scale
    cm_counter = 0
    for x in range(0, img.width, grid_spacing_px):
        # Draw vertical line
        draw.line([(x, 0), (x, img.height)], fill=line_color, width=line_width)

        # Add scale label at the top
        label = f"{cm_counter}"
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = x - text_width // 2
        text_y = 5

        # Draw background rectangle
        padding = 2
        draw.rectangle(
            [(text_x - padding, text_y - padding),
             (text_x + text_width + padding, text_y + text_height + padding)],
            fill='white'
        )

        # Draw text
        draw.text((text_x, text_y), label, fill=line_color, font=font)

        cm_counter += grid_spacing_cm

    # Draw horizontal lines
    for y in range(0, img.height, grid_spacing_px):
        draw.line([(0, y), (img.width, y)], fill=line_color, width=line_width)

    # Add timestamp to bottom-right corner
    timestamp_label = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    bbox = draw.textbbox((0, 0), timestamp_label, font=timestamp_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    padding = 10
    text_x = img.width - text_width - padding
    text_y = img.height - text_height - padding

    bg_padding = 5
    draw.rectangle(
        [(text_x - bg_padding, text_y - bg_padding),
         (text_x + text_width + bg_padding, text_y + text_height + bg_padding)],
        fill='white'
    )
    draw.text((text_x, text_y), timestamp_label, fill=line_color, font=timestamp_font)

    # Add weight to top-right corner if provided
    if weight is not None:
        weight_label = f"Weight: {weight}"
        bbox = draw.textbbox((0, 0), weight_label, font=timestamp_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        padding = 10
        text_x = img.width - text_width - padding
        text_y = padding

        bg_padding = 5
        draw.rectangle(
            [(text_x - bg_padding, text_y - bg_padding),
             (text_x + text_width + bg_padding, text_y + text_height + bg_padding)],
            fill='white'
        )
        draw.text((text_x, text_y), weight_label, fill=line_color, font=timestamp_font)

    # Add calibration info to bottom-left corner
    calib_label = f"Calibrated: {pixels_per_cm:.2f} px/cm"
    bbox = draw.textbbox((0, 0), calib_label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    padding = 10
    text_x = padding
    text_y = img.height - text_height - padding

    bg_padding = 5
    draw.rectangle(
        [(text_x - bg_padding, text_y - bg_padding),
         (text_x + text_width + bg_padding, text_y + text_height + bg_padding)],
        fill='white'
    )
    draw.text((text_x, text_y), calib_label, fill=line_color, font=font)

    # Save
    img.save(output_path, dpi=(dpi, dpi))
    print(f"  Saved: {output_path.name}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Add calibrated grid lines to images using ArUco markers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow:
  1. Generate an ArUco marker:
     python generate_aruco_marker.py --size 10

  2. Print the marker and measure it to verify size

  3. Take photos with the marker visible in frame

  4. Run this script:
     python add_grid_calibrated.py --calibrate-size 10 --spacing 1.0

Examples:
  # 1cm calibrated grid with 10cm marker
  python add_grid_calibrated.py --calibrate-size 10 --spacing 1.0

  # 5cm grid with red lines and weight
  python add_grid_calibrated.py --calibrate-size 10 --spacing 5 --color red --weight "180 lbs"

  # Debug mode to visualize marker detection
  python add_grid_calibrated.py --calibrate-size 10 --debug

Note: The grid spacing now represents TRUE real-world dimensions based on the
      calibration marker, not DPI-based estimates.
        """)

    parser.add_argument('--calibrate-size', type=float, required=True,
                        help='Real-world size of the ArUco marker in cm (REQUIRED)')
    parser.add_argument('--spacing', type=float, default=5.0,
                        help='Grid spacing in centimeters (default: 5.0)')
    parser.add_argument('--line-width', type=int, default=2,
                        help='Line width in pixels (default: 2)')
    parser.add_argument('--color', type=str, default='black',
                        choices=['red', 'green', 'blue', 'black', 'white'],
                        help='Grid line color (default: black)')
    parser.add_argument('--weight', type=str, default=None,
                        help='Weight to display on the image (e.g., "180 lbs", "82 kg")')
    parser.add_argument('--debug', action='store_true',
                        help='Save debug images showing detected markers')

    args = parser.parse_args()

    # Color mapping
    color_map = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'black': (0, 0, 0),
        'white': (255, 255, 255)
    }

    # Setup paths
    images_dir = Path('images')

    # Create grid and originals directories with date
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = Path(f'grid_calibrated_{date_str}')
    originals_dir = Path(f'originals_calibrated_{date_str}')

    # Create directories if they don't exist
    output_dir.mkdir(exist_ok=True)
    originals_dir.mkdir(exist_ok=True)

    # Supported image formats
    supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}

    # Check if images directory exists
    if not images_dir.exists():
        print(f"ERROR: '{images_dir}' directory not found!")
        print("Please create an 'images' folder and place your images there.")
        exit(1)

    # Process all images in the images folder
    image_files = [f for f in images_dir.iterdir() if f.suffix.lower() in supported_formats]

    if not image_files:
        print(f"No image files found in '{images_dir}' directory.")
        print(f"Supported formats: {', '.join(supported_formats)}")
        exit(1)

    print(f"Found {len(image_files)} image(s) to process.")
    print(f"Looking for ArUco markers of size {args.calibrate_size} cm...")

    success_count = 0
    skipped_count = 0

    for img_path in image_files:
        # Copy original to originals directory
        original_dest = originals_dir / img_path.name
        try:
            shutil.copy2(img_path, original_dest)
            print(f"Copied: {img_path.name} -> originals_calibrated_{date_str}/")
        except Exception as e:
            print(f"  ERROR copying {img_path.name}: {e}")

        # Process the image
        output_path = output_dir / f"{img_path.stem}_calibrated_{date_str}{img_path.suffix}"
        try:
            success = add_calibrated_grid_to_image(
                img_path, output_path,
                marker_size_cm=args.calibrate_size,
                grid_spacing_cm=args.spacing,
                line_color=color_map[args.color],
                line_width=args.line_width,
                weight=args.weight,
                debug=args.debug
            )
            if success:
                success_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"  ERROR processing {img_path.name}: {e}")
            import traceback
            traceback.print_exc()
            skipped_count += 1

    print(f"\nDone!")
    print(f"  Successfully processed: {success_count} image(s)")
    print(f"  Skipped (no marker): {skipped_count} image(s)")
    print(f"  Originals saved to: '{originals_dir}'")
    print(f"  Grid images saved to: '{output_dir}'")

    if skipped_count > 0:
        print(f"\nTip: Make sure ArUco markers are visible and in focus.")
        print(f"     Use --debug flag to see detection visualization.")


if __name__ == '__main__':
    main()

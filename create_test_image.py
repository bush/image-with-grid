#!/usr/bin/env python3
"""
Create a test image with an ArUco marker for testing the calibration system.
"""
from PIL import Image, ImageDraw, ImageFont
import sys

def create_test_image(marker_path, output_path):
    """Create a test image with a marker and some reference objects."""

    # Load the marker
    marker = Image.open(marker_path)

    # Create a larger canvas (simulating a photo)
    canvas_width = 2400
    canvas_height = 1800
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

    # Draw some colored rectangles as "subjects" to measure
    draw = ImageDraw.Draw(canvas)

    # Draw a light gray background
    draw.rectangle([(0, 0), (canvas_width, canvas_height)], fill='#f0f0f0')

    # Draw some colored rectangles (pretend objects)
    # Blue rectangle - 200 pixels wide (should be measurable with calibration)
    draw.rectangle([(800, 500), (1000, 700)], fill='#3498db', outline='black', width=3)

    # Green rectangle
    draw.rectangle([(1200, 600), (1500, 900)], fill='#2ecc71', outline='black', width=3)

    # Red rectangle
    draw.rectangle([(500, 1000), (900, 1300)], fill='#e74c3c', outline='black', width=3)

    # Add some text labels
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font = ImageFont.load_default()

    draw.text((820, 550), "Object 1", fill='white', font=font)
    draw.text((1250, 700), "Object 2", fill='white', font=font)
    draw.text((620, 1100), "Object 3", fill='white', font=font)

    # Paste the marker in the top-left area
    # Resize marker to be reasonable in the scene (about 1/4 original size)
    marker_display_size = (marker.width // 3, marker.height // 3)
    marker_resized = marker.resize(marker_display_size, Image.Resampling.LANCZOS)

    # Position marker
    marker_x = 100
    marker_y = 100
    canvas.paste(marker_resized, (marker_x, marker_y))

    # Draw a border around the marker area
    draw.rectangle(
        [(marker_x - 5, marker_y - 5),
         (marker_x + marker_resized.width + 5, marker_y + marker_resized.height + 5)],
        outline='red', width=3
    )

    # Add label for marker
    draw.text((marker_x, marker_y - 50), "ArUco Marker (10cm)", fill='red', font=font)

    # Save the test image
    canvas.save(output_path, dpi=(300, 300))
    print(f"Test image created: {output_path}")
    print(f"  Size: {canvas_width}x{canvas_height} pixels")
    print(f"  Marker placed at: ({marker_x}, {marker_y})")
    print(f"  Marker display size: {marker_display_size[0]}x{marker_display_size[1]} pixels")

if __name__ == '__main__':
    marker_path = 'test_marker.png'
    output_path = 'images/test_calibration.png'

    create_test_image(marker_path, output_path)

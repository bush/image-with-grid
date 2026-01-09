from PIL import Image, ImageDraw, ImageFont
import argparse
import shutil
from pathlib import Path
from datetime import datetime

# Convert cm to pixels
def cm_to_pixels(cm, dpi):
    inches = cm / 2.54
    return int(inches * dpi)

def add_grid_to_image(img_path, output_path, grid_spacing_cm=1.0, line_color=(0, 0, 0), line_width=2, weight=None, viewpoint=None):
    """Add grid lines to an image"""
    print(f"\nProcessing: {img_path.name}")

    # Open the image
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    # Get DPI from image (default to 72 if not specified)
    if 'dpi' not in img.info:
        print("  WARNING: DPI not found in image metadata. Defaulting to 72 DPI.")
        print("  Grid spacing may not be accurate. Consider specifying DPI manually.")
        dpi = 72
    else:
        dpi = img.info['dpi'][0]  # Use horizontal DPI
        print(f"  Image DPI: {dpi}")

    # Calculate grid spacing in pixels
    grid_spacing_px = cm_to_pixels(grid_spacing_cm, dpi)
    print(f"  Grid spacing: {grid_spacing_cm} cm = {grid_spacing_px} pixels")

    # Try to load fonts
    try:
        # Try to use a system font for scale
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        # Font for timestamp - larger for easy readability
        timestamp_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
    except:
        # Fall back to default font
        font = ImageFont.load_default()
        timestamp_font = ImageFont.load_default()

    # Draw vertical lines and x-axis scale
    cm_counter = 0
    for x in range(0, img.width, grid_spacing_px):
        # Draw vertical line
        draw.line([(x, 0), (x, img.height)], fill=line_color, width=line_width)

        # Add scale label at the top
        label = f"{cm_counter}"
        # Get text bounding box to center it
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Draw text with a white background for visibility
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

    # Get text bounding box using larger font
    bbox = draw.textbbox((0, 0), timestamp_label, font=timestamp_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Position in bottom-right corner with padding
    padding = 10
    text_x = img.width - text_width - padding
    text_y = img.height - text_height - padding

    # Draw background rectangle for visibility
    bg_padding = 5
    draw.rectangle(
        [(text_x - bg_padding, text_y - bg_padding),
         (text_x + text_width + bg_padding, text_y + text_height + bg_padding)],
        fill='white'
    )

    # Draw timestamp text with larger font
    draw.text((text_x, text_y), timestamp_label, fill=line_color, font=timestamp_font)

    # Add weight to top-right corner if provided
    if weight is not None:
        weight_label = f"Weight: {weight}"

        # Get text bounding box using larger font
        bbox = draw.textbbox((0, 0), weight_label, font=timestamp_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position in top-right corner with padding
        padding = 10
        text_x = img.width - text_width - padding
        text_y = padding

        # Draw background rectangle for visibility
        bg_padding = 5
        draw.rectangle(
            [(text_x - bg_padding, text_y - bg_padding),
             (text_x + text_width + bg_padding, text_y + text_height + bg_padding)],
            fill='white'
        )

        # Draw weight text with larger font
        draw.text((text_x, text_y), weight_label, fill=line_color, font=timestamp_font)

    # Add viewpoint to top-left corner if provided
    if viewpoint is not None:
        viewpoint_label = f"Camera: {viewpoint}"

        # Get text bounding box using larger font
        bbox = draw.textbbox((0, 0), viewpoint_label, font=timestamp_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position in top-left corner with padding
        padding = 10
        text_x = padding
        text_y = padding

        # Draw background rectangle for visibility
        bg_padding = 5
        draw.rectangle(
            [(text_x - bg_padding, text_y - bg_padding),
             (text_x + text_width + bg_padding, text_y + text_height + bg_padding)],
            fill='white'
        )

        # Draw viewpoint text with larger font
        draw.text((text_x, text_y), viewpoint_label, fill=line_color, font=timestamp_font)

    # Save
    img.save(output_path, dpi=(dpi, dpi))
    print(f"  Saved: {output_path.name}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Add grid lines to images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 5cm grid with default settings
  python add_grid.py

  # 10cm grid with red lines
  python add_grid.py --spacing 10.0 --color red

  # 1cm grid with thicker lines
  python add_grid.py --spacing 1.0 --line-width 3

  # 5cm grid with weight displayed
  python add_grid.py --weight "180 lbs"

  # 5cm grid with weight in kilograms
  python add_grid.py --weight "82 kg"

  # 5cm grid with camera viewpoint information
  python add_grid.py --viewpoint "Dist: 2m, Height: 1.5m"

  # Combine weight and viewpoint
  python add_grid.py --weight "180 lbs" --viewpoint "Dist: 2m, Height: 1.5m"
        """)

    parser.add_argument('--spacing', type=float, default=5.0,
                        help='Grid spacing in centimeters (default: 5.0)')
    parser.add_argument('--line-width', type=int, default=2,
                        help='Line width in pixels (default: 2)')
    parser.add_argument('--color', type=str, default='black',
                        choices=['red', 'green', 'blue', 'black', 'white'],
                        help='Grid line color (default: black)')
    parser.add_argument('--weight', type=str, default=None,
                        help='Weight to display on the image (e.g., "180 lbs", "82 kg")')
    parser.add_argument('--viewpoint', type=str, default=None,
                        help='Camera viewpoint information (e.g., "Dist: 2m, Height: 1.5m")')

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
    output_dir = Path(f'grid_{date_str}')
    originals_dir = Path(f'originals_{date_str}')

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

    for img_path in image_files:
        # Copy original to originals directory
        original_dest = originals_dir / img_path.name
        try:
            shutil.copy2(img_path, original_dest)
            print(f"Copied: {img_path.name} -> originals_{date_str}/")
        except Exception as e:
            print(f"  ERROR copying {img_path.name}: {e}")

        # Process the image
        output_path = output_dir / f"{img_path.stem}_grid_{date_str}{img_path.suffix}"
        try:
            add_grid_to_image(
                img_path, output_path,
                grid_spacing_cm=args.spacing,
                line_color=color_map[args.color],
                line_width=args.line_width,
                weight=args.weight,
                viewpoint=args.viewpoint
            )
        except Exception as e:
            print(f"  ERROR processing {img_path.name}: {e}")

    print(f"\nDone!")
    print(f"  Originals saved to: '{originals_dir}'")
    print(f"  Grid images saved to: '{output_dir}'")

if __name__ == '__main__':
    main()

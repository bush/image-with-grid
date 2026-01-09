#!/usr/bin/env python3
"""
Script to explore and extract depth information from iPhone photos.
This will help determine what depth data is available for grid perspective correction.
"""

from PIL import Image
import os
import sys
from pathlib import Path

def analyze_image(image_path):
    """Analyze an image file for depth data and metadata."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {image_path.name}")
    print(f"{'='*80}")

    try:
        # Open the image
        img = Image.open(image_path)

        # Basic image info
        print(f"\n📷 Basic Info:")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
        print(f"   Size: {img.width} x {img.height} pixels")

        # EXIF data
        print(f"\n📊 EXIF Metadata:")
        exif = img.getexif()
        if exif:
            # Key EXIF tags we're interested in
            important_tags = {
                271: "Make",
                272: "Model",
                274: "Orientation",
                282: "XResolution",
                283: "YResolution",
                296: "ResolutionUnit",
                36867: "DateTimeOriginal",
                37377: "ShutterSpeedValue",
                37378: "ApertureValue",
                37379: "BrightnessValue",
                37380: "ExposureBias",
                37381: "MaxApertureValue",
                37383: "MeteringMode",
                37385: "Flash",
                37386: "FocalLength",
                41486: "FocalLengthIn35mmFilm",
                41989: "FocalLengthIn35mmFormat",
            }

            found_tags = False
            for tag_id, tag_name in important_tags.items():
                value = exif.get(tag_id)
                if value:
                    print(f"   {tag_name}: {value}")
                    found_tags = True

            if not found_tags:
                print("   No relevant EXIF data found")

            # Print all EXIF tags for debugging
            print(f"\n📋 All EXIF Tags ({len(exif)} total):")
            for tag_id, value in exif.items():
                print(f"   Tag {tag_id}: {value}")
        else:
            print("   No EXIF data found")

        # Check for additional image info
        print(f"\n🔍 Additional Image Info:")
        print(f"   Info dict keys: {list(img.info.keys())}")
        for key, value in img.info.items():
            if isinstance(value, (str, int, float, tuple)):
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: <{type(value).__name__} - {len(str(value))} chars>")

        # Check for depth map in image layers/bands
        print(f"\n🗺️  Depth Map Check:")
        print(f"   Image bands: {img.getbands()}")
        print(f"   Number of layers: {len(img.getbands())}")

        # For HEIC/Portrait mode images, depth might be in auxiliary images
        # Try to check if this is a format that might contain depth
        if img.format in ['JPEG', 'HEIF', 'HEIC']:
            print(f"   ✓ Format {img.format} may contain depth data")
            print(f"   Note: Depth extraction requires specialized libraries")
        else:
            print(f"   ✗ Format {img.format} unlikely to contain depth data")

    except Exception as e:
        print(f"❌ Error analyzing {image_path.name}: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to analyze all images in the images directory."""
    print("\n" + "="*80)
    print("iPhone Depth Data Explorer")
    print("="*80)

    # Check images directory
    images_dir = Path('images')
    if not images_dir.exists():
        print(f"\n❌ ERROR: '{images_dir}' directory not found!")
        print("Please create an 'images' folder and place your iPhone photos there.")
        sys.exit(1)

    # Supported formats
    supported_formats = {'.png', '.jpg', '.jpeg', '.heic', '.heif', '.bmp', '.tiff', '.tif'}

    # Find all image files
    image_files = [f for f in images_dir.iterdir()
                   if f.is_file() and f.suffix.lower() in supported_formats]

    if not image_files:
        print(f"\n❌ No image files found in '{images_dir}' directory.")
        print(f"Supported formats: {', '.join(supported_formats)}")
        sys.exit(1)

    print(f"\nFound {len(image_files)} image(s) to analyze.")

    # Analyze each image
    for img_path in image_files:
        analyze_image(img_path)

    # Recommendations
    print("\n" + "="*80)
    print("📝 Recommendations:")
    print("="*80)
    print("""
For depth-aware grid rendering, we need:

1. Depth Map Data
   - iPhone Portrait mode photos store depth in auxiliary images
   - Requires 'pillow-heif' or 'pyheif' libraries to extract
   - May need to convert HEIC to access depth data

2. Camera Intrinsics
   - Focal length (found in EXIF)
   - Sensor dimensions (may need to look up based on iPhone model)
   - Needed to calculate real-world dimensions from depth

3. Next Steps:
   a) Install depth extraction libraries: pip install pillow-heif
   b) Try extracting depth maps from Portrait mode photos
   c) Implement perspective-correct grid based on depth data

Note: Not all photos contain depth data - only Portrait mode or
      photos taken with depth capture enabled.
""")

if __name__ == '__main__':
    main()

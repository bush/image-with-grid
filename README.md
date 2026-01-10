# Calibrated Grid System

This experimental system uses ArUco markers to automatically calibrate grid spacing to represent true real-world dimensions in your photos.

## What's the Difference?

- **Original `add_grid.py`**: Uses DPI metadata to estimate grid spacing. Not always accurate.
- **New `add_grid_calibrated.py`**: Detects a calibration marker in your photo and calculates exact pixel-to-cm ratio. Much more accurate!

## How It Works

1. Print an ArUco marker of known size (e.g., 10cm)
2. Place the marker in your photos
3. The script detects the marker and calculates: `pixels_per_cm = marker_size_in_pixels / marker_size_in_cm`
4. Grid lines are drawn using this calibrated scale

## Quick Start Guide

### Step 1: Install Dependencies

```bash
pip install -r requirements-calibrated.txt
```

This installs:
- Pillow (image processing)
- opencv-python (ArUco marker detection)
- numpy (required by OpenCV)

### Step 2: Generate an ArUco Marker

```bash
python generate_aruco_marker.py --size 10
```

This creates `aruco_marker.png` - a 10cm x 10cm calibration marker.

**Options:**
- `--size 10`: Marker size in cm (default: 10)
- `--id 0`: Marker ID 0-249 (default: 0)
- `--dpi 300`: Print resolution (default: 300)
- `--output filename.png`: Custom output filename

### Step 3: Print the Marker

1. Print `aruco_marker.png` at **100% scale** (no "fit to page")
2. Use high-quality printer settings
3. **Measure the printed marker** with a ruler to verify it's exactly 10cm
4. If it's not exactly 10cm, adjust the `--dpi` value and regenerate

**Tip:** Laminate or mount the marker on cardboard for durability.

### Step 4: Take Photos with the Marker

- Place the marker somewhere visible in your photos
- The marker should be:
  - In focus and well-lit
  - Flat (not curled or bent)
  - Not occluded or partially hidden
  - Reasonably sized in frame (not tiny)

### Step 5: Run the Calibrated Grid Script

```bash
# Place your images in the 'images/' folder
python add_grid_calibrated.py --calibrate-size 10 --spacing 1.0
```

The script will:
1. Detect the ArUco marker in each image
2. Calculate the calibrated scale
3. Draw a grid where each square represents 1cm x 1cm
4. Save results to `grid_calibrated_YYYY-MM-DD/`

## Command-Line Options

### Required:
- `--calibrate-size 10`: Real-world size of your marker in cm

### Optional:
- `--spacing 1.0`: Grid spacing in cm (default: 5.0)
- `--line-width 2`: Line thickness in pixels (default: 2)
- `--color black`: Line color: red, green, blue, black, white (default: black)
- `--weight "180 lbs"`: Display weight on image
- `--viewpoint "2m away"`: Display camera distance/height
- `--debug`: Save debug images showing marker detection

## Examples

```bash
# 1cm grid with 10cm calibration marker
python add_grid_calibrated.py --calibrate-size 10 --spacing 1

# 5cm grid with weight and viewpoint
python add_grid_calibrated.py --calibrate-size 10 --spacing 5 --weight "82 kg" --viewpoint "Dist: 2m"

# Red 2cm grid with debug visualization
python add_grid_calibrated.py --calibrate-size 10 --spacing 2 --color red --debug

# Thick black 1cm grid
python add_grid_calibrated.py --calibrate-size 10 --spacing 1 --line-width 4
```

## Testing the Calibration

Before processing all your images, test the calibration:

```bash
# Test on a single image
python calibration.py images/test.png 10
```

This will:
- Detect the marker
- Show the calibrated scale (pixels per cm)
- Save a debug image with marker highlighted
- Display example conversions (1cm, 5cm, 10cm in pixels)

## Troubleshooting

### "No ArUco marker detected"

**Causes:**
- Marker is not in the image
- Marker is out of focus or blurry
- Marker is too small in frame
- Poor lighting or glare on marker
- Marker is damaged or printed incorrectly

**Solutions:**
1. Use `--debug` flag to see what the detector sees
2. Ensure marker is clear and well-lit
3. Make marker larger in frame
4. Verify printed marker size is correct
5. Try regenerating with higher `--dpi`

### Grid spacing seems wrong

**Causes:**
- Wrong `--calibrate-size` value
- Marker was printed at wrong scale
- Marker is at an angle to camera

**Solutions:**
1. Measure your printed marker with a ruler
2. Use the exact measured size in `--calibrate-size`
3. Keep marker as flat and perpendicular to camera as possible

### Script crashes with OpenCV error

**Solution:**
```bash
pip install --upgrade opencv-python
```

## How ArUco Markers Work

ArUco markers are like QR codes designed for computer vision:
- Black and white pattern that's easy for cameras to detect
- Built-in error correction
- Can be detected at various angles and distances
- Each marker has a unique ID
- Widely used in robotics, AR, and photogrammetry

The 6x6_250 dictionary we use has 250 different marker IDs (0-249).

## File Overview

| File | Purpose |
|------|---------|
| `generate_aruco_marker.py` | Creates printable ArUco markers |
| `calibration.py` | Core calibration logic (marker detection) |
| `add_grid_calibrated.py` | Main script - adds calibrated grid to images |
| `requirements-calibrated.txt` | Python dependencies |
| `add_grid.py` | Original DPI-based script (unchanged) |

## Use Cases

This calibrated system is perfect for:
- Body measurement tracking (fitness progress photos)
- Medical/clinical photography
- Product sizing verification
- Scientific documentation
- Forensic photography
- Any application requiring accurate dimensional measurements from photos

## Limitations

- Marker must be visible in frame
- Works best when marker is perpendicular to camera
- Assumes flat subject at same distance as marker
- For 3D subjects or varying depths, only objects at marker's distance will have accurate scaling

## Advanced: Perspective Correction

The current system assumes objects are at the same distance as the marker. For objects at different depths, the grid represents the scale at the marker's distance. For true 3D calibration, you would need:
- Camera intrinsics (focal length, sensor size)
- Depth map or 3D reconstruction
- Perspective transformation math

This is a much more complex project but could be added in the future!

# Worm_annotation

This is a GUI to annotate deeptangle labels.
## Installation

Installation steps:
* git clone, or download, this repository in a folder of your computer
* git clone https://github.com/WeheliyeHashi/Worm_annotation.git
* open a terminal window in that folder


```bash
conda env create -f requirements.yml
conda activate Worm_annotation
pip install -e .
```


## Starting the program

Now that the GUI is installed, you can launch it by executing
`worm_annotator` in your terminal window (provided the `Worm_annotation`
environment is active)


### Updating an existing installation

Assuming that this code was cloned or donwloaded to desktop and that the `Worm_annotation` environment has already been created, you can update the code by executing
```bash
cd ~/Worm_annotation
conda activate Worm_annotation
git pull
pip install -e .
```
```
# Video Clip Extractor with Spatial Tiling

This script extracts grayscale clips of 11 frames from a video, skips frames as specified, and tiles each clip spatially into non-overlapping `512x512` patches. The resulting patches are saved in an HDF5 file for downstream machine learning or analysis tasks.

## Features

- Supports temporal downsampling using frame skipping
- Extracts fixed-length clips (default: 11 frames)
- Tiles each frame spatially into `512x512` patches
- Saves data into compressed HDF5 format

## small code to create data annotation from videos.

```python
import numpy as np
import h5py
import cv2
from pathlib import Path

# Parameters
video_file = Path("data/video_1.mp4")
skip_frame = 10
frames = 11
patch_size = 512

# Paths
save_file = Path(f"data_annotation/{video_file.stem}_annotations.hdf5")
save_file.parent.mkdir(parents=True, exist_ok=True)

# Load video
cap = cv2.VideoCapture(str(video_file))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
ret, sample_frame = cap.read()
if not ret:
    raise RuntimeError("Could not read video.")
H, W = sample_frame.shape[:2]
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start

# Create HDF5 file
with h5py.File(save_file, 'a' if save_file.exists() else 'w') as f:
    y_group = f.require_group('y_train')
    x_group = f.require_group('x_train')
    clip_idx = 0

    for i in range(0, frame_count - frames * skip_frame, skip_frame * frames):
        clip = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        for _ in range(frames * skip_frame):
            ret, frame = cap.read()
            if not ret:
                break
            clip.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        clip = clip[::skip_frame]  # Downsample temporally

        if len(clip) != frames:
            print(f"Skipping clip {clip_idx}: not enough frames.")
            continue

        clip_np = np.stack(clip)  # Shape: (11, H, W)

        # Tile each clip spatially
        for y in range(0, H - patch_size + 1, patch_size):
            for x in range(0, W - patch_size + 1, patch_size):
                patch = clip_np[:, y:y+patch_size, x:x+patch_size]
                if patch.shape == (frames, patch_size, patch_size):
                    name = f"array_{clip_idx:06d}"
                    x_group.create_dataset(name, data=patch[None], compression='gzip')
                    y_group.create_dataset(name, data=np.zeros([1, 1, 3, 49, 2]), compression='gzip')
                    clip_idx += 1

cap.release()
```

## Example Usage

```python
video_file = Path("data/video_1.mp4")
skip_frame = 10
frames = 11
patch_size = 512

# Then run the script
python your_script.py
```

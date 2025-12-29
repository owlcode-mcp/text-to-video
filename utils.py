"""
Utility functions for text-to-video generation
"""
import os
from datetime import datetime
from tqdm import tqdm
import numpy as np

def generate_filename(prefix="video", extension="mp4"):
    """Generate timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def format_filesize(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def extend_video_frames(frames, target_duration, fps):
    """
    Extend video frames to match target duration

    Args:
        frames: numpy array of video frames (T, H, W, C)
        target_duration: desired duration in seconds
        fps: frames per second

    Returns:
        Extended frames array
    """
    current_frames = len(frames)
    target_frames = int(target_duration * fps)

    if current_frames >= target_frames:
        return frames[:target_frames]

    # Calculate how many times to loop
    loops_needed = (target_frames // current_frames) + 1

    # Repeat frames
    extended = np.tile(frames, (loops_needed, 1, 1, 1))

    # Trim to exact length
    return extended[:target_frames]

def interpolate_frames(frames, target_frames):
    """
    Simple frame interpolation using linear interpolation

    Args:
        frames: numpy array of video frames (T, H, W, C)
        target_frames: desired number of frames

    Returns:
        Interpolated frames array
    """
    from scipy import interpolate

    current_frames = len(frames)
    if current_frames >= target_frames:
        return frames[:target_frames]

    # Create interpolation indices
    x = np.linspace(0, current_frames - 1, current_frames)
    x_new = np.linspace(0, current_frames - 1, target_frames)

    # Interpolate each pixel channel
    interpolated = np.zeros((target_frames, *frames.shape[1:]), dtype=frames.dtype)

    for h in range(frames.shape[1]):
        for w in range(frames.shape[2]):
            for c in range(frames.shape[3]):
                f = interpolate.interp1d(x, frames[:, h, w, c], kind='linear')
                interpolated[:, h, w, c] = f(x_new)

    return interpolated

class ProgressCallback:
    """Callback for tracking generation progress"""

    def __init__(self, total_steps):
        self.pbar = tqdm(total=total_steps, desc="Generating video")
        self.step = 0

    def __call__(self, pipe, step, timestep, callback_kwargs):
        self.step += 1
        self.pbar.update(1)
        return callback_kwargs

    def close(self):
        self.pbar.close()

def print_system_info():
    """Print system information for debugging"""
    import torch
    import config

    print("\n=== System Information ===")
    print(f"Device: {config.detect_device()}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {config.get_available_vram():.2f} GB")
        print(f"Use quantization: {config.should_use_quantization()}")
    else:
        print("No GPU detected - will use CPU (slow)")

    print("=" * 30 + "\n")

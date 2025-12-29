"""
Configuration module for text-to-video generation
"""
import os
import torch

# Model configurations
MODELS = {
    'cogvideox-2b': {
        'repo_id': 'THUDM/CogVideoX-2b',
        'min_vram_gb': 8,
        'default_resolution': (480, 720),
        'max_frames': 49,
        'fps': 8,
    },
    'cogvideox-5b': {
        'repo_id': 'THUDM/CogVideoX-5b',
        'min_vram_gb': 24,
        'default_resolution': (720, 1280),
        'max_frames': 49,
        'fps': 8,
    },
}

# Resolution presets
RESOLUTIONS = {
    '480p': (480, 720),
    '720p': (720, 1280),
    '1080p': (1080, 1920),
}

# Default settings
DEFAULT_MODEL = 'cogvideox-2b'
DEFAULT_RESOLUTION = '480p'
DEFAULT_DURATION = 10
DEFAULT_FPS = 8
OUTPUT_DIR = 'outputs'

# FTP Configuration (from environment or MCP)
FTP_HOST = os.getenv('FTP_HOST', '')
FTP_PORT = int(os.getenv('FTP_PORT', '21'))
FTP_USER = os.getenv('FTP_USER', '')
FTP_PASSWORD = os.getenv('FTP_PASSWORD', '')
FTP_REMOTE_DIR = os.getenv('FTP_REMOTE_DIR', '/videos')

def detect_device():
    """Detect available compute device"""
    if torch.cuda.is_available():
        return 'cuda'
    elif torch.backends.mps.is_available():
        return 'mps'
    else:
        return 'cpu'

def get_available_vram():
    """Get available VRAM in GB"""
    if torch.cuda.is_available():
        return torch.cuda.get_device_properties(0).total_memory / (1024**3)
    return 0

def should_use_quantization():
    """Determine if quantization should be used based on available VRAM"""
    vram = get_available_vram()
    return vram > 0 and vram < 12  # Use quantization if VRAM < 12GB

def get_model_config(model_name):
    """Get configuration for specified model"""
    return MODELS.get(model_name, MODELS[DEFAULT_MODEL])

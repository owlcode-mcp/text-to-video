#!/bin/bash
# Setup script for text-to-video generator

set -e

echo "================================"
echo "Text-to-Video Generator Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.8+
required_version="3.8"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "ERROR: Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
echo "This may take several minutes..."
pip install -r requirements.txt

# Create output directory
echo ""
echo "Creating output directory..."
mkdir -p outputs
echo "Output directory created"

# Check GPU availability
echo ""
echo "Checking GPU availability..."
python3 << EOF
import torch
if torch.cuda.is_available():
    print(f"✓ GPU detected: {torch.cuda.get_device_name(0)}")
    print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
else:
    print("⚠ No GPU detected. Video generation will be slow on CPU.")
    print("  Consider using a machine with NVIDIA GPU for faster generation.")
EOF

echo ""
echo "================================"
echo "Setup complete!"
echo "================================"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To generate a video, run:"
echo "  python text_to_video.py --prompt 'Your text here'"
echo ""

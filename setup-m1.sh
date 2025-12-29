#!/bin/bash
# Setup script for Apple M1/M2/M3 Silicon

set -e

echo "========================================"
echo "Text-to-Video Setup for Apple Silicon"
echo "========================================"
echo ""

# Check if running on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "WARNING: Not running on ARM64 architecture"
    echo "Current architecture: $(uname -m)"
    echo "For best M1/M2 performance, use native ARM64 Python"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Verify Python is ARM64
python_arch=$(python3 -c "import platform; print(platform.machine())")
echo "Python architecture: $python_arch"

if [ "$python_arch" != "arm64" ]; then
    echo "WARNING: Python is not ARM64 native (running under Rosetta)"
    echo "For best performance, install ARM64 native Python:"
    echo "  - Download from python.org, or"
    echo "  - Use miniforge: brew install miniforge"
    echo ""
fi

# Check if Python 3.10+
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "ERROR: Python 3.10 or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "Installing M1-optimized dependencies..."
echo "This may take 10-15 minutes..."
pip install -r requirements-m1.txt

# Install psutil for memory detection
pip install psutil

# Create output directory
echo ""
echo "Creating output directory..."
mkdir -p outputs
echo "✓ Output directory created"

# Test MPS availability
echo ""
echo "Testing Apple MPS (Metal) support..."
python3 << 'EOF'
import torch
import platform

print(f"System: {platform.system()} {platform.machine()}")
print(f"Python: {platform.python_version()}")
print(f"PyTorch: {torch.__version__}")
print()

if torch.backends.mps.is_available():
    print("✓ MPS (Metal Performance Shaders) is available!")
    try:
        # Test MPS
        device = torch.device("mps")
        x = torch.ones(5, device=device)
        print(f"✓ MPS test successful: {x}")
        print()
        print("Your M1/M2 GPU will be used for video generation!")
    except Exception as e:
        print(f"⚠ MPS available but test failed: {e}")
        print("Will fall back to CPU")
else:
    print("⚠ MPS not available - will use CPU")
    print("This is normal on non-Apple Silicon or older macOS")

# Check memory
import psutil
total_ram = psutil.virtual_memory().total / (1024**3)
print(f"\nSystem RAM: {total_ram:.1f} GB")
if total_ram >= 16:
    print("✓ Sufficient RAM for video generation")
elif total_ram >= 8:
    print("✓ RAM adequate (recommend using 480p resolution)")
else:
    print("⚠ Low RAM - video generation may be slow")
EOF

echo ""
echo "========================================"
echo "✓ Setup complete!"
echo "========================================"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To generate a test video:"
echo "  python3 test_simple.py --prompt 'A beautiful sunset' --resolution 480p"
echo ""
echo "For AI-powered generation (requires model download ~5GB):"
echo "  python3 text_to_video.py --prompt 'A colorful ocean wave' --model cogvideox-2b"
echo ""
echo "M1/M2 Performance Tips:"
echo "  - Use --resolution 480p for faster generation"
echo "  - Close other apps to free up unified memory"
echo "  - First run will download models (~5-10 minutes)"
echo "  - Expect 3-7 minutes generation time with cogvideox-2b"
echo ""

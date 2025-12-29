# Text-to-Video Generator with FTP Upload

Generate realistic, colorful videos from text prompts using open-source AI models, with automatic FTP upload.

## Features

- 🎥 AI-powered text-to-video generation using CogVideoX models
- 🎨 Realistic and colorful video output
- ⚙️ Configurable resolution, duration, and FPS
- 📤 Automatic FTP upload
- 🚀 GPU acceleration support with CPU fallback
- 🔧 Memory optimization for lower-end GPUs

## Requirements

- Python 3.8 or higher
- 8GB+ RAM (16GB recommended)
- GPU with 8GB+ VRAM (recommended, not required)
- ~10GB disk space for model weights
- FTP server credentials

## Installation

1. Clone or navigate to this repository:
```bash
cd /home/pi/work/text-to-video
```

2. Run the setup script:
```bash
bash setup.sh
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

## Configuration

### FTP Settings

Set environment variables for FTP upload:

```bash
export FTP_HOST="your-ftp-server.com"
export FTP_PORT="21"
export FTP_USER="your-username"
export FTP_PASSWORD="your-password"
export FTP_REMOTE_DIR="/videos"
```

Or add them to your `~/.bashrc` or `~/.bash_profile`.

## Usage

### Basic Usage

Generate a 10-second video from a text prompt:

```bash
python text_to_video.py --prompt "A colorful sunset over ocean waves"
```

### Advanced Options

```bash
python text_to_video.py \
  --prompt "A vibrant garden with butterflies flying around colorful flowers" \
  --duration 10 \
  --resolution 720p \
  --fps 8 \
  --model cogvideox-2b \
  --output my_video.mp4
```

### Available Options

- `--prompt` (required): Text description of the video
- `--duration`: Video duration in seconds (default: 10)
- `--resolution`: Video resolution - `480p`, `720p`, or `1080p` (default: 480p)
- `--model`: Model to use - `cogvideox-2b` or `cogvideox-5b` (default: cogvideox-2b)
- `--fps`: Frames per second (default: 8)
- `--output`: Custom output filename (default: auto-generated)
- `--output-dir`: Output directory (default: outputs)
- `--no-upload`: Skip FTP upload for testing

### Testing Without Upload

Test video generation without uploading to FTP:

```bash
python text_to_video.py \
  --prompt "Test video" \
  --no-upload
```

## Models

### CogVideoX-2B (Default)
- Size: ~5GB
- VRAM: 8GB minimum
- Quality: Good
- Speed: Moderate
- License: Apache 2.0

### CogVideoX-5B (Better Quality)
- Size: ~10GB
- VRAM: 24GB minimum
- Quality: Excellent
- Speed: Slower
- License: CogVideoX License

## Performance

### With GPU (NVIDIA RTX 3090 or similar)
- Generation time: 2-5 minutes per video
- Memory: 8-12GB VRAM

### With CPU Only
- Generation time: 20-60 minutes per video
- Memory: 16GB+ RAM recommended
- **Not recommended for production use**

## Troubleshooting

### Out of Memory Error

If you encounter OOM errors:
1. Use the smaller model: `--model cogvideox-2b`
2. Lower resolution: `--resolution 480p`
3. Close other applications
4. Enable swap if on limited hardware

### Slow Generation

- Ensure GPU is being used (check with `nvidia-smi`)
- Lower resolution and FPS
- Use CPU if GPU has insufficient VRAM

### FTP Upload Fails

- Verify FTP credentials
- Check network connection
- Ensure FTP server allows uploads
- Verify remote directory exists

## Examples

### Realistic Nature Scene
```bash
python text_to_video.py --prompt "A majestic waterfall in a lush green forest with sunlight streaming through trees"
```

### Urban Cityscape
```bash
python text_to_video.py --prompt "A vibrant city street at night with neon signs and people walking"
```

### Abstract Art
```bash
python text_to_video.py --prompt "Colorful abstract patterns morphing and flowing like liquid paint"
```

## File Structure

```
text-to-video/
├── text_to_video.py    # Main script
├── config.py           # Configuration settings
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── setup.sh           # Setup script
├── README.md          # This file
└── outputs/           # Generated videos
```

## License

This project uses open-source models:
- CogVideoX-2B: Apache 2.0 License
- CogVideoX-5B: CogVideoX License

## Credits

- **CogVideoX**: Tsinghua University & Zhipu AI
- **Diffusers**: Hugging Face
- **PyTorch**: Meta AI

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review model documentation
3. Open an issue on the repository

---

Generated with Claude Code

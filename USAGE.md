# Text-to-Video Usage Guide

Complete guide for generating AI videos from text prompts and uploading to FTP.

## Quick Start

### Option 1: Simple Test Video (2 seconds, no AI model needed)

```bash
python3 test_simple.py --prompt "Test" --duration 10 --resolution 480p --no-upload
```

### Option 2: AI-Generated Video (requires model download ~5GB)

```bash
# Set FTP credentials
export FTP_HOST="ftp.example.com"
export FTP_USER="username"
export FTP_PASSWORD="password"

# Generate video
python3 text_to_video.py --prompt "A colorful sunset over the ocean" --duration 10
```

## Platform-Specific Setup

### Apple M1/M2/M3 (macOS)

```bash
bash setup-m1.sh
source venv/bin/activate
```

See [README-M1.md](README-M1.md) for M1-specific optimizations and troubleshooting.

### Linux / Raspberry Pi

```bash
bash setup.sh
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Command-Line Options

### text_to_video.py (AI Generation)

```bash
python3 text_to_video.py \
  --prompt "Your video description" \
  --duration 10 \
  --resolution 720p \
  --model cogvideox-2b \
  --fps 8 \
  --output my_video.mp4 \
  --no-upload  # Skip FTP upload
```

**Options:**
- `--prompt`: Text description (required)
- `--duration`: Video length in seconds (default: 10)
- `--resolution`: 480p, 720p, or 1080p (default: 480p)
- `--model`: cogvideox-2b or cogvideox-5b (default: cogvideox-2b)
- `--fps`: Frames per second (default: 8)
- `--output`: Custom filename (default: auto-generated)
- `--no-upload`: Skip FTP upload

### test_simple.py (Fast Test)

```bash
python3 test_simple.py \
  --duration 10 \
  --resolution 480p \
  --fps 8 \
  --no-upload
```

Generates a colorful gradient video in ~2 seconds without AI.

## FTP Upload

### Setup FTP Credentials

```bash
export FTP_HOST="ftp.example.com"
export FTP_PORT="21"
export FTP_USER="username"
export FTP_PASSWORD="password"
export FTP_REMOTE_DIR="/videos"
```

### Upload Existing Video

```bash
python3 upload_video_mcp.py
```

Uploads the most recent video from `outputs/` directory.

### Manual Upload

```bash
python3 upload_to_ftp.py <local_file> <host> <port> <user> <password> <remote_path>
```

## Example Prompts

### Nature Scenes
```
"A majestic waterfall in a lush green forest with sunlight streaming through trees"
"Rolling hills covered with lavender flowers swaying in the breeze"
"Snow-capped mountains reflected in a crystal clear alpine lake"
```

### Urban Landscapes
```
"A vibrant city street at night with neon signs and people walking"
"Sunset over a modern city skyline with glass buildings reflecting golden light"
"Rain falling on a busy street with colorful umbrellas and puddle reflections"
```

### Abstract & Artistic
```
"Colorful abstract patterns morphing and flowing like liquid paint"
"Geometric shapes floating and rotating in a gradient background"
"Swirling galaxies with stars and nebula clouds in vibrant colors"
```

### Ocean & Water
```
"Gentle ocean waves rolling onto a sandy beach at sunset"
"Colorful coral reef with tropical fish swimming peacefully"
"Underwater scene with sun rays penetrating the clear blue water"
```

## Performance Guidelines

### Model Recommendations

| Hardware | Model | Resolution | Time | Quality |
|----------|-------|------------|------|---------|
| M1 8GB | cogvideox-2b | 480p | 5-8 min | Good |
| M1 16GB | cogvideox-2b | 720p | 4-6 min | Good |
| M2/M3 | cogvideox-5b | 720p | 4-6 min | Excellent |
| RTX 3080 | cogvideox-5b | 1080p | 2-4 min | Excellent |
| CPU only | cogvideox-2b | 480p | 30+ min | Good |

### Memory Requirements

- **cogvideox-2b**: 8GB VRAM/RAM minimum
- **cogvideox-5b**: 24GB VRAM/RAM minimum
- Add 2-4GB for operating system

### Disk Space

- Model weights: 5-10GB
- Generated videos: 1-3MB per 10-second video
- Total recommended: 20GB free space

## Troubleshooting

### "Out of memory" error

1. Use smaller model: `--model cogvideox-2b`
2. Lower resolution: `--resolution 480p`
3. Reduce duration: `--duration 6`
4. Close other applications

### "Module not found" error

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or for M1:
pip install -r requirements-m1.txt
```

### "T5 tokenizer" error

```bash
pip install sentencepiece protobuf --upgrade
```

### "FTP connection refused"

Check FTP credentials:
```bash
echo $FTP_HOST
echo $FTP_USER
```

Test FTP connection:
```bash
ftp $FTP_HOST
```

### Slow generation

- **First run**: Model download takes 10-15 minutes
- **Subsequent runs**: Should be faster (3-8 minutes)
- **CPU-only**: 30+ minutes is normal

## File Structure

```
text-to-video/
├── text_to_video.py          # Main AI video generator
├── test_simple.py            # Fast test without AI
├── upload_video_mcp.py       # FTP upload utility
├── config.py                 # Configuration
├── utils.py                  # Helper functions
├── requirements.txt          # Python dependencies
├── requirements-m1.txt       # M1-optimized dependencies
├── setup.sh                  # Linux/Pi setup
├── setup-m1.sh              # M1 setup
├── README.md                 # Main documentation
├── README-M1.md             # M1-specific guide
├── USAGE.md                  # This file
└── outputs/                  # Generated videos
```

## Advanced Usage

### Custom Video Settings

```python
# Edit config.py to add custom resolutions or models
RESOLUTIONS['custom'] = (1024, 1024)  # Square video
```

### Batch Processing

Create multiple videos:
```bash
for prompt in "Sunset" "Ocean" "Mountains"; do
  python3 text_to_video.py --prompt "$prompt" --duration 10
done
```

### Integration with Other Tools

Output videos are standard MP4 H.264 files, compatible with:
- Adobe Premiere / After Effects
- Final Cut Pro
- DaVinci Resolve
- FFmpeg
- Web browsers

### Extending Videos

Use FFmpeg to loop or extend:
```bash
ffmpeg -stream_loop 2 -i input.mp4 -c copy output_longer.mp4
```

## Best Practices

1. **Be specific in prompts**: "Red sunset over calm ocean" vs "sunset"
2. **Start with 480p**: Test prompts quickly, then upscale
3. **Use simple scenes first**: Complex scenes with multiple objects are harder
4. **Monitor system resources**: Check Activity Monitor / Task Manager
5. **Save FTP credentials**: Add to ~/.bashrc or ~/.zshrc

## Support & Updates

- GitHub: https://github.com/owlcode-mcp/text-to-video
- Issues: Report bugs via GitHub Issues
- Updates: Pull latest changes with `git pull`

---

Generated with Claude Code

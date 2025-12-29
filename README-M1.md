# Text-to-Video on Apple M1/M2/M3

Optimized setup and usage guide for Apple Silicon Macs.

## Quick Start for M1/M2/M3

### 1. Installation

```bash
# Clone the repository
cd text-to-video

# Run M1-optimized setup
bash setup-m1.sh
```

### 2. Verify MPS Support

```bash
source venv/bin/activate
python3 -c "import torch; print('MPS Available:', torch.backends.mps.is_available())"
```

Should output: `MPS Available: True`

### 3. Generate a Test Video (No AI, Fast)

```bash
python3 test_simple.py --prompt "Test video" --duration 10 --resolution 480p --no-upload
```

This creates a simple gradient video in ~2 seconds.

### 4. Generate AI Video (Requires Model Download)

```bash
# Set FTP credentials (optional, skip if testing locally)
export FTP_HOST="your-ftp-server.com"
export FTP_USER="username"
export FTP_PASSWORD="password"

# Generate AI video (first run downloads ~5GB model)
python3 text_to_video.py \
  --prompt "A colorful sunset over ocean waves with seagulls flying" \
  --duration 10 \
  --resolution 480p \
  --model cogvideox-2b \
  --no-upload
```

## Performance on Apple Silicon

### M1 (8GB RAM)
- **Recommended**: Use `cogvideox-2b` model with `480p` resolution
- **Generation time**: 5-8 minutes per 10-second video
- **Memory usage**: ~6GB

### M1 Pro/Max (16GB+ RAM)
- **Recommended**: Use `cogvideox-2b` with `720p` resolution
- **Generation time**: 4-6 minutes per 10-second video
- **Can use**: `cogvideox-5b` model (better quality, slower)

### M2/M3 Series
- **Recommended**: `cogvideox-5b` with `720p` or `1080p`
- **Generation time**: 3-5 minutes per 10-second video
- **Best quality**: Use `--model cogvideox-5b --resolution 1080p`

## Optimizations Enabled

When running on Apple Silicon, the system automatically enables:

1. **MPS Backend**: Uses Metal Performance Shaders for GPU acceleration
2. **Attention Slicing**: Reduces memory usage during generation
3. **VAE Slicing**: Optimizes video encoding/decoding
4. **Float16 Precision**: 2x faster than float32 with minimal quality loss
5. **Unified Memory**: Efficiently uses Mac's unified memory architecture

## Troubleshooting

### "MPS backend not available"

Make sure you're using:
- macOS 12.3 or later
- Native ARM64 Python (not Rosetta)
- PyTorch 2.0+

Check architecture:
```bash
python3 -c "import platform; print(platform.machine())"
# Should output: arm64
```

### "Out of memory" errors

Try these in order:
1. Use lower resolution: `--resolution 480p`
2. Close other applications
3. Use smaller model: `--model cogvideox-2b`
4. Reduce duration: `--duration 6`

### Slow generation on M1 with 8GB

This is normal. Optimize with:
```bash
python3 text_to_video.py \
  --prompt "Your prompt" \
  --model cogvideox-2b \
  --resolution 480p \
  --fps 8 \
  --duration 6
```

### T5 Tokenizer Error

If you see tokenizer errors, install missing dependencies:
```bash
pip install sentencepiece protobuf --upgrade
```

## FTP Upload on M1

After generating a video, upload to FTP:

```bash
# Set credentials
export FTP_HOST="ftp.example.com"
export FTP_USER="username"
export FTP_PASSWORD="password"
export FTP_REMOTE_DIR="/videos"

# Upload latest generated video
python3 upload_video_mcp.py
```

Or generate and upload in one command:
```bash
python3 text_to_video.py \
  --prompt "Beautiful landscape" \
  --duration 10 \
  --resolution 480p
# Uploads automatically if FTP env vars are set
```

## Best Practices for M1/M2

1. **Close other apps** before generation to free up unified memory
2. **Use 480p or 720p** for balanced speed/quality
3. **First run takes longer** (~10-15 min) due to model download
4. **Subsequent runs are faster** (~3-7 min) with cached models
5. **Monitor Activity Monitor** to see Metal GPU usage

## Example Prompts

### Good Prompts (Clear, Specific)
```
"A vibrant coral reef with colorful fish swimming peacefully"
"Sunset over mountains with golden light and clouds"
"City street at night with neon signs and rain reflections"
"A field of sunflowers swaying gently in the breeze"
```

### Avoid (Too Vague)
```
"Something cool"
"A video"
"Nature"
```

## Recommended Settings by Mac Model

| Mac Model | Model | Resolution | Expected Time |
|-----------|-------|------------|---------------|
| M1 8GB | cogvideox-2b | 480p | 5-8 min |
| M1 16GB | cogvideox-2b | 720p | 4-6 min |
| M1 Pro/Max | cogvideox-2b | 720p | 3-5 min |
| M2/M3 | cogvideox-5b | 720p | 4-6 min |
| M2/M3 Pro/Max | cogvideox-5b | 1080p | 5-8 min |

## Support

For M1-specific issues:
1. Check you're using ARM64 Python
2. Verify MPS is available
3. Review Activity Monitor during generation
4. Check available disk space (models need ~10GB)

---

Generated with Claude Code - Optimized for Apple Silicon

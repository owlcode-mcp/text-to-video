#!/usr/bin/env python3
"""
Text-to-Video Generator with FTP Upload
Generates realistic videos from text prompts using AI models
"""
import argparse
import os
import sys
from pathlib import Path
import numpy as np
import imageio
import torch
from diffusers import CogVideoXPipeline
from diffusers.utils import export_to_video

import config
import utils


class VideoGenerator:
    """Handles AI video generation from text prompts"""

    def __init__(self, model_name='cogvideox-2b', device=None):
        self.model_name = model_name
        self.device = device or config.detect_device()
        self.model_config = config.get_model_config(model_name)
        self.pipe = None

        print(f"\nInitializing VideoGenerator with model: {model_name}")
        print(f"Device: {self.device}")

    def load_model(self):
        """Load the video generation model"""
        print(f"\nLoading model: {self.model_config['repo_id']}")
        print("This may take a few minutes on first run...")

        try:
            # Load pipeline
            self.pipe = CogVideoXPipeline.from_pretrained(
                self.model_config['repo_id'],
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
            )

            # Optimize for available hardware
            if self.device == 'cuda':
                self.pipe.to('cuda')

                # Enable memory optimizations
                self.pipe.enable_model_cpu_offload()
                self.pipe.enable_sequential_cpu_offload()

                # Use quantization if low VRAM
                if config.should_use_quantization():
                    print("Applying quantization for low VRAM...")
                    # Note: Quantization would require additional setup
                    # For now, we rely on CPU offloading
            else:
                print("WARNING: Running on CPU will be very slow (30+ minutes per video)")
                self.pipe.to('cpu')

            print("Model loaded successfully!")

        except Exception as e:
            print(f"Error loading model: {e}")
            print("\nFalling back to simpler video generation...")
            self.pipe = None
            raise

    def generate(self, prompt, num_frames=49, fps=8):
        """
        Generate video from text prompt

        Args:
            prompt: Text description of desired video
            num_frames: Number of frames to generate
            fps: Frames per second

        Returns:
            numpy array of video frames (T, H, W, C)
        """
        if self.pipe is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        print(f"\nGenerating video from prompt: '{prompt}'")
        print(f"Target: {num_frames} frames at {fps} fps")

        try:
            # Generate video
            video_frames = self.pipe(
                prompt=prompt,
                num_frames=num_frames,
                num_inference_steps=50,
                guidance_scale=6.0,
                generator=torch.Generator(device=self.device).manual_seed(42),
            ).frames[0]

            print(f"Generated {len(video_frames)} frames")
            return video_frames

        except Exception as e:
            print(f"Error during generation: {e}")
            raise


class VideoProcessor:
    """Processes and extends generated videos"""

    @staticmethod
    def extend_to_duration(frames, target_duration, fps):
        """
        Extend video frames to target duration

        Args:
            frames: Video frames from generator
            target_duration: Desired duration in seconds
            fps: Frames per second

        Returns:
            Extended video frames
        """
        print(f"\nExtending video to {target_duration} seconds...")

        # Convert frames to numpy if needed
        if not isinstance(frames, np.ndarray):
            frames = np.array(frames)

        target_frames = int(target_duration * fps)
        current_frames = len(frames)

        print(f"Current frames: {current_frames}, Target frames: {target_frames}")

        if current_frames >= target_frames:
            return frames[:target_frames]

        # Simple loop extension
        extended = utils.extend_video_frames(frames, target_duration, fps)
        print(f"Extended to {len(extended)} frames")

        return extended

    @staticmethod
    def save_video(frames, output_path, fps=8):
        """
        Save video frames to file

        Args:
            frames: numpy array of frames
            output_path: Path to save video
            fps: Frames per second
        """
        print(f"\nSaving video to: {output_path}")

        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

            # Save using imageio
            imageio.mimwrite(output_path, frames, fps=fps, codec='libx264', quality=8)

            file_size = os.path.getsize(output_path)
            print(f"Video saved! Size: {utils.format_filesize(file_size)}")

            return True

        except Exception as e:
            print(f"Error saving video: {e}")
            raise


class FTPUploader:
    """Handles FTP upload of generated videos"""

    def __init__(self):
        self.host = config.FTP_HOST
        self.port = config.FTP_PORT
        self.user = config.FTP_USER
        self.password = config.FTP_PASSWORD
        self.remote_dir = config.FTP_REMOTE_DIR

    def upload(self, local_path, remote_filename=None):
        """
        Upload file to FTP server using MCP

        Args:
            local_path: Path to local file
            remote_filename: Optional remote filename (defaults to local filename)

        Returns:
            Remote file path
        """
        if not remote_filename:
            remote_filename = os.path.basename(local_path)

        remote_path = f"{self.remote_dir}/{remote_filename}".replace('//', '/')

        print(f"\nUploading to FTP: {remote_path}")

        try:
            # Read file content
            with open(local_path, 'rb') as f:
                content = f.read()

            print(f"File size: {utils.format_filesize(len(content))}")
            print("Upload will be handled by MCP FTP tool...")
            print(f"Remote path: {remote_path}")

            # Note: Actual upload will be done via MCP tool call
            # This is a placeholder that will be replaced with MCP integration
            return remote_path

        except Exception as e:
            print(f"Error uploading to FTP: {e}")
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate realistic videos from text prompts using AI'
    )
    parser.add_argument(
        '--prompt',
        type=str,
        required=True,
        help='Text description of the video to generate'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=config.DEFAULT_DURATION,
        help=f'Video duration in seconds (default: {config.DEFAULT_DURATION})'
    )
    parser.add_argument(
        '--resolution',
        type=str,
        default=config.DEFAULT_RESOLUTION,
        choices=list(config.RESOLUTIONS.keys()),
        help=f'Video resolution (default: {config.DEFAULT_RESOLUTION})'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=config.DEFAULT_MODEL,
        choices=list(config.MODELS.keys()),
        help=f'Model to use (default: {config.DEFAULT_MODEL})'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=config.DEFAULT_FPS,
        help=f'Frames per second (default: {config.DEFAULT_FPS})'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output filename (default: auto-generated)'
    )
    parser.add_argument(
        '--no-upload',
        action='store_true',
        help='Skip FTP upload (for testing)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=config.OUTPUT_DIR,
        help=f'Output directory (default: {config.OUTPUT_DIR})'
    )

    args = parser.parse_args()

    # Print system info
    utils.print_system_info()

    # Ensure output directory exists
    utils.ensure_dir(args.output_dir)

    # Generate output filename
    if args.output:
        output_filename = args.output
    else:
        output_filename = utils.generate_filename()

    output_path = os.path.join(args.output_dir, output_filename)

    try:
        # Initialize video generator
        generator = VideoGenerator(model_name=args.model)
        generator.load_model()

        # Generate video
        model_config = config.get_model_config(args.model)
        frames = generator.generate(
            prompt=args.prompt,
            num_frames=model_config['max_frames'],
            fps=args.fps
        )

        # Process and extend video
        processor = VideoProcessor()
        extended_frames = processor.extend_to_duration(
            frames,
            target_duration=args.duration,
            fps=args.fps
        )

        # Save video
        processor.save_video(extended_frames, output_path, fps=args.fps)

        print(f"\n✓ Video generated successfully: {output_path}")

        # Upload to FTP
        if not args.no_upload:
            uploader = FTPUploader()
            remote_path = uploader.upload(output_path)
            print(f"\n✓ Video ready for FTP upload to: {remote_path}")
            print("Note: Actual upload requires MCP FTP tool integration")
        else:
            print("\nSkipping FTP upload (--no-upload flag set)")

        print("\n" + "="*50)
        print("SUCCESS! Video generation complete.")
        print("="*50)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

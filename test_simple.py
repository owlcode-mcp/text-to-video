#!/usr/bin/env python3
"""
Simple test script to generate a test video without heavy AI models
Tests the FTP upload functionality with a simple generated video
"""
import os
import sys
import argparse
import numpy as np
import imageio
from ftplib import FTP

import config
import utils


def generate_simple_test_video(output_path, duration=10, fps=8, resolution=(480, 720)):
    """
    Generate a simple test video with colorful gradients

    Args:
        output_path: Where to save the video
        duration: Duration in seconds
        fps: Frames per second
        resolution: (height, width) tuple
    """
    print(f"\nGenerating simple test video...")
    print(f"Duration: {duration}s, FPS: {fps}, Resolution: {resolution[1]}x{resolution[0]}")

    num_frames = duration * fps
    height, width = resolution

    frames = []

    for i in range(num_frames):
        # Create colorful gradient that changes over time
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Create animated gradient
        t = i / num_frames

        # Red channel: horizontal gradient
        frame[:, :, 0] = (np.linspace(0, 255, width) * (1 - t * 0.5)).astype(np.uint8)

        # Green channel: vertical gradient
        frame[:, :, 1] = (np.linspace(0, 255, height).reshape(-1, 1) * (0.5 + t * 0.5)).astype(np.uint8)

        # Blue channel: diagonal gradient
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        frame[:, :, 2] = ((x + y) / (width + height) * 255 * (0.5 + np.sin(t * 2 * np.pi) * 0.5)).astype(np.uint8)

        frames.append(frame)

    # Save video
    print(f"Saving video to: {output_path}")
    imageio.mimwrite(output_path, frames, fps=fps, codec='libx264', quality=8)

    file_size = os.path.getsize(output_path)
    print(f"✓ Test video created! Size: {utils.format_filesize(file_size)}")

    return output_path


def upload_to_ftp(local_path):
    """Upload file to FTP server"""
    print("\n" + "="*50)
    print("Testing FTP Upload")
    print("="*50)

    # Get FTP config
    host = config.FTP_HOST
    port = config.FTP_PORT
    user = config.FTP_USER
    password = config.FTP_PASSWORD
    remote_dir = config.FTP_REMOTE_DIR

    if not host or not user:
        print("ERROR: FTP not configured!")
        print("Set these environment variables:")
        print("  export FTP_HOST='your-ftp-server.com'")
        print("  export FTP_USER='your-username'")
        print("  export FTP_PASSWORD='your-password'")
        print("  export FTP_REMOTE_DIR='/videos'")
        return False

    remote_filename = os.path.basename(local_path)
    remote_path = f"{remote_dir}/{remote_filename}".replace('//', '/')

    print(f"\nFTP Configuration:")
    print(f"  Host: {host}:{port}")
    print(f"  User: {user}")
    print(f"  Remote path: {remote_path}")

    try:
        file_size = os.path.getsize(local_path)
        print(f"\nFile size: {utils.format_filesize(file_size)}")
        print(f"Connecting to {host}:{port}...")

        # Connect to FTP
        ftp = FTP()
        ftp.connect(host, port)
        ftp.login(user, password)

        print("✓ Connected successfully!")

        # Navigate to or create remote directory
        try:
            ftp.cwd(remote_dir)
        except:
            print(f"Creating remote directory: {remote_dir}")
            dirs = remote_dir.strip('/').split('/')
            for d in dirs:
                if d:
                    try:
                        ftp.cwd(d)
                    except:
                        ftp.mkd(d)
                        ftp.cwd(d)

        # Upload with progress
        print(f"\nUploading {remote_filename}...")

        uploaded_bytes = [0]

        def callback(data):
            uploaded_bytes[0] += len(data)
            percent = (uploaded_bytes[0] / file_size) * 100
            print(f"  Progress: {percent:.1f}% ({utils.format_filesize(uploaded_bytes[0])}/{utils.format_filesize(file_size)})", end='\r')

        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_filename}', f, callback=callback)

        print()  # New line after progress
        print(f"✓ Upload complete!")

        # Verify
        file_list = ftp.nlst()
        if remote_filename in file_list:
            print(f"✓ File verified on server: {remote_path}")

            # Get file size on server
            try:
                ftp.sendcmd('TYPE I')  # Binary mode
                size = ftp.size(remote_filename)
                print(f"  Server file size: {utils.format_filesize(size)}")

                if size == file_size:
                    print("  ✓ File size matches!")
                else:
                    print(f"  ⚠ Warning: Size mismatch (local: {file_size}, remote: {size})")
            except:
                pass

            success = True
        else:
            print("⚠ Warning: Could not verify file on server")
            success = False

        ftp.quit()

        return success

    except Exception as e:
        print(f"\n❌ Error uploading to FTP: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Simple test video generator and FTP uploader')
    parser.add_argument('--duration', type=int, default=10, help='Video duration in seconds')
    parser.add_argument('--fps', type=int, default=8, help='Frames per second')
    parser.add_argument('--resolution', type=str, default='480p', choices=['480p', '720p', '1080p'])
    parser.add_argument('--output', type=str, default=None, help='Output filename')
    parser.add_argument('--no-upload', action='store_true', help='Skip FTP upload')

    args = parser.parse_args()

    # Ensure output directory exists
    utils.ensure_dir('outputs')

    # Generate filename
    if args.output:
        output_path = os.path.join('outputs', args.output)
    else:
        output_path = os.path.join('outputs', utils.generate_filename('test_video'))

    # Get resolution
    resolution = config.RESOLUTIONS[args.resolution]

    print("\n" + "="*50)
    print("Simple Test Video Generator")
    print("="*50)

    try:
        # Generate test video
        generate_simple_test_video(output_path, args.duration, args.fps, resolution)

        # Upload to FTP
        if not args.no_upload:
            success = upload_to_ftp(output_path)

            if success:
                print("\n" + "="*50)
                print("✓ TEST PASSED - FTP upload successful!")
                print("="*50)
                return 0
            else:
                print("\n" + "="*50)
                print("❌ TEST FAILED - FTP upload failed")
                print("="*50)
                return 1
        else:
            print("\nSkipping FTP upload (--no-upload flag)")
            print("\n" + "="*50)
            print("✓ TEST VIDEO CREATED")
            print("="*50)
            return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

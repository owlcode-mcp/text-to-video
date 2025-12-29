#!/usr/bin/env python3
"""
Test FTP upload using environment variables or default MCP FTP server
"""
import os
import sys
from ftplib import FTP

# Try to get FTP credentials from environment
# If not set, we'll try common defaults or prompt
FTP_HOST = os.getenv('FTP_HOST', 'localhost')
FTP_PORT = int(os.getenv('FTP_PORT', '21'))
FTP_USER = os.getenv('FTP_USER', 'anonymous')
FTP_PASSWORD = os.getenv('FTP_PASSWORD', 'anonymous')

def upload_video(local_path, remote_filename=None):
    """Upload video to FTP server"""
    if not os.path.exists(local_path):
        print(f"Error: File not found: {local_path}")
        return False

    if not remote_filename:
        remote_filename = os.path.basename(local_path)

    remote_path = f"/videos/{remote_filename}"

    print(f"FTP Configuration:")
    print(f"  Host: {FTP_HOST}:{FTP_PORT}")
    print(f"  User: {FTP_USER}")
    print(f"  Remote path: {remote_path}")
    print()

    try:
        file_size = os.path.getsize(local_path)
        print(f"File: {local_path}")
        print(f"Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print()

        print(f"Connecting to {FTP_HOST}:{FTP_PORT}...")
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASSWORD)
        print("✓ Connected!")

        # Navigate to /videos directory
        try:
            ftp.cwd('/videos')
        except:
            print("Creating /videos directory...")
            ftp.mkd('/videos')
            ftp.cwd('/videos')

        # Upload with progress
        print(f"\nUploading {remote_filename}...")
        uploaded = [0]

        def callback(data):
            uploaded[0] += len(data)
            percent = (uploaded[0] / file_size) * 100
            mb_uploaded = uploaded[0] / 1024 / 1024
            mb_total = file_size / 1024 / 1024
            print(f"  Progress: {percent:5.1f}% ({mb_uploaded:.2f}/{mb_total:.2f} MB)", end='\r')

        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_filename}', f, callback=callback)

        print()  # New line after progress
        print("✓ Upload complete!")

        # Verify
        ftp.sendcmd('TYPE I')
        remote_size = ftp.size(remote_filename)
        print(f"\nVerification:")
        print(f"  Local size:  {file_size:,} bytes")
        print(f"  Remote size: {remote_size:,} bytes")

        if remote_size == file_size:
            print("  ✓ File size matches!")
            success = True
        else:
            print("  ✗ Warning: Size mismatch!")
            success = False

        ftp.quit()
        return success

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("FTP Video Upload Test")
    print("=" * 60)
    print()

    # Find the most recent test video
    import glob
    videos = glob.glob('outputs/test_video_*.mp4')
    if not videos:
        print("Error: No test videos found in outputs/")
        sys.exit(1)

    # Sort by modification time, get most recent
    latest_video = max(videos, key=os.path.getmtime)

    print(f"Found video: {latest_video}")
    print()

    success = upload_video(latest_video)

    print()
    print("=" * 60)
    if success:
        print("✓ TEST PASSED - Video uploaded successfully!")
    else:
        print("✗ TEST FAILED - Upload failed")
    print("=" * 60)

    sys.exit(0 if success else 1)

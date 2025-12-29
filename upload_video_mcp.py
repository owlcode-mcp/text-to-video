#!/usr/bin/env python3
"""
Upload binary video file to FTP using Python ftplib with MCP-style credentials
This script reads FTP credentials from environment variables and uploads the video
"""
import os
import sys
import glob

# Import from our modules
import utils

def get_ftp_config():
    """Get FTP configuration from environment variables"""
    host = os.getenv('FTP_HOST')
    port = int(os.getenv('FTP_PORT', '21'))
    user = os.getenv('FTP_USER')
    password = os.getenv('FTP_PASSWORD')
    remote_dir = os.getenv('FTP_REMOTE_DIR', '/videos')

    if not host or not user or not password:
        print("ERROR: FTP credentials not configured!")
        print("\nPlease set the following environment variables:")
        print("  export FTP_HOST='ftp.example.com'")
        print("  export FTP_USER='username'")
        print("  export FTP_PASSWORD='password'")
        print("  export FTP_PORT='21'  # Optional, defaults to 21")
        print("  export FTP_REMOTE_DIR='/videos'  # Optional, defaults to /videos")
        return None

    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'remote_dir': remote_dir
    }

def upload_video_to_ftp(video_path, config):
    """Upload video file to FTP server"""
    from ftplib import FTP

    filename = os.path.basename(video_path)
    remote_path = f"{config['remote_dir']}/{filename}"

    print(f"\nUploading to FTP:")
    print(f"  Server: {config['host']}:{config['port']}")
    print(f"  User: {config['user']}")
    print(f"  Remote path: {remote_path}")

    try:
        file_size = os.path.getsize(video_path)
        print(f"  File size: {utils.format_filesize(file_size)}")

        # Connect
        print(f"\nConnecting...")
        ftp = FTP()
        ftp.connect(config['host'], config['port'])
        ftp.login(config['user'], config['password'])
        print("✓ Connected!")

        # Navigate to remote directory, create if needed
        try:
            ftp.cwd(config['remote_dir'])
        except:
            print(f"Creating directory {config['remote_dir']}...")
            parts = config['remote_dir'].strip('/').split('/')
            for part in parts:
                if part:
                    try:
                        ftp.cwd(part)
                    except:
                        ftp.mkd(part)
                        ftp.cwd(part)

        # Upload with progress
        print(f"\nUploading {filename}...")
        uploaded = [0]

        def progress_callback(data):
            uploaded[0] += len(data)
            percent = (uploaded[0] / file_size) * 100
            print(f"  Progress: {percent:5.1f}% ({utils.format_filesize(uploaded[0])}/{utils.format_filesize(file_size)})", end='\r')

        with open(video_path, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f, callback=progress_callback)

        print()  # New line
        print("✓ Upload complete!")

        # Verify
        ftp.sendcmd('TYPE I')
        remote_size = ftp.size(filename)

        print(f"\nVerification:")
        print(f"  Local:  {utils.format_filesize(file_size)}")
        print(f"  Remote: {utils.format_filesize(remote_size)}")

        if remote_size == file_size:
            print("  ✓ Size matches!")
            ftp.quit()
            return True
        else:
            print("  ✗ Size mismatch!")
            ftp.quit()
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("Video Upload to FTP")
    print("=" * 70)

    # Get FTP config
    config = get_ftp_config()
    if not config:
        return 1

    # Find latest video
    videos = glob.glob('outputs/test_video_*.mp4')
    if not videos:
        print("\nERROR: No test videos found in outputs/")
        return 1

    latest_video = max(videos, key=os.path.getmtime)
    print(f"\nVideo file: {latest_video}")

    # Upload
    success = upload_video_to_ftp(latest_video, config)

    print("\n" + "=" * 70)
    if success:
        print("✓ SUCCESS - Video uploaded to FTP!")
    else:
        print("✗ FAILED - Upload unsuccessful")
    print("=" * 70)

    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())

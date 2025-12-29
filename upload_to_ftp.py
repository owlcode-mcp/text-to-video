#!/usr/bin/env python3
"""
Simple FTP upload utility
"""
import sys
import os
from ftplib import FTP

def upload_file(local_path, ftp_host, ftp_port, ftp_user, ftp_password, remote_path):
    """Upload file to FTP server"""
    try:
        print(f"Connecting to {ftp_host}:{ftp_port}...")
        ftp = FTP()
        ftp.connect(ftp_host, ftp_port)
        ftp.login(ftp_user, ftp_password)
        print("Connected!")

        # Get directory and filename
        remote_dir = os.path.dirname(remote_path)
        remote_filename = os.path.basename(remote_path)

        # Navigate to directory
        if remote_dir:
            ftp.cwd(remote_dir)

        # Upload file
        file_size = os.path.getsize(local_path)
        print(f"Uploading {local_path} ({file_size} bytes) to {remote_path}...")

        uploaded = [0]
        def callback(data):
            uploaded[0] += len(data)
            percent = (uploaded[0] / file_size) * 100
            print(f"Progress: {percent:.1f}%", end='\r')

        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_filename}', f, callback=callback)

        print("\n✓ Upload complete!")

        # Verify
        ftp.sendcmd('TYPE I')
        size = ftp.size(remote_filename)
        print(f"Remote file size: {size} bytes")

        if size == file_size:
            print("✓ File size matches!")
        else:
            print(f"⚠ Warning: Size mismatch")

        ftp.quit()
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 7:
        print("Usage: upload_to_ftp.py <local_file> <host> <port> <user> <password> <remote_path>")
        sys.exit(1)

    success = upload_file(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6])
    sys.exit(0 if success else 1)

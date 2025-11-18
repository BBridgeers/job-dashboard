#!/usr/bin/env python3
"""
Google Drive TXT File Downloader
Downloads job search TXT files from Google Drive for migration
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    """Authenticate with Google Drive API"""
    creds = None

    # Check for existing token
    if os.path.exists('gdrive_token.pickle'):
        with open('gdrive_token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('gdrive_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    if not creds or not creds.valid:
        print("⚠️  Authentication required. Please run google_drive_uploader.py first to authenticate.")
        return None

    return build('drive', 'v3', credentials=creds)

def download_txt_files():
    """Download all job_search_*.txt files from Google Drive"""

    print("📥 Downloading TXT Files from Google Drive...")
    print("=" * 60)

    service = authenticate()
    if not service:
        return False

    try:
        # Search for job_search TXT files
        query = "name contains 'job_search' and name contains '.txt' and trashed=false"
        results = service.files().list(
            q=query,
            pageSize=50,
            fields="files(id, name, modifiedTime)"
        ).execute()

        files = results.get('files', [])

        if not files:
            print("⚠️  No job_search TXT files found in Google Drive")
            return False

        print(f"Found {len(files)} TXT files:")

        downloaded = 0
        for file in files:
            file_id = file['id']
            file_name = file['name']

            print(f"  📄 Downloading: {file_name}")

            # Download file
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Write to local file
            with open(file_name, 'wb') as f:
                f.write(fh.getvalue())

            print(f"     ✅ Downloaded: {file_name}")
            downloaded += 1

        print("\n" + "=" * 60)
        print(f"✅ Downloaded {downloaded} files successfully!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ Error downloading files: {e}")
        return False

if __name__ == "__main__":
    download_txt_files()
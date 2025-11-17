# gdrive_uploader.py
"""
Google Drive Auto-Upload Module
Automatically uploads job search results to Google Drive
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes - we only need file creation permission
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GDriveUploader:
    def __init__(self, credentials_file='gdrive_credentials.json'):
        """Initialize Google Drive uploader"""
        self.credentials_file = credentials_file
        self.token_file = 'gdrive_token.pickle'
        self.service = None

    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None

        # Check if we have saved credentials
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next time
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)
        return True

    def find_or_create_folder(self, folder_name='Job Search Results'):
        """Find or create a folder in Google Drive"""
        if not self.service:
            self.authenticate()

        # Search for existing folder
        results = self.service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        folders = results.get('files', [])

        if folders:
            print(f"📁 Found existing folder: {folder_name}")
            return folders[0]['id']
        else:
            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            print(f"📁 Created new folder: {folder_name}")
            return folder['id']

    def upload_file(self, file_path, folder_id=None):
        """Upload a file to Google Drive"""
        if not self.service:
            self.authenticate()

        file_path = Path(file_path)

        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None

        # Create file metadata
        file_metadata = {
            'name': file_path.name
        }

        if folder_id:
            file_metadata['parents'] = [folder_id]

        # Upload file
        media = MediaFileUpload(
            str(file_path),
            mimetype='text/plain',
            resumable=True
        )

        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            print(f"📤 Uploaded to Google Drive: {file.get('name')}")
            print(f"🔗 View at: {file.get('webViewLink')}")
            return file.get('id')

        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            return None

    def upload_job_search_result(self, file_path):
        """
        Upload job search result file to 'Job Search Results' folder
        This is the main function to call from job search scripts
        """
        try:
            # Authenticate
            self.authenticate()

            # Find or create folder
            folder_id = self.find_or_create_folder('Job Search Results')

            # Upload file
            file_id = self.upload_file(file_path, folder_id)

            return file_id is not None

        except Exception as e:
            print(f"❌ Google Drive upload error: {str(e)}")
            print("⚠️  File saved locally but not uploaded to Google Drive")
            return False

# Convenience function for easy import
def upload_to_gdrive(file_path):
    """Simple function to upload a file to Google Drive"""
    uploader = GDriveUploader()
    return uploader.upload_job_search_result(file_path)

if __name__ == "__main__":
    # Test the uploader
    print("Testing Google Drive uploader...")
    uploader = GDriveUploader()
    uploader.authenticate()
    print("✅ Authentication successful!")

def upload_file(filename, folder_name='Dashboard'):
    """Wrapper that matches build_dashboard.py signature"""
    return upload_to_gdrive(filename)

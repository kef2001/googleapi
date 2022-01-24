# -*- coding: utf-8 -*-
import hashlib
import io
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


def download_file(fileid):
    """
    Google Drive에 올라가 있는 특정 파일을 다운로드 합니다.
    :param fileid: Google Drive FileId
    :return: Boolean
    """
    SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.metadata.readonly']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('drive', 'v3', credentials=creds)
        fileName = service.files().get(fileId=fileid).execute().get('name')
        if os.path.exists(fileName):
            with open(fileName, 'rb') as f:
                checksum = hashlib.md5(f.read()).hexdigest()
            md5Checksum = service.files().get(fileId=fileid, fields='md5Checksum').execute() # 구글 드라이브에 업로드되어있는 파일의 md5Checksum
            if checksum == md5Checksum['md5Checksum']:
                return False
        req = service.files().get_media(fileId= fileid)
        fh = io.FileIO(fileName,'wb')
        downloader = MediaIoBaseDownload(fh, req)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print('Download %d%%' %int(status.progress() * 100))
        return True

    except HttpError as error:
        print(f'An error occurred: {error}')
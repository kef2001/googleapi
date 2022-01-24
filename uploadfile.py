# -*- coding: utf-8 -*-

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def upload_file(file_path, file_name, google_folder_id):
    """
    Google Drive 특정 폴더에 파일을 업로드 합니다.
    :param file_path: 로컬에 파일이 위치한 폴더 경로
    :param file_name: 파일 이름(확장자 포함)
    :param google_folder_id: Google folder id
    :return: 업로드 완료된 파일의 google file id
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
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

        metadata = {'name':(file_name), 'mimeType': '*/*', "parents":[google_folder_id]}
        media = MediaFileUpload(os.path.join(file_path, file_name), mimetype='*/*', resumable=True)
        res = service.files().create(body=metadata, media_body=media, fields='id').execute()
        if res:
            print('"%s" 업로드 성공' % file_name)
            return res
    except HttpError as error:
        print(f'An error occurred: {error}')
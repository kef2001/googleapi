# -*- coding: utf-8 -*-

import os.path
import hashlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload



def update_file(file_path, file_name, file_id):
    """
    Google Drive에 위치한 특정 파일을 업데이트 합니다.
    update를 하면 해당 파일의 revision 이 추가됩니다.
    :param file_path: 로컬에 파일이 위치한 폴더 경로
    :param file_name: 파일 이름(확장자 포함)
    :param file_id: 업데이트 하려고 하는 파일의 Google fileId
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
        md5Checksum = service.files().get(fileId=file_id, fields='md5Checksum').execute() # 구글 드라이브에 업로드되어있는 파일의 md5Checksum
        with open(name,'rb') as f:
            checksum = hashlib.md5(f.read()).hexdigest() # 업로드 하려고 하는 파일의 md5Checksum
        if checksum == md5Checksum['md5Checksum'] :
            # 구글 드라이브의 파일과 현재 업로드하려는 파일이 동일한경우 False를 리턴함
            return False
        
        metadata = {'name':(file_name), 'mimeType':'*/*'}
        media = MediaFileUpload(os.path.join(file_path,file_name),mimetype= '*/*',resumable=True)
        res = service.files().update(body=metadata,fileId=file_id, media_body=media, fields='id').execute()
        if res:
            print('"%s" 업로드 성공' %file_name)
            return True
    except HttpError as error:
        print(f'An error occurred: {error}')
#!/usr/bin/env python3
"""
유튜브 업로드 스크립트
생성된 영상을 유튜브에 자동으로 업로드합니다.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import pickle

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("⚠️  Google API 라이브러리가 필요합니다.")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class YouTubeUploader:
    """유튜브 업로더 클래스"""

    # 유튜브 API 스코프
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    def __init__(self, credentials_file: str = "../config/client_secrets.json",
                 token_file: str = "../config/token.pickle"):
        """
        초기화

        Args:
            credentials_file: OAuth 2.0 클라이언트 시크릿 파일 경로
            token_file: 저장된 인증 토큰 파일 경로
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = None

        if not GOOGLE_API_AVAILABLE:
            raise ImportError("Google API 라이브러리가 필요합니다.")

    def authenticate(self):
        """유튜브 API 인증"""
        creds = None

        # 저장된 토큰이 있으면 로드
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # 유효하지 않은 토큰이면 재인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"OAuth 클라이언트 시크릿 파일이 없습니다: {self.credentials_file}\n"
                        "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고 "
                        "client_secrets.json 파일을 다운로드하세요."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # 토큰 저장
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        # YouTube API 클라이언트 빌드
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✅ 유튜브 API 인증 완료")

    def upload_video(self, video_file: str, metadata_file: Optional[str] = None,
                    title: Optional[str] = None, description: Optional[str] = None,
                    tags: Optional[list] = None, category_id: str = "22",
                    privacy_status: str = "public") -> Dict:
        """
        유튜브에 영상 업로드

        Args:
            video_file: 업로드할 영상 파일 경로
            metadata_file: 메타데이터 JSON 파일 경로 (선택)
            title: 영상 제목
            description: 영상 설명
            tags: 태그 리스트
            category_id: 카테고리 ID (22=People & Blogs)
            privacy_status: 공개 상태 (public, private, unlisted)

        Returns:
            업로드 결과 정보
        """
        if self.youtube is None:
            self.authenticate()

        # 메타데이터 로드
        if metadata_file and os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                title = title or metadata.get("title", "")
                description = description or metadata.get("description", "")
                tags = tags or metadata.get("tags", [])

        # 기본값 설정
        if not title:
            title = f"운세 영상 - {datetime.now().strftime('%Y-%m-%d')}"
        if not description:
            description = "매일 업데이트되는 운세와 토종비결"
        if not tags:
            tags = ["운세", "사주", "토정비결", "유튜브숏츠"]

        # 숏츠 태그 추가
        if "#shorts" not in description.lower():
            description += "\n\n#shorts"

        # 영상 메타데이터 설정
        body = {
            'snippet': {
                'title': title[:100],  # 유튜브 제목 최대 100자
                'description': description[:5000],  # 유튜브 설명 최대 5000자
                'tags': tags[:500],  # 최대 500개 태그
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            }
        }

        # 영상 파일 업로드
        media = MediaFileUpload(
            video_file,
            chunksize=-1,
            resumable=True,
            mimetype='video/mp4'
        )

        print(f"📤 유튜브 업로드 시작: {video_file}")
        print(f"   제목: {title}")
        print(f"   공개 상태: {privacy_status}")

        request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   업로드 진행률: {progress}%")

        video_id = response.get('id')
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"✅ 업로드 완료!")
        print(f"   영상 ID: {video_id}")
        print(f"   URL: {video_url}")

        # 업로드 결과 저장
        result = {
            "video_id": video_id,
            "video_url": video_url,
            "title": title,
            "upload_time": datetime.now().isoformat(),
            "privacy_status": privacy_status
        }

        # 결과를 JSON 파일로 저장
        result_file = Path(video_file).with_suffix('.upload.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    def update_video(self, video_id: str, title: Optional[str] = None,
                    description: Optional[str] = None, tags: Optional[list] = None):
        """
        기존 영상 메타데이터 업데이트

        Args:
            video_id: 유튜브 영상 ID
            title: 새 제목
            description: 새 설명
            tags: 새 태그
        """
        if self.youtube is None:
            self.authenticate()

        # 현재 영상 정보 가져오기
        video_response = self.youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        if not video_response['items']:
            raise ValueError(f"영상을 찾을 수 없습니다: {video_id}")

        snippet = video_response['items'][0]['snippet']

        # 업데이트할 항목만 변경
        if title:
            snippet['title'] = title
        if description:
            snippet['description'] = description
        if tags:
            snippet['tags'] = tags

        # 업데이트 요청
        self.youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': snippet
            }
        ).execute()

        print(f"✅ 영상 업데이트 완료: {video_id}")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='유튜브 영상 업로드')
    parser.add_argument('--video', type=str, required=True,
                       help='업로드할 영상 파일')
    parser.add_argument('--metadata', type=str,
                       help='메타데이터 JSON 파일')
    parser.add_argument('--title', type=str, help='영상 제목')
    parser.add_argument('--description', type=str, help='영상 설명')
    parser.add_argument('--tags', type=str, nargs='+', help='태그 리스트')
    parser.add_argument('--privacy', type=str, default='public',
                       choices=['public', 'private', 'unlisted'],
                       help='공개 상태')
    parser.add_argument('--credentials', type=str,
                       default='../config/client_secrets.json',
                       help='OAuth 클라이언트 시크릿 파일')

    args = parser.parse_args()

    uploader = YouTubeUploader(credentials_file=args.credentials)
    uploader.upload_video(
        video_file=args.video,
        metadata_file=args.metadata,
        title=args.title,
        description=args.description,
        tags=args.tags,
        privacy_status=args.privacy
    )


if __name__ == "__main__":
    main()

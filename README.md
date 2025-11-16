# YouTube Shorts 자동화 - 신년운세 & 토종비결

n8n을 활용하여 신년운세, 토종비결 등의 유튜브 숏츠를 자동으로 생성하고 업로드하는 시스템입니다.

## 주요 기능

- **자동 콘텐츠 생성**: OpenAI GPT-4를 활용하여 운세 및 토종비결 콘텐츠 자동 생성
- **영상 자동 제작**: 생성된 콘텐츠를 바탕으로 유튜브 숏츠 영상 자동 생성
- **자동 업로드**: 완성된 영상을 유튜브에 자동으로 업로드
- **n8n 워크플로우**: 전체 프로세스를 n8n으로 자동화하여 매일 정해진 시간에 실행

## 프로젝트 구조

```
anime_photo/
├── scripts/                    # Python 스크립트
│   ├── generate_content.py    # 콘텐츠 생성 (운세/토종비결)
│   ├── generate_video.py      # 영상 생성
│   └── upload_youtube.py      # 유튜브 업로드
├── workflows/                  # n8n 워크플로우
│   └── youtube_shorts_automation.json
├── output/                     # 출력 디렉토리
│   ├── content/               # 생성된 콘텐츠 JSON
│   ├── images/                # 생성된 이미지
│   └── videos/                # 생성된 영상
├── config/                     # 설정 파일
│   └── client_secrets.json    # YouTube API OAuth 설정
├── .env                        # 환경 변수
├── .env.example               # 환경 변수 예시
├── requirements.txt           # Python 패키지 의존성
└── README.md                  # 이 파일
```

## 시작하기

### 1. 사전 요구사항

- Python 3.8 이상
- n8n (설치 방법은 아래 참조)
- OpenAI API 키
- Google Cloud Console 프로젝트 (YouTube API 사용)
- FFmpeg (영상 처리용)

### 2. 설치

#### Python 패키지 설치

```bash
pip install -r requirements.txt
```

#### FFmpeg 설치

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html 에서 다운로드
```

#### n8n 설치

```bash
# npm을 사용한 전역 설치
npm install -g n8n

# 또는 Docker 사용
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 3. API 설정

#### OpenAI API 키 발급

1. https://platform.openai.com/api-keys 에서 API 키 생성
2. `.env` 파일에 키 추가

```bash
cp .env.example .env
# .env 파일을 열어서 OPENAI_API_KEY 설정
```

#### YouTube API 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. YouTube Data API v3 활성화
4. OAuth 2.0 클라이언트 ID 생성:
   - 애플리케이션 유형: 데스크톱 앱
   - 생성된 JSON 파일을 `config/client_secrets.json`으로 저장

### 4. 스크립트 실행 권한 설정

```bash
chmod +x scripts/*.py
```

### 5. 개별 스크립트 테스트

#### 콘텐츠 생성 테스트

```bash
cd scripts

# 운세 생성
python3 generate_content.py --type fortune --zodiac "용띠" --year 2025

# 토종비결 생성
python3 generate_content.py --type tojong --topic "금전운"
```

#### 영상 생성 테스트

```bash
# 생성된 콘텐츠로 영상 만들기
python3 generate_video.py --content ../output/content/fortune_용띠_2025_*.json

# 이미지만 생성 (테스트용)
python3 generate_video.py --content ../output/content/fortune_용띠_2025_*.json --image-only
```

#### 유튜브 업로드 테스트

```bash
# 처음 실행 시 OAuth 인증 진행
python3 upload_youtube.py \
  --video ../output/videos/fortune_*.mp4 \
  --privacy unlisted  # 테스트는 unlisted로 시작
```

## n8n 워크플로우 설정

### 1. n8n 실행

```bash
n8n start
```

브라우저에서 http://localhost:5678 접속

### 2. 워크플로우 임포트

1. n8n 웹 인터페이스에서 "Import from File" 클릭
2. `workflows/youtube_shorts_automation.json` 파일 선택
3. 워크플로우가 로드됩니다

### 3. 노드 설정 검토

워크플로우에서 다음 노드들을 확인하고 경로를 수정하세요:

- **매일 실행 스케줄**: 원하는 시간으로 설정 (예: 매일 오전 9시)
- **콘텐츠 생성**: 스크립트 경로 확인
- **영상 생성**: 스크립트 경로 확인
- **유튜브 업로드**: 스크립트 경로 및 인증 설정 확인

### 4. 워크플로우 활성화

- 워크플로우 화면 우측 상단의 "Active" 토글 활성화
- 설정한 스케줄에 따라 자동 실행됩니다

## 워크플로우 동작 방식

```
[스케줄 트리거]
    ↓
[콘텐츠 타입 결정] (운세 or 토종비결 랜덤)
    ↓
[콘텐츠 생성] (GPT-4로 텍스트 생성)
    ↓
[최신 콘텐츠 파일 가져오기]
    ↓
[영상 생성] (텍스트 → 비주얼 콘텐츠)
    ↓
[최신 영상 파일 가져오기]
    ↓
[유튜브 업로드]
    ↓
[성공/실패 확인]
    ↓
[알림 발송] (옵션)
```

## 커스터마이징

### 콘텐츠 템플릿 수정

`scripts/generate_content.py` 파일에서 프롬프트를 수정하여 콘텐츠 스타일을 변경할 수 있습니다.

```python
# 운세 생성 프롬프트 수정
prompt = f"""
{year}년 {zodiac}의 신년운세를 작성해주세요.
... 원하는 스타일로 수정 ...
"""
```

### 영상 디자인 수정

`scripts/generate_video.py`의 테마 설정을 수정:

```python
self.themes = {
    "fortune": {
        "bg_color": (40, 20, 60),     # 배경색
        "text_color": (255, 215, 0),   # 텍스트 색
        "accent_color": (255, 105, 180) # 강조 색
    }
}
```

### 스케줄 변경

n8n 워크플로우의 "Schedule Trigger" 노드에서 실행 시간 조정:

- 매일 특정 시간: `hoursInterval: 24` + 시작 시간 설정
- 주 단위: `daysInterval: 7`
- 특정 요일: Cron 표현식 사용

## 문제 해결

### MoviePy 설치 오류

```bash
# ImageMagick 설치 (MoviePy 의존성)
sudo apt-get install imagemagick

# 또는 conda 사용
conda install -c conda-forge moviepy
```

### 한글 폰트 문제

```bash
# Ubuntu/Debian에 나눔고딕 설치
sudo apt-get install fonts-nanum fonts-nanum-coding

# macOS는 기본 한글 폰트 사용
```

### YouTube API 할당량 초과

- 무료 할당량: 일일 10,000 단위
- 영상 업로드: ~1,600 단위
- 하루 6개 영상까지 업로드 가능
- 더 필요한 경우 Google에 할당량 증가 요청

### OAuth 인증 만료

```bash
# 토큰 파일 삭제 후 재인증
rm config/token.pickle
python3 scripts/upload_youtube.py --video [영상파일]
```

## 보안 주의사항

- `.env` 파일은 절대 공개 저장소에 커밋하지 마세요
- `config/client_secrets.json`도 .gitignore에 추가되어 있습니다
- API 키가 노출되면 즉시 재발급하세요

## 개선 아이디어

- [ ] 배경음악 자동 선택 및 삽입
- [ ] 다양한 비주얼 템플릿 추가
- [ ] 썸네일 자동 생성
- [ ] 인스타그램, 틱톡 자동 업로드
- [ ] 조회수/댓글 분석 대시보드
- [ ] A/B 테스트로 최적의 업로드 시간 찾기
- [ ] 음성 나레이션 추가 (TTS)

## 라이선스

MIT License

## 기여

이슈와 PR은 언제나 환영합니다!

## 문의

프로젝트 관련 문의사항은 이슈로 남겨주세요.

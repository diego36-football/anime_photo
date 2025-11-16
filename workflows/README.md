# n8n 워크플로우 가이드

## 워크플로우 개요

`youtube_shorts_automation.json`은 유튜브 숏츠 자동 생성 및 업로드를 위한 전체 워크플로우입니다.

## 워크플로우 노드 설명

### 1. 매일 실행 스케줄 (Schedule Trigger)
- **역할**: 정해진 시간에 워크플로우를 자동으로 시작
- **설정**:
  - Interval: 24시간마다
  - 시작 시간: 원하는 시간으로 조정 가능
- **권장 시간**: 오전 9시 (시청자가 활동하기 전)

### 2. 콘텐츠 타입 결정 (Set Node)
- **역할**: 운세 또는 토종비결 중 하나를 랜덤하게 선택
- **로직**: `Math.random() > 0.5`로 50% 확률로 선택
- **커스터마이징**:
  - 특정 타입만 생성하려면: `"fortune"` 또는 `"tojong"` 고정값 사용
  - 확률 조정: `Math.random() > 0.7`로 변경하여 70% 운세, 30% 토종비결

### 3. 콘텐츠 생성 (Execute Command)
- **역할**: Python 스크립트를 실행하여 GPT-4로 콘텐츠 생성
- **명령어**:
  ```bash
  cd /home/user/anime_photo/scripts &&
  python3 generate_content.py --type {{ $json.content_type }} --output-dir ../output/content
  ```
- **주의사항**: 경로를 실제 프로젝트 경로로 수정 필요

### 4. 최신 콘텐츠 파일 가져오기 (Read Binary Files)
- **역할**: 방금 생성된 JSON 파일을 읽어옴
- **설정**:
  - 경로: `/home/user/anime_photo/output/content`
  - 필터: `*.json`
  - 정렬: 수정 날짜 기준 내림차순
  - 최대 결과: 1개 (가장 최신 파일)

### 5. 영상 생성 (Execute Command)
- **역할**: 콘텐츠 JSON을 바탕으로 숏츠 영상 생성
- **명령어**:
  ```bash
  cd /home/user/anime_photo/scripts &&
  python3 generate_video.py --content {{ $json.file_path }} --duration 30 --output-dir ../output/videos
  ```
- **파라미터**:
  - `--duration`: 영상 길이 (기본 30초)
  - `--music`: 배경음악 파일 경로 (옵션)

### 6. 최신 영상 파일 가져오기 (Read Binary Files)
- **역할**: 방금 생성된 MP4 파일을 읽어옴
- **설정**: 콘텐츠 파일과 동일하게 최신 파일 선택

### 7. 유튜브 업로드 (Execute Command)
- **역할**: 생성된 영상을 유튜브에 업로드
- **명령어**:
  ```bash
  cd /home/user/anime_photo/scripts &&
  python3 upload_youtube.py --video {{ $json.file_path }} --metadata {{ $json.file_path.replace('.mp4', '.json') }} --privacy public
  ```
- **파라미터**:
  - `--privacy`: public, private, unlisted 중 선택
  - `--metadata`: 영상 메타데이터 JSON 파일

### 8. 업로드 성공 확인 (IF Node)
- **역할**: 업로드 성공 여부를 확인하여 분기 처리
- **조건**: `$json.success == true`

### 9. 성공 알림 (Discord/Slack)
- **역할**: 업로드 성공 시 알림 발송 (옵션)
- **설정**: Discord/Slack 웹훅 URL 필요
- **메시지**:
  ```
  ✅ YouTube Shorts 자동 업로드 완료!
  영상 ID: {{ $json.video_id }}
  URL: {{ $json.video_url }}
  ```

### 10. 실패 알림 (Discord/Slack)
- **역할**: 업로드 실패 시 알림 발송 (옵션)
- **메시지**:
  ```
  ❌ YouTube Shorts 업로드 실패
  에러: {{ $json.error }}
  ```

### 11. 완료 로그 (Set Node)
- **역할**: 워크플로우 완료 정보를 로그로 저장
- **데이터**:
  - workflow_status: "completed"
  - timestamp: 완료 시간

## 워크플로우 임포트 방법

### 1. n8n 접속
```bash
n8n start
```
브라우저에서 http://localhost:5678 접속

### 2. 워크플로우 임포트
1. 좌측 메뉴에서 "Workflows" 클릭
2. 우측 상단 "Add workflow" → "Import from File" 선택
3. `youtube_shorts_automation.json` 파일 선택
4. 워크플로우가 로드됩니다

### 3. 노드 설정 수정

모든 `Execute Command` 노드에서 경로를 실제 환경에 맞게 수정:

```bash
# 수정 전
cd /home/user/anime_photo/scripts

# 수정 후 (실제 경로로 변경)
cd /your/actual/path/anime_photo/scripts
```

### 4. 워크플로우 테스트

임포트 후 먼저 수동으로 테스트:
1. 워크플로우 화면에서 "Execute Workflow" 버튼 클릭
2. 각 노드가 순차적으로 실행되는지 확인
3. 에러 발생 시 해당 노드를 클릭하여 로그 확인

### 5. 활성화

테스트가 성공하면:
1. 우측 상단 "Active" 토글을 ON으로 변경
2. 설정한 스케줄에 따라 자동 실행됩니다

## 커스터마이징 예시

### 1. 특정 띠의 운세만 생성

"콘텐츠 생성" 노드의 명령어를 수정:

```bash
python3 generate_content.py --type fortune --zodiac "용띠" --year 2025
```

### 2. 하루에 여러 번 실행

"매일 실행 스케줄" 노드를 수정:
- Interval: 6시간마다 → `hoursInterval: 6`
- 하루 4번 실행됩니다

### 3. 특정 요일에만 실행

Cron 표현식 사용:
```
0 9 * * 1,3,5  # 월, 수, 금 오전 9시
```

### 4. 배경음악 추가

"영상 생성" 노드에 `--music` 파라미터 추가:

```bash
python3 generate_video.py --content {{ $json.file_path }} --duration 30 --music /path/to/music.mp3
```

### 5. 여러 SNS에 동시 업로드

"유튜브 업로드" 노드 이후에 다음 노드들을 추가:
- Instagram API 노드
- TikTok API 노드
- Twitter API 노드

## 문제 해결

### 워크플로우가 실행되지 않음
- n8n이 실행 중인지 확인: `ps aux | grep n8n`
- 워크플로우가 "Active" 상태인지 확인
- n8n 로그 확인: `~/.n8n/logs/`

### Execute Command 노드 에러
- 경로가 올바른지 확인
- Python 스크립트에 실행 권한이 있는지 확인: `chmod +x scripts/*.py`
- 가상환경이 활성화되어 있는지 확인

### 파일을 찾을 수 없음
- "Read Binary Files" 노드의 경로를 절대 경로로 변경
- 출력 디렉토리가 존재하는지 확인: `ls -la output/`

### 업로드 실패
- YouTube OAuth 인증이 되어 있는지 확인
- API 할당량을 초과하지 않았는지 확인
- 네트워크 연결 상태 확인

## 고급 기능

### 1. 에러 핸들링 추가

각 노드에 "On Error" 워크플로우를 연결하여:
- 에러 로그 저장
- 관리자에게 알림 발송
- 재시도 로직 구현

### 2. 데이터베이스 연동

업로드 이력을 데이터베이스에 저장:
- MySQL/PostgreSQL 노드 추가
- 업로드 성공/실패 이력 관리
- 통계 및 분석 데이터 수집

### 3. 조건부 실행

특정 조건에서만 실행:
- 요일별로 다른 콘텐츠 생성
- 조회수가 높은 시간대에만 업로드
- 이전 영상의 성과에 따라 전략 변경

### 4. 웹훅 트리거

스케줄 대신 웹훅으로 수동 실행:
- Webhook 노드를 트리거로 사용
- 외부에서 HTTP 요청으로 워크플로우 시작
- 모바일 앱이나 웹 대시보드에서 제어

## 참고 자료

- [n8n 공식 문서](https://docs.n8n.io/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [OpenAI API 문서](https://platform.openai.com/docs)

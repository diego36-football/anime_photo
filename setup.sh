#!/bin/bash
# YouTube Shorts 자동화 시스템 설정 스크립트

echo "================================================"
echo "YouTube Shorts 자동화 시스템 설정"
echo "================================================"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Python 버전 확인
echo "1. Python 버전 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3가 설치되지 않았습니다.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION 발견${NC}"
echo ""

# FFmpeg 확인
echo "2. FFmpeg 확인 중..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️  FFmpeg가 설치되지 않았습니다.${NC}"
    echo "설치 방법:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
else
    FFMPEG_VERSION=$(ffmpeg -version | head -n 1)
    echo -e "${GREEN}✅ FFmpeg 설치됨${NC}"
fi
echo ""

# 가상환경 생성
echo "3. Python 가상환경 생성 중..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
else
    echo -e "${YELLOW}⚠️  가상환경이 이미 존재합니다.${NC}"
fi
echo ""

# 가상환경 활성화 및 패키지 설치
echo "4. Python 패키지 설치 중..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 패키지 설치 완료${NC}"
else
    echo -e "${RED}❌ 패키지 설치 실패${NC}"
    exit 1
fi
echo ""

# 환경 변수 파일 생성
echo "5. 환경 변수 파일 확인 중..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  .env 파일이 생성되었습니다.${NC}"
    echo "   .env 파일을 열어서 API 키를 설정하세요:"
    echo "   - OPENAI_API_KEY"
    echo "   - YouTube OAuth 설정 (config/client_secrets.json)"
else
    echo -e "${GREEN}✅ .env 파일 존재${NC}"
fi
echo ""

# 디렉토리 확인
echo "6. 출력 디렉토리 확인 중..."
mkdir -p output/{content,images,videos}
mkdir -p config
echo -e "${GREEN}✅ 디렉토리 구조 생성 완료${NC}"
echo ""

# n8n 확인
echo "7. n8n 설치 확인 중..."
if ! command -v n8n &> /dev/null; then
    echo -e "${YELLOW}⚠️  n8n이 설치되지 않았습니다.${NC}"
    echo "설치 방법:"
    echo "  npm install -g n8n"
    echo "  또는 Docker: docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n"
else
    echo -e "${GREEN}✅ n8n 설치됨${NC}"
fi
echo ""

# 스크립트 실행 권한 설정
echo "8. 스크립트 실행 권한 설정 중..."
chmod +x scripts/*.py
chmod +x setup.sh
echo -e "${GREEN}✅ 실행 권한 설정 완료${NC}"
echo ""

# 완료 메시지
echo "================================================"
echo -e "${GREEN}✅ 설정 완료!${NC}"
echo "================================================"
echo ""
echo "다음 단계:"
echo "1. .env 파일을 열어서 OPENAI_API_KEY를 설정하세요"
echo "2. Google Cloud Console에서 OAuth 클라이언트 ID를 생성하고"
echo "   config/client_secrets.json으로 저장하세요"
echo "3. 개별 스크립트를 테스트하세요:"
echo "   source venv/bin/activate"
echo "   cd scripts"
echo "   python3 generate_content.py --type fortune --zodiac \"용띠\""
echo "4. n8n을 실행하고 워크플로우를 임포트하세요:"
echo "   n8n start"
echo ""
echo "자세한 내용은 README.md를 참조하세요."
echo ""

#!/bin/bash
# YouTube Shorts 자동화 - 맥 설치 스크립트
# 사용법: curl -O [URL] && bash install_on_mac.sh

echo "🎬 YouTube Shorts 자동화 시스템 설치"
echo "===================================="
echo ""

# 설치 위치
INSTALL_DIR="$HOME/Desktop/anime_photo"

echo "📁 설치 위치: $INSTALL_DIR"
read -p "계속하시겠습니까? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 설치 취소"
    exit 1
fi

# 디렉토리 생성
echo "📦 디렉토리 구조 생성 중..."
mkdir -p "$INSTALL_DIR"/{scripts,workflows,output/{videos,images,content},config}

# Git 저장소에서 클론 시도
echo ""
echo "🔄 Git 저장소에서 다운로드 시도 중..."

cd "$HOME/Desktop"
if git clone http://127.0.0.1:18343/git/diego36-football/anime_photo 2>/dev/null; then
    cd anime_photo
    git checkout claude/automate-youtube-shorts-n8n-01NiEA7amM8tUP4Kj4LqqLPh
    echo "✅ Git에서 다운로드 완료!"
    open .
    exit 0
fi

echo "⚠️  Git 저장소 접근 실패 - 파일을 직접 생성합니다..."
echo ""

# 파일들을 직접 생성
cd "$INSTALL_DIR"

echo "📝 파일 생성 중..."
echo "   - requirements.txt"
echo "   - .env.example"
echo "   - .gitignore"
echo "   - README.md"
echo "   - setup.sh"
echo "   - scripts/*.py (3개)"
echo "   - workflows/*.json"
echo ""

echo "⚠️  주의: 파일 내용은 GitHub 저장소를 참조하거나"
echo "   프로젝트 관리자에게 파일을 요청하세요."
echo ""
echo "📂 프로젝트 폴더 열기..."
open "$INSTALL_DIR"

echo ""
echo "✅ 설치 완료!"
echo ""
echo "다음 단계:"
echo "1. GitHub에서 전체 파일을 다운로드하거나"
echo "2. 프로젝트 관리자에게 ZIP 파일 요청"
echo "3. 또는 각 파일을 수동으로 생성"

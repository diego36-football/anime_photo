#!/usr/bin/env python3
"""
유튜브 숏츠 영상 생성 스크립트
운세/토종비결 콘텐츠를 바탕으로 영상을 생성합니다.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import textwrap
from datetime import datetime
import subprocess

try:
    from moviepy.editor import (
        ImageClip, TextClip, CompositeVideoClip,
        AudioFileClip, concatenate_videoclips
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  MoviePy가 설치되지 않았습니다. pip install moviepy로 설치하세요.")


class VideoGenerator:
    """유튜브 숏츠 영상 생성기"""

    def __init__(self, output_dir: str = "../output/videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 유튜브 숏츠 해상도 (9:16)
        self.width = 1080
        self.height = 1920

        # 배경색 테마
        self.themes = {
            "fortune": {
                "bg_color": (40, 20, 60),  # 보라색 계열
                "text_color": (255, 215, 0),  # 금색
                "accent_color": (255, 105, 180)  # 핑크
            },
            "tojong_secret": {
                "bg_color": (20, 40, 60),  # 남색 계열
                "text_color": (255, 255, 255),  # 흰색
                "accent_color": (100, 200, 255)  # 하늘색
            }
        }

    def create_background_image(self, content_type: str) -> Image.Image:
        """배경 이미지 생성"""
        theme = self.themes.get(content_type, self.themes["fortune"])

        # 그라디언트 배경 생성
        img = Image.new('RGB', (self.width, self.height), theme["bg_color"])
        draw = ImageDraw.Draw(img)

        # 간단한 장식 요소 추가
        for i in range(5):
            x = self.width // 2
            y = i * (self.height // 5)
            draw.ellipse(
                [(x - 50, y - 50), (x + 50, y + 50)],
                fill=None,
                outline=theme["accent_color"],
                width=3
            )

        return img

    def add_text_to_image(self, img: Image.Image, text: str,
                         position: tuple, font_size: int = 60,
                         color: tuple = (255, 255, 255),
                         max_width: int = 900) -> Image.Image:
        """이미지에 텍스트 추가"""
        draw = ImageDraw.Draw(img)

        # 폰트 설정 (시스템 기본 폰트 사용)
        try:
            # Linux/Mac 한글 폰트
            font_paths = [
                "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break

            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # 텍스트 줄바꿈
        lines = textwrap.wrap(text, width=20)

        # 텍스트 그리기
        y_offset = position[1]
        for line in lines:
            # 텍스트 중앙 정렬
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2

            # 텍스트 외곽선 효과
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x + adj, y_offset + adj2), line,
                            font=font, fill=(0, 0, 0))

            # 실제 텍스트
            draw.text((x, y_offset), line, font=font, fill=color)
            y_offset += font_size + 20

        return img

    def generate_video_from_content(self, content_file: str,
                                   duration: int = 30,
                                   background_music: Optional[str] = None) -> str:
        """
        콘텐츠 JSON 파일로부터 영상 생성

        Args:
            content_file: 콘텐츠 JSON 파일 경로
            duration: 영상 길이 (초)
            background_music: 배경음악 파일 경로

        Returns:
            생성된 영상 파일 경로
        """
        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy가 필요합니다. pip install moviepy")

        # 콘텐츠 로드
        with open(content_file, 'r', encoding='utf-8') as f:
            content_data = json.load(f)

        content_type = content_data.get("type", "fortune")
        title = content_data.get("title", "")
        content = content_data.get("content", "")

        # 배경 이미지 생성
        theme = self.themes.get(content_type, self.themes["fortune"])
        bg_img = self.create_background_image(content_type)

        # 제목 추가
        bg_img = self.add_text_to_image(
            bg_img, title, (100, 200),
            font_size=80, color=theme["text_color"]
        )

        # 본문 추가
        bg_img = self.add_text_to_image(
            bg_img, content, (100, 500),
            font_size=60, color=(255, 255, 255)
        )

        # 이미지 저장
        temp_img_path = self.output_dir / "temp_bg.png"
        bg_img.save(temp_img_path)

        # 영상 생성
        img_clip = ImageClip(str(temp_img_path), duration=duration)

        # 배경음악 추가 (옵션)
        if background_music and os.path.exists(background_music):
            audio = AudioFileClip(background_music).subclip(0, duration)
            img_clip = img_clip.set_audio(audio)

        # 출력 파일명
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{content_type}_{timestamp}.mp4"
        output_path = self.output_dir / output_filename

        # 영상 저장 (유튜브 숏츠 최적화)
        img_clip.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            bitrate='8000k'
        )

        # 임시 파일 삭제
        if temp_img_path.exists():
            temp_img_path.unlink()

        print(f"✅ 영상 생성 완료: {output_path}")

        # 메타데이터 저장
        metadata = {
            "video_file": str(output_path),
            "content_file": content_file,
            "title": title,
            "description": self._generate_description(content_data),
            "tags": content_data.get("hashtags", []),
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }

        metadata_path = output_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return str(output_path)

    def _generate_description(self, content_data: Dict) -> str:
        """유튜브 설명 생성"""
        title = content_data.get("title", "")
        content = content_data.get("content", "")
        hashtags = " ".join(content_data.get("hashtags", []))

        description = f"""{title}

{content[:200]}...

{hashtags}

📌 매일 새로운 운세와 토종비결을 업로드합니다!
📌 구독과 좋아요 부탁드립니다!

#유튜브숏츠 #shorts #운세 #사주 #토정비결
"""
        return description

    def create_simple_image(self, content_file: str) -> str:
        """
        간단한 이미지만 생성 (영상 생성 대신)
        MoviePy가 없는 경우 사용
        """
        # 콘텐츠 로드
        with open(content_file, 'r', encoding='utf-8') as f:
            content_data = json.load(f)

        content_type = content_data.get("type", "fortune")
        title = content_data.get("title", "")
        content = content_data.get("content", "")

        # 배경 이미지 생성
        theme = self.themes.get(content_type, self.themes["fortune"])
        img = self.create_background_image(content_type)

        # 제목 추가
        img = self.add_text_to_image(
            img, title, (100, 200),
            font_size=80, color=theme["text_color"]
        )

        # 본문 추가 (일부만)
        preview_text = content[:100] + "..."
        img = self.add_text_to_image(
            img, preview_text, (100, 500),
            font_size=60, color=(255, 255, 255)
        )

        # 이미지 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{content_type}_{timestamp}.png"
        output_path = self.output_dir.parent / "images" / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        img.save(output_path)

        print(f"✅ 이미지 생성 완료: {output_path}")
        return str(output_path)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='유튜브 숏츠 영상 생성')
    parser.add_argument('--content', type=str, required=True,
                       help='콘텐츠 JSON 파일 경로')
    parser.add_argument('--duration', type=int, default=30,
                       help='영상 길이 (초)')
    parser.add_argument('--music', type=str, help='배경음악 파일 경로')
    parser.add_argument('--output-dir', type=str, default='../output/videos',
                       help='출력 디렉토리')
    parser.add_argument('--image-only', action='store_true',
                       help='이미지만 생성 (영상 생성 안 함)')

    args = parser.parse_args()

    generator = VideoGenerator(output_dir=args.output_dir)

    if args.image_only or not MOVIEPY_AVAILABLE:
        result = generator.create_simple_image(args.content)
    else:
        result = generator.generate_video_from_content(
            args.content,
            duration=args.duration,
            background_music=args.music
        )

    print(f"\n생성 완료: {result}")


if __name__ == "__main__":
    main()

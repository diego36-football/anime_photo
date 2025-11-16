#!/usr/bin/env python3
"""
운세 및 토종비결 콘텐츠 생성 스크립트
OpenAI GPT API를 사용하여 신년운세, 토종비결 등의 콘텐츠를 생성합니다.
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List
import openai
from pathlib import Path

# OpenAI API 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

class ContentGenerator:
    """콘텐츠 생성기 클래스"""

    def __init__(self, output_dir: str = "../output/content"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 띠 목록
        self.zodiac_animals = [
            "쥐띠", "소띠", "호랑이띠", "토끼띠", "용띠", "뱀띠",
            "말띠", "양띠", "원숭이띠", "닭띠", "개띠", "돼지띠"
        ]

        # 토종비결 주제
        self.topics = [
            "금전운", "사업운", "연애운", "건강운", "학업운",
            "취업운", "가족운", "인간관계", "재물운", "승진운"
        ]

    def generate_fortune(self, zodiac: str = None, year: int = None) -> Dict:
        """
        신년운세 생성

        Args:
            zodiac: 띠 (예: "용띠")
            year: 연도 (기본값: 현재 연도)

        Returns:
            생성된 운세 데이터
        """
        if zodiac is None:
            zodiac = random.choice(self.zodiac_animals)

        if year is None:
            year = datetime.now().year

        prompt = f"""
        {year}년 {zodiac}의 신년운세를 작성해주세요.

        다음 항목을 포함해주세요:
        1. 전체 운세 (2-3문장)
        2. 금전운 (1-2문장)
        3. 연애운 (1-2문장)
        4. 건강운 (1-2문장)
        5. 조언 (1-2문장)

        유튜브 숏츠에 적합하게 짧고 임팩트 있게 작성해주세요.
        각 섹션을 명확히 구분하고, 긍정적이면서도 현실적인 톤으로 작성해주세요.
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 전문 사주 및 운세 상담가입니다. 유튜브 숏츠용 콘텐츠를 작성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )

            content = response.choices[0].message.content

            result = {
                "type": "fortune",
                "zodiac": zodiac,
                "year": year,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "title": f"{year}년 {zodiac} 신년운세",
                "hashtags": [
                    f"#{zodiac}", f"#{year}년운세", "#신년운세",
                    "#오늘의운세", "#사주", "#토정비결", "#유튜브숏츠"
                ]
            }

            # 파일로 저장
            filename = f"fortune_{zodiac}_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ 운세 생성 완료: {filepath}")
            return result

        except Exception as e:
            print(f"❌ 운세 생성 중 오류 발생: {e}")
            raise

    def generate_tojong_secret(self, topic: str = None) -> Dict:
        """
        토종비결 생성

        Args:
            topic: 주제 (예: "금전운")

        Returns:
            생성된 토종비결 데이터
        """
        if topic is None:
            topic = random.choice(self.topics)

        prompt = f"""
        오늘의 {topic}에 대한 토종비결을 작성해주세요.

        다음 형식으로 작성해주세요:
        1. 제목 (임팩트 있는 한 줄)
        2. 오늘의 한마디 (2-3문장)
        3. 주의사항 (1-2문장)
        4. 행운의 팁 (1-2문장)

        유튜브 숏츠에 적합하게 짧고 기억에 남도록 작성해주세요.
        전통적인 토종비결의 느낌을 살리면서도 현대적으로 해석해주세요.
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 전통 토종비결 전문가입니다. 유튜브 숏츠용 콘텐츠를 작성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=400
            )

            content = response.choices[0].message.content
            today = datetime.now().strftime("%Y년 %m월 %d일")

            result = {
                "type": "tojong_secret",
                "topic": topic,
                "date": today,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "title": f"{today} {topic} 토종비결",
                "hashtags": [
                    f"#{topic}", "#토종비결", "#오늘의운세",
                    "#사주", "#운세", "#유튜브숏츠", "#오늘의한마디"
                ]
            }

            # 파일로 저장
            filename = f"tojong_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ 토종비결 생성 완료: {filepath}")
            return result

        except Exception as e:
            print(f"❌ 토종비결 생성 중 오류 발생: {e}")
            raise

def main():
    """메인 함수 - CLI로 실행 가능"""
    import argparse

    parser = argparse.ArgumentParser(description='운세 및 토종비결 콘텐츠 생성')
    parser.add_argument('--type', choices=['fortune', 'tojong'], required=True,
                       help='생성할 콘텐츠 타입')
    parser.add_argument('--zodiac', type=str, help='띠 (운세 생성 시)')
    parser.add_argument('--topic', type=str, help='주제 (토종비결 생성 시)')
    parser.add_argument('--year', type=int, help='연도 (운세 생성 시)')
    parser.add_argument('--output-dir', type=str, default='../output/content',
                       help='출력 디렉토리')

    args = parser.parse_args()

    generator = ContentGenerator(output_dir=args.output_dir)

    if args.type == 'fortune':
        result = generator.generate_fortune(zodiac=args.zodiac, year=args.year)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.type == 'tojong':
        result = generator.generate_tojong_secret(topic=args.topic)
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

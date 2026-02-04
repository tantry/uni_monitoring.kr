# test_format.py - Test formatting in console
"""
Test the source and music type formatting
"""

from sources import format_source_line, get_music_types, get_music_icons, get_music_names

test_programs = [
    {
        'source': 'jinhaksa',
        'university': '서울대학교',
        'department': '실용음악학과',
        'program': '재즈보컬 추가모집 (R&B 포함)'
    },
    {
        'source': 'uway',
        'university': '경기대학교',
        'department': '음악학과',
        'program': '성악 추가모집'
    },
    {
        'source': 'unn',
        'university': '정책 뉴스',
        'department': '',
        'program': '2025학년도 추가모집 기간 연장'
    },
    {
        'source': 'adigo',
        'university': '인하대학교',
        'department': '음악대학',
        'program': '피아노 추가모집'
    }
]

print("🎵 Testing Source Display Formats\n")
print("="*60)

for program in test_programs:
    source_line = format_source_line(program['source'], program['university'])
    
    text = f"{program['department']} {program['program']}"
    music_types = get_music_types(text)
    music_icons = get_music_icons(music_types)
    music_names = get_music_names(music_types)
    
    print(f"\n{source_line}")
    print(f"{music_icons} {music_names}")
    print(f"• 프로그램: {program['program']}")
    print(f"• 학과: {program['department']}")
    print(f"• 감지된 유형: {music_types}")
    print("-"*40)

print("\n✅ 포맷 테스트 완료!")

import requests

# Test accessing one of the article detail pages we found
test_urls = [
    "https://www.adiga.kr/cct/pbf/noticeDetail.do?menuId=PCCCTPBF1000&prtlBbsId=26511",
    "https://www.adiga.kr/cct/pbf/noticeDetail.do?menuId=PCCCTPBF1000&prtlBbsId=25714",
    "https://adiga.kr/cct/pbf/noticeDetail.do?menuId=PCCCTPBF1000&prtlBbsId=20980",
]

headers = {'User-Agent': 'Mozilla/5.0'}

for url in test_urls:
    print(f"\nTesting: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Check if it looks like an article
            if len(response.content) > 5000:
                print(f"  ✅ Looks like a real article page")
                
                # Check for admission keywords
                content_lower = response.text.lower()
                admission_keywords = ['입학', '모집', '공고', '전형']
                found_keywords = [kw for kw in admission_keywords if kw in content_lower]
                
                if found_keywords:
                    print(f"  ✅ Contains admission keywords: {found_keywords}")
                else:
                    print(f"  ⚠ No admission keywords found")
            else:
                print(f"  ⚠ Page too small, might be blocked or require login")
        else:
            print(f"  ❌ Cannot access (might require authentication)")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

import requests

url = "https://www.adiga.kr/cct/pbf/noticeList.do?menuId=PCCCTPBF1000"
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

print(f"Status: {response.status_code}")
print(f"Content length: {len(response.content)} bytes")
print("\nFirst 500 chars:")
print(response.text[:500])

#!/bin/bash
echo "=== Examining Working Adiga Page ==="
echo ""

# Look at the debug file we already have
if [ -f "debug_noticeDetail.do.html" ]; then
    echo "1. First 1000 characters of working page:"
    head -c 1000 debug_noticeDetail.do.html
    echo -e "\n\n..."
    
    echo ""
    echo "2. Looking for article content patterns:"
    grep -i -o -E "(입학|모집|전형|공고|안내|학과|대학|admission|recruit|announce)" debug_noticeDetail.do.html | head -20
    
    echo ""
    echo "3. Checking for JavaScript functions:"
    grep -i "fnDetailPopup\|goDetail\|javascript:" debug_noticeDetail.do.html | head -10
    
    echo ""
    echo "4. Checking for links:"
    grep -o 'href="[^"]*"' debug_noticeDetail.do.html | head -10
    grep -o "onclick=\"[^\"]*\"" debug_noticeDetail.do.html | head -10
    
    echo ""
    echo "5. Checking for prtlBbsId patterns:"
    grep -o "prtlBbsId=[0-9]*" debug_noticeDetail.do.html
    
    echo ""
    echo "6. Checking article structure:"
    echo "Title tags:"
    grep -i "<title>" debug_noticeDetail.do.html
    echo ""
    echo "Heading tags:"
    grep -i "<h[1-4]" debug_noticeDetail.do.html | head -10
else
    echo "debug_noticeDetail.do.html not found, fetching fresh..."
    curl -s "https://www.adiga.kr/cct/pbf/noticeDetail.do?menuId=PCCCTPBF1000&prtlBbsId=26511" -o fresh_page.html
    echo "Saved as fresh_page.html"
    head -c 1000 fresh_page.html
fi

#!/usr/bin/env python3
"""
Adiga Content Extractor - Robust content extraction from Adiga's hidden fields
"""
import re
import html
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import logging

class AdigaContentExtractor:
    """Extracts actual content from Adiga.kr's complex HTML structure"""
    
    def __init__(self):
        self.logger = logging.getLogger("content_extractor")
        
    def extract_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extract content from Adiga HTML with multiple fallback strategies
        
        Returns:
            Dictionary with extracted content and metadata
        """
        result = {
            'raw_content': '',
            'clean_content': '',
            'extraction_method': 'unknown',
            'has_content': False,
            'content_length': 0
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # STRATEGY 1: Extract from hidden field with HTML content
            hidden_content = self._extract_from_hidden_field(soup)
            if hidden_content:
                result['raw_content'] = hidden_content
                result['clean_content'] = self._clean_html_content(hidden_content)
                result['extraction_method'] = 'hidden_field'
                result['has_content'] = True
            
            # STRATEGY 2: If hidden field fails, extract from visible popup
            if not result['has_content']:
                visible_content = self._extract_from_popup(soup)
                if visible_content:
                    result['raw_content'] = visible_content
                    result['clean_content'] = self._clean_visible_content(visible_content)
                    result['extraction_method'] = 'popup_content'
                    result['has_content'] = True
            
            # STRATEGY 3: Extract metadata and basic info as fallback
            if not result['has_content']:
                basic_info = self._extract_basic_info(soup)
                if basic_info:
                    result['raw_content'] = basic_info
                    result['clean_content'] = basic_info
                    result['extraction_method'] = 'basic_info'
                    result['has_content'] = len(basic_info) > 0
            
            # Calculate final content
            if result['has_content']:
                result['clean_content'] = self._final_cleanup(result['clean_content'])
                result['content_length'] = len(result['clean_content'])
            
            # Add debugging info
            result['debug'] = {
                'html_length': len(html_content),
                'input_id_found': 'lnaCn1' in html_content,
                'popup_cont_found': bool(soup.find('div', id='newsPopCont'))
            }
            
        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}")
            result['error'] = str(e)
        
        return result
    
    def _extract_from_hidden_field(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract HTML content from hidden input field (Adiga's primary method)"""
        try:
            # Find the hidden input field containing HTML content
            hidden_input = soup.find('input', id='lnaCn1')
            if hidden_input and hidden_input.get('value'):
                html_content = hidden_input['value']
                
                # The content is HTML-encoded, so decode it
                decoded_content = html.unescape(html_content)
                
                # Parse the inner HTML
                inner_soup = BeautifulSoup(decoded_content, 'html.parser')
                
                # Extract text from inner HTML
                text_content = inner_soup.get_text(separator=' ', strip=True)
                
                if text_content and len(text_content) > 50:  # Reasonable minimum
                    self.logger.info(f"Extracted {len(text_content)} chars from hidden field")
                    return text_content
        
        except Exception as e:
            self.logger.debug(f"Hidden field extraction failed: {e}")
        
        return None
    
    def _extract_from_popup(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract content from popup container"""
        try:
            popup = soup.find('div', id='newsPopCont')
            if popup:
                # Try to find content in ArchiveDtContent div
                archive_content = popup.find('div', class_='ArchiveDtContent')
                if archive_content:
                    content_text = archive_content.get_text(separator=' ', strip=True)
                    if content_text and len(content_text) > 30:
                        self.logger.info(f"Extracted {len(content_text)} chars from popup")
                        return content_text
                
                # Fallback: extract all text from popup
                all_text = popup.get_text(separator=' ', strip=True)
                if all_text and len(all_text) > 50:
                    # Remove title section if present
                    title_word = popup.find('div', class_='titleWordInfo')
                    if title_word:
                        title_text = title_word.get_text(strip=True)
                        all_text = all_text.replace(title_text, '').strip()
                    
                    self.logger.info(f"Extracted {len(all_text)} chars from popup text")
                    return all_text
        
        except Exception as e:
            self.logger.debug(f"Popup extraction failed: {e}")
        
        return None
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> str:
        """Extract basic information as fallback"""
        info_parts = []
        
        try:
            # Extract title
            title_elem = soup.find('meta', property='og:title')
            if title_elem and title_elem.get('content'):
                info_parts.append(f"제목: {title_elem['content']}")
            
            # Extract description
            desc_elem = soup.find('meta', property='og:description')
            if desc_elem and desc_elem.get('content'):
                info_parts.append(f"요약: {desc_elem['content']}")
            
            # Extract from page title
            page_title = soup.find('title')
            if page_title:
                title_text = page_title.get_text(strip=True)
                if title_text and '제목 없음' not in title_text:
                    info_parts.append(f"페이지 제목: {title_text}")
        
        except Exception as e:
            self.logger.debug(f"Basic info extraction failed: {e}")
        
        return ' '.join(info_parts) if info_parts else ''
    
    def _clean_html_content(self, content: str) -> str:
        """Clean HTML content for display"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common HTML artifacts
        artifacts = [
            r'&nbsp;', r'&amp;', r'&lt;', r'&gt;', r'&quot;', r'&#\d+;',
            r'<[^>]+>', r'\\[ntr]', r'\u200b', r'\xa0'
        ]
        
        for artifact in artifacts:
            content = re.sub(artifact, ' ', content)
        
        # Decode any remaining HTML entities
        content = html.unescape(content)
        
        return content.strip()
    
    def _clean_visible_content(self, content: str) -> str:
        """Clean visible content"""
        content = re.sub(r'\s+', ' ', content)
        content = html.unescape(content)
        return content.strip()
    
    def _final_cleanup(self, content: str) -> str:
        """Final cleanup of content"""
        if not content:
            return ""
        
        # Remove multiple spaces
        content = re.sub(r'\s{2,}', ' ', content)
        
        # Trim to reasonable length for Telegram
        max_length = 1000
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content.strip()

# Singleton instance
_extractor_instance = None

def get_content_extractor() -> AdigaContentExtractor:
    """Get singleton content extractor instance"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = AdigaContentExtractor()
    return _extractor_instance

def extract_content(html_content: str, url: str = "") -> Dict[str, Any]:
    """Convenience function to extract content"""
    extractor = get_content_extractor()
    return extractor.extract_content(html_content, url)


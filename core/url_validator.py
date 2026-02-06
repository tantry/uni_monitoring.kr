#!/usr/bin/env python3
"""
URL Validator and Corrector for ensuring Telegram links actually work
"""
import requests
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
import logging
from typing import Dict, Any, Optional, Tuple
import re

class URLValidator:
    """Validates and corrects URLs to ensure they work in Telegram"""
    
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
        })
        self.logger = logging.getLogger("url_validator")
    
    def validate_adiga_url(self, url: str) -> Dict[str, Any]:
        """
        Validate an adiga.kr URL and return analysis
        
        Returns:
            Dictionary with validation results and corrected URL if needed
        """
        result = {
            'original_url': url,
            'is_valid': False,
            'status_code': None,
            'requires_js': False,
            'requires_login': False,
            'has_content': False,
            'corrected_url': url,
            'error': None,
            'content_type': None,
            'content_length': 0
        }
        
        try:
            # First, try to access the URL
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            result['status_code'] = response.status_code
            result['content_type'] = response.headers.get('content-type', '')
            result['content_length'] = len(response.text)
            
            if response.status_code == 200:
                result['is_valid'] = True
                
                # Analyze the content
                content = response.text.lower()
                
                # Check for common issues
                if 'javascript' in content and ('disabled' in content or 'enable' in content):
                    result['requires_js'] = True
                    self.logger.warning(f"URL requires JavaScript: {url}")
                
                if '로그인' in response.text or 'login' in content:
                    result['requires_login'] = True
                    self.logger.warning(f"URL requires login: {url}")
                
                # Check if it has actual article content
                article_indicators = ['article', 'content', '게시글', '기사', '내용', '본문']
                has_indicators = any(indicator in response.text for indicator in article_indicators)
                result['has_content'] = has_indicators
                
                # Try to find a better URL pattern if this one doesn't have content
                if not has_indicators:
                    corrected = self._try_correct_adiga_url(url, response.text)
                    if corrected and corrected != url:
                        result['corrected_url'] = corrected
                        self.logger.info(f"Corrected URL: {url} -> {corrected}")
                        
                        # Test the corrected URL
                        try:
                            corrected_response = self.session.get(corrected, timeout=self.timeout)
                            if corrected_response.status_code == 200:
                                corrected_content = corrected_response.text.lower()
                                if any(indicator in corrected_response.text for indicator in article_indicators):
                                    result['has_content'] = True
                                    self.logger.info(f"Corrected URL has content!")
                        except:
                            pass
                
            else:
                result['error'] = f"HTTP {response.status_code}"
                self.logger.error(f"URL returned {response.status_code}: {url}")
                
        except requests.exceptions.Timeout:
            result['error'] = "Timeout"
            self.logger.error(f"Timeout accessing URL: {url}")
        except requests.exceptions.ConnectionError as e:
            result['error'] = f"Connection error: {e}"
            self.logger.error(f"Connection error: {url} - {e}")
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error accessing URL {url}: {e}")
        
        return result
    
    def _try_correct_adiga_url(self, original_url: str, page_content: str) -> Optional[str]:
        """
        Try to find a better URL pattern for adiga.kr articles
        
        Returns:
            Corrected URL or None if no correction found
        """
        parsed = urlparse(original_url)
        
        # Pattern 1: Try with different parameter formats
        if 'prtlBbsId' in original_url:
            # Extract article ID
            qs = parse_qs(parsed.query)
            article_id = qs.get('prtlBbsId', [''])[0]
            
            if article_id:
                # Try alternative URL patterns
                alternatives = [
                    # More direct pattern
                    f"https://www.adiga.kr/PageLink.do?link=/enw/news/newsDetail&prtlBbsId={article_id}",
                    # Simplified pattern
                    f"https://www.adiga.kr/newsDetail.do?prtlBbsId={article_id}",
                    # Mobile pattern
                    f"https://m.adiga.kr/news/{article_id}",
                ]
                
                # Check each alternative
                for alt_url in alternatives:
                    try:
                        resp = self.session.head(alt_url, timeout=5, allow_redirects=True)
                        if resp.status_code == 200:
                            return alt_url
                    except:
                        continue
        
        # Pattern 2: Look for article links in the page
        article_links = re.findall(r'href=[\"\'](https?://[^\"\']*adiga[^\"\']*article[^\"\']*)[\"\']', page_content, re.IGNORECASE)
        article_links += re.findall(r'href=[\"\'](https?://[^\"\']*adiga[^\"\']*news[^\"\']*)[\"\']', page_content, re.IGNORECASE)
        
        for link in article_links:
            if 'prtlBbsId' in link and article_id in link:
                return link
        
        return None
    
    def ensure_working_url(self, url: str, source_name: str = "unknown") -> str:
        """
        Ensure a URL works, with fallback strategies
        
        Returns:
            Working URL (original or corrected)
        """
        if 'adiga.kr' in url:
            validation = self.validate_adiga_url(url)
            
            if validation['is_valid'] and validation['has_content']:
                return validation['corrected_url']
            elif validation['is_valid'] and not validation['has_content']:
                self.logger.warning(f"URL accessible but no content found: {url}")
                return validation['corrected_url']  # Still return the corrected version
            else:
                self.logger.error(f"URL validation failed: {url} - {validation.get('error')}")
                # Return original as fallback
                return url
        else:
            # For non-adiga sites, do basic validation
            try:
                response = self.session.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    return url
                else:
                    self.logger.warning(f"Non-adiga URL returned {response.status_code}: {url}")
                    return url
            except:
                self.logger.warning(f"Could not validate non-adiga URL: {url}")
                return url
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()

# Singleton instance
_validator_instance = None

def get_url_validator() -> URLValidator:
    """Get singleton URL validator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = URLValidator()
    return _validator_instance

def validate_url(url: str) -> Dict[str, Any]:
    """Convenience function to validate a URL"""
    validator = get_url_validator()
    return validator.validate_adiga_url(url) if 'adiga.kr' in url else {'original_url': url, 'is_valid': True}

def ensure_working_url(url: str, source_name: str = "unknown") -> str:
    """Convenience function to ensure a URL works"""
    validator = get_url_validator()
    return validator.ensure_working_url(url, source_name)


"""
Robust HTML Parser - No Shortcuts Approach
==========================================
A production-grade HTML parsing system with multiple fallback strategies.
This ensures the Helix engine works reliably regardless of dependency availability.
"""

import re
import html
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class ParsedElement:
    """Represents a parsed HTML element with attributes and content."""
    tag: str
    attrs: Dict[str, str]
    text: str = ""
    id: Optional[str] = None
    classes: List[str] = None
    
    def __post_init__(self):
        if self.classes is None:
            self.classes = []
        
        # Extract common attributes
        self.id = self.attrs.get('id')
        if 'class' in self.attrs:
            self.classes = self.attrs['class'].split()
    
    def get(self, attr: str, default: str = "") -> str:
        """Get attribute value with default."""
        return self.attrs.get(attr, default)
    
    def has_class(self, class_name: str) -> bool:
        """Check if element has specific class."""
        return class_name in self.classes
    
    def matches_selector(self, selector: str) -> bool:
        """Check if element matches a CSS selector (simplified)."""
        selector = selector.strip()
        
        # ID selector
        if selector.startswith('#'):
            return self.id == selector[1:]
        
        # Class selector  
        if selector.startswith('.'):
            return self.has_class(selector[1:])
        
        # Tag selector
        if ' ' not in selector and '[' not in selector:
            return self.tag.lower() == selector.lower()
        
        # Attribute selector
        if '[' in selector and ']' in selector:
            attr_match = re.search(r'\[([^=\]]+)(?:([*^$|~]?)=["\']?([^"\']*?)["\']?)?\]', selector)
            if attr_match:
                attr_name = attr_match.group(1)
                operator = attr_match.group(2) or '='
                attr_value = attr_match.group(3) or ''
                
                element_value = self.get(attr_name)
                
                if not element_value and operator == '=':
                    return False
                
                if operator == '*=' and attr_value:
                    return attr_value.lower() in element_value.lower()
                elif operator == '=' and attr_value:
                    return element_value.lower() == attr_value.lower()
                elif not attr_value:  # Just checking attribute exists
                    return attr_name in self.attrs
        
        return False


class RobustHTMLParser:
    """
    Production-grade HTML parser with multiple fallback strategies.
    
    Parsing strategy priority:
    1. BeautifulSoup with lxml (fastest, most accurate)
    2. BeautifulSoup with html.parser (built-in, reliable)
    3. BeautifulSoup with html5lib (most forgiving)
    4. Regex-based parsing (always works)
    """
    
    def __init__(self):
        self.available_parsers = self._detect_available_parsers()
        self.current_parser = None
        
    def _detect_available_parsers(self) -> List[str]:
        """Detect which HTML parsers are available."""
        parsers = []
        
        try:
            from bs4 import BeautifulSoup
            # Test lxml
            try:
                BeautifulSoup("<test></test>", 'lxml')
                parsers.append('lxml')
            except:
                pass
            
            # Test html.parser (always available)
            try:
                BeautifulSoup("<test></test>", 'html.parser')
                parsers.append('html.parser')
            except:
                pass
            
            # Test html5lib
            try:
                BeautifulSoup("<test></test>", 'html5lib')
                parsers.append('html5lib')
            except:
                pass
                
        except ImportError:
            pass
        
        # Always add regex fallback
        parsers.append('regex')
        
        return parsers
    
    def parse(self, html_content: str) -> 'RobustSoup':
        """Parse HTML with the best available parser."""
        
        if not html_content:
            return RobustSoup([], 'empty')
        
        # Try each parser in priority order
        for parser in self.available_parsers:
            try:
                if parser == 'regex':
                    return self._parse_with_regex(html_content)
                else:
                    return self._parse_with_beautifulsoup(html_content, parser)
                    
            except Exception as e:
                print(f"⚠️ Parser {parser} failed: {e}")
                continue
        
        # Final fallback - should never reach here
        return RobustSoup([], 'failed')
    
    def _parse_with_beautifulsoup(self, html_content: str, parser: str) -> 'RobustSoup':
        """Parse using BeautifulSoup with specified parser."""
        
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, parser)
        self.current_parser = f'beautifulsoup_{parser}'
        
        return RobustSoup(soup, self.current_parser)
    
    def _parse_with_regex(self, html_content: str) -> 'RobustSoup':
        """Parse using regex as final fallback."""
        
        elements = []
        
        # Pattern to match HTML elements with attributes
        element_pattern = r'<(\w+)([^>]*?)(?:\s*/\s*>|>(.*?)</\1>)'
        
        for match in re.finditer(element_pattern, html_content, re.IGNORECASE | re.DOTALL):
            tag = match.group(1)
            attrs_str = match.group(2) or ''
            content = match.group(3) or ''
            
            # Parse attributes
            attrs = {}
            attr_pattern = r'(\w+)(?:\s*=\s*["\']([^"\']*)["\'])?'
            for attr_match in re.finditer(attr_pattern, attrs_str):
                attr_name = attr_match.group(1)
                attr_value = attr_match.group(2) or ''
                attrs[attr_name] = attr_value
            
            # Clean text content
            text_content = re.sub(r'<[^>]+>', '', content).strip()
            
            element = ParsedElement(tag=tag, attrs=attrs, text=text_content)
            elements.append(element)
        
        self.current_parser = 'regex'
        return RobustSoup(elements, self.current_parser)


class RobustSoup:
    """
    Unified interface for parsed HTML that works with both BeautifulSoup and regex parsing.
    Provides BeautifulSoup-compatible methods while maintaining robustness.
    """
    
    def __init__(self, soup_or_elements: Union[Any, List[ParsedElement]], parser_used: str):
        self.soup_or_elements = soup_or_elements
        self.parser_used = parser_used
        self._is_beautifulsoup = parser_used.startswith('beautifulsoup')
    
    def find(self, tag: str = None, attrs: Dict = None, **kwargs) -> Optional[Union[Any, ParsedElement]]:
        """Find first element matching criteria."""
        
        if self._is_beautifulsoup:
            # Use BeautifulSoup's find method
            return self.soup_or_elements.find(tag, attrs, **kwargs)
        else:
            # Use regex-parsed elements
            for element in self.soup_or_elements:
                if self._element_matches(element, tag, attrs, **kwargs):
                    return element
            return None
    
    def find_all(self, tag: str = None, attrs: Dict = None, **kwargs) -> List[Union[Any, ParsedElement]]:
        """Find all elements matching criteria."""
        
        if self._is_beautifulsoup:
            # Use BeautifulSoup's find_all method
            return self.soup_or_elements.find_all(tag, attrs, **kwargs)
        else:
            # Use regex-parsed elements
            results = []
            for element in self.soup_or_elements:
                if self._element_matches(element, tag, attrs, **kwargs):
                    results.append(element)
            return results
    
    def select(self, selector: str) -> List[Union[Any, ParsedElement]]:
        """Select elements using CSS selector."""
        
        if self._is_beautifulsoup:
            try:
                return self.soup_or_elements.select(selector)
            except:
                # Fallback to manual matching
                pass
        
        # Manual CSS selector matching
        results = []
        for element in (self.soup_or_elements if not self._is_beautifulsoup else self._extract_elements()):
            if element.matches_selector(selector):
                results.append(element)
        
        return results
    
    def _element_matches(self, element: ParsedElement, tag: str = None, attrs: Dict = None, **kwargs) -> bool:
        """Check if element matches search criteria."""
        
        # Check tag
        if tag and element.tag.lower() != tag.lower():
            return False
        
        # Check attributes
        if attrs:
            for attr_name, attr_value in attrs.items():
                element_value = element.get(attr_name)
                
                if callable(attr_value):
                    # Lambda function check
                    if not attr_value(element_value):
                        return False
                elif attr_value is True:
                    # Just check attribute exists
                    if attr_name not in element.attrs:
                        return False
                else:
                    # Exact value match
                    if element_value != str(attr_value):
                        return False
        
        # Check other keyword arguments
        for key, value in kwargs.items():
            if key == 'id' and element.id != value:
                return False
            elif key == 'class_' and not element.has_class(value):
                return False
            elif key == 'string' and value not in element.text:
                return False
        
        return True
    
    def _extract_elements(self) -> List[ParsedElement]:
        """Extract elements from BeautifulSoup for manual processing."""
        if not self._is_beautifulsoup:
            return self.soup_or_elements
        
        # Convert BeautifulSoup elements to ParsedElement format
        elements = []
        for tag in self.soup_or_elements.find_all():
            attrs = dict(tag.attrs) if hasattr(tag, 'attrs') else {}
            text = tag.get_text() if hasattr(tag, 'get_text') else ''
            
            element = ParsedElement(tag=tag.name, attrs=attrs, text=text)
            elements.append(element)
        
        return elements


# Global parser instance
_html_parser = RobustHTMLParser()

def parse_html(html_content: str) -> RobustSoup:
    """
    Parse HTML content using the most robust method available.
    
    This function automatically selects the best available parser and
    provides a unified interface regardless of dependencies.
    """
    return _html_parser.parse(html_content)

def get_parser_info() -> Dict[str, Any]:
    """Get information about available parsers."""
    return {
        "available_parsers": _html_parser.available_parsers,
        "current_parser": _html_parser.current_parser,
        "beautifulsoup_available": any('beautifulsoup' in p for p in _html_parser.available_parsers)
    }
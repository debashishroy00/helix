"""
Layer 3: Visual Fingerprinting
==============================

This layer uses computer vision to identify elements by their visual appearance.
Critical for handling canvas-rendered UIs, complex visualizations, and when
DOM structure is unreliable.

Patent Justification:
- Works when DOM is completely unreliable (canvas, WebGL, shadow DOM)
- Identifies elements by how they LOOK, not how they're coded
- Provides fallback coordinates when no selector works

Example:
    - OCR to find button text
    - Shape detection for standard UI patterns
    - Color/style matching for branded elements
"""

import asyncio
import base64
from io import BytesIO
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from PIL import Image
import cv2
import pytesseract

from src.layers.base import BaseLayer
from src.models.element import ElementStrategy, ElementContext, StrategyType


class VisualFingerprintLayer(BaseLayer):
    """
    Layer 3: Uses computer vision and OCR to identify elements visually.
    
    This layer is positioned third because it's computationally expensive
    but provides a reliable fallback when DOM-based methods fail.
    """
    
    def __init__(self):
        super().__init__(StrategyType.VISUAL_FINGERPRINT)
        
        # Visual patterns for common UI elements
        self.button_patterns = {
            "rounded_rect": {"min_area": 1000, "aspect_ratio": (2, 6)},
            "pill_shape": {"min_area": 800, "aspect_ratio": (2.5, 8)},
            "square": {"min_area": 400, "aspect_ratio": (0.8, 1.2)}
        }
        
        # Platform-specific visual signatures
        self.platform_colors = {
            "salesforce_lightning": {
                "primary_button": [(0, 112, 210), (16, 124, 252)],  # Salesforce blue
                "secondary_button": [(255, 255, 255), (250, 250, 250)]
            },
            "sap_fiori": {
                "primary_button": [(0, 112, 242), (10, 122, 255)],  # SAP blue
                "accent": [(247, 148, 30), (255, 158, 40)]  # SAP orange
            }
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Generate visual-based strategies using OCR and computer vision.
        """
        strategies = []
        
        try:
            # Take screenshot
            screenshot = await self._capture_screenshot(page)
            if not screenshot:
                return strategies
            
            # Convert to formats needed for different operations
            pil_image = Image.open(BytesIO(screenshot))
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Strategy 1: OCR-based text search
            ocr_strategies = await self._ocr_strategies(pil_image, cv_image, context)
            strategies.extend(ocr_strategies)
            
            # Strategy 2: Shape-based detection
            shape_strategies = await self._shape_detection_strategies(cv_image, context)
            strategies.extend(shape_strategies)
            
            # Strategy 3: Color-based detection (platform-specific)
            if context.platform.value in self.platform_colors:
                color_strategies = await self._color_based_strategies(cv_image, context)
                strategies.extend(color_strategies)
            
            # Strategy 4: Template matching for known UI patterns
            template_strategies = await self._template_matching_strategies(cv_image, context)
            strategies.extend(template_strategies)
            
            return strategies
            
        except Exception as e:
            print(f"Visual fingerprint error: {str(e)}")
            return strategies
    
    async def _capture_screenshot(self, page: Any) -> Optional[bytes]:
        """Capture screenshot of the current viewport."""
        try:
            # Handle both Playwright and Selenium
            if hasattr(page, 'screenshot'):  # Playwright
                return await page.screenshot()
            elif hasattr(page, 'get_screenshot_as_png'):  # Selenium
                return page.get_screenshot_as_png()
            else:
                print("Unsupported page object for screenshots")
                return None
        except Exception as e:
            print(f"Screenshot capture error: {str(e)}")
            return None
    
    async def _ocr_strategies(
        self, 
        pil_image: Image.Image,
        cv_image: np.ndarray,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Use OCR to find text matching the intent."""
        strategies = []
        
        try:
            # Perform OCR with location data
            ocr_data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Search for text matching intent
            intent_words = context.intent.lower().split()
            
            for i, text in enumerate(ocr_data['text']):
                if not text.strip():
                    continue
                
                text_lower = text.lower()
                
                # Check if text matches intent
                match_score = self._calculate_text_match_score(text_lower, intent_words)
                
                if match_score > 0.5:
                    # Get bounding box
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    
                    # Calculate center point for clicking
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # Create visual click strategy
                    strategy = ElementStrategy(
                        strategy_type=self.layer_type,
                        selector=f"visual:click({center_x},{center_y})",
                        confidence=min(match_score * 0.9, 0.85),
                        metadata={
                            "method": "ocr",
                            "matched_text": text,
                            "bbox": {"x": x, "y": y, "width": w, "height": h},
                            "match_score": match_score
                        }
                    )
                    strategies.append(strategy)
            
            # Also try to find containing elements for the text
            if strategies:
                # Generate a selector for text-based search
                best_match = max(strategies, key=lambda s: s.confidence)
                text = best_match.metadata["matched_text"]
                
                text_strategies = [
                    ElementStrategy(
                        strategy_type=self.layer_type,
                        selector=f'//*[contains(text(), "{text}")]',
                        confidence=best_match.confidence * 0.8,
                        metadata={"method": "ocr_xpath", "text": text}
                    ),
                    ElementStrategy(
                        strategy_type=self.layer_type,
                        selector=f'*:contains("{text}")',
                        confidence=best_match.confidence * 0.7,
                        metadata={"method": "ocr_css", "text": text}
                    )
                ]
                strategies.extend(text_strategies)
            
        except Exception as e:
            print(f"OCR error: {str(e)}")
        
        return strategies
    
    async def _shape_detection_strategies(
        self,
        cv_image: np.ndarray,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Detect UI elements by their shapes."""
        strategies = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Look for button-like shapes based on intent
            if any(word in context.intent.lower() for word in ["button", "submit", "click"]):
                for contour in contours:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Check if it matches button patterns
                    is_button = False
                    for pattern_name, criteria in self.button_patterns.items():
                        if (area >= criteria["min_area"] and
                            criteria["aspect_ratio"][0] <= aspect_ratio <= criteria["aspect_ratio"][1]):
                            is_button = True
                            break
                    
                    if is_button:
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        strategy = ElementStrategy(
                            strategy_type=self.layer_type,
                            selector=f"visual:click({center_x},{center_y})",
                            confidence=0.6,
                            metadata={
                                "method": "shape_detection",
                                "shape": pattern_name,
                                "bbox": {"x": x, "y": y, "width": w, "height": h},
                                "area": area,
                                "aspect_ratio": aspect_ratio
                            }
                        )
                        strategies.append(strategy)
        
        except Exception as e:
            print(f"Shape detection error: {str(e)}")
        
        return strategies
    
    async def _color_based_strategies(
        self,
        cv_image: np.ndarray,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Detect elements by platform-specific colors."""
        strategies = []
        
        try:
            platform_colors = self.platform_colors.get(context.platform.value, {})
            
            for element_type, color_ranges in platform_colors.items():
                if element_type.replace("_", " ") in context.intent.lower():
                    # Create mask for color range
                    mask = np.zeros(cv_image.shape[:2], dtype=np.uint8)
                    
                    for color_range in color_ranges:
                        lower = np.array(color_range[0])
                        upper = np.array(color_range[1]) if len(color_range) > 1 else lower + 20
                        
                        color_mask = cv2.inRange(cv_image, lower, upper)
                        mask = cv2.bitwise_or(mask, color_mask)
                    
                    # Find contours in color mask
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)
                        area = w * h
                        
                        if area > 500:  # Minimum area threshold
                            center_x = x + w // 2
                            center_y = y + h // 2
                            
                            strategy = ElementStrategy(
                                strategy_type=self.layer_type,
                                selector=f"visual:click({center_x},{center_y})",
                                confidence=0.7,
                                metadata={
                                    "method": "color_detection",
                                    "element_type": element_type,
                                    "platform": context.platform.value,
                                    "bbox": {"x": x, "y": y, "width": w, "height": h}
                                }
                            )
                            strategies.append(strategy)
        
        except Exception as e:
            print(f"Color detection error: {str(e)}")
        
        return strategies
    
    async def _template_matching_strategies(
        self,
        cv_image: np.ndarray,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Match against known UI pattern templates."""
        # This would load and match against a library of UI patterns
        # For now, returning empty list - would be implemented with actual templates
        return []
    
    def _calculate_text_match_score(self, text: str, intent_words: List[str]) -> float:
        """Calculate how well text matches the intent."""
        if not text or not intent_words:
            return 0.0
        
        text_words = text.split()
        matches = 0
        
        for intent_word in intent_words:
            for text_word in text_words:
                # Exact match
                if intent_word == text_word:
                    matches += 1.0
                # Partial match
                elif intent_word in text_word or text_word in intent_word:
                    matches += 0.5
                # Fuzzy match (simple Levenshtein-like)
                elif self._simple_fuzzy_match(intent_word, text_word) > 0.8:
                    matches += 0.3
        
        # Normalize score
        max_possible = len(intent_words)
        return min(matches / max_possible, 1.0) if max_possible > 0 else 0.0
    
    def _simple_fuzzy_match(self, s1: str, s2: str) -> float:
        """Simple fuzzy string matching."""
        if s1 == s2:
            return 1.0
        
        len_ratio = min(len(s1), len(s2)) / max(len(s1), len(s2))
        
        # Count common characters
        common = sum(1 for c in s1 if c in s2)
        char_ratio = common / max(len(s1), len(s2))
        
        return (len_ratio + char_ratio) / 2
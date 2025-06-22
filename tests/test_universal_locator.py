"""
Test Universal Locator Core Functionality
=========================================

Tests for the core element identification system.
Verifies that the 7-layer architecture works correctly.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.core.universal_locator import UniversalLocator
from src.models.element import ElementContext, Platform, ElementResult, StrategyType


@pytest.fixture
def mock_page():
    """Mock page object for testing."""
    page = Mock()
    page.locator = Mock()
    page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
    return page


@pytest.fixture
def sample_context():
    """Sample element context for testing."""
    return ElementContext(
        platform=Platform.SALESFORCE_LIGHTNING,
        page_type="form",
        intent="submit button",
        additional_context={"form_type": "account_creation"}
    )


@pytest.fixture
def universal_locator():
    """Universal locator instance for testing."""
    return UniversalLocator()


@pytest.mark.asyncio
async def test_find_element_success(universal_locator, mock_page, sample_context):
    """Test successful element identification."""
    # Mock a successful element find
    mock_element = Mock()
    mock_page.locator.return_value.count = AsyncMock(return_value=1)
    mock_page.locator.return_value.first = mock_element
    
    result = await universal_locator.find_element(mock_page, sample_context)
    
    assert isinstance(result, ElementResult)
    assert result.found is True
    assert result.element is not None
    assert result.strategy_used is not None
    assert result.time_taken_ms >= 0


@pytest.mark.asyncio 
async def test_find_element_not_found(universal_locator, mock_page, sample_context):
    """Test when element is not found by any strategy."""
    # Mock no elements found
    mock_page.locator.return_value.count = AsyncMock(return_value=0)
    
    result = await universal_locator.find_element(mock_page, sample_context)
    
    assert isinstance(result, ElementResult)
    assert result.found is False
    assert result.element is None
    assert len(result.attempts) > 0  # Should have tried multiple strategies


@pytest.mark.asyncio
async def test_semantic_layer_generates_strategies(universal_locator, mock_page, sample_context):
    """Test that semantic layer generates multiple strategies."""
    semantic_layer = universal_locator.layers[StrategyType.SEMANTIC_INTENT]
    
    with patch.object(semantic_layer, '_fallback_strategies') as mock_fallback:
        mock_fallback.return_value = [
            Mock(strategy_type=StrategyType.SEMANTIC_INTENT, confidence=0.8),
            Mock(strategy_type=StrategyType.SEMANTIC_INTENT, confidence=0.6)
        ]
        
        strategies = await semantic_layer.generate_strategies(mock_page, sample_context)
        
        assert len(strategies) >= 2
        assert all(s.strategy_type == StrategyType.SEMANTIC_INTENT for s in strategies)


@pytest.mark.asyncio
async def test_visual_layer_with_screenshot(universal_locator, mock_page, sample_context):
    """Test that visual layer processes screenshots."""
    visual_layer = universal_locator.layers[StrategyType.VISUAL_FINGERPRINT]
    
    # Mock PIL and OpenCV operations
    with patch('src.layers.visual_fingerprint.Image') as mock_image, \
         patch('src.layers.visual_fingerprint.cv2') as mock_cv2, \
         patch('src.layers.visual_fingerprint.pytesseract') as mock_tesseract:
        
        mock_tesseract.image_to_data.return_value = {
            'text': ['Submit', 'Cancel', ''],
            'left': [100, 200, 0],
            'top': [50, 50, 0],
            'width': [80, 60, 0],
            'height': [30, 30, 0]
        }
        
        strategies = await visual_layer.generate_strategies(mock_page, sample_context)
        
        # Should find at least one strategy from OCR
        assert len(strategies) >= 1
        visual_strategies = [s for s in strategies if s.selector.startswith('visual:')]
        assert len(visual_strategies) >= 1


@pytest.mark.asyncio 
async def test_caching_mechanism(universal_locator, mock_page, sample_context):
    """Test that successful strategies are cached."""
    # Mock cache client
    mock_cache = AsyncMock()
    universal_locator.cache_client = mock_cache
    mock_cache.get.return_value = None  # No cached strategy initially
    
    # Mock successful find
    mock_element = Mock()
    mock_page.locator.return_value.count = AsyncMock(return_value=1)
    mock_page.locator.return_value.first = mock_element
    
    result = await universal_locator.find_element(mock_page, sample_context)
    
    assert result.found is True
    # Verify cache was written to
    mock_cache.setex.assert_called_once()


@pytest.mark.asyncio
async def test_strategy_weight_learning(universal_locator, mock_page, sample_context):
    """Test that strategy weights are updated based on success/failure."""
    initial_weights = universal_locator.strategy_weights.copy()
    
    # Mock successful find with semantic strategy
    mock_element = Mock()
    mock_page.locator.return_value.count = AsyncMock(return_value=1)
    mock_page.locator.return_value.first = mock_element
    
    result = await universal_locator.find_element(mock_page, sample_context)
    
    # Weights should be updated
    weight_key = f"{sample_context.platform.value}:semantic_intent"
    if weight_key in initial_weights:
        assert universal_locator.strategy_weights[weight_key] >= initial_weights[weight_key]


def test_cache_key_generation(universal_locator, sample_context):
    """Test that cache keys are generated consistently."""
    key1 = universal_locator._generate_cache_key(sample_context)
    key2 = universal_locator._generate_cache_key(sample_context)
    
    assert key1 == key2
    assert key1.startswith("helix:element:")
    assert len(key1.split(":")[-1]) == 16  # MD5 hash should be 16 chars


@pytest.mark.asyncio
async def test_parallel_layer_execution(universal_locator, mock_page, sample_context):
    """Test that layers execute in parallel for performance."""
    start_time = asyncio.get_event_loop().time()
    
    await universal_locator._generate_all_strategies(mock_page, sample_context, 2000)
    
    end_time = asyncio.get_event_loop().time()
    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    # Should complete in reasonable time (parallel execution)
    assert execution_time < 1000  # Less than 1 second for mock operations


def test_ml_fusion_strategy_ranking(universal_locator, sample_context):
    """Test that ML fusion properly ranks strategies."""
    # Create mock strategies with different confidences
    strategies = [
        Mock(strategy_type=StrategyType.SEMANTIC_INTENT, confidence=0.6, metadata={}),
        Mock(strategy_type=StrategyType.VISUAL_FINGERPRINT, confidence=0.8, metadata={}),
        Mock(strategy_type=StrategyType.SEMANTIC_INTENT, confidence=0.7, metadata={})
    ]
    
    ranked = universal_locator._apply_ml_fusion(strategies, sample_context)
    
    # Should be sorted by weighted confidence (highest first)
    assert len(ranked) == 3
    assert ranked[0].confidence >= ranked[1].confidence >= ranked[2].confidence


@pytest.mark.asyncio
async def test_visual_fallback_execution(universal_locator, mock_page):
    """Test visual fallback click functionality."""
    strategies = [
        Mock(selector="visual:click(100,50)", confidence=0.7, 
             strategy_type=StrategyType.VISUAL_FINGERPRINT, metadata={})
    ]
    
    # Mock mouse click
    mock_page.mouse = Mock()
    mock_page.mouse.click = AsyncMock()
    
    result = await universal_locator._try_visual_fallback(mock_page, strategies)
    
    assert result.found is True
    mock_page.mouse.click.assert_called_once_with(100, 50)


def test_performance_metrics_tracking(universal_locator):
    """Test that performance metrics are properly tracked."""
    initial_stats = universal_locator.get_stats()
    
    # Simulate some operations
    universal_locator.stats["total_requests"] = 10
    universal_locator.stats["successful_identifications"] = 9
    universal_locator.stats["cache_hits"] = 3
    universal_locator.stats["visual_fallbacks"] = 1
    
    stats = universal_locator.get_stats()
    
    assert stats["total_requests"] == 10
    assert stats["overall_success_rate"] == 0.9
    assert stats["cache_hit_rate"] == 0.3
    assert stats["visual_fallback_rate"] == 0.1


@pytest.mark.asyncio
async def test_timeout_handling(universal_locator, mock_page, sample_context):
    """Test that operations respect timeout constraints."""
    # Set very short timeout
    short_timeout = 10  # 10ms
    
    result = await universal_locator.find_element(mock_page, sample_context, short_timeout)
    
    # Should complete within reasonable time even with short timeout
    assert result.time_taken_ms < 2000  # Should not exceed reasonable bounds


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
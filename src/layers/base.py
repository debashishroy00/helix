from abc import ABC, abstractmethod
from typing import List, Optional, Any
import asyncio
from datetime import datetime

from src.models.element import ElementStrategy, ElementContext, StrategyType


class BaseLayer(ABC):
    """
    Abstract base class for all element identification layers.
    Each of the 7 layers must implement this interface.
    
    Patent Note: The specific combination of these 7 layers working together
    provides complete coverage that no subset can achieve.
    """
    
    def __init__(self, layer_type: StrategyType):
        self.layer_type = layer_type
        self.metrics = {
            "total_calls": 0,
            "successful_strategies": 0,
            "average_confidence": 0.0,
            "average_time_ms": 0.0
        }
    
    @abstractmethod
    async def generate_strategies(
        self, 
        page: Any,  # Playwright/Selenium page object
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Generate one or more strategies for finding the element.
        
        Args:
            page: The page object (Playwright Page or Selenium WebDriver)
            context: Context information about what we're looking for
            
        Returns:
            List of strategies, ordered by confidence (highest first)
            
        Patent Note: Each layer uses a fundamentally different approach,
        ensuring coverage when other methods fail.
        """
        pass
    
    async def execute(
        self,
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Wrapper method that tracks metrics and handles errors.
        """
        start_time = datetime.utcnow()
        self.metrics["total_calls"] += 1
        
        try:
            strategies = await self.generate_strategies(page, context)
            
            # Track metrics
            if strategies:
                self.metrics["successful_strategies"] += len(strategies)
                avg_confidence = sum(s.confidence for s in strategies) / len(strategies)
                
                # Update running average
                total = self.metrics["total_calls"]
                self.metrics["average_confidence"] = (
                    (self.metrics["average_confidence"] * (total - 1) + avg_confidence) / total
                )
            
            # Track timing
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics["average_time_ms"] = (
                (self.metrics["average_time_ms"] * (self.metrics["total_calls"] - 1) + elapsed_ms) 
                / self.metrics["total_calls"]
            )
            
            return strategies
            
        except Exception as e:
            # Log error but don't crash - other layers may succeed
            print(f"Error in {self.layer_type.value}: {str(e)}")
            return []
    
    def get_metrics(self) -> dict:
        """Return performance metrics for this layer."""
        return {
            "layer": self.layer_type.value,
            **self.metrics
        }


class AsyncLayerExecutor:
    """
    Executes multiple layers in parallel for performance.
    Critical for achieving <2 second response time target.
    """
    
    @staticmethod
    async def execute_layers(
        layers: List[BaseLayer],
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Execute multiple layers in parallel and collect all strategies.
        
        Patent Note: Parallel execution is key to performance while
        maintaining the independence of each layer's approach.
        """
        # Create tasks for all layers
        tasks = [
            layer.execute(page, context)
            for layer in layers
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results, handling any exceptions
        all_strategies = []
        for result in results:
            if isinstance(result, list):
                all_strategies.extend(result)
            elif isinstance(result, Exception):
                print(f"Layer execution error: {result}")
        
        # Sort by confidence (highest first)
        all_strategies.sort(key=lambda s: s.confidence, reverse=True)
        
        return all_strategies
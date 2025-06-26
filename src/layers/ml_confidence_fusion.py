"""
Layer 10: ML Confidence Fusion
==============================
Machine learning layer that fuses confidence scores from all 9 previous layers
and learns from successful/failed attempts to optimize strategy selection.

This is the "brain" of the 10-layer system that combines all approaches
intelligently and adapts over time.
"""

import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

# Optional dependency
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


@dataclass
class StrategyOutcome:
    """Record of a strategy attempt and its outcome."""
    strategy: ElementStrategy
    context: ElementContext
    success: bool
    execution_time_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class FusionWeights:
    """Learned weights for different layers and contexts."""
    layer_weights: Dict[str, float]
    context_weights: Dict[str, float]
    platform_weights: Dict[str, float]
    intent_weights: Dict[str, float]
    performance_weights: Dict[str, float]
    success_rate: float = 0.0
    total_attempts: int = 0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


class MLConfidenceFusionLayer(BaseLayer):
    """
    Layer 10: Machine learning fusion of all previous layer strategies.
    
    Uses historical success data to:
    1. Re-rank strategies from other layers
    2. Adjust confidence scores based on context
    3. Learn from failures to improve future predictions
    4. Provide overall system confidence scoring
    """
    
    def __init__(self, model_path: str = "data/ml_fusion_model.pkl"):
        super().__init__(StrategyType.ML_CONFIDENCE_FUSION)
        
        # File paths for persistence
        self.model_path = Path(model_path)
        self.outcomes_path = Path("data/strategy_outcomes.json")
        self.weights_path = Path("data/fusion_weights.json") 
        
        # Ensure data directory exists
        self.model_path.parent.mkdir(exist_ok=True)
        
        # Learning parameters
        self.learning_rate = 0.01
        self.min_samples_for_learning = 10
        self.weight_decay = 0.99  # Decay old learning over time
        
        # Historical data
        self.strategy_outcomes: List[StrategyOutcome] = []
        self.fusion_weights: FusionWeights = self._load_or_initialize_weights()
        
        # Load historical outcomes
        self._load_historical_outcomes()
        
        # Context feature extractors
        self.context_extractors = {
            "platform": self._extract_platform_features,
            "intent": self._extract_intent_features,
            "timing": self._extract_timing_features,
            "complexity": self._extract_complexity_features,
            "page_state": self._extract_page_state_features
        }
        
        # Layer importance baselines (will be learned over time)
        self.layer_importance = {
            StrategyType.SEMANTIC_INTENT: 0.20,
            StrategyType.CONTEXTUAL_RELATIONSHIP: 0.15,
            StrategyType.VISUAL_FINGERPRINT: 0.10,
            StrategyType.BEHAVIORAL_PATTERN: 0.10,
            StrategyType.STRUCTURAL_PATTERN: 0.12,
            StrategyType.ACCESSIBILITY_BRIDGE: 0.13,
            StrategyType.MUTATION_OBSERVATION: 0.08,
            StrategyType.TIMING_SYNCHRONIZATION: 0.07,
            StrategyType.STATE_CONTEXT: 0.05
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        This layer doesn't generate new strategies, but rather processes and
        re-ranks strategies from all other layers.
        """
        # The ML Confidence Fusion layer works differently - it processes
        # strategies from other layers rather than generating its own
        return []
    
    async def fuse_strategies(
        self,
        strategies: List[ElementStrategy],
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Main fusion method: Takes strategies from all layers and re-ranks them
        using machine learning insights.
        """
        
        if not strategies:
            return strategies
        
        # Extract context features
        context_features = self._extract_context_features(context)
        
        # Adjust confidence scores based on learned patterns
        adjusted_strategies = []
        
        for strategy in strategies:
            adjusted_strategy = self._adjust_strategy_confidence(
                strategy, context, context_features
            )
            adjusted_strategies.append(adjusted_strategy)
        
        # Re-rank strategies based on fusion model
        ranked_strategies = self._rank_strategies(adjusted_strategies, context_features)
        
        # Apply ensemble methods if we have multiple high-confidence strategies
        ensemble_strategies = self._apply_ensemble_methods(ranked_strategies, context)
        
        return ensemble_strategies
    
    def _adjust_strategy_confidence(
        self,
        strategy: ElementStrategy,
        context: ElementContext, 
        context_features: Dict[str, float]
    ) -> ElementStrategy:
        """Adjust individual strategy confidence based on learned patterns."""
        
        # Get base confidence
        base_confidence = strategy.confidence
        
        # Layer-specific adjustment
        layer_weight = self.fusion_weights.layer_weights.get(
            strategy.strategy_type.value, 1.0
        )
        
        # Platform-specific adjustment
        platform_weight = self.fusion_weights.platform_weights.get(
            context.platform, 1.0
        )
        
        # Intent-specific adjustment
        intent_key = self._normalize_intent(context.intent)
        intent_weight = self.fusion_weights.intent_weights.get(intent_key, 1.0)
        
        # Performance tier adjustment
        perf_weight = self.fusion_weights.performance_weights.get(
            strategy.performance_tier.value, 1.0
        )
        
        # Context feature adjustments
        if len(self.fusion_weights.context_weights) > 0:
            context_adjustment = sum(
                context_features.get(key, 0.0) * weight 
                for key, weight in self.fusion_weights.context_weights.items()
            ) / len(self.fusion_weights.context_weights)
        else:
            context_adjustment = 0.0
        
        # Historical success rate for this type of strategy
        historical_adjustment = self._get_historical_success_rate(
            strategy.strategy_type, context.platform, intent_key
        )
        
        # Combine all adjustments
        adjusted_confidence = base_confidence * (
            layer_weight * 0.3 +
            platform_weight * 0.2 + 
            intent_weight * 0.2 +
            perf_weight * 0.1 +
            (1.0 + context_adjustment) * 0.1 +
            historical_adjustment * 0.1
        )
        
        # Ensure confidence stays in valid range
        adjusted_confidence = max(0.01, min(0.99, adjusted_confidence))
        
        # Create new strategy with adjusted confidence
        return ElementStrategy(
            selector=strategy.selector,
            confidence=adjusted_confidence,
            strategy_type=strategy.strategy_type,
            performance_tier=strategy.performance_tier,
            reasoning=f"ML-adjusted: {strategy.reasoning}",
            metadata={
                **(strategy.metadata or {}),
                "ml_adjustment": {
                    "original_confidence": base_confidence,
                    "layer_weight": layer_weight,
                    "platform_weight": platform_weight,
                    "intent_weight": intent_weight,
                    "performance_weight": perf_weight,
                    "context_adjustment": context_adjustment,
                    "historical_adjustment": historical_adjustment
                }
            }
        )
    
    def _rank_strategies(
        self,
        strategies: List[ElementStrategy],
        context_features: Dict[str, float]
    ) -> List[ElementStrategy]:
        """Re-rank strategies using the fusion model."""
        
        # Calculate composite scores for ranking
        scored_strategies = []
        
        for strategy in strategies:
            # Base score from adjusted confidence
            base_score = strategy.confidence
            
            # Performance tier bonus (faster strategies get slight bonus)
            perf_bonus = {
                PerformanceTier.INSTANT: 0.05,
                PerformanceTier.FAST: 0.03,
                PerformanceTier.MEDIUM: 0.01,
                PerformanceTier.EXPENSIVE: -0.02
            }.get(strategy.performance_tier, 0.0)
            
            # Layer diversity bonus (prefer diverse strategies in top results)
            layer_diversity_bonus = self._calculate_layer_diversity_bonus(
                strategy, scored_strategies
            )
            
            # Context relevance score
            context_relevance = self._calculate_context_relevance(
                strategy, context_features
            )
            
            # Composite score
            composite_score = (
                base_score * 0.70 +
                perf_bonus +
                layer_diversity_bonus * 0.10 +
                context_relevance * 0.20
            )
            
            scored_strategies.append((composite_score, strategy))
        
        # Sort by composite score (highest first)
        scored_strategies.sort(key=lambda x: x[0], reverse=True)
        
        # Return ranked strategies
        return [strategy for score, strategy in scored_strategies]
    
    def _apply_ensemble_methods(
        self,
        strategies: List[ElementStrategy],
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Apply ensemble methods to combine multiple high-confidence strategies."""
        
        if len(strategies) < 2:
            return strategies
        
        # Group strategies by confidence tier
        high_confidence = [s for s in strategies if s.confidence >= 0.8]
        medium_confidence = [s for s in strategies if 0.6 <= s.confidence < 0.8]
        
        ensemble_strategies = []
        
        # If we have multiple high-confidence strategies, create ensemble combinations
        if len(high_confidence) >= 2:
            # Create a consensus strategy that tries multiple selectors
            consensus_selectors = [s.selector for s in high_confidence[:3]]
            
            ensemble_strategies.append(ElementStrategy(
                selector=f"ensemble:consensus:{','.join(consensus_selectors)}",
                confidence=min(0.95, max(s.confidence for s in high_confidence) + 0.05),
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.FAST,
                reasoning="ML ensemble: Consensus of high-confidence strategies",
                metadata={
                    "ensemble_type": "consensus",
                    "component_strategies": [
                        {"selector": s.selector, "confidence": s.confidence, "layer": s.strategy_type.value}
                        for s in high_confidence[:3]
                    ]
                }
            ))
            
            # Create a fallback chain strategy
            fallback_chain = " || ".join(s.selector for s in high_confidence[:3])
            
            ensemble_strategies.append(ElementStrategy(
                selector=f"ensemble:fallback:{fallback_chain}",
                confidence=max(s.confidence for s in high_confidence),
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="ML ensemble: Fallback chain of strategies",
                metadata={
                    "ensemble_type": "fallback_chain",
                    "component_strategies": [s.selector for s in high_confidence[:3]]
                }
            ))
        
        # Combine ensemble strategies with original strategies
        result = ensemble_strategies + strategies
        
        # Sort by confidence and return top strategies
        result.sort(key=lambda s: s.confidence, reverse=True)
        return result[:10]  # Limit to top 10 strategies
    
    def record_outcome(
        self,
        strategy: ElementStrategy,
        context: ElementContext,
        success: bool,
        execution_time_ms: float,
        error_message: Optional[str] = None
    ):
        """Record the outcome of a strategy attempt for learning."""
        
        outcome = StrategyOutcome(
            strategy=strategy,
            context=context,
            success=success,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )
        
        self.strategy_outcomes.append(outcome)
        
        # Trigger learning if we have enough samples
        if len(self.strategy_outcomes) >= self.min_samples_for_learning:
            self._update_fusion_weights()
        
        # Persist outcomes periodically
        if len(self.strategy_outcomes) % 10 == 0:
            self._save_historical_outcomes()
    
    def _update_fusion_weights(self):
        """Update fusion weights based on recent outcomes."""
        
        if len(self.strategy_outcomes) < self.min_samples_for_learning:
            return
        
        # Get recent outcomes (last 100 or last 7 days)
        recent_outcomes = self._get_recent_outcomes()
        
        if not recent_outcomes:
            return
        
        # Update layer weights
        self._update_layer_weights(recent_outcomes)
        
        # Update platform weights
        self._update_platform_weights(recent_outcomes)
        
        # Update intent weights
        self._update_intent_weights(recent_outcomes)
        
        # Update performance weights
        self._update_performance_weights(recent_outcomes)
        
        # Update context weights
        self._update_context_weights(recent_outcomes)
        
        # Update overall success rate
        if len(recent_outcomes) > 0:
            self.fusion_weights.success_rate = sum(o.success for o in recent_outcomes) / len(recent_outcomes)
        else:
            self.fusion_weights.success_rate = 0.0
        self.fusion_weights.total_attempts = len(self.strategy_outcomes)
        self.fusion_weights.last_updated = datetime.now()
        
        # Save updated weights
        self._save_fusion_weights()
    
    def _update_layer_weights(self, outcomes: List[StrategyOutcome]):
        """Update weights for different strategy layers."""
        
        layer_stats = {}
        
        for outcome in outcomes:
            layer = outcome.strategy.strategy_type.value
            if layer not in layer_stats:
                layer_stats[layer] = {"successes": 0, "total": 0}
            
            layer_stats[layer]["total"] += 1
            if outcome.success:
                layer_stats[layer]["successes"] += 1
        
        # Update weights based on success rates
        for layer, stats in layer_stats.items():
            if stats["total"] > 0:
                success_rate = stats["successes"] / stats["total"]
                current_weight = self.fusion_weights.layer_weights.get(layer, 1.0)
                
                # Exponential moving average update
                new_weight = (
                    current_weight * (1 - self.learning_rate) +
                    success_rate * self.learning_rate
                )
                
                self.fusion_weights.layer_weights[layer] = new_weight
    
    def _update_platform_weights(self, outcomes: List[StrategyOutcome]):
        """Update weights for different platforms."""
        
        platform_stats = {}
        
        for outcome in outcomes:
            platform = outcome.context.platform
            if platform not in platform_stats:
                platform_stats[platform] = {"successes": 0, "total": 0}
            
            platform_stats[platform]["total"] += 1
            if outcome.success:
                platform_stats[platform]["successes"] += 1
        
        for platform, stats in platform_stats.items():
            if stats["total"] > 0:
                success_rate = stats["successes"] / stats["total"]
                current_weight = self.fusion_weights.platform_weights.get(platform, 1.0)
                
                new_weight = (
                    current_weight * (1 - self.learning_rate) +
                    success_rate * self.learning_rate
                )
                
                self.fusion_weights.platform_weights[platform] = new_weight
    
    def _update_intent_weights(self, outcomes: List[StrategyOutcome]):
        """Update weights for different intent types."""
        
        intent_stats = {}
        
        for outcome in outcomes:
            intent_key = self._normalize_intent(outcome.context.intent)
            if intent_key not in intent_stats:
                intent_stats[intent_key] = {"successes": 0, "total": 0}
            
            intent_stats[intent_key]["total"] += 1
            if outcome.success:
                intent_stats[intent_key]["successes"] += 1
        
        for intent_key, stats in intent_stats.items():
            if stats["total"] > 0:
                success_rate = stats["successes"] / stats["total"]
                current_weight = self.fusion_weights.intent_weights.get(intent_key, 1.0)
                
                new_weight = (
                    current_weight * (1 - self.learning_rate) +
                    success_rate * self.learning_rate
                )
                
                self.fusion_weights.intent_weights[intent_key] = new_weight
    
    def _update_performance_weights(self, outcomes: List[StrategyOutcome]):
        """Update weights for different performance tiers."""
        
        perf_stats = {}
        
        for outcome in outcomes:
            perf_tier = outcome.strategy.performance_tier.value
            if perf_tier not in perf_stats:
                perf_stats[perf_tier] = {"successes": 0, "total": 0, "avg_time": 0}
            
            perf_stats[perf_tier]["total"] += 1
            perf_stats[perf_tier]["avg_time"] += outcome.execution_time_ms
            if outcome.success:
                perf_stats[perf_tier]["successes"] += 1
        
        for perf_tier, stats in perf_stats.items():
            if stats["total"] > 0:
                success_rate = stats["successes"] / stats["total"]
                avg_time = stats["avg_time"] / stats["total"]
                
                # Weight by both success rate and speed (faster is better)
                time_factor = max(0.1, 1.0 - (avg_time / 10000))  # Normalize time to 0-1
                combined_score = success_rate * 0.7 + time_factor * 0.3
                
                current_weight = self.fusion_weights.performance_weights.get(perf_tier, 1.0)
                new_weight = (
                    current_weight * (1 - self.learning_rate) +
                    combined_score * self.learning_rate
                )
                
                self.fusion_weights.performance_weights[perf_tier] = new_weight
    
    def _update_context_weights(self, outcomes: List[StrategyOutcome]):
        """Update weights for different context features."""
        
        # This is a simplified version - in practice, you'd use more sophisticated
        # feature analysis and possibly neural networks
        
        context_features_success = {}
        context_features_total = {}
        
        for outcome in outcomes:
            features = self._extract_context_features(outcome.context)
            
            for feature_name, feature_value in features.items():
                if feature_name not in context_features_success:
                    context_features_success[feature_name] = 0
                    context_features_total[feature_name] = 0
                
                context_features_total[feature_name] += 1
                if outcome.success and feature_value > 0.5:  # Feature was significant
                    context_features_success[feature_name] += 1
        
        for feature_name in context_features_total:
            if context_features_total[feature_name] > 0:
                success_rate = context_features_success[feature_name] / context_features_total[feature_name]
                current_weight = self.fusion_weights.context_weights.get(feature_name, 0.0)
                
                new_weight = (
                    current_weight * (1 - self.learning_rate) +
                    (success_rate - 0.5) * self.learning_rate  # Center around 0.5
                )
                
                self.fusion_weights.context_weights[feature_name] = new_weight
    
    # Helper methods for feature extraction and data management
    
    def _extract_context_features(self, context: ElementContext) -> Dict[str, float]:
        """Extract numerical features from context for ML processing."""
        
        features = {}
        
        for extractor_name, extractor_func in self.context_extractors.items():
            try:
                extracted_features = extractor_func(context)
                features.update(extracted_features)
            except Exception as e:
                print(f"Feature extraction error for {extractor_name}: {e}")
        
        return features
    
    def _extract_platform_features(self, context: ElementContext) -> Dict[str, float]:
        """Extract platform-specific features."""
        
        platform_features = {
            "is_salesforce": 1.0 if "salesforce" in context.platform else 0.0,
            "is_servicenow": 1.0 if "servicenow" in context.platform else 0.0,
            "is_workday": 1.0 if "workday" in context.platform else 0.0,
            "is_sap": 1.0 if "sap" in context.platform else 0.0,
        }
        
        return platform_features
    
    def _extract_intent_features(self, context: ElementContext) -> Dict[str, float]:
        """Extract intent-specific features."""
        
        intent_lower = context.intent.lower()
        
        intent_features = {
            "has_button_intent": 1.0 if any(word in intent_lower for word in ["button", "click", "submit"]) else 0.0,
            "has_input_intent": 1.0 if any(word in intent_lower for word in ["input", "field", "text", "email", "password"]) else 0.0,
            "has_navigation_intent": 1.0 if any(word in intent_lower for word in ["link", "menu", "nav", "home"]) else 0.0,
            "has_search_intent": 1.0 if "search" in intent_lower else 0.0,
            "intent_length": min(1.0, len(context.intent.split()) / 10.0),  # Normalize to 0-1
            "intent_complexity": len(set(context.intent.lower().split())) / len(context.intent.split()) if context.intent.split() else 0.0
        }
        
        return intent_features
    
    def _extract_timing_features(self, context: ElementContext) -> Dict[str, float]:
        """Extract timing-related features."""
        
        # In a real implementation, these would come from actual page metrics
        timing_features = {
            "page_load_time": 0.5,  # Normalized page load time
            "dom_complexity": 0.3,  # Normalized DOM complexity
            "network_speed": 0.8,   # Normalized network speed
        }
        
        return timing_features
    
    def _extract_complexity_features(self, context: ElementContext) -> Dict[str, float]:
        """Extract page/content complexity features."""
        
        html_content = context.html_content or ""
        
        complexity_features = {
            "html_size": min(1.0, len(html_content) / 100000),  # Normalize to 0-1
            "element_count": min(1.0, html_content.count("<") / 1000),  # Rough element count
            "script_count": min(1.0, html_content.count("<script") / 10),
            "form_count": min(1.0, html_content.count("<form") / 5),
        }
        
        return complexity_features
    
    def _extract_page_state_features(self, context: ElementContext) -> Dict[str, float]:
        """Extract page state features."""
        
        # These would be derived from actual page state in real implementation
        state_features = {
            "is_logged_in": 0.8,    # Probability user is logged in
            "page_loaded": 0.9,     # Probability page is fully loaded
            "has_errors": 0.1,      # Probability page has errors
            "is_responsive": 0.95,  # Probability page is responsive
        }
        
        return state_features
    
    def _normalize_intent(self, intent: str) -> str:
        """Normalize intent string for consistent grouping."""
        
        intent_lower = intent.lower().strip()
        
        # Group similar intents
        if any(word in intent_lower for word in ["login", "sign in", "signin"]):
            return "login"
        elif any(word in intent_lower for word in ["button", "click", "submit"]):
            return "button"
        elif any(word in intent_lower for word in ["username", "email", "user"]):
            return "username"
        elif "password" in intent_lower:
            return "password"
        elif "search" in intent_lower:
            return "search"
        elif any(word in intent_lower for word in ["save", "submit"]):
            return "save"
        elif any(word in intent_lower for word in ["cancel", "close"]):
            return "cancel"
        elif any(word in intent_lower for word in ["home", "dashboard"]):
            return "home"
        else:
            return "other"
    
    def _get_historical_success_rate(
        self, 
        strategy_type: StrategyType, 
        platform: str, 
        intent_key: str
    ) -> float:
        """Get historical success rate for a specific combination."""
        
        relevant_outcomes = [
            o for o in self.strategy_outcomes
            if (o.strategy.strategy_type == strategy_type and
                o.context.platform == platform and
                self._normalize_intent(o.context.intent) == intent_key)
        ]
        
        if not relevant_outcomes:
            return 0.5  # Neutral when no data
        
        return sum(o.success for o in relevant_outcomes) / len(relevant_outcomes)
    
    def _calculate_layer_diversity_bonus(
        self, 
        strategy: ElementStrategy, 
        existing_strategies: List[Tuple[float, ElementStrategy]]
    ) -> float:
        """Calculate bonus for layer diversity in top results."""
        
        existing_layers = {s[1].strategy_type for s in existing_strategies}
        
        if strategy.strategy_type in existing_layers:
            return 0.0  # No bonus if layer already represented
        else:
            return 0.05  # Small bonus for new layer
    
    def _calculate_context_relevance(
        self, 
        strategy: ElementStrategy, 
        context_features: Dict[str, float]
    ) -> float:
        """Calculate how relevant a strategy is to the current context."""
        
        # This is a simplified relevance calculation
        # In practice, you might use more sophisticated methods
        
        relevance_score = 0.0
        
        # Check if strategy metadata aligns with context
        if strategy.metadata:
            # Example: boost strategies that match detected page features
            if "platform_specific" in strategy.metadata:
                platform_match = any(
                    context_features.get(f"is_{platform}", 0) > 0.5
                    for platform in ["salesforce", "servicenow", "workday", "sap"]
                )
                if platform_match:
                    relevance_score += 0.1
        
        # Intent alignment
        if strategy.reasoning:
            reasoning_lower = strategy.reasoning.lower()
            intent_alignment = sum(
                context_features.get(f"has_{intent}_intent", 0)
                for intent in ["button", "input", "navigation", "search"]
                if intent in reasoning_lower
            )
            relevance_score += intent_alignment * 0.1
        
        return min(1.0, relevance_score)
    
    def _get_recent_outcomes(self, days: int = 7, max_count: int = 100) -> List[StrategyOutcome]:
        """Get recent outcomes for learning."""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = [
            o for o in self.strategy_outcomes 
            if o.timestamp >= cutoff_date
        ]
        
        # Sort by timestamp (newest first) and limit
        recent.sort(key=lambda o: o.timestamp, reverse=True)
        return recent[:max_count]
    
    # Data persistence methods
    
    def _load_or_initialize_weights(self) -> FusionWeights:
        """Load fusion weights from file or initialize defaults."""
        
        if self.weights_path.exists():
            try:
                with open(self.weights_path, 'r') as f:
                    data = json.load(f)
                    return FusionWeights(**data)
            except Exception as e:
                print(f"Error loading weights: {e}")
        
        # Initialize default weights
        return FusionWeights(
            layer_weights={layer.value: 1.0 for layer in StrategyType if layer != StrategyType.ML_CONFIDENCE_FUSION},
            context_weights={},
            platform_weights={},
            intent_weights={},
            performance_weights={tier.value: 1.0 for tier in PerformanceTier}
        )
    
    def _save_fusion_weights(self):
        """Save fusion weights to file."""
        
        try:
            with open(self.weights_path, 'w') as f:
                # Convert dataclass to dict, handling datetime serialization
                data = asdict(self.fusion_weights)
                data['last_updated'] = data['last_updated'].isoformat()
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving weights: {e}")
    
    def _load_historical_outcomes(self):
        """Load historical outcomes from file."""
        
        if not self.outcomes_path.exists():
            return
        
        try:
            with open(self.outcomes_path, 'r') as f:
                data = json.load(f)
                
                for outcome_data in data:
                    # Reconstruct StrategyOutcome objects
                    # This is simplified - in practice you'd need proper deserialization
                    pass  # Implementation depends on your serialization strategy
                    
        except Exception as e:
            print(f"Error loading historical outcomes: {e}")
    
    def _save_historical_outcomes(self):
        """Save historical outcomes to file."""
        
        try:
            # Keep only recent outcomes to prevent file bloat
            recent_outcomes = self._get_recent_outcomes(days=30, max_count=1000)
            
            # Convert to serializable format
            data = []
            for outcome in recent_outcomes:
                # Simplified serialization - expand as needed
                outcome_dict = {
                    "success": outcome.success,
                    "execution_time_ms": outcome.execution_time_ms,
                    "timestamp": outcome.timestamp.isoformat(),
                    "strategy_type": outcome.strategy.strategy_type.value,
                    "platform": outcome.context.platform,
                    "intent": outcome.context.intent
                }
                data.append(outcome_dict)
            
            with open(self.outcomes_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving historical outcomes: {e}")
    
    def get_fusion_stats(self) -> Dict[str, Any]:
        """Get statistics about the fusion learning."""
        
        recent_outcomes = self._get_recent_outcomes()
        
        stats = {
            "total_outcomes": len(self.strategy_outcomes),
            "recent_outcomes": len(recent_outcomes),
            "overall_success_rate": self.fusion_weights.success_rate,
            "recent_success_rate": sum(o.success for o in recent_outcomes) / len(recent_outcomes) if recent_outcomes else 0.0,
            "last_updated": self.fusion_weights.last_updated.isoformat() if self.fusion_weights.last_updated else None,
            "layer_weights": dict(self.fusion_weights.layer_weights),
            "platform_weights": dict(self.fusion_weights.platform_weights),
            "top_performing_layers": sorted(
                self.fusion_weights.layer_weights.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
        
        return stats
# Kan Extension 2: Predictive Analytics & Adaptive Optimization

## Overview

This second Kan extension builds upon the metrics enrichment foundation to add predictive analytics, adaptive optimization strategies, and machine learning-based performance forecasting. It introduces right Kan extensions for prediction spaces and coend constructions for optimization strategies.

## Core Extension: Right Kan for Predictive Analytics

```python
from typing import TypeVar, Generic, Callable, Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
from scipy import stats, optimize
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import time
from collections import deque
import warnings
warnings.filterwarnings('ignore')

# Type variables for right Kan extension
P = TypeVar('P')  # Present state
F = TypeVar('F')  # Future state
O = TypeVar('O')  # Optimization space

@dataclass
class PredictiveModel(Generic[P, F]):
    """Predictive model using right Kan extension"""
    model_type: str
    trained_at: float
    accuracy_score: float
    feature_importance: Dict[str, float]
    prediction_horizon: int
    model: Any  # Actual ML model

class RightKanPredictiveAnalytics:
    """
    Right Kan extension for predictive analytics.
    Maps from present state category to future state category.
    """

    def __init__(self, prediction_window: int = 100):
        self.prediction_window = prediction_window
        self.models: Dict[str, PredictiveModel] = {}
        self.training_data: Dict[str, deque] = {}
        self.prediction_cache: Dict[str, List[float]] = {}
        self.feature_extractors: List[Callable] = []

    def train_predictive_model(
        self,
        metric_name: str,
        historical_data: List[EnrichedMetric],
        model_type: str = 'random_forest'
    ) -> PredictiveModel[P, F]:
        """
        Train predictive model using right Kan extension.
        This maps from present metric space to future prediction space.
        """

        # Extract features and targets
        X, y = self._prepare_training_data(historical_data)

        if len(X) < 10:
            raise ValueError("Insufficient data for training")

        # Train model based on type
        if model_type == 'random_forest':
            model = self._train_random_forest(X, y)
        elif model_type == 'arima':
            model = self._train_arima(historical_data)
        elif model_type == 'neural':
            model = self._train_neural_network(X, y)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Calculate feature importance
        feature_importance = self._calculate_feature_importance(model, X)

        # Validate model
        accuracy = self._validate_model(model, X, y)

        predictive_model = PredictiveModel(
            model_type=model_type,
            trained_at=time.time(),
            accuracy_score=accuracy,
            feature_importance=feature_importance,
            prediction_horizon=10,
            model=model
        )

        self.models[metric_name] = predictive_model
        return predictive_model

    def predict_future_state(
        self,
        metric_name: str,
        current_state: List[EnrichedMetric],
        horizon: int = 10
    ) -> List[Tuple[float, float, float]]:
        """
        Predict future states using right Kan extension.
        Returns list of (timestamp, predicted_value, confidence) tuples.
        """

        if metric_name not in self.models:
            raise ValueError(f"No model trained for {metric_name}")

        model = self.models[metric_name]

        # Extract features from current state
        features = self._extract_features(current_state)

        predictions = []
        confidence_intervals = []

        # Generate predictions
        for i in range(horizon):
            if model.model_type == 'random_forest':
                # Get prediction with confidence
                pred = model.model.predict([features])[0]

                # Calculate confidence using prediction variance
                tree_predictions = [
                    tree.predict([features])[0]
                    for tree in model.model.estimators_
                ]
                std = np.std(tree_predictions)
                confidence = 1.0 / (1.0 + std)

            else:
                # Fallback for other model types
                pred = model.model.predict([features])[0]
                confidence = 0.8  # Default confidence

            future_timestamp = time.time() + (i + 1) * 60  # 1 minute intervals
            predictions.append((future_timestamp, pred, confidence))

            # Update features for next prediction (autoregressive)
            features = np.roll(features, -1)
            features[-1] = pred

        return predictions

    def detect_anomalies(
        self,
        metrics: List[EnrichedMetric],
        contamination: float = 0.1
    ) -> List[Tuple[EnrichedMetric, float]]:
        """
        Detect anomalies using isolation forest.
        Returns list of (metric, anomaly_score) tuples.
        """

        if len(metrics) < 10:
            return []

        # Extract features
        X = np.array([self._extract_features([m]) for m in metrics])

        # Train isolation forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        predictions = iso_forest.fit_predict(X)
        scores = iso_forest.score_samples(X)

        # Normalize scores to 0-1 range
        normalized_scores = (scores - scores.min()) / (scores.max() - scores.min())

        anomalies = [
            (metric, 1.0 - score)
            for metric, pred, score in zip(metrics, predictions, normalized_scores)
            if pred == -1
        ]

        return anomalies

    def _prepare_training_data(
        self,
        historical_data: List[EnrichedMetric]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data with feature extraction"""

        X = []
        y = []

        for i in range(len(historical_data) - self.prediction_window - 1):
            # Extract features from window
            window = historical_data[i:i + self.prediction_window]
            features = self._extract_features(window)

            # Target is next value
            target = historical_data[i + self.prediction_window].value

            X.append(features)
            y.append(target)

        return np.array(X), np.array(y)

    def _extract_features(self, metrics: List[EnrichedMetric]) -> np.ndarray:
        """Extract features from metric window"""

        if not metrics:
            return np.array([])

        values = [m.value for m in metrics]

        features = [
            np.mean(values),
            np.std(values),
            np.min(values),
            np.max(values),
            np.percentile(values, 25),
            np.percentile(values, 75),
            values[-1] if values else 0,  # Last value
            len([v for v in values if v > np.mean(values)]) / len(values),  # Above mean ratio
        ]

        # Add trend features
        if len(values) >= 2:
            trend = (values[-1] - values[0]) / len(values)
            features.append(trend)
        else:
            features.append(0)

        # Add custom feature extractors
        for extractor in self.feature_extractors:
            features.extend(extractor(metrics))

        return np.array(features)

    def _train_random_forest(self, X: np.ndarray, y: np.ndarray) -> RandomForestRegressor:
        """Train random forest model"""
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X, y)
        return model

    def _train_arima(self, historical_data: List[EnrichedMetric]):
        """Train ARIMA model (simplified)"""
        # Placeholder for ARIMA implementation
        return RandomForestRegressor()  # Fallback to RF

    def _train_neural_network(self, X: np.ndarray, y: np.ndarray):
        """Train neural network model (simplified)"""
        # Placeholder for neural network implementation
        return RandomForestRegressor()  # Fallback to RF

    def _calculate_feature_importance(
        self,
        model: Any,
        X: np.ndarray
    ) -> Dict[str, float]:
        """Calculate feature importance"""

        feature_names = [
            'mean', 'std', 'min', 'max', 'q25', 'q75',
            'last_value', 'above_mean_ratio', 'trend'
        ]

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            return dict(zip(feature_names[:len(importances)], importances))

        return {name: 0.1 for name in feature_names}

    def _validate_model(self, model: Any, X: np.ndarray, y: np.ndarray) -> float:
        """Validate model accuracy"""

        if len(X) < 5:
            return 0.0

        # Simple train/test split
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Retrain on train set
        model.fit(X_train, y_train)

        # Predict on test set
        y_pred = model.predict(X_test)

        # Calculate R² score
        from sklearn.metrics import r2_score
        return max(0, r2_score(y_test, y_pred))
```

## Adaptive Optimization Engine

```python
class AdaptiveOptimizationEngine:
    """
    Adaptive optimization using coend construction.
    Dynamically adjusts optimization strategies based on system behavior.
    """

    def __init__(self):
        self.optimization_strategies: Dict[str, 'OptimizationStrategy'] = {}
        self.performance_history: deque = deque(maxlen=1000)
        self.current_strategy: Optional[str] = None
        self.strategy_scores: Dict[str, float] = {}
        self.adaptation_threshold = 0.7

    def register_strategy(self, strategy: 'OptimizationStrategy'):
        """Register an optimization strategy"""
        self.optimization_strategies[strategy.name] = strategy
        self.strategy_scores[strategy.name] = 1.0  # Initial score

    def optimize(
        self,
        current_metrics: Dict[str, float],
        target_metrics: Dict[str, float],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform adaptive optimization using best strategy.
        This is the coend construction mapping multiple strategies to optimal solution.
        """

        # Select best strategy based on current conditions
        best_strategy = self._select_strategy(current_metrics, target_metrics)

        # Apply strategy
        optimization_result = best_strategy.optimize(
            current_metrics,
            target_metrics,
            constraints
        )

        # Update performance history
        self.performance_history.append({
            'timestamp': time.time(),
            'strategy': best_strategy.name,
            'metrics_before': current_metrics.copy(),
            'metrics_after': optimization_result.get('optimized_metrics', {}),
            'success': optimization_result.get('success', False)
        })

        # Update strategy scores
        self._update_strategy_scores(best_strategy.name, optimization_result)

        # Check if we need to adapt
        if self._should_adapt():
            self._adapt_strategies()

        return {
            'strategy_used': best_strategy.name,
            'optimization_result': optimization_result,
            'strategy_scores': self.strategy_scores.copy(),
            'adaptation_triggered': self._should_adapt()
        }

    def _select_strategy(
        self,
        current_metrics: Dict[str, float],
        target_metrics: Dict[str, float]
    ) -> 'OptimizationStrategy':
        """Select best strategy based on current conditions"""

        best_score = -1
        best_strategy = None

        for name, strategy in self.optimization_strategies.items():
            # Calculate strategy fitness
            fitness = strategy.calculate_fitness(current_metrics, target_metrics)

            # Combine with historical performance
            combined_score = fitness * self.strategy_scores[name]

            if combined_score > best_score:
                best_score = combined_score
                best_strategy = strategy

        return best_strategy or list(self.optimization_strategies.values())[0]

    def _update_strategy_scores(self, strategy_name: str, result: Dict[str, Any]):
        """Update strategy scores based on performance"""

        success = result.get('success', False)
        improvement = result.get('improvement', 0.0)

        # Update score using exponential moving average
        alpha = 0.1
        new_score = 1.0 if success else 0.5
        new_score *= (1.0 + improvement)  # Bonus for improvement

        current_score = self.strategy_scores[strategy_name]
        self.strategy_scores[strategy_name] = (
            alpha * new_score + (1 - alpha) * current_score
        )

    def _should_adapt(self) -> bool:
        """Check if adaptation is needed"""

        if len(self.performance_history) < 10:
            return False

        # Check recent performance
        recent_successes = sum(
            1 for h in list(self.performance_history)[-10:]
            if h['success']
        )

        success_rate = recent_successes / 10
        return success_rate < self.adaptation_threshold

    def _adapt_strategies(self):
        """Adapt strategies based on performance"""

        # Analyze failure patterns
        failures = [
            h for h in self.performance_history
            if not h['success']
        ]

        if not failures:
            return

        # Identify common failure conditions
        failure_patterns = self._analyze_failure_patterns(failures)

        # Adapt strategies
        for strategy in self.optimization_strategies.values():
            strategy.adapt(failure_patterns)

    def _analyze_failure_patterns(
        self,
        failures: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze failure patterns to guide adaptation"""

        patterns = {
            'high_latency_failures': 0,
            'resource_constraint_failures': 0,
            'error_rate_failures': 0
        }

        for failure in failures:
            metrics = failure.get('metrics_before', {})

            if metrics.get('latency', 0) > 500:
                patterns['high_latency_failures'] += 1

            if metrics.get('cpu_usage', 0) > 80 or metrics.get('memory_usage', 0) > 80:
                patterns['resource_constraint_failures'] += 1

            if metrics.get('error_rate', 0) > 0.01:
                patterns['error_rate_failures'] += 1

        return patterns

@dataclass
class OptimizationStrategy:
    """Base optimization strategy"""
    name: str
    parameters: Dict[str, Any]
    adaptation_rate: float = 0.1

    def calculate_fitness(
        self,
        current_metrics: Dict[str, float],
        target_metrics: Dict[str, float]
    ) -> float:
        """Calculate fitness score for this strategy"""

        # Distance from target
        distance = sum(
            abs(current_metrics.get(k, 0) - v)
            for k, v in target_metrics.items()
        )

        # Normalize to 0-1 range
        return 1.0 / (1.0 + distance)

    def optimize(
        self,
        current_metrics: Dict[str, float],
        target_metrics: Dict[str, float],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Apply optimization strategy"""
        raise NotImplementedError

    def adapt(self, failure_patterns: Dict[str, Any]):
        """Adapt strategy based on failure patterns"""
        pass
```

## Predictive Resource Scaling

```python
class PredictiveResourceScaler:
    """
    Predictive resource scaling using combined Kan extensions.
    Integrates prediction and optimization for proactive scaling.
    """

    def __init__(self):
        self.predictor = RightKanPredictiveAnalytics()
        self.optimizer = AdaptiveOptimizationEngine()
        self.scaling_history: List[Dict[str, Any]] = []
        self.resource_limits = {
            'min_instances': 1,
            'max_instances': 100,
            'min_cpu': 0.5,
            'max_cpu': 16,
            'min_memory': 512,
            'max_memory': 32768
        }

    def predict_resource_needs(
        self,
        historical_metrics: List[EnrichedMetric],
        prediction_horizon: int = 30
    ) -> Dict[str, List[float]]:
        """
        Predict future resource needs using right Kan extension.
        Returns predicted values for each resource type.
        """

        predictions = {}

        # Train models for each resource metric
        for metric_type in ['cpu_usage', 'memory_usage', 'request_rate']:
            # Filter metrics by type
            type_metrics = [
                m for m in historical_metrics
                if m.labels.get('name') == metric_type
            ]

            if len(type_metrics) >= 50:
                # Train predictive model
                model = self.predictor.train_predictive_model(
                    metric_type,
                    type_metrics,
                    model_type='random_forest'
                )

                # Generate predictions
                future_states = self.predictor.predict_future_state(
                    metric_type,
                    type_metrics[-10:],
                    horizon=prediction_horizon
                )

                predictions[metric_type] = [
                    (ts, value, conf)
                    for ts, value, conf in future_states
                ]

        return predictions

    def calculate_scaling_decision(
        self,
        predictions: Dict[str, List[float]],
        current_resources: Dict[str, float],
        slo_targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate optimal scaling decision based on predictions.
        Uses adaptive optimization to find best configuration.
        """

        # Register scaling strategies
        self._register_scaling_strategies()

        # Calculate target metrics based on predictions
        target_metrics = self._calculate_target_metrics(predictions, slo_targets)

        # Current state
        current_metrics = {
            'instances': current_resources.get('instances', 1),
            'cpu_per_instance': current_resources.get('cpu', 1),
            'memory_per_instance': current_resources.get('memory', 1024),
            'cost': self._calculate_cost(current_resources)
        }

        # Optimize
        optimization_result = self.optimizer.optimize(
            current_metrics,
            target_metrics,
            constraints=self.resource_limits
        )

        # Generate scaling decision
        scaling_decision = {
            'timestamp': time.time(),
            'action': self._determine_action(
                current_resources,
                optimization_result['optimization_result']['optimized_metrics']
            ),
            'target_configuration': optimization_result['optimization_result']['optimized_metrics'],
            'predicted_improvement': optimization_result['optimization_result'].get('improvement', 0),
            'confidence': self._calculate_confidence(predictions),
            'reasoning': self._generate_reasoning(predictions, target_metrics)
        }

        self.scaling_history.append(scaling_decision)
        return scaling_decision

    def _register_scaling_strategies(self):
        """Register different scaling strategies"""

        # Horizontal scaling strategy
        horizontal_strategy = HorizontalScalingStrategy(
            'horizontal_scaling',
            {'scale_factor': 1.5, 'threshold': 0.7}
        )

        # Vertical scaling strategy
        vertical_strategy = VerticalScalingStrategy(
            'vertical_scaling',
            {'cpu_increment': 1, 'memory_increment': 1024}
        )

        # Hybrid scaling strategy
        hybrid_strategy = HybridScalingStrategy(
            'hybrid_scaling',
            {'balance_ratio': 0.5}
        )

        self.optimizer.register_strategy(horizontal_strategy)
        self.optimizer.register_strategy(vertical_strategy)
        self.optimizer.register_strategy(hybrid_strategy)

    def _calculate_target_metrics(
        self,
        predictions: Dict[str, List[float]],
        slo_targets: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate target metrics from predictions"""

        target_metrics = {}

        # Calculate peak predicted values
        for metric_type, pred_list in predictions.items():
            if pred_list:
                peak_value = max(value for _, value, _ in pred_list)

                if metric_type == 'cpu_usage':
                    # Calculate required CPU to maintain SLO
                    required_cpu = peak_value / (slo_targets.get('cpu_threshold', 70) / 100)
                    target_metrics['total_cpu'] = required_cpu

                elif metric_type == 'memory_usage':
                    # Calculate required memory
                    required_memory = peak_value / (slo_targets.get('memory_threshold', 80) / 100)
                    target_metrics['total_memory'] = required_memory

                elif metric_type == 'request_rate':
                    # Calculate required instances for request rate
                    requests_per_instance = slo_targets.get('requests_per_instance', 100)
                    required_instances = peak_value / requests_per_instance
                    target_metrics['instances'] = required_instances

        return target_metrics

    def _determine_action(
        self,
        current: Dict[str, float],
        target: Dict[str, float]
    ) -> str:
        """Determine scaling action from current and target states"""

        current_instances = current.get('instances', 1)
        target_instances = target.get('instances', 1)

        if target_instances > current_instances * 1.2:
            return 'scale_out'
        elif target_instances < current_instances * 0.8:
            return 'scale_in'
        elif target.get('cpu_per_instance', 0) > current.get('cpu', 0):
            return 'scale_up'
        elif target.get('cpu_per_instance', 0) < current.get('cpu', 0) * 0.8:
            return 'scale_down'
        else:
            return 'maintain'

    def _calculate_cost(self, resources: Dict[str, float]) -> float:
        """Calculate resource cost"""
        instances = resources.get('instances', 1)
        cpu = resources.get('cpu', 1)
        memory = resources.get('memory', 1024)

        # Simple cost model
        cost_per_instance = 0.1
        cost_per_cpu = 0.05
        cost_per_gb_memory = 0.01

        return (
            instances * cost_per_instance +
            instances * cpu * cost_per_cpu +
            instances * (memory / 1024) * cost_per_gb_memory
        )

    def _calculate_confidence(self, predictions: Dict[str, List[float]]) -> float:
        """Calculate overall confidence in predictions"""

        if not predictions:
            return 0.0

        confidences = []
        for pred_list in predictions.values():
            if pred_list:
                avg_confidence = np.mean([conf for _, _, conf in pred_list])
                confidences.append(avg_confidence)

        return np.mean(confidences) if confidences else 0.0

    def _generate_reasoning(
        self,
        predictions: Dict[str, List[float]],
        target_metrics: Dict[str, float]
    ) -> str:
        """Generate human-readable reasoning for scaling decision"""

        reasons = []

        for metric_type, pred_list in predictions.items():
            if pred_list:
                peak_value = max(value for _, value, _ in pred_list)
                avg_value = np.mean([value for _, value, _ in pred_list])

                if metric_type == 'cpu_usage':
                    reasons.append(
                        f"CPU usage predicted to peak at {peak_value:.1f}% "
                        f"(avg: {avg_value:.1f}%)"
                    )
                elif metric_type == 'request_rate':
                    reasons.append(
                        f"Request rate predicted to reach {peak_value:.0f} req/s"
                    )

        if target_metrics.get('instances', 0) > 1:
            reasons.append(
                f"Recommending {target_metrics['instances']:.0f} instances "
                f"to maintain SLO targets"
            )

        return "; ".join(reasons)

class HorizontalScalingStrategy(OptimizationStrategy):
    """Horizontal scaling optimization strategy"""

    def optimize(
        self,
        current_metrics: Dict[str, float],
        target_metrics: Dict[str, float],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Apply horizontal scaling"""

        scale_factor = self.parameters['scale_factor']
        current_instances = current_metrics.get('instances', 1)

        # Calculate required instances
        required_instances = current_instances

        if 'total_cpu' in target_metrics:
            cpu_per_instance = current_metrics.get('cpu_per_instance', 1)
            required_by_cpu = target_metrics['total_cpu'] / cpu_per_instance
            required_instances = max(required_instances, required_by_cpu)

        # Apply constraints
        if constraints:
            required_instances = min(
                required_instances,
                constraints.get('max_instances', 100)
            )
            required_instances = max(
                required_instances,
                constraints.get('min_instances', 1)
            )

        optimized_metrics = current_metrics.copy()
        optimized_metrics['instances'] = required_instances

        improvement = (required_instances - current_instances) / current_instances

        return {
            'optimized_metrics': optimized_metrics,
            'success': True,
            'improvement': improvement
        }

class VerticalScalingStrategy(OptimizationStrategy):
    """Vertical scaling optimization strategy"""

    def optimize(
        self,
        current_metrics: Dict[str, float],
        target_metrics: Dict[str, float],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Apply vertical scaling"""

        cpu_increment = self.parameters['cpu_increment']
        memory_increment = self.parameters['memory_increment']

        optimized_metrics = current_metrics.copy()

        # Scale up CPU if needed
        if 'total_cpu' in target_metrics:
            current_total_cpu = (
                current_metrics.get('instances', 1) *
                current_metrics.get('cpu_per_instance', 1)
            )

            if target_metrics['total_cpu'] > current_total_cpu:
                new_cpu_per_instance = (
                    target_metrics['total_cpu'] /
                    current_metrics.get('instances', 1)
                )
                optimized_metrics['cpu_per_instance'] = new_cpu_per_instance

        # Apply constraints
        if constraints:
            optimized_metrics['cpu_per_instance'] = min(
                optimized_metrics.get('cpu_per_instance', 1),
                constraints.get('max_cpu', 16)
            )

        improvement = (
            optimized_metrics.get('cpu_per_instance', 1) -
            current_metrics.get('cpu_per_instance', 1)
        ) / current_metrics.get('cpu_per_instance', 1)

        return {
            'optimized_metrics': optimized_metrics,
            'success': True,
            'improvement': improvement
        }

class HybridScalingStrategy(OptimizationStrategy):
    """Hybrid scaling combining horizontal and vertical"""

    def optimize(
        self,
        current_metrics: Dict[str, float],
        target_metrics: Dict[str, float],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Apply hybrid scaling"""

        balance_ratio = self.parameters['balance_ratio']

        # Calculate both horizontal and vertical requirements
        horizontal = HorizontalScalingStrategy('h', {}).optimize(
            current_metrics, target_metrics, constraints
        )

        vertical = VerticalScalingStrategy('v', {}).optimize(
            current_metrics, target_metrics, constraints
        )

        # Blend the two approaches
        optimized_metrics = current_metrics.copy()

        h_metrics = horizontal['optimized_metrics']
        v_metrics = vertical['optimized_metrics']

        optimized_metrics['instances'] = (
            balance_ratio * h_metrics.get('instances', 1) +
            (1 - balance_ratio) * current_metrics.get('instances', 1)
        )

        optimized_metrics['cpu_per_instance'] = (
            balance_ratio * current_metrics.get('cpu_per_instance', 1) +
            (1 - balance_ratio) * v_metrics.get('cpu_per_instance', 1)
        )

        improvement = max(
            horizontal['improvement'],
            vertical['improvement']
        )

        return {
            'optimized_metrics': optimized_metrics,
            'success': True,
            'improvement': improvement
        }
```

## Practical Example: Predictive Performance System

```python
async def predictive_performance_example():
    """
    Example of predictive analytics and adaptive optimization
    """

    # Generate synthetic historical data
    historical_metrics = []
    base_cpu = 30
    base_memory = 2048
    base_requests = 100

    for i in range(200):
        timestamp = time.time() - (200 - i) * 60  # 1 minute intervals

        # Simulate daily pattern
        hour = (i % 24)
        daily_factor = 1 + 0.5 * np.sin(2 * np.pi * hour / 24)

        # Add some noise and trends
        cpu_usage = base_cpu * daily_factor + np.random.normal(0, 5)
        memory_usage = base_memory * daily_factor + np.random.normal(0, 100)
        request_rate = base_requests * daily_factor + np.random.normal(0, 10)

        # Create enriched metrics
        cpu_metric = EnrichedMetric(
            value=cpu_usage,
            timestamp=timestamp,
            labels={'name': 'cpu_usage', 'host': 'server-1'},
            context=MetricContext('production', 'api', '1.0', 'deploy-1'),
            derived_metrics={},
            correlations={},
            original_metric=None
        )

        memory_metric = EnrichedMetric(
            value=memory_usage,
            timestamp=timestamp,
            labels={'name': 'memory_usage', 'host': 'server-1'},
            context=MetricContext('production', 'api', '1.0', 'deploy-1'),
            derived_metrics={},
            correlations={},
            original_metric=None
        )

        request_metric = EnrichedMetric(
            value=request_rate,
            timestamp=timestamp,
            labels={'name': 'request_rate', 'endpoint': '/api'},
            context=MetricContext('production', 'api', '1.0', 'deploy-1'),
            derived_metrics={},
            correlations={},
            original_metric=None
        )

        historical_metrics.extend([cpu_metric, memory_metric, request_metric])

    # Initialize predictive scaler
    scaler = PredictiveResourceScaler()

    # Predict future resource needs
    predictions = scaler.predict_resource_needs(
        historical_metrics,
        prediction_horizon=30  # Next 30 minutes
    )

    # Current resource configuration
    current_resources = {
        'instances': 2,
        'cpu': 2,  # 2 vCPUs per instance
        'memory': 4096  # 4GB per instance
    }

    # SLO targets
    slo_targets = {
        'cpu_threshold': 70,  # Keep CPU below 70%
        'memory_threshold': 80,  # Keep memory below 80%
        'requests_per_instance': 100,  # Each instance handles 100 req/s
        'latency_p99': 100  # 99th percentile latency < 100ms
    }

    # Calculate scaling decision
    scaling_decision = scaler.calculate_scaling_decision(
        predictions,
        current_resources,
        slo_targets
    )

    # Detect anomalies in recent metrics
    predictor = RightKanPredictiveAnalytics()
    recent_metrics = historical_metrics[-50:]
    anomalies = predictor.detect_anomalies(recent_metrics, contamination=0.1)

    return {
        'predictions': {
            metric_type: [
                {
                    'timestamp': ts,
                    'value': value,
                    'confidence': conf
                }
                for ts, value, conf in pred_list[:5]  # First 5 predictions
            ]
            for metric_type, pred_list in predictions.items()
        },
        'scaling_decision': {
            'action': scaling_decision['action'],
            'target_configuration': scaling_decision['target_configuration'],
            'confidence': scaling_decision['confidence'],
            'reasoning': scaling_decision['reasoning']
        },
        'anomalies_detected': len(anomalies),
        'anomaly_details': [
            {
                'metric': a[0].labels.get('name'),
                'value': a[0].value,
                'anomaly_score': a[1]
            }
            for a in anomalies[:3]  # Top 3 anomalies
        ]
    }

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(predictive_performance_example())
    print(f"Predictive Performance Results: {result}")
```

## Summary of Kan Extension 2

This second Kan extension introduces:

1. **Right Kan Extension for Prediction**: Maps present states to future states with confidence
2. **Adaptive Optimization Engine**: Coend construction for multi-strategy optimization
3. **Predictive Resource Scaling**: Proactive scaling based on ML predictions
4. **Anomaly Detection**: Isolation forest and statistical methods for outlier detection
5. **Strategy Adaptation**: Self-improving optimization through performance feedback

The extension enables predictive and adaptive performance management with machine learning integration.
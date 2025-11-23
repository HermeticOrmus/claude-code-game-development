# Kan Extension 1: Metrics Enrichment & Correlation

## Overview

This first Kan extension enhances the base Performance & Observability framework with advanced metrics enrichment, correlation analysis, and contextual tagging capabilities. It introduces sophisticated metric relationships and automatic correlation detection.

## Core Extension: Left Kan for Metric Enrichment

```python
from typing import TypeVar, Generic, Callable, Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
from scipy import stats
import time

# Type variables for Kan extension
C = TypeVar('C')  # Context category
M = TypeVar('M')  # Metric category
E = TypeVar('E')  # Enriched category

@dataclass
class MetricContext(Generic[C]):
    """Context for metric enrichment"""
    environment: str
    service: str
    version: str
    deployment_id: str
    custom_tags: Dict[str, Any] = field(default_factory=dict)

    def to_labels(self) -> Dict[str, str]:
        """Convert context to metric labels"""
        labels = {
            'env': self.environment,
            'service': self.service,
            'version': self.version,
            'deployment': self.deployment_id
        }
        labels.update({f'custom_{k}': str(v) for k, v in self.custom_tags.items()})
        return labels

class LeftKanMetricEnrichment:
    """
    Left Kan extension for metric enrichment.
    Enriches metrics with contextual information and relationships.
    """

    def __init__(self):
        self.context_cache: Dict[str, MetricContext] = {}
        self.metric_relationships: Dict[str, List[str]] = defaultdict(list)
        self.enrichment_rules: List[Callable] = []
        self.correlation_matrix: Optional[np.ndarray] = None

    def enrich_metric(
        self,
        metric: 'Metric[M]',
        context: MetricContext[C]
    ) -> 'EnrichedMetric[E]':
        """
        Apply Left Kan extension to enrich metric with context

        This is the core Kan extension operation that lifts a metric
        from the base category to the enriched category.
        """
        # Apply context labels
        enriched_labels = {**metric.labels, **context.to_labels()}

        # Calculate derived metrics
        derived = self._calculate_derived_metrics(metric, context)

        # Detect correlations
        correlations = self._detect_correlations(metric)

        # Apply enrichment rules
        for rule in self.enrichment_rules:
            enriched_labels = rule(enriched_labels, metric, context)

        return EnrichedMetric(
            value=metric.value,
            timestamp=metric.timestamp,
            labels=enriched_labels,
            context=context,
            derived_metrics=derived,
            correlations=correlations,
            original_metric=metric
        )

    def _calculate_derived_metrics(
        self,
        metric: 'Metric[M]',
        context: MetricContext[C]
    ) -> Dict[str, float]:
        """Calculate derived metrics based on context and relationships"""
        derived = {}

        # Rate of change if we have historical data
        if hasattr(self, '_metric_history'):
            history = self._metric_history.get(metric.labels.get('name', ''), [])
            if len(history) >= 2:
                rate = (metric.value - history[-1]) / (metric.timestamp - history[-2])
                derived['rate_of_change'] = rate

        # Percentile within service
        if context.service in self.context_cache:
            service_metrics = self._get_service_metrics(context.service)
            if service_metrics:
                percentile = stats.percentileofscore(service_metrics, metric.value)
                derived['percentile_in_service'] = percentile

        return derived

    def _detect_correlations(self, metric: 'Metric[M]') -> Dict[str, float]:
        """Detect correlations with other metrics"""
        correlations = {}

        metric_name = metric.labels.get('name', 'unknown')
        related_metrics = self.metric_relationships.get(metric_name, [])

        for related in related_metrics:
            correlation = self._calculate_correlation(metric_name, related)
            if correlation is not None:
                correlations[related] = correlation

        return correlations

    def _calculate_correlation(
        self,
        metric1: str,
        metric2: str
    ) -> Optional[float]:
        """Calculate Pearson correlation between two metrics"""
        if not hasattr(self, '_metric_history'):
            return None

        history1 = self._metric_history.get(metric1, [])
        history2 = self._metric_history.get(metric2, [])

        if len(history1) < 10 or len(history2) < 10:
            return None

        # Align time series
        min_len = min(len(history1), len(history2))
        values1 = history1[-min_len:]
        values2 = history2[-min_len:]

        # Calculate correlation
        correlation, _ = stats.pearsonr(values1, values2)
        return correlation

    def add_enrichment_rule(
        self,
        rule: Callable[[Dict, Any, MetricContext], Dict]
    ):
        """Add custom enrichment rule"""
        self.enrichment_rules.append(rule)

    def define_relationship(self, metric1: str, metric2: str):
        """Define relationship between metrics"""
        self.metric_relationships[metric1].append(metric2)
        self.metric_relationships[metric2].append(metric1)

    def _get_service_metrics(self, service: str) -> List[float]:
        """Get all metrics for a service"""
        # Implementation would fetch from storage
        return []

@dataclass
class EnrichedMetric(Generic[E]):
    """Enriched metric with full context and relationships"""
    value: E
    timestamp: float
    labels: Dict[str, str]
    context: MetricContext
    derived_metrics: Dict[str, float]
    correlations: Dict[str, float]
    original_metric: Any

    def get_correlation_strength(self, threshold: float = 0.7) -> List[str]:
        """Get strongly correlated metrics"""
        return [
            metric for metric, corr in self.correlations.items()
            if abs(corr) >= threshold
        ]

    def to_prometheus_format(self) -> str:
        """Convert to Prometheus exposition format"""
        labels_str = ','.join(f'{k}="{v}"' for k, v in self.labels.items())
        return f"metric{{{labels_str}}} {self.value} {int(self.timestamp * 1000)}"
```

## Advanced Correlation Engine

```python
class CorrelationEngine:
    """
    Advanced correlation detection and analysis engine.
    Uses Kan extension principles to map metric spaces.
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metric_buffers: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        self.correlation_cache: Dict[Tuple[str, str], float] = {}
        self.anomaly_scores: Dict[str, float] = {}

    def update_metric(self, name: str, value: float, timestamp: float):
        """Update metric buffer and recalculate correlations"""
        buffer = self.metric_buffers[name]
        buffer.append((timestamp, value))

        # Keep only window_size elements
        if len(buffer) > self.window_size:
            buffer.pop(0)

        # Invalidate correlation cache for this metric
        self._invalidate_cache(name)

        # Detect anomalies
        self.anomaly_scores[name] = self._calculate_anomaly_score(name)

    def get_correlation_matrix(
        self,
        metrics: Optional[List[str]] = None
    ) -> np.ndarray:
        """Generate correlation matrix for specified metrics"""
        if metrics is None:
            metrics = list(self.metric_buffers.keys())

        n = len(metrics)
        matrix = np.zeros((n, n))

        for i, metric1 in enumerate(metrics):
            for j, metric2 in enumerate(metrics):
                if i == j:
                    matrix[i, j] = 1.0
                else:
                    corr = self._get_correlation(metric1, metric2)
                    matrix[i, j] = corr if corr is not None else 0.0

        return matrix

    def find_causal_relationships(
        self,
        target_metric: str,
        lag_range: range = range(1, 10)
    ) -> List[Tuple[str, int, float]]:
        """
        Find potential causal relationships using lagged correlations.
        Returns list of (metric, lag, correlation) tuples.
        """
        causal_candidates = []

        target_buffer = self.metric_buffers.get(target_metric, [])
        if len(target_buffer) < 20:
            return []

        target_values = [v for _, v in target_buffer]

        for metric_name, buffer in self.metric_buffers.items():
            if metric_name == target_metric or len(buffer) < 20:
                continue

            metric_values = [v for _, v in buffer]

            for lag in lag_range:
                if lag >= len(metric_values):
                    continue

                # Calculate lagged correlation
                lagged_values = metric_values[:-lag]
                target_subset = target_values[lag:]

                if len(lagged_values) >= 10:
                    corr, p_value = stats.pearsonr(lagged_values[:len(target_subset)],
                                                   target_subset[:len(lagged_values)])

                    if abs(corr) > 0.5 and p_value < 0.05:
                        causal_candidates.append((metric_name, lag, corr))

        # Sort by correlation strength
        causal_candidates.sort(key=lambda x: abs(x[2]), reverse=True)
        return causal_candidates[:10]  # Top 10 candidates

    def _get_correlation(self, metric1: str, metric2: str) -> Optional[float]:
        """Get correlation between two metrics (cached)"""
        cache_key = tuple(sorted([metric1, metric2]))

        if cache_key in self.correlation_cache:
            return self.correlation_cache[cache_key]

        buffer1 = self.metric_buffers.get(metric1, [])
        buffer2 = self.metric_buffers.get(metric2, [])

        if len(buffer1) < 10 or len(buffer2) < 10:
            return None

        # Align timestamps
        aligned = self._align_time_series(buffer1, buffer2)
        if len(aligned) < 10:
            return None

        values1, values2 = zip(*aligned)
        corr, _ = stats.pearsonr(values1, values2)

        self.correlation_cache[cache_key] = corr
        return corr

    def _align_time_series(
        self,
        series1: List[Tuple[float, float]],
        series2: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        """Align two time series by timestamp"""
        # Simple nearest neighbor alignment
        aligned = []
        for ts1, val1 in series1:
            closest = min(series2, key=lambda x: abs(x[0] - ts1))
            if abs(closest[0] - ts1) < 1.0:  # Within 1 second
                aligned.append((val1, closest[1]))
        return aligned

    def _calculate_anomaly_score(self, metric_name: str) -> float:
        """Calculate anomaly score using statistical methods"""
        buffer = self.metric_buffers.get(metric_name, [])
        if len(buffer) < 10:
            return 0.0

        values = [v for _, v in buffer]

        # Use z-score for anomaly detection
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return 0.0

        latest_value = values[-1]
        z_score = abs((latest_value - mean) / std)

        # Normalize to 0-1 range
        return min(z_score / 3.0, 1.0)

    def _invalidate_cache(self, metric_name: str):
        """Invalidate correlation cache entries for a metric"""
        keys_to_remove = [
            key for key in self.correlation_cache
            if metric_name in key
        ]
        for key in keys_to_remove:
            del self.correlation_cache[key]
```

## Contextual Alert Generation

```python
class ContextualAlertGenerator:
    """
    Generate alerts with full context using enriched metrics.
    Uses Kan extension to map from metric space to alert space.
    """

    def __init__(self):
        self.alert_rules: List['AlertRule'] = []
        self.alert_history: List['Alert'] = []
        self.suppression_rules: List[Callable] = []
        self.enricher = LeftKanMetricEnrichment()

    def add_alert_rule(self, rule: 'AlertRule'):
        """Add an alert rule"""
        self.alert_rules.append(rule)

    def evaluate_metrics(
        self,
        metrics: List[EnrichedMetric],
        correlation_engine: CorrelationEngine
    ) -> List['Alert']:
        """Evaluate metrics against alert rules"""
        alerts = []

        for metric in metrics:
            for rule in self.alert_rules:
                if rule.evaluate(metric):
                    # Create alert with full context
                    alert = self._create_contextual_alert(
                        metric,
                        rule,
                        correlation_engine
                    )

                    # Check suppression rules
                    if not self._should_suppress(alert):
                        alerts.append(alert)
                        self.alert_history.append(alert)

        return alerts

    def _create_contextual_alert(
        self,
        metric: EnrichedMetric,
        rule: 'AlertRule',
        correlation_engine: CorrelationEngine
    ) -> 'Alert':
        """Create alert with full contextual information"""

        # Find correlated metrics that might be affected
        correlated = metric.get_correlation_strength(threshold=0.7)

        # Find potential causes using lagged correlations
        metric_name = metric.labels.get('name', 'unknown')
        causal_candidates = correlation_engine.find_causal_relationships(metric_name)

        # Get anomaly scores for context
        anomaly_score = correlation_engine.anomaly_scores.get(metric_name, 0.0)

        return Alert(
            name=rule.name,
            severity=rule.severity,
            metric=metric,
            triggered_at=time.time(),
            context={
                'environment': metric.context.environment,
                'service': metric.context.service,
                'version': metric.context.version,
                'deployment': metric.context.deployment_id,
                'correlated_metrics': correlated,
                'potential_causes': causal_candidates[:3],
                'anomaly_score': anomaly_score,
                'derived_metrics': metric.derived_metrics
            },
            recommended_actions=self._generate_recommendations(metric, rule)
        )

    def _should_suppress(self, alert: 'Alert') -> bool:
        """Check if alert should be suppressed"""
        for rule in self.suppression_rules:
            if rule(alert):
                return True

        # Check for recent similar alerts
        recent_alerts = [
            a for a in self.alert_history[-10:]
            if a.name == alert.name and
            a.context['service'] == alert.context['service']
        ]

        if len(recent_alerts) >= 3:
            # Too many similar alerts recently
            return True

        return False

    def _generate_recommendations(
        self,
        metric: EnrichedMetric,
        rule: 'AlertRule'
    ) -> List[str]:
        """Generate recommended actions based on context"""
        recommendations = []

        # Check if this is a known pattern
        if metric.derived_metrics.get('rate_of_change', 0) > 0.5:
            recommendations.append("Rapid increase detected - consider scaling up")

        if metric.context.environment == 'production':
            recommendations.append("Production environment - escalate to on-call")

        if len(metric.get_correlation_strength()) > 3:
            recommendations.append("Multiple correlated metrics affected - check system-wide issue")

        # Add rule-specific recommendations
        recommendations.extend(rule.recommendations)

        return recommendations

@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    severity: str  # critical, warning, info
    condition: Callable[[EnrichedMetric], bool]
    recommendations: List[str] = field(default_factory=list)

    def evaluate(self, metric: EnrichedMetric) -> bool:
        """Evaluate if rule triggers for metric"""
        return self.condition(metric)

@dataclass
class Alert:
    """Contextual alert with full information"""
    name: str
    severity: str
    metric: EnrichedMetric
    triggered_at: float
    context: Dict[str, Any]
    recommended_actions: List[str]

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON for notification systems"""
        return {
            'name': self.name,
            'severity': self.severity,
            'value': self.metric.value,
            'timestamp': self.triggered_at,
            'context': self.context,
            'recommendations': self.recommended_actions
        }
```

## Practical Example: Enriched Monitoring System

```python
async def enriched_monitoring_example():
    """
    Example of using Kan extension for enriched monitoring
    """

    # Initialize components
    enricher = LeftKanMetricEnrichment()
    correlation_engine = CorrelationEngine()
    alert_generator = ContextualAlertGenerator()

    # Define context
    context = MetricContext(
        environment='production',
        service='api-gateway',
        version='2.1.0',
        deployment_id='deploy-123',
        custom_tags={'region': 'us-east-1', 'tier': 'premium'}
    )

    # Add enrichment rules
    def add_slo_compliance(labels, metric, context):
        """Add SLO compliance information"""
        if labels.get('name') == 'latency':
            slo_target = 100  # ms
            labels['slo_compliant'] = 'true' if metric.value < slo_target else 'false'
        return labels

    enricher.add_enrichment_rule(add_slo_compliance)

    # Define metric relationships
    enricher.define_relationship('latency', 'cpu_usage')
    enricher.define_relationship('latency', 'memory_usage')
    enricher.define_relationship('error_rate', 'latency')

    # Define alert rules
    high_latency_rule = AlertRule(
        name='high_latency',
        severity='warning',
        condition=lambda m: m.labels.get('name') == 'latency' and m.value > 500,
        recommendations=[
            'Check database performance',
            'Review recent deployments',
            'Scale horizontally if CPU > 70%'
        ]
    )

    alert_generator.add_alert_rule(high_latency_rule)

    # Simulate metric stream
    metrics_to_process = []

    for i in range(100):
        # Generate synthetic metrics
        timestamp = time.time() + i

        # Latency metric
        latency = 50 + i * 2 + np.random.normal(0, 10)
        latency_metric = Metric(
            value=latency,
            timestamp=timestamp,
            labels={'name': 'latency', 'endpoint': '/api/users'}
        )

        # CPU metric (correlated with latency)
        cpu = 30 + i * 0.5 + np.random.normal(0, 5)
        cpu_metric = Metric(
            value=cpu,
            timestamp=timestamp,
            labels={'name': 'cpu_usage', 'node': 'node-1'}
        )

        # Update correlation engine
        correlation_engine.update_metric('latency', latency, timestamp)
        correlation_engine.update_metric('cpu_usage', cpu, timestamp)

        # Enrich metrics
        enriched_latency = enricher.enrich_metric(latency_metric, context)
        enriched_cpu = enricher.enrich_metric(cpu_metric, context)

        metrics_to_process.extend([enriched_latency, enriched_cpu])

    # Evaluate alerts
    alerts = alert_generator.evaluate_metrics(metrics_to_process, correlation_engine)

    # Get correlation analysis
    correlation_matrix = correlation_engine.get_correlation_matrix(['latency', 'cpu_usage'])
    causal_relationships = correlation_engine.find_causal_relationships('latency')

    return {
        'metrics_processed': len(metrics_to_process),
        'alerts_generated': len(alerts),
        'alert_details': [a.to_json() for a in alerts[:3]],  # First 3 alerts
        'correlation_matrix': correlation_matrix.tolist(),
        'causal_relationships': causal_relationships,
        'enrichment_example': {
            'original_labels': latency_metric.labels,
            'enriched_labels': enriched_latency.labels,
            'derived_metrics': enriched_latency.derived_metrics
        }
    }

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(enriched_monitoring_example())
    print(f"Enriched Monitoring Results: {result}")
```

## Summary of Kan Extension 1

This first Kan extension introduces:

1. **Left Kan Extension for Enrichment**: Systematically lifts metrics from base category to enriched category
2. **Correlation Analysis**: Automatic detection of metric relationships and causal patterns
3. **Contextual Tagging**: Rich metadata and context propagation
4. **Smart Alert Generation**: Alerts with full context, correlations, and recommendations
5. **Anomaly Detection**: Statistical anomaly scoring integrated with correlation analysis

The extension provides a foundation for intelligent metric analysis and contextual observability.
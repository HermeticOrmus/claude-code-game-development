# Kan Extension 3: Distributed Tracing & Complex System Observability

## Overview

This third Kan extension advances the framework with sophisticated distributed tracing capabilities, service mesh observability, and complex system analysis. It introduces profunctor-based trace composition and end-based distributed aggregation patterns.

## Core Extension: Profunctor-Based Distributed Tracing

```python
from typing import TypeVar, Generic, Callable, Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import networkx as nx
import numpy as np
from collections import defaultdict, deque
import hashlib
import json
import time
import asyncio
from enum import Enum

# Type variables for profunctor tracing
S = TypeVar('S')  # Source service
T = TypeVar('T')  # Target service
Tr = TypeVar('Tr')  # Trace type

class SpanKind(Enum):
    """OpenTelemetry-compatible span kinds"""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"

@dataclass
class DistributedSpan(Generic[S, T]):
    """
    Distributed span representing profunctor morphism S -> T.
    Models the trace flow between services.
    """
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    service_name: str
    operation_name: str
    start_time: float
    end_time: Optional[float]
    kind: SpanKind
    attributes: Dict[str, Any]
    events: List[Tuple[float, str, Dict]]
    links: List[str]
    status: str = "ok"
    error: Optional[str] = None

    def duration_ms(self) -> float:
        """Calculate span duration in milliseconds"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add event to span"""
        self.events.append((time.time(), name, attributes or {}))

    def set_error(self, error: str):
        """Set error on span"""
        self.status = "error"
        self.error = error
        self.add_event("error", {"message": error})

class ProfunctorTracer:
    """
    Profunctor-based distributed tracer.
    Implements contravariant-covariant trace composition.
    """

    def __init__(self):
        self.traces: Dict[str, List[DistributedSpan]] = defaultdict(list)
        self.active_spans: Dict[str, DistributedSpan] = {}
        self.service_graph = nx.DiGraph()
        self.trace_aggregations: Dict[str, 'TraceAggregation'] = {}
        self.sampling_rate = 1.0

    def start_trace(
        self,
        service: str,
        operation: str,
        parent_trace_id: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Start a new trace or continue existing trace.
        Returns (trace_id, span_id).
        """

        # Sampling decision
        if not self._should_sample():
            return ("", "")

        # Generate IDs
        if parent_trace_id:
            trace_id = parent_trace_id
        else:
            trace_id = self._generate_trace_id()

        span_id = self._generate_span_id()

        # Create root span
        span = DistributedSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            service_name=service,
            operation_name=operation,
            start_time=time.time(),
            end_time=None,
            kind=SpanKind.SERVER,
            attributes={
                'service.name': service,
                'service.version': '1.0.0',
                'deployment.environment': 'production'
            },
            events=[],
            links=[]
        )

        self.active_spans[span_id] = span
        self.traces[trace_id].append(span)

        # Update service graph
        self.service_graph.add_node(service, operations={operation})

        return trace_id, span_id

    def start_span(
        self,
        trace_id: str,
        parent_span_id: str,
        service: str,
        operation: str,
        kind: SpanKind = SpanKind.INTERNAL
    ) -> str:
        """
        Start a child span within a trace.
        This implements the profunctor composition S -> T -> U.
        """

        if not trace_id:
            return ""

        span_id = self._generate_span_id()

        # Get parent span to establish service relationship
        parent_span = self.active_spans.get(parent_span_id)
        if parent_span:
            # Add edge in service graph (profunctor arrow)
            self.service_graph.add_edge(
                parent_span.service_name,
                service,
                operations=[(parent_span.operation_name, operation)]
            )

        span = DistributedSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            service_name=service,
            operation_name=operation,
            start_time=time.time(),
            end_time=None,
            kind=kind,
            attributes={'service.name': service},
            events=[],
            links=[]
        )

        self.active_spans[span_id] = span
        self.traces[trace_id].append(span)

        return span_id

    def end_span(self, span_id: str, status: str = "ok", error: str = None):
        """End an active span"""

        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.end_time = time.time()
            span.status = status

            if error:
                span.set_error(error)

            # Remove from active spans
            del self.active_spans[span_id]

            # Trigger aggregation if trace is complete
            if self._is_trace_complete(span.trace_id):
                self._aggregate_trace(span.trace_id)

    def _is_trace_complete(self, trace_id: str) -> bool:
        """Check if all spans in trace are complete"""
        spans = self.traces.get(trace_id, [])
        return all(span.end_time is not None for span in spans)

    def _aggregate_trace(self, trace_id: str):
        """
        Aggregate completed trace using end construction.
        This creates the coend over the trace category.
        """

        spans = self.traces[trace_id]
        if not spans:
            return

        aggregation = TraceAggregation(trace_id)

        # Calculate trace metrics
        aggregation.total_duration = max(s.end_time for s in spans if s.end_time) - \
                                    min(s.start_time for s in spans)

        # Build span tree for critical path analysis
        span_tree = self._build_span_tree(spans)
        aggregation.critical_path = self._find_critical_path(span_tree)

        # Service-level aggregations
        service_metrics = defaultdict(lambda: {'count': 0, 'total_time': 0})

        for span in spans:
            service = span.service_name
            service_metrics[service]['count'] += 1
            service_metrics[service]['total_time'] += span.duration_ms()

        aggregation.service_metrics = dict(service_metrics)

        # Error analysis
        errors = [s for s in spans if s.status == 'error']
        aggregation.error_rate = len(errors) / len(spans) if spans else 0
        aggregation.error_services = list(set(s.service_name for s in errors))

        self.trace_aggregations[trace_id] = aggregation

    def _build_span_tree(self, spans: List[DistributedSpan]) -> Dict[str, List[DistributedSpan]]:
        """Build parent-child relationship tree from spans"""
        tree = defaultdict(list)

        for span in spans:
            if span.parent_span_id:
                tree[span.parent_span_id].append(span)
            else:
                tree['root'].append(span)

        return tree

    def _find_critical_path(self, span_tree: Dict) -> List[str]:
        """Find critical path through span tree"""

        def find_longest_path(span_id: str, tree: Dict, visited: Set = None) -> Tuple[float, List[str]]:
            if visited is None:
                visited = set()

            if span_id in visited:
                return 0, []

            visited.add(span_id)

            if span_id not in tree or not tree[span_id]:
                return 0, [span_id]

            max_duration = 0
            max_path = [span_id]

            for child_span in tree[span_id]:
                child_duration, child_path = find_longest_path(
                    child_span.span_id,
                    tree,
                    visited
                )

                total_duration = child_span.duration_ms() + child_duration

                if total_duration > max_duration:
                    max_duration = total_duration
                    max_path = [span_id] + child_path

            return max_duration, max_path

        _, critical_path = find_longest_path('root', span_tree)
        return critical_path

    def get_service_dependencies(self) -> Dict[str, List[str]]:
        """Get service dependency graph"""
        dependencies = {}

        for node in self.service_graph.nodes():
            dependencies[node] = list(self.service_graph.successors(node))

        return dependencies

    def _should_sample(self) -> bool:
        """Sampling decision"""
        return np.random.random() < self.sampling_rate

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        return hashlib.md5(f"{time.time()}".encode()).hexdigest()[:16]

    def _generate_span_id(self) -> str:
        """Generate unique span ID"""
        return hashlib.md5(f"{time.time()}{np.random.random()}".encode()).hexdigest()[:8]

@dataclass
class TraceAggregation:
    """Aggregated trace metrics (coend construction result)"""
    trace_id: str
    total_duration: float = 0
    critical_path: List[str] = field(default_factory=list)
    service_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    error_rate: float = 0
    error_services: List[str] = field(default_factory=list)
```

## Service Mesh Observability

```python
class ServiceMeshObserver:
    """
    Service mesh observability with distributed aggregation.
    Implements end-based categorical constructions for mesh analysis.
    """

    def __init__(self):
        self.services: Dict[str, 'ServiceNode'] = {}
        self.traffic_flows: List['TrafficFlow'] = []
        self.mesh_topology = nx.DiGraph()
        self.health_scores: Dict[str, float] = {}
        self.slo_compliance: Dict[str, Dict[str, float]] = {}

    def register_service(self, service: 'ServiceNode'):
        """Register service in mesh"""
        self.services[service.name] = service
        self.mesh_topology.add_node(service.name, **service.metadata)

    def record_traffic_flow(
        self,
        source: str,
        destination: str,
        request_count: int,
        success_count: int,
        latency_p50: float,
        latency_p99: float
    ):
        """Record traffic flow between services"""

        flow = TrafficFlow(
            source=source,
            destination=destination,
            timestamp=time.time(),
            request_count=request_count,
            success_count=success_count,
            error_count=request_count - success_count,
            latency_p50=latency_p50,
            latency_p99=latency_p99
        )

        self.traffic_flows.append(flow)

        # Update mesh topology
        self.mesh_topology.add_edge(
            source,
            destination,
            weight=request_count,
            latency=latency_p99
        )

        # Update service health scores
        self._update_health_scores(flow)

    def analyze_mesh_patterns(self) -> Dict[str, Any]:
        """
        Analyze service mesh patterns using categorical constructions.
        This implements the end functor over the service category.
        """

        analysis = {
            'topology_metrics': self._analyze_topology(),
            'traffic_patterns': self._analyze_traffic_patterns(),
            'failure_cascades': self._detect_failure_cascades(),
            'bottlenecks': self._identify_bottlenecks(),
            'slo_violations': self._check_slo_violations()
        }

        return analysis

    def _analyze_topology(self) -> Dict[str, Any]:
        """Analyze mesh topology structure"""

        if not self.mesh_topology.nodes():
            return {}

        return {
            'total_services': self.mesh_topology.number_of_nodes(),
            'total_connections': self.mesh_topology.number_of_edges(),
            'avg_connections_per_service': self.mesh_topology.number_of_edges() /
                                         self.mesh_topology.number_of_nodes(),
            'strongly_connected_components': len(list(
                nx.strongly_connected_components(self.mesh_topology)
            )),
            'central_services': self._find_central_services(),
            'isolated_services': self._find_isolated_services()
        }

    def _analyze_traffic_patterns(self) -> Dict[str, Any]:
        """Analyze traffic flow patterns"""

        if not self.traffic_flows:
            return {}

        # Group flows by time window
        time_window = 300  # 5 minutes
        current_time = time.time()
        recent_flows = [
            f for f in self.traffic_flows
            if current_time - f.timestamp < time_window
        ]

        # Calculate traffic metrics
        total_requests = sum(f.request_count for f in recent_flows)
        total_errors = sum(f.error_count for f in recent_flows)

        # Find hot paths
        path_traffic = defaultdict(int)
        for flow in recent_flows:
            path = f"{flow.source}->{flow.destination}"
            path_traffic[path] += flow.request_count

        hot_paths = sorted(
            path_traffic.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'total_requests': total_requests,
            'error_rate': total_errors / total_requests if total_requests > 0 else 0,
            'hot_paths': hot_paths,
            'avg_latency_p50': np.mean([f.latency_p50 for f in recent_flows])
                              if recent_flows else 0,
            'avg_latency_p99': np.mean([f.latency_p99 for f in recent_flows])
                              if recent_flows else 0
        }

    def _detect_failure_cascades(self) -> List[Dict[str, Any]]:
        """Detect potential failure cascade patterns"""

        cascades = []

        # Check for services with high error rates
        error_rates = defaultdict(lambda: {'errors': 0, 'total': 0})

        for flow in self.traffic_flows[-100:]:  # Last 100 flows
            error_rates[flow.destination]['errors'] += flow.error_count
            error_rates[flow.destination]['total'] += flow.request_count

        # Identify failing services
        failing_services = [
            service for service, stats in error_rates.items()
            if stats['total'] > 0 and stats['errors'] / stats['total'] > 0.1
        ]

        # For each failing service, find dependent services
        for failing_service in failing_services:
            dependents = list(self.mesh_topology.predecessors(failing_service))

            if dependents:
                cascades.append({
                    'failing_service': failing_service,
                    'affected_services': dependents,
                    'error_rate': error_rates[failing_service]['errors'] /
                                 error_rates[failing_service]['total'],
                    'risk_level': 'high' if len(dependents) > 3 else 'medium'
                })

        return cascades

    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks in mesh"""

        bottlenecks = []

        # Calculate service latencies
        service_latencies = defaultdict(list)

        for flow in self.traffic_flows[-100:]:
            service_latencies[flow.destination].append(flow.latency_p99)

        # Find services with high latency
        for service, latencies in service_latencies.items():
            if not latencies:
                continue

            avg_latency = np.mean(latencies)
            if avg_latency > 500:  # 500ms threshold
                # Check incoming traffic volume
                incoming_traffic = sum(
                    f.request_count for f in self.traffic_flows[-100:]
                    if f.destination == service
                )

                bottlenecks.append({
                    'service': service,
                    'avg_latency_p99': avg_latency,
                    'incoming_traffic': incoming_traffic,
                    'severity': 'critical' if avg_latency > 1000 else 'warning'
                })

        return sorted(bottlenecks, key=lambda x: x['avg_latency_p99'], reverse=True)

    def _check_slo_violations(self) -> Dict[str, List[str]]:
        """Check SLO violations across services"""

        violations = defaultdict(list)

        for service_name, service in self.services.items():
            if not service.slos:
                continue

            # Check each SLO
            for slo_name, slo_target in service.slos.items():
                if slo_name == 'availability':
                    # Calculate availability
                    recent_flows = [
                        f for f in self.traffic_flows[-100:]
                        if f.destination == service_name
                    ]

                    if recent_flows:
                        total = sum(f.request_count for f in recent_flows)
                        success = sum(f.success_count for f in recent_flows)
                        availability = success / total if total > 0 else 0

                        if availability < slo_target:
                            violations[service_name].append(
                                f"Availability {availability:.2%} < {slo_target:.2%}"
                            )

                elif slo_name == 'latency_p99':
                    # Check latency SLO
                    recent_latencies = [
                        f.latency_p99 for f in self.traffic_flows[-100:]
                        if f.destination == service_name
                    ]

                    if recent_latencies:
                        avg_p99 = np.mean(recent_latencies)
                        if avg_p99 > slo_target:
                            violations[service_name].append(
                                f"Latency P99 {avg_p99:.0f}ms > {slo_target:.0f}ms"
                            )

        return dict(violations)

    def _find_central_services(self) -> List[str]:
        """Find most central services in mesh"""

        if not self.mesh_topology.nodes():
            return []

        # Calculate betweenness centrality
        centrality = nx.betweenness_centrality(self.mesh_topology)

        # Sort by centrality
        sorted_services = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [s for s, _ in sorted_services[:5]]

    def _find_isolated_services(self) -> List[str]:
        """Find isolated or poorly connected services"""

        isolated = []

        for node in self.mesh_topology.nodes():
            in_degree = self.mesh_topology.in_degree(node)
            out_degree = self.mesh_topology.out_degree(node)

            if in_degree == 0 and out_degree == 0:
                isolated.append(node)

        return isolated

    def _update_health_scores(self, flow: 'TrafficFlow'):
        """Update service health scores based on traffic flow"""

        success_rate = flow.success_count / flow.request_count if flow.request_count > 0 else 0

        # Update destination service health
        current_score = self.health_scores.get(flow.destination, 1.0)

        # Exponential moving average
        alpha = 0.1
        new_score = alpha * success_rate + (1 - alpha) * current_score

        self.health_scores[flow.destination] = new_score

@dataclass
class ServiceNode:
    """Service node in mesh"""
    name: str
    version: str
    replicas: int
    metadata: Dict[str, Any]
    slos: Dict[str, float]  # SLO targets

@dataclass
class TrafficFlow:
    """Traffic flow between services"""
    source: str
    destination: str
    timestamp: float
    request_count: int
    success_count: int
    error_count: int
    latency_p50: float
    latency_p99: float
```

## Complex System Analysis

```python
class ComplexSystemAnalyzer:
    """
    Analyzer for complex distributed systems.
    Uses higher-order categorical constructions for system understanding.
    """

    def __init__(self):
        self.tracer = ProfunctorTracer()
        self.mesh_observer = ServiceMeshObserver()
        self.system_state = SystemState()
        self.analysis_history = deque(maxlen=100)

    async def analyze_system(
        self,
        traces: List[Dict[str, Any]],
        metrics: List[EnrichedMetric],
        topology: nx.DiGraph
    ) -> 'SystemAnalysis':
        """
        Perform comprehensive system analysis.
        Combines multiple observability dimensions.
        """

        analysis = SystemAnalysis()

        # Trace analysis
        trace_insights = await self._analyze_traces(traces)
        analysis.trace_insights = trace_insights

        # Dependency analysis
        dependency_insights = self._analyze_dependencies(topology)
        analysis.dependency_insights = dependency_insights

        # Performance analysis
        performance_insights = self._analyze_performance(metrics)
        analysis.performance_insights = performance_insights

        # Chaos engineering recommendations
        chaos_recommendations = self._generate_chaos_recommendations(
            trace_insights,
            dependency_insights,
            performance_insights
        )
        analysis.chaos_recommendations = chaos_recommendations

        # System health score
        analysis.overall_health = self._calculate_system_health(
            trace_insights,
            performance_insights
        )

        # Store analysis
        self.analysis_history.append(analysis)

        return analysis

    async def _analyze_traces(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distributed traces for patterns"""

        insights = {
            'total_traces': len(traces),
            'service_interactions': defaultdict(int),
            'operation_latencies': defaultdict(list),
            'error_patterns': [],
            'slow_operations': []
        }

        for trace_data in traces:
            # Parse trace
            spans = trace_data.get('spans', [])

            for span in spans:
                # Track service interactions
                if span.get('parent_span_id'):
                    parent_service = self._get_service_from_span(
                        spans,
                        span['parent_span_id']
                    )
                    child_service = span.get('service_name')

                    if parent_service and child_service:
                        interaction = f"{parent_service}->{child_service}"
                        insights['service_interactions'][interaction] += 1

                # Track operation latencies
                operation = span.get('operation_name')
                duration = span.get('duration_ms', 0)

                insights['operation_latencies'][operation].append(duration)

                # Identify errors
                if span.get('status') == 'error':
                    insights['error_patterns'].append({
                        'service': span.get('service_name'),
                        'operation': operation,
                        'error': span.get('error')
                    })

                # Identify slow operations
                if duration > 1000:  # > 1 second
                    insights['slow_operations'].append({
                        'service': span.get('service_name'),
                        'operation': operation,
                        'duration_ms': duration
                    })

        # Calculate operation statistics
        operation_stats = {}
        for op, latencies in insights['operation_latencies'].items():
            if latencies:
                operation_stats[op] = {
                    'p50': np.percentile(latencies, 50),
                    'p95': np.percentile(latencies, 95),
                    'p99': np.percentile(latencies, 99),
                    'mean': np.mean(latencies),
                    'std': np.std(latencies)
                }

        insights['operation_stats'] = operation_stats

        return insights

    def _analyze_dependencies(self, topology: nx.DiGraph) -> Dict[str, Any]:
        """Analyze service dependencies and risks"""

        insights = {
            'critical_dependencies': [],
            'circular_dependencies': [],
            'single_points_of_failure': [],
            'dependency_depth': {}
        }

        if not topology.nodes():
            return insights

        # Find critical dependencies (high centrality)
        centrality = nx.betweenness_centrality(topology)
        critical = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        insights['critical_dependencies'] = [
            {'service': s, 'centrality': c}
            for s, c in critical
        ]

        # Find circular dependencies
        try:
            cycles = list(nx.simple_cycles(topology))
            insights['circular_dependencies'] = cycles[:5]  # Top 5 cycles
        except:
            pass

        # Find single points of failure
        for node in topology.nodes():
            # Check if removing node disconnects graph
            temp_graph = topology.copy()
            temp_graph.remove_node(node)

            if nx.number_weakly_connected_components(temp_graph) > \
               nx.number_weakly_connected_components(topology):
                insights['single_points_of_failure'].append(node)

        # Calculate dependency depth for each service
        for node in topology.nodes():
            # Find longest path from node
            try:
                longest_path = max(
                    nx.single_source_shortest_path_length(topology, node).values(),
                    default=0
                )
                insights['dependency_depth'][node] = longest_path
            except:
                insights['dependency_depth'][node] = 0

        return insights

    def _analyze_performance(self, metrics: List[EnrichedMetric]) -> Dict[str, Any]:
        """Analyze performance metrics"""

        insights = {
            'resource_utilization': {},
            'performance_trends': {},
            'capacity_analysis': {},
            'optimization_opportunities': []
        }

        if not metrics:
            return insights

        # Group metrics by type
        metrics_by_type = defaultdict(list)
        for metric in metrics:
            metric_type = metric.labels.get('name', 'unknown')
            metrics_by_type[metric_type].append(metric)

        # Analyze each metric type
        for metric_type, type_metrics in metrics_by_type.items():
            values = [m.value for m in type_metrics]

            if not values:
                continue

            # Calculate statistics
            insights['resource_utilization'][metric_type] = {
                'current': values[-1] if values else 0,
                'mean': np.mean(values),
                'max': np.max(values),
                'min': np.min(values),
                'trend': self._calculate_trend(values)
            }

            # Capacity analysis
            if metric_type in ['cpu_usage', 'memory_usage']:
                capacity_used = np.percentile(values, 95)
                insights['capacity_analysis'][metric_type] = {
                    'p95_usage': capacity_used,
                    'headroom': 100 - capacity_used,
                    'scaling_recommended': capacity_used > 80
                }

            # Find optimization opportunities
            if metric_type == 'cpu_usage' and np.mean(values) < 30:
                insights['optimization_opportunities'].append(
                    f"Low CPU usage ({np.mean(values):.1f}%) - consider downsizing"
                )

        return insights

    def _generate_chaos_recommendations(
        self,
        trace_insights: Dict[str, Any],
        dependency_insights: Dict[str, Any],
        performance_insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate chaos engineering recommendations"""

        recommendations = []

        # Recommend testing critical dependencies
        for dep in dependency_insights.get('critical_dependencies', [])[:3]:
            recommendations.append({
                'type': 'dependency_failure',
                'target': dep['service'],
                'reason': f"High centrality score ({dep['centrality']:.2f})",
                'test': f"Inject network latency or failures to {dep['service']}"
            })

        # Recommend testing single points of failure
        for spof in dependency_insights.get('single_points_of_failure', [])[:2]:
            recommendations.append({
                'type': 'service_failure',
                'target': spof,
                'reason': "Single point of failure in system",
                'test': f"Simulate complete failure of {spof}"
            })

        # Recommend load testing for high-utilization services
        for metric_type, utilization in performance_insights.get('resource_utilization', {}).items():
            if utilization.get('mean', 0) > 70:
                recommendations.append({
                    'type': 'load_test',
                    'target': metric_type,
                    'reason': f"High average utilization ({utilization['mean']:.1f}%)",
                    'test': "Increase load by 50% to test scaling behavior"
                })

        return recommendations

    def _calculate_system_health(
        self,
        trace_insights: Dict[str, Any],
        performance_insights: Dict[str, Any]
    ) -> float:
        """Calculate overall system health score (0-100)"""

        health_score = 100.0

        # Deduct for errors
        error_count = len(trace_insights.get('error_patterns', []))
        if error_count > 0:
            health_score -= min(error_count * 2, 20)

        # Deduct for slow operations
        slow_count = len(trace_insights.get('slow_operations', []))
        if slow_count > 0:
            health_score -= min(slow_count, 10)

        # Deduct for high resource usage
        for utilization in performance_insights.get('resource_utilization', {}).values():
            if utilization.get('current', 0) > 90:
                health_score -= 10
            elif utilization.get('current', 0) > 80:
                health_score -= 5

        return max(0, health_score)

    def _get_service_from_span(self, spans: List[Dict], span_id: str) -> Optional[str]:
        """Get service name from span ID"""
        for span in spans:
            if span.get('span_id') == span_id:
                return span.get('service_name')
        return None

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'

        # Simple linear regression
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)

        if abs(slope) < 0.1:
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'

@dataclass
class SystemState:
    """Current system state"""
    timestamp: float = field(default_factory=time.time)
    services: Dict[str, ServiceNode] = field(default_factory=dict)
    active_traces: int = 0
    error_rate: float = 0
    avg_latency: float = 0

@dataclass
class SystemAnalysis:
    """Comprehensive system analysis result"""
    trace_insights: Dict[str, Any] = field(default_factory=dict)
    dependency_insights: Dict[str, Any] = field(default_factory=dict)
    performance_insights: Dict[str, Any] = field(default_factory=dict)
    chaos_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    overall_health: float = 100.0

    def to_json(self) -> str:
        """Convert to JSON format"""
        return json.dumps({
            'trace_insights': self.trace_insights,
            'dependency_insights': {
                k: v if not isinstance(v, nx.DiGraph) else str(v)
                for k, v in self.dependency_insights.items()
            },
            'performance_insights': self.performance_insights,
            'chaos_recommendations': self.chaos_recommendations,
            'overall_health': self.overall_health
        }, default=str)
```

## Practical Example: Distributed System Observability

```python
async def distributed_observability_example():
    """
    Example of distributed tracing and complex system observability
    """

    # Initialize components
    tracer = ProfunctorTracer()
    mesh_observer = ServiceMeshObserver()
    analyzer = ComplexSystemAnalyzer()

    # Define service mesh
    services = [
        ServiceNode(
            name='api-gateway',
            version='2.1.0',
            replicas=3,
            metadata={'tier': 'edge'},
            slos={'availability': 0.999, 'latency_p99': 100}
        ),
        ServiceNode(
            name='user-service',
            version='1.5.2',
            replicas=2,
            metadata={'tier': 'backend'},
            slos={'availability': 0.99, 'latency_p99': 200}
        ),
        ServiceNode(
            name='order-service',
            version='3.0.1',
            replicas=2,
            metadata={'tier': 'backend'},
            slos={'availability': 0.99, 'latency_p99': 300}
        ),
        ServiceNode(
            name='payment-service',
            version='1.2.0',
            replicas=1,
            metadata={'tier': 'critical'},
            slos={'availability': 0.9999, 'latency_p99': 500}
        ),
        ServiceNode(
            name='database',
            version='5.7',
            replicas=1,
            metadata={'tier': 'data'},
            slos={'availability': 0.9999, 'latency_p99': 50}
        )
    ]

    # Register services
    for service in services:
        mesh_observer.register_service(service)

    # Simulate distributed trace
    trace_id, root_span_id = tracer.start_trace('api-gateway', 'handle_request')

    # API Gateway -> User Service
    user_span_id = tracer.start_span(
        trace_id,
        root_span_id,
        'user-service',
        'get_user',
        SpanKind.CLIENT
    )

    # User Service -> Database
    db_span_id = tracer.start_span(
        trace_id,
        user_span_id,
        'database',
        'query_user',
        SpanKind.CLIENT
    )

    # Complete database span
    await asyncio.sleep(0.01)  # Simulate query time
    tracer.end_span(db_span_id)

    # Complete user service span
    await asyncio.sleep(0.02)
    tracer.end_span(user_span_id)

    # API Gateway -> Order Service
    order_span_id = tracer.start_span(
        trace_id,
        root_span_id,
        'order-service',
        'create_order',
        SpanKind.CLIENT
    )

    # Order Service -> Payment Service
    payment_span_id = tracer.start_span(
        trace_id,
        order_span_id,
        'payment-service',
        'process_payment',
        SpanKind.CLIENT
    )

    # Simulate payment processing
    await asyncio.sleep(0.05)
    tracer.end_span(payment_span_id)

    # Complete order service
    await asyncio.sleep(0.01)
    tracer.end_span(order_span_id)

    # Complete root span
    await asyncio.sleep(0.01)
    tracer.end_span(root_span_id)

    # Record traffic flows
    mesh_observer.record_traffic_flow(
        'api-gateway', 'user-service',
        request_count=1000, success_count=990,
        latency_p50=20, latency_p99=150
    )

    mesh_observer.record_traffic_flow(
        'user-service', 'database',
        request_count=990, success_count=985,
        latency_p50=5, latency_p99=25
    )

    mesh_observer.record_traffic_flow(
        'api-gateway', 'order-service',
        request_count=500, success_count=495,
        latency_p50=100, latency_p99=400
    )

    mesh_observer.record_traffic_flow(
        'order-service', 'payment-service',
        request_count=495, success_count=490,
        latency_p50=200, latency_p99=800
    )

    # Analyze mesh patterns
    mesh_analysis = mesh_observer.analyze_mesh_patterns()

    # Get service dependencies
    dependencies = tracer.get_service_dependencies()

    # Get trace aggregation
    trace_aggregation = tracer.trace_aggregations.get(trace_id)

    # Create synthetic metrics for analysis
    metrics = []
    for service in services:
        cpu_metric = EnrichedMetric(
            value=np.random.uniform(30, 70),
            timestamp=time.time(),
            labels={'name': 'cpu_usage', 'service': service.name},
            context=MetricContext('production', service.name, service.version, 'deploy-1'),
            derived_metrics={},
            correlations={},
            original_metric=None
        )
        metrics.append(cpu_metric)

    # Perform complex system analysis
    system_analysis = await analyzer.analyze_system(
        traces=[{'spans': tracer.traces[trace_id]}],
        metrics=metrics,
        topology=mesh_observer.mesh_topology
    )

    return {
        'trace_id': trace_id,
        'trace_aggregation': {
            'total_duration_ms': trace_aggregation.total_duration * 1000 if trace_aggregation else 0,
            'critical_path': trace_aggregation.critical_path if trace_aggregation else [],
            'service_metrics': trace_aggregation.service_metrics if trace_aggregation else {}
        },
        'service_dependencies': dependencies,
        'mesh_analysis': {
            'topology_metrics': mesh_analysis['topology_metrics'],
            'traffic_patterns': mesh_analysis['traffic_patterns'],
            'bottlenecks': mesh_analysis['bottlenecks'],
            'slo_violations': mesh_analysis['slo_violations']
        },
        'system_health': system_analysis.overall_health,
        'chaos_recommendations': system_analysis.chaos_recommendations[:3]
    }

# Run the example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(distributed_observability_example())
    print(f"Distributed Observability Results: {json.dumps(result, indent=2, default=str)}")
```

## Summary of Kan Extension 3

This third Kan extension introduces:

1. **Profunctor-Based Tracing**: Contravariant-covariant trace composition for distributed systems
2. **Service Mesh Observability**: End-based categorical constructions for mesh analysis
3. **Complex System Analysis**: Multi-dimensional observability combining traces, metrics, and topology
4. **Failure Cascade Detection**: Automatic identification of potential failure propagation paths
5. **Chaos Engineering Recommendations**: Intelligent suggestions for resilience testing

The extension provides comprehensive distributed system observability with advanced analytical capabilities.
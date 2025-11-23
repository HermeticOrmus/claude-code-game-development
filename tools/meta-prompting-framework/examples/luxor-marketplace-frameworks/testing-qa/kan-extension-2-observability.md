# Kan Extension 2: Test Observability & Distributed Tracing

## Extension Overview

Building upon the orchestration layer, this second Kan extension introduces comprehensive observability, distributed tracing, and real-time monitoring capabilities for test execution. It provides deep insights into test behavior, performance bottlenecks, and system interactions during testing.

## Categorical Framework: Monoidal Test Composition

```python
from typing import TypeVar, Generic, Tuple, Optional, Dict, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import opentelemetry
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger import JaegerExporter
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Monoidal category for test composition
T = TypeVar('T')

class TestMonoid(Generic[T], ABC):
    """Monoidal structure for composable test observability"""

    @abstractmethod
    def unit(self) -> T:
        """Identity element for composition"""
        pass

    @abstractmethod
    def tensor(self, a: T, b: T) -> T:
        """Tensor product for parallel composition"""
        pass

    @abstractmethod
    def compose(self, a: T, b: T) -> T:
        """Sequential composition"""
        pass

class ObservabilityMonoid(TestMonoid[TraceContext]):
    """Monoidal structure for trace composition"""

    def unit(self) -> TraceContext:
        """Empty trace context"""
        return TraceContext(spans=[], metrics={}, logs=[])

    def tensor(self, a: TraceContext, b: TraceContext) -> TraceContext:
        """Parallel trace composition"""
        return TraceContext(
            spans=self._merge_parallel_spans(a.spans, b.spans),
            metrics=self._merge_metrics(a.metrics, b.metrics),
            logs=a.logs + b.logs
        )

    def compose(self, a: TraceContext, b: TraceContext) -> TraceContext:
        """Sequential trace composition"""
        return TraceContext(
            spans=self._chain_spans(a.spans, b.spans),
            metrics=self._aggregate_metrics(a.metrics, b.metrics),
            logs=self._order_logs(a.logs + b.logs)
        )
```

## Distributed Tracing Infrastructure

```python
@dataclass
class TraceContext:
    """Context for distributed tracing"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    baggage: Dict[str, str]
    spans: List[Span]
    metrics: Dict[str, float]
    logs: List[LogEntry]

class DistributedTracer:
    """Distributed tracing for test execution"""

    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)
        self.exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        self.span_processor = BatchSpanProcessor(self.exporter)

    def start_test_trace(self, test: TestCase) -> TraceContext:
        """Start a new trace for test execution"""

        with self.tracer.start_as_current_span(
            f"test.{test.module}.{test.name}",
            kind=trace.SpanKind.INTERNAL
        ) as span:
            # Set test attributes
            span.set_attribute("test.id", test.id)
            span.set_attribute("test.type", test.type)
            span.set_attribute("test.module", test.module)
            span.set_attribute("test.priority", test.priority)

            # Add test metadata
            for key, value in test.metadata.items():
                span.set_attribute(f"test.metadata.{key}", str(value))

            # Create trace context
            ctx = TraceContext(
                trace_id=span.get_span_context().trace_id,
                span_id=span.get_span_context().span_id,
                parent_span_id=None,
                baggage={},
                spans=[span],
                metrics={},
                logs=[]
            )

            return ctx

    def trace_test_phase(self, ctx: TraceContext, phase: str) -> Span:
        """Trace a specific test phase"""

        with self.tracer.start_as_current_span(
            f"test.phase.{phase}",
            context=ctx,
            kind=trace.SpanKind.INTERNAL
        ) as span:
            span.set_attribute("phase.name", phase)
            span.set_attribute("phase.start_time", time.time())

            # Add phase-specific attributes
            if phase == "setup":
                span.set_attribute("phase.fixtures", ctx.baggage.get("fixtures", ""))
            elif phase == "execution":
                span.set_attribute("phase.timeout", ctx.baggage.get("timeout", "30s"))
            elif phase == "teardown":
                span.set_attribute("phase.cleanup", ctx.baggage.get("cleanup", ""))

            return span

    def trace_external_call(self, ctx: TraceContext, service: str,
                           operation: str) -> Span:
        """Trace external service calls during tests"""

        with self.tracer.start_as_current_span(
            f"external.{service}.{operation}",
            context=ctx,
            kind=trace.SpanKind.CLIENT
        ) as span:
            span.set_attribute("service.name", service)
            span.set_attribute("service.operation", operation)
            span.set_attribute("service.version", self._get_service_version(service))

            # Propagate context for distributed tracing
            carrier = {}
            TraceContextPropagator().inject(carrier, context=ctx)
            span.set_attribute("propagation.carrier", json.dumps(carrier))

            return span
```

## Real-Time Metrics Collection

```python
class TestMetricsCollector:
    """Comprehensive metrics collection for test execution"""

    def __init__(self):
        # Prometheus metrics
        self.test_duration_histogram = Histogram(
            'test_duration_seconds',
            'Test execution duration in seconds',
            ['test_type', 'test_module', 'test_name']
        )

        self.test_result_counter = Counter(
            'test_results_total',
            'Total number of test results',
            ['result', 'test_type']
        )

        self.test_memory_gauge = Gauge(
            'test_memory_bytes',
            'Memory usage during test execution',
            ['test_name']
        )

        self.test_cpu_gauge = Gauge(
            'test_cpu_percent',
            'CPU usage during test execution',
            ['test_name']
        )

        self.coverage_gauge = Gauge(
            'test_coverage_percent',
            'Code coverage percentage',
            ['module']
        )

        # Custom metrics
        self.custom_metrics = {}

    def record_test_execution(self, test: TestCase, result: TestResult):
        """Record comprehensive test execution metrics"""

        # Duration metrics
        self.test_duration_histogram.labels(
            test_type=test.type,
            test_module=test.module,
            test_name=test.name
        ).observe(result.duration)

        # Result metrics
        self.test_result_counter.labels(
            result=result.status,
            test_type=test.type
        ).inc()

        # Resource metrics
        self.test_memory_gauge.labels(
            test_name=test.name
        ).set(result.memory_usage)

        self.test_cpu_gauge.labels(
            test_name=test.name
        ).set(result.cpu_usage)

        # Coverage metrics
        if result.coverage:
            self.coverage_gauge.labels(
                module=test.module
            ).set(result.coverage.percentage)

    def record_custom_metric(self, name: str, value: float, labels: Dict = None):
        """Record custom test metrics"""

        if name not in self.custom_metrics:
            self.custom_metrics[name] = Gauge(
                f'test_custom_{name}',
                f'Custom metric: {name}',
                list(labels.keys()) if labels else []
            )

        if labels:
            self.custom_metrics[name].labels(**labels).set(value)
        else:
            self.custom_metrics[name].set(value)

    def get_metrics_summary(self) -> Dict:
        """Get summary of all collected metrics"""

        return {
            'total_tests': sum(
                self.test_result_counter._metrics.values()
            ),
            'average_duration': self._calculate_average_duration(),
            'success_rate': self._calculate_success_rate(),
            'coverage': self._get_overall_coverage(),
            'resource_usage': {
                'peak_memory': self._get_peak_memory(),
                'average_cpu': self._get_average_cpu()
            }
        }
```

## Advanced Logging & Event Streaming

```python
class StructuredTestLogger:
    """Structured logging for test execution"""

    def __init__(self):
        self.logger = structlog.get_logger()
        self.event_stream = EventStream()
        self.log_aggregator = LogAggregator()

    def log_test_event(self, event_type: str, test: TestCase,
                      data: Dict = None, level: str = "info"):
        """Log structured test event"""

        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'test_id': test.id,
            'test_name': test.name,
            'test_module': test.module,
            'level': level,
            'data': data or {}
        }

        # Add correlation ID for tracing
        if hasattr(test, 'trace_id'):
            event['trace_id'] = test.trace_id
            event['span_id'] = test.span_id

        # Log based on level
        log_method = getattr(self.logger, level)
        log_method(event_type, **event)

        # Stream to event bus
        self.event_stream.publish(event)

        # Aggregate for analysis
        self.log_aggregator.add(event)

    def log_test_lifecycle(self, test: TestCase, phase: str, **kwargs):
        """Log test lifecycle events"""

        lifecycle_events = {
            'queued': 'Test queued for execution',
            'started': 'Test execution started',
            'setup': 'Test setup phase',
            'running': 'Test main execution',
            'teardown': 'Test teardown phase',
            'completed': 'Test execution completed',
            'failed': 'Test execution failed',
            'skipped': 'Test was skipped',
            'retried': 'Test being retried'
        }

        self.log_test_event(
            f"test.lifecycle.{phase}",
            test,
            {
                'description': lifecycle_events.get(phase, phase),
                **kwargs
            }
        )

class EventStream:
    """Real-time event streaming for test execution"""

    def __init__(self):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.websocket_server = WebSocketServer()

    def publish(self, event: Dict):
        """Publish event to multiple channels"""

        # Kafka for persistence and processing
        self.kafka_producer.send('test-events', event)

        # WebSocket for real-time UI updates
        self.websocket_server.broadcast(event)

        # Webhook notifications
        self._send_webhook_notifications(event)

    def _send_webhook_notifications(self, event: Dict):
        """Send webhook notifications for important events"""

        if event.get('level') in ['error', 'critical']:
            webhook_url = os.getenv('TEST_WEBHOOK_URL')
            if webhook_url:
                requests.post(webhook_url, json=event)
```

## Performance Profiling Integration

```python
class TestPerformanceProfiler:
    """Deep performance profiling for test execution"""

    def __init__(self):
        self.profiler = cProfile.Profile()
        self.memory_profiler = memory_profiler.LineProfiler()
        self.flame_graph_generator = FlameGraphGenerator()

    def profile_test(self, test: TestCase) -> ProfilingResult:
        """Profile test execution"""

        # CPU profiling
        self.profiler.enable()

        # Memory profiling
        @self.memory_profiler
        def run_test():
            return test.execute()

        try:
            # Execute test with profiling
            result = run_test()

            # Stop profiling
            self.profiler.disable()

            # Collect profiling data
            cpu_stats = pstats.Stats(self.profiler)
            memory_stats = self.memory_profiler.get_stats()

            # Generate flame graph
            flame_graph = self.flame_graph_generator.generate(cpu_stats)

            return ProfilingResult(
                cpu_stats=cpu_stats,
                memory_stats=memory_stats,
                flame_graph=flame_graph,
                hotspots=self._identify_hotspots(cpu_stats),
                memory_leaks=self._detect_memory_leaks(memory_stats)
            )

        except Exception as e:
            self.profiler.disable()
            raise

    def _identify_hotspots(self, stats: pstats.Stats) -> List[Hotspot]:
        """Identify performance hotspots"""

        hotspots = []
        stats.sort_stats('cumulative')

        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            if ct > 0.1:  # Functions taking > 100ms
                hotspots.append(Hotspot(
                    function=f"{func[0]}:{func[1]}:{func[2]}",
                    total_time=tt,
                    cumulative_time=ct,
                    calls=nc,
                    callers=list(callers.keys())
                ))

        return sorted(hotspots, key=lambda h: h.cumulative_time, reverse=True)

    def _detect_memory_leaks(self, memory_stats: Dict) -> List[MemoryLeak]:
        """Detect potential memory leaks"""

        leaks = []
        for filename, lines in memory_stats.items():
            for line_no, line_stats in lines:
                if line_stats.memory_usage_diff > 10 * 1024 * 1024:  # > 10MB
                    leaks.append(MemoryLeak(
                        file=filename,
                        line=line_no,
                        memory_increase=line_stats.memory_usage_diff,
                        occurrences=line_stats.occurrences
                    ))

        return leaks
```

## Distributed Log Aggregation

```python
class DistributedLogAggregator:
    """Aggregate logs from distributed test execution"""

    def __init__(self):
        self.elasticsearch = Elasticsearch(['localhost:9200'])
        self.log_buffer = []
        self.aggregation_rules = []

    async def aggregate_logs(self, test_run_id: str) -> AggregatedLogs:
        """Aggregate logs from all test execution nodes"""

        # Query all logs for test run
        query = {
            "query": {
                "match": {
                    "test_run_id": test_run_id
                }
            },
            "sort": [
                {"timestamp": {"order": "asc"}}
            ]
        }

        response = self.elasticsearch.search(
            index="test-logs",
            body=query,
            size=10000
        )

        logs = response['hits']['hits']

        # Group logs by test
        grouped_logs = self._group_by_test(logs)

        # Apply aggregation rules
        aggregated = self._apply_aggregation_rules(grouped_logs)

        # Detect patterns
        patterns = self._detect_patterns(aggregated)

        # Generate insights
        insights = self._generate_insights(aggregated, patterns)

        return AggregatedLogs(
            test_run_id=test_run_id,
            total_logs=len(logs),
            grouped_logs=grouped_logs,
            patterns=patterns,
            insights=insights
        )

    def _detect_patterns(self, logs: Dict) -> List[Pattern]:
        """Detect patterns in aggregated logs"""

        patterns = []

        # Error pattern detection
        error_patterns = self._detect_error_patterns(logs)
        patterns.extend(error_patterns)

        # Performance pattern detection
        perf_patterns = self._detect_performance_patterns(logs)
        patterns.extend(perf_patterns)

        # Anomaly detection
        anomalies = self._detect_anomalies(logs)
        patterns.extend(anomalies)

        return patterns

    def _detect_error_patterns(self, logs: Dict) -> List[ErrorPattern]:
        """Detect common error patterns"""

        error_logs = [
            log for log in logs
            if log.get('level') in ['error', 'critical']
        ]

        # Group similar errors
        error_groups = {}
        for error in error_logs:
            error_hash = self._hash_error(error)
            if error_hash not in error_groups:
                error_groups[error_hash] = []
            error_groups[error_hash].append(error)

        # Create patterns from groups
        patterns = []
        for error_hash, errors in error_groups.items():
            if len(errors) > 1:  # Pattern if occurs multiple times
                patterns.append(ErrorPattern(
                    pattern_id=error_hash,
                    occurrences=len(errors),
                    first_seen=min(e['timestamp'] for e in errors),
                    last_seen=max(e['timestamp'] for e in errors),
                    affected_tests=[e['test_id'] for e in errors],
                    sample_error=errors[0]
                ))

        return patterns
```

## Test Execution Dashboard

```python
class TestExecutionDashboard:
    """Real-time dashboard for test execution monitoring"""

    def __init__(self):
        self.grafana = GrafanaClient()
        self.prometheus = PrometheusClient()
        self.websocket_server = WebSocketServer()

    def create_dashboard(self, test_run: TestRun) -> Dashboard:
        """Create comprehensive test execution dashboard"""

        dashboard = {
            'title': f"Test Run: {test_run.id}",
            'panels': [
                self._create_overview_panel(),
                self._create_progress_panel(),
                self._create_performance_panel(),
                self._create_failures_panel(),
                self._create_coverage_panel(),
                self._create_resource_panel()
            ]
        }

        # Create in Grafana
        self.grafana.create_dashboard(dashboard)

        # Start real-time updates
        self._start_realtime_updates(test_run.id)

        return Dashboard(
            url=f"http://localhost:3000/d/{test_run.id}",
            panels=dashboard['panels']
        )

    def _create_overview_panel(self) -> Panel:
        """Create test execution overview panel"""

        return {
            'type': 'stat',
            'title': 'Test Execution Overview',
            'targets': [
                {
                    'expr': 'sum(test_results_total)',
                    'legendFormat': 'Total Tests'
                },
                {
                    'expr': 'sum(test_results_total{result="passed"})/sum(test_results_total)',
                    'legendFormat': 'Pass Rate'
                },
                {
                    'expr': 'avg(test_duration_seconds)',
                    'legendFormat': 'Avg Duration'
                }
            ]
        }

    def _create_performance_panel(self) -> Panel:
        """Create performance monitoring panel"""

        return {
            'type': 'graph',
            'title': 'Test Performance',
            'targets': [
                {
                    'expr': 'histogram_quantile(0.99, test_duration_seconds)',
                    'legendFormat': 'p99 Duration'
                },
                {
                    'expr': 'histogram_quantile(0.95, test_duration_seconds)',
                    'legendFormat': 'p95 Duration'
                },
                {
                    'expr': 'histogram_quantile(0.50, test_duration_seconds)',
                    'legendFormat': 'p50 Duration'
                }
            ]
        }

    async def _start_realtime_updates(self, test_run_id: str):
        """Start real-time dashboard updates via WebSocket"""

        while True:
            # Get latest metrics
            metrics = await self._get_latest_metrics(test_run_id)

            # Broadcast to connected clients
            await self.websocket_server.broadcast({
                'type': 'metrics_update',
                'test_run_id': test_run_id,
                'metrics': metrics,
                'timestamp': time.time()
            })

            await asyncio.sleep(1)  # Update every second
```

## Alerting & Notification System

```python
class TestAlertingSystem:
    """Intelligent alerting for test execution issues"""

    def __init__(self):
        self.alert_manager = AlertManager()
        self.notification_channels = {
            'slack': SlackNotifier(),
            'email': EmailNotifier(),
            'pagerduty': PagerDutyNotifier()
        }
        self.alert_rules = []

    def configure_alerts(self, rules: List[AlertRule]):
        """Configure alerting rules"""

        self.alert_rules = rules

        # Register rules with Prometheus AlertManager
        for rule in rules:
            self.alert_manager.register_rule({
                'alert': rule.name,
                'expr': rule.expression,
                'for': rule.duration,
                'labels': rule.labels,
                'annotations': rule.annotations
            })

    def check_alerts(self, metrics: Dict) -> List[Alert]:
        """Check if any alerts should be triggered"""

        triggered_alerts = []

        for rule in self.alert_rules:
            if self._evaluate_rule(rule, metrics):
                alert = Alert(
                    rule=rule,
                    triggered_at=datetime.utcnow(),
                    metrics=metrics,
                    severity=rule.severity
                )
                triggered_alerts.append(alert)
                self._send_alert(alert)

        return triggered_alerts

    def _send_alert(self, alert: Alert):
        """Send alert through configured channels"""

        message = self._format_alert_message(alert)

        # Route based on severity
        if alert.severity == 'critical':
            channels = ['pagerduty', 'slack', 'email']
        elif alert.severity == 'warning':
            channels = ['slack', 'email']
        else:
            channels = ['slack']

        for channel in channels:
            if channel in self.notification_channels:
                self.notification_channels[channel].send(message)

    def _format_alert_message(self, alert: Alert) -> str:
        """Format alert message"""

        return f"""
🚨 Test Execution Alert: {alert.rule.name}

Severity: {alert.severity}
Time: {alert.triggered_at}

Condition: {alert.rule.expression}
Current Value: {alert.metrics}

Description: {alert.rule.annotations.get('description', '')}
Runbook: {alert.rule.annotations.get('runbook', '')}
"""
```

## Integration Example

```python
# Example usage of observability layer
async def run_observable_test_suite():
    """Run tests with full observability"""

    # Initialize observability components
    tracer = DistributedTracer()
    metrics = TestMetricsCollector()
    logger = StructuredTestLogger()
    profiler = TestPerformanceProfiler()
    dashboard = TestExecutionDashboard()
    alerting = TestAlertingSystem()

    # Configure alerting rules
    alerting.configure_alerts([
        AlertRule(
            name="high_failure_rate",
            expression="rate(test_results_total{result='failed'}[5m]) > 0.1",
            duration="5m",
            severity="critical"
        ),
        AlertRule(
            name="slow_tests",
            expression="histogram_quantile(0.95, test_duration_seconds) > 30",
            duration="10m",
            severity="warning"
        )
    ])

    # Create dashboard
    test_run = TestRun(id=str(uuid4()))
    dashboard_url = dashboard.create_dashboard(test_run)
    print(f"📊 Dashboard: {dashboard_url}")

    # Execute tests with full observability
    for test in test_suite:
        # Start trace
        trace_ctx = tracer.start_test_trace(test)

        # Log lifecycle
        logger.log_test_lifecycle(test, 'started')

        try:
            # Profile execution
            with profiler.profile_test(test) as profile:
                # Execute test
                result = await test.execute()

                # Record metrics
                metrics.record_test_execution(test, result)

                # Log success
                logger.log_test_lifecycle(test, 'completed', result=result)

        except Exception as e:
            # Log failure
            logger.log_test_lifecycle(test, 'failed', error=str(e))

            # Record failure metrics
            metrics.record_test_execution(test, TestResult(status='failed'))

        finally:
            # Finalize trace
            tracer.finalize_trace(trace_ctx)

            # Check alerts
            current_metrics = metrics.get_metrics_summary()
            alerting.check_alerts(current_metrics)

    # Generate final report
    print("✅ Test execution completed with full observability")

# Run with asyncio
if __name__ == "__main__":
    asyncio.run(run_observable_test_suite())
```

This Kan extension adds comprehensive observability including distributed tracing, real-time metrics, structured logging, performance profiling, and intelligent alerting, providing deep insights into test execution behavior.
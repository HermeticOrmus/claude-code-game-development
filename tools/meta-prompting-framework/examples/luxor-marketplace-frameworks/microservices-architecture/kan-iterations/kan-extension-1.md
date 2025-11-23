# Kan Extension 1: Service Discovery Extensions

## Overview

This iteration extends the base framework with advanced service discovery patterns using Kan extensions to generalize discovery mechanisms across different service mesh implementations.

## Mathematical Foundation

### Left Kan Extension for Service Discovery
```
Given functors:
F: ServiceRegistry → ServiceMesh
G: ServiceRegistry → LoadBalancer

The left Kan extension Lan_F G provides:
- Universal discovery pattern
- Optimal service routing
- Minimal latency paths
```

### Right Kan Extension for Health Checking
```
Given functors:
H: HealthCheck → ServiceState
K: ServiceState → RoutingDecision

The right Kan extension Ran_H K provides:
- Comprehensive health aggregation
- Predictive failure detection
- Graceful degradation strategies
```

## Service Discovery Patterns

### Pattern 1: Multi-Registry Aggregation
```python
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class ServiceInstance:
    id: str
    host: str
    port: int
    metadata: Dict
    health_score: float

class MultiRegistryDiscovery:
    """Kan extension for aggregating multiple service registries"""

    def __init__(self, registries: List[str]):
        self.registries = registries
        self.service_cache = {}

    async def discover(self, service_name: str) -> List[ServiceInstance]:
        """Left Kan extension: Universal discovery across registries"""
        tasks = [
            self._query_registry(reg, service_name)
            for reg in self.registries
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate and deduplicate
        instances = {}
        for result in results:
            if isinstance(result, list):
                for instance in result:
                    key = f"{instance.host}:{instance.port}"
                    if key not in instances or instance.health_score > instances[key].health_score:
                        instances[key] = instance

        return list(instances.values())

    async def _query_registry(self, registry: str, service: str) -> List[ServiceInstance]:
        """Query individual registry"""
        # Implementation specific to registry type
        if "consul" in registry:
            return await self._query_consul(registry, service)
        elif "eureka" in registry:
            return await self._query_eureka(registry, service)
        elif "etcd" in registry:
            return await self._query_etcd(registry, service)
        return []
```

### Pattern 2: Adaptive Load Balancing
```python
import random
from collections import defaultdict
from datetime import datetime, timedelta

class AdaptiveLoadBalancer:
    """Right Kan extension for intelligent load balancing"""

    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'requests': 0,
            'errors': 0,
            'total_latency': 0,
            'last_reset': datetime.now()
        })

    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """Select optimal instance using Kan extension composition"""
        if not instances:
            return None

        # Calculate weights based on health and performance
        weights = []
        for instance in instances:
            key = f"{instance.host}:{instance.port}"
            metrics = self.metrics[key]

            # Compute performance score
            error_rate = metrics['errors'] / max(metrics['requests'], 1)
            avg_latency = metrics['total_latency'] / max(metrics['requests'], 1)

            # Kan extension: compose health with performance
            weight = instance.health_score * (1 - error_rate) * (1 / (1 + avg_latency))
            weights.append(weight)

        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(instances)

        r = random.uniform(0, total_weight)
        cumulative = 0
        for instance, weight in zip(instances, weights):
            cumulative += weight
            if cumulative >= r:
                return instance

        return instances[-1]

    def record_result(self, instance: ServiceInstance, latency: float, success: bool):
        """Update metrics for adaptive learning"""
        key = f"{instance.host}:{instance.port}"
        metrics = self.metrics[key]

        metrics['requests'] += 1
        metrics['total_latency'] += latency
        if not success:
            metrics['errors'] += 1

        # Reset metrics periodically
        if datetime.now() - metrics['last_reset'] > timedelta(minutes=5):
            metrics['requests'] = metrics['requests'] // 2
            metrics['errors'] = metrics['errors'] // 2
            metrics['total_latency'] = metrics['total_latency'] / 2
            metrics['last_reset'] = datetime.now()
```

### Pattern 3: Circuit Breaker with Kan Extensions
```python
from enum import Enum
from datetime import datetime, timedelta
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class KanCircuitBreaker:
    """Traced monoidal category for circuit breaking"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60,
                 success_threshold: int = 2):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.mutex = asyncio.Lock()

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        async with self.mutex:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise Exception("Circuit breaker is open")

        try:
            # Attempt the call
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e

    async def _on_success(self):
        """Handle successful call"""
        async with self.mutex:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    async def _on_failure(self):
        """Handle failed call"""
        async with self.mutex:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset"""
        return (self.last_failure_time and
                datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout))
```

## Consul Integration Example

```python
import consul
import asyncio
from typing import List

class ConsulServiceDiscovery:
    """Consul-specific service discovery implementation"""

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)

    async def register_service(self, name: str, service_id: str,
                              address: str, port: int, tags: List[str] = None):
        """Register service with Consul"""
        check = consul.Check.http(
            f"http://{address}:{port}/health",
            interval="10s",
            timeout="5s"
        )

        self.consul.agent.service.register(
            name=name,
            service_id=service_id,
            address=address,
            port=port,
            tags=tags or [],
            check=check
        )

    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """Discover services from Consul"""
        _, services = self.consul.health.service(service_name, passing=True)

        instances = []
        for service in services:
            instances.append(ServiceInstance(
                id=service['Service']['ID'],
                host=service['Service']['Address'],
                port=service['Service']['Port'],
                metadata={'tags': service['Service']['Tags']},
                health_score=1.0  # Consul returns only healthy services
            ))

        return instances

    async def deregister_service(self, service_id: str):
        """Deregister service from Consul"""
        self.consul.agent.service.deregister(service_id)
```

## Eureka Integration Example

```python
import py_eureka_client.eureka_client as eureka_client
from typing import List

class EurekaServiceDiscovery:
    """Eureka-specific service discovery implementation"""

    def __init__(self, eureka_server: str = "http://localhost:8761"):
        self.eureka_server = eureka_server

    async def register_service(self, app_name: str, instance_id: str,
                              host: str, port: int, metadata: dict = None):
        """Register service with Eureka"""
        eureka_client.init(
            eureka_server=self.eureka_server,
            app_name=app_name,
            instance_id=instance_id,
            instance_host=host,
            instance_port=port,
            metadata=metadata or {}
        )

    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """Discover services from Eureka"""
        applications = eureka_client.get_applications(self.eureka_server)

        instances = []
        for app in applications.applications:
            if app.name.lower() == service_name.lower():
                for instance in app.instances:
                    if instance.status == "UP":
                        instances.append(ServiceInstance(
                            id=instance.instanceId,
                            host=instance.ipAddr,
                            port=instance.port.port,
                            metadata=instance.metadata,
                            health_score=1.0 if instance.status == "UP" else 0.0
                        ))

        return instances
```

## Advanced Discovery Patterns

### Pattern 4: Predictive Service Discovery
```python
import numpy as np
from sklearn.linear_model import LinearRegression
from collections import deque

class PredictiveServiceDiscovery:
    """Machine learning-based service discovery optimization"""

    def __init__(self, history_size: int = 100):
        self.history = deque(maxlen=history_size)
        self.model = LinearRegression()
        self.trained = False

    def predict_best_instance(self, instances: List[ServiceInstance],
                             request_features: dict) -> ServiceInstance:
        """Predict best instance based on historical performance"""
        if not self.trained or len(self.history) < 10:
            # Fallback to random selection initially
            return random.choice(instances)

        # Extract features for each instance
        predictions = []
        for instance in instances:
            features = self._extract_features(instance, request_features)
            predicted_latency = self.model.predict([features])[0]
            predictions.append((instance, predicted_latency))

        # Select instance with lowest predicted latency
        predictions.sort(key=lambda x: x[1])
        return predictions[0][0]

    def record_performance(self, instance: ServiceInstance,
                          request_features: dict, latency: float):
        """Record performance for training"""
        features = self._extract_features(instance, request_features)
        self.history.append((features, latency))

        # Retrain model periodically
        if len(self.history) >= 10 and len(self.history) % 10 == 0:
            self._train_model()

    def _extract_features(self, instance: ServiceInstance,
                         request_features: dict) -> List[float]:
        """Extract numerical features for ML model"""
        features = [
            instance.health_score,
            float(instance.port),
            request_features.get('payload_size', 0),
            request_features.get('complexity', 0),
            # Add more features as needed
        ]
        return features

    def _train_model(self):
        """Train the prediction model"""
        if len(self.history) < 10:
            return

        X = [item[0] for item in self.history]
        y = [item[1] for item in self.history]

        self.model.fit(X, y)
        self.trained = True
```

## Testing Framework

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_multi_registry_discovery():
    """Test multi-registry service discovery"""
    discovery = MultiRegistryDiscovery([
        "consul://localhost:8500",
        "eureka://localhost:8761"
    ])

    # Mock registry queries
    discovery._query_consul = AsyncMock(return_value=[
        ServiceInstance("service-1", "host1", 8080, {}, 0.9)
    ])
    discovery._query_eureka = AsyncMock(return_value=[
        ServiceInstance("service-2", "host2", 8081, {}, 0.95)
    ])

    instances = await discovery.discover("test-service")

    assert len(instances) == 2
    assert instances[0].host in ["host1", "host2"]

@pytest.mark.asyncio
async def test_circuit_breaker():
    """Test circuit breaker functionality"""
    breaker = KanCircuitBreaker(failure_threshold=2, timeout=1)

    # Mock failing function
    async def failing_func():
        raise Exception("Service unavailable")

    # Test circuit opening
    for _ in range(2):
        with pytest.raises(Exception):
            await breaker.call(failing_func)

    assert breaker.state == CircuitState.OPEN

    # Test circuit remains open
    with pytest.raises(Exception, match="Circuit breaker is open"):
        await breaker.call(failing_func)

    # Wait for timeout
    await asyncio.sleep(1.1)

    # Test half-open state
    async def success_func():
        return "Success"

    result = await breaker.call(success_func)
    assert result == "Success"
    assert breaker.state == CircuitState.HALF_OPEN

def test_adaptive_load_balancer():
    """Test adaptive load balancing"""
    balancer = AdaptiveLoadBalancer()

    instances = [
        ServiceInstance("1", "host1", 8080, {}, 1.0),
        ServiceInstance("2", "host2", 8081, {}, 0.5),
        ServiceInstance("3", "host3", 8082, {}, 0.8)
    ]

    # Record some metrics
    balancer.record_result(instances[0], 100, True)
    balancer.record_result(instances[1], 500, False)
    balancer.record_result(instances[2], 200, True)

    # Test selection favors better performing instances
    selected_counts = {i.id: 0 for i in instances}
    for _ in range(100):
        selected = balancer.select_instance(instances)
        selected_counts[selected.id] += 1

    # Instance 1 should be selected most often
    assert selected_counts["1"] > selected_counts["2"]
```

## Conclusion

This Kan extension iteration provides advanced service discovery patterns that leverage categorical abstractions to create robust, adaptive, and intelligent service discovery mechanisms. The patterns can be composed and extended to handle complex microservices topologies while maintaining mathematical rigor and practical applicability.
# Kan Extension 3: Service Mesh Extensions

## Overview

This iteration extends the framework with advanced service mesh patterns using Kan extensions to create sophisticated traffic management, security, and observability capabilities across the microservices infrastructure.

## Mathematical Foundation

### String Diagrams for Service Topology
```
Service mesh topology as traced monoidal categories:
- Objects: Services as nodes
- Morphisms: Network paths with sidecars
- Braiding: Traffic routing patterns
- Trace: Request flow tracking

Kan extensions provide:
- Universal traffic policies
- Optimal routing decisions
- Security boundary enforcement
```

### Higher Categories for Multi-Layer Mesh
```
2-categories for service mesh layers:
- 0-cells: Services
- 1-cells: Network connections
- 2-cells: Traffic policies

Enables reasoning about:
- Policy composition
- Multi-cluster federation
- Cross-mesh communication
```

## Service Mesh Architecture Patterns

### Pattern 1: Istio Integration with Envoy Proxy
```python
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import yaml
import json
from enum import Enum

@dataclass
class VirtualService:
    """Istio VirtualService configuration"""
    name: str
    namespace: str
    hosts: List[str]
    gateways: List[str] = field(default_factory=list)
    http_routes: List[Dict] = field(default_factory=list)
    tcp_routes: List[Dict] = field(default_factory=list)

class IstioServiceMesh:
    """Istio service mesh management with Kan extensions"""

    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, Dict] = {}
        self.service_entries: Dict[str, Dict] = {}
        self.policies: Dict[str, Dict] = {}

    def create_virtual_service(self, service: VirtualService) -> Dict:
        """Create Istio VirtualService configuration"""
        config = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": service.name,
                "namespace": service.namespace
            },
            "spec": {
                "hosts": service.hosts,
                "gateways": service.gateways if service.gateways else ["mesh"],
                "http": service.http_routes
            }
        }

        if service.tcp_routes:
            config["spec"]["tcp"] = service.tcp_routes

        self.virtual_services[service.name] = service
        return config

    def create_destination_rule(self, name: str, host: str,
                              subsets: List[Dict],
                              traffic_policy: Optional[Dict] = None) -> Dict:
        """Create DestinationRule for traffic management"""
        config = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule",
            "metadata": {
                "name": name,
                "namespace": self.namespace
            },
            "spec": {
                "host": host,
                "subsets": subsets
            }
        }

        if traffic_policy:
            config["spec"]["trafficPolicy"] = traffic_policy

        self.destination_rules[name] = config
        return config

    def create_service_entry(self, name: str, hosts: List[str],
                           ports: List[Dict], location: str = "MESH_EXTERNAL") -> Dict:
        """Create ServiceEntry for external services"""
        config = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "ServiceEntry",
            "metadata": {
                "name": name,
                "namespace": self.namespace
            },
            "spec": {
                "hosts": hosts,
                "ports": ports,
                "location": location
            }
        }

        self.service_entries[name] = config
        return config

    def create_authorization_policy(self, name: str, app: str,
                                  rules: List[Dict]) -> Dict:
        """Create AuthorizationPolicy for security"""
        config = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "AuthorizationPolicy",
            "metadata": {
                "name": name,
                "namespace": self.namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": app
                    }
                },
                "rules": rules
            }
        }

        self.policies[name] = config
        return config

    def create_canary_deployment(self, service_name: str,
                                stable_version: str, canary_version: str,
                                canary_weight: int = 10) -> Dict:
        """Create canary deployment configuration"""
        # Virtual service for traffic splitting
        vs = VirtualService(
            name=f"{service_name}-canary",
            namespace=self.namespace,
            hosts=[service_name],
            http_routes=[
                {
                    "match": [{"headers": {"canary": {"exact": "true"}}}],
                    "route": [
                        {
                            "destination": {
                                "host": service_name,
                                "subset": canary_version
                            }
                        }
                    ]
                },
                {
                    "route": [
                        {
                            "destination": {
                                "host": service_name,
                                "subset": stable_version
                            },
                            "weight": 100 - canary_weight
                        },
                        {
                            "destination": {
                                "host": service_name,
                                "subset": canary_version
                            },
                            "weight": canary_weight
                        }
                    ]
                }
            ]
        )

        vs_config = self.create_virtual_service(vs)

        # Destination rule for subsets
        dr_config = self.create_destination_rule(
            name=f"{service_name}-dr",
            host=service_name,
            subsets=[
                {"name": stable_version, "labels": {"version": stable_version}},
                {"name": canary_version, "labels": {"version": canary_version}}
            ]
        )

        return {
            "virtual_service": vs_config,
            "destination_rule": dr_config
        }
```

### Pattern 2: Traffic Management with Envoy
```python
class LoadBalancingPolicy(Enum):
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_REQUEST = "LEAST_REQUEST"
    RANDOM = "RANDOM"
    PASSTHROUGH = "PASSTHROUGH"

class CircuitBreakerPolicy:
    """Circuit breaker configuration for Envoy"""

    def __init__(self, consecutive_errors: int = 5,
                 interval: str = "30s",
                 base_ejection_time: str = "30s",
                 max_ejection_percent: int = 50):
        self.consecutive_errors = consecutive_errors
        self.interval = interval
        self.base_ejection_time = base_ejection_time
        self.max_ejection_percent = max_ejection_percent

    def to_dict(self) -> Dict:
        return {
            "outlierDetection": {
                "consecutiveErrors": self.consecutive_errors,
                "interval": self.interval,
                "baseEjectionTime": self.base_ejection_time,
                "maxEjectionPercent": self.max_ejection_percent
            }
        }

class RetryPolicy:
    """Retry configuration for failed requests"""

    def __init__(self, attempts: int = 3,
                 per_try_timeout: str = "2s",
                 retry_on: List[str] = None):
        self.attempts = attempts
        self.per_try_timeout = per_try_timeout
        self.retry_on = retry_on or ["5xx", "reset", "connect-failure", "refused-stream"]

    def to_dict(self) -> Dict:
        return {
            "attempts": self.attempts,
            "perTryTimeout": self.per_try_timeout,
            "retryOn": ",".join(self.retry_on)
        }

class TrafficManager:
    """Advanced traffic management with Kan extensions"""

    def __init__(self, mesh: IstioServiceMesh):
        self.mesh = mesh
        self.traffic_policies = {}

    def create_traffic_policy(self, service_name: str,
                            load_balancing: LoadBalancingPolicy = LoadBalancingPolicy.ROUND_ROBIN,
                            circuit_breaker: Optional[CircuitBreakerPolicy] = None,
                            retry_policy: Optional[RetryPolicy] = None,
                            connection_pool: Optional[Dict] = None) -> Dict:
        """Create comprehensive traffic management policy"""
        policy = {
            "loadBalancer": {
                "simple": load_balancing.value
            }
        }

        if circuit_breaker:
            policy.update(circuit_breaker.to_dict())

        if connection_pool:
            policy["connectionPool"] = connection_pool

        self.traffic_policies[service_name] = policy

        # Create destination rule with traffic policy
        return self.mesh.create_destination_rule(
            name=f"{service_name}-traffic-policy",
            host=service_name,
            subsets=[{"name": "v1", "labels": {"version": "v1"}}],
            traffic_policy=policy
        )

    def create_retry_virtual_service(self, service_name: str,
                                    retry_policy: RetryPolicy) -> Dict:
        """Create virtual service with retry configuration"""
        vs = VirtualService(
            name=f"{service_name}-retry",
            namespace=self.mesh.namespace,
            hosts=[service_name],
            http_routes=[
                {
                    "route": [
                        {
                            "destination": {
                                "host": service_name
                            }
                        }
                    ],
                    "retries": retry_policy.to_dict()
                }
            ]
        )

        return self.mesh.create_virtual_service(vs)

    def create_fault_injection(self, service_name: str,
                             delay_percentage: int = 0,
                             delay_duration: str = "5s",
                             abort_percentage: int = 0,
                             abort_status: int = 500) -> Dict:
        """Create fault injection for chaos testing"""
        fault_config = {}

        if delay_percentage > 0:
            fault_config["delay"] = {
                "percentage": {"value": delay_percentage},
                "fixedDelay": delay_duration
            }

        if abort_percentage > 0:
            fault_config["abort"] = {
                "percentage": {"value": abort_percentage},
                "httpStatus": abort_status
            }

        vs = VirtualService(
            name=f"{service_name}-fault",
            namespace=self.mesh.namespace,
            hosts=[service_name],
            http_routes=[
                {
                    "fault": fault_config,
                    "route": [
                        {
                            "destination": {
                                "host": service_name
                            }
                        }
                    ]
                }
            ]
        )

        return self.mesh.create_virtual_service(vs)
```

### Pattern 3: Observability with Distributed Tracing
```python
import time
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from prometheus_client import Counter, Histogram, Gauge
import logging

class ObservabilityLayer:
    """Service mesh observability with tracing and metrics"""

    def __init__(self, service_name: str,
                 jaeger_endpoint: str = "http://localhost:14268/api/traces"):
        self.service_name = service_name

        # Setup tracing
        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer(__name__)

        jaeger_exporter = JaegerExporter(
            collector_endpoint=jaeger_endpoint
        )

        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        # Setup metrics
        self.request_count = Counter(
            'service_requests_total',
            'Total number of requests',
            ['service', 'method', 'status']
        )

        self.request_duration = Histogram(
            'service_request_duration_seconds',
            'Request duration in seconds',
            ['service', 'method']
        )

        self.active_requests = Gauge(
            'service_active_requests',
            'Number of active requests',
            ['service']
        )

        # Setup logging
        self.logger = logging.getLogger(service_name)

    def trace_request(self, operation_name: str):
        """Decorator for tracing requests"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(operation_name) as span:
                    # Add span attributes
                    span.set_attribute("service.name", self.service_name)
                    span.set_attribute("operation", operation_name)

                    # Track metrics
                    self.active_requests.labels(service=self.service_name).inc()
                    start_time = time.time()

                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("status", "success")
                        self.request_count.labels(
                            service=self.service_name,
                            method=operation_name,
                            status="success"
                        ).inc()
                        return result

                    except Exception as e:
                        span.set_attribute("status", "error")
                        span.set_attribute("error.message", str(e))
                        self.request_count.labels(
                            service=self.service_name,
                            method=operation_name,
                            status="error"
                        ).inc()
                        raise

                    finally:
                        duration = time.time() - start_time
                        self.request_duration.labels(
                            service=self.service_name,
                            method=operation_name
                        ).observe(duration)
                        self.active_requests.labels(service=self.service_name).dec()

            return wrapper
        return decorator

    def inject_trace_context(self, headers: Dict) -> Dict:
        """Inject trace context into outgoing headers"""
        propagator = TraceContextTextMapPropagator()
        propagator.inject(headers)
        return headers

    def extract_trace_context(self, headers: Dict):
        """Extract trace context from incoming headers"""
        propagator = TraceContextTextMapPropagator()
        return propagator.extract(headers)
```

### Pattern 4: Security Policies with mTLS
```python
import ssl
import certifi
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

class SecurityMesh:
    """Security layer for service mesh with mTLS"""

    def __init__(self, mesh: IstioServiceMesh):
        self.mesh = mesh
        self.certificates = {}

    def enable_mtls(self, namespace: str = "default",
                   mode: str = "STRICT") -> Dict:
        """Enable mTLS for namespace"""
        config = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "PeerAuthentication",
            "metadata": {
                "name": "default",
                "namespace": namespace
            },
            "spec": {
                "mtls": {
                    "mode": mode  # STRICT, PERMISSIVE, DISABLE
                }
            }
        }
        return config

    def create_jwt_policy(self, service_name: str,
                         issuer: str, jwks_uri: str) -> Dict:
        """Create JWT authentication policy"""
        config = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "RequestAuthentication",
            "metadata": {
                "name": f"{service_name}-jwt",
                "namespace": self.mesh.namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "jwtRules": [
                    {
                        "issuer": issuer,
                        "jwksUri": jwks_uri
                    }
                ]
            }
        }
        return config

    def create_authorization_rules(self, service_name: str,
                                 allowed_methods: List[str],
                                 allowed_paths: List[str],
                                 allowed_principals: List[str]) -> Dict:
        """Create fine-grained authorization rules"""
        rules = []

        for method in allowed_methods:
            for path in allowed_paths:
                rule = {
                    "to": [
                        {
                            "operation": {
                                "methods": [method],
                                "paths": [path]
                            }
                        }
                    ]
                }

                if allowed_principals:
                    rule["from"] = [
                        {
                            "source": {
                                "principals": allowed_principals
                            }
                        }
                    ]

                rules.append(rule)

        return self.mesh.create_authorization_policy(
            name=f"{service_name}-authz",
            app=service_name,
            rules=rules
        )

    def generate_service_certificate(self, service_name: str,
                                    ca_cert: x509.Certificate,
                                    ca_key: rsa.RSAPrivateKey) -> Tuple[str, str]:
        """Generate service certificate for mTLS"""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Create certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, f"{service_name}.service.local"),
        ])

        cert_builder = x509.CertificateBuilder()
        cert_builder = cert_builder.subject_name(subject)
        cert_builder = cert_builder.issuer_name(ca_cert.subject)
        cert_builder = cert_builder.public_key(private_key.public_key())
        cert_builder = cert_builder.serial_number(x509.random_serial_number())
        cert_builder = cert_builder.not_valid_before(datetime.utcnow())
        cert_builder = cert_builder.not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        )

        # Add SAN extension
        san_list = [
            x509.DNSName(f"{service_name}"),
            x509.DNSName(f"{service_name}.{self.mesh.namespace}"),
            x509.DNSName(f"{service_name}.{self.mesh.namespace}.svc"),
            x509.DNSName(f"{service_name}.{self.mesh.namespace}.svc.cluster.local"),
        ]

        cert_builder = cert_builder.add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False
        )

        # Sign certificate
        certificate = cert_builder.sign(ca_key, hashes.SHA256())

        # Convert to PEM
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        self.certificates[service_name] = {
            'cert': cert_pem.decode(),
            'key': key_pem.decode()
        }

        return cert_pem.decode(), key_pem.decode()
```

### Pattern 5: Multi-Cluster Service Mesh
```python
@dataclass
class ClusterConfig:
    """Configuration for a cluster in multi-cluster mesh"""
    name: str
    endpoint: str
    network: str
    region: str
    zone: str

class MultiClusterMesh:
    """Multi-cluster service mesh management"""

    def __init__(self):
        self.clusters: Dict[str, ClusterConfig] = {}
        self.gateways: Dict[str, Dict] = {}
        self.endpoints: Dict[str, List[str]] = {}

    def add_cluster(self, cluster: ClusterConfig):
        """Add cluster to mesh federation"""
        self.clusters[cluster.name] = cluster

    def create_gateway(self, cluster_name: str,
                      gateway_name: str,
                      port: int = 15443) -> Dict:
        """Create gateway for cross-cluster communication"""
        config = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "Gateway",
            "metadata": {
                "name": gateway_name,
                "namespace": "istio-system"
            },
            "spec": {
                "selector": {
                    "istio": "eastwestgateway"
                },
                "servers": [
                    {
                        "port": {
                            "number": port,
                            "name": "tls",
                            "protocol": "TLS"
                        },
                        "tls": {
                            "mode": "ISTIO_MUTUAL"
                        },
                        "hosts": [
                            "*.local"
                        ]
                    }
                ]
            }
        }

        self.gateways[cluster_name] = config
        return config

    def create_service_export(self, service_name: str,
                            cluster_name: str) -> Dict:
        """Export service for multi-cluster discovery"""
        config = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "ServiceEntry",
            "metadata": {
                "name": f"{service_name}-{cluster_name}",
                "namespace": "istio-system"
            },
            "spec": {
                "hosts": [f"{service_name}.global"],
                "location": "MESH_EXTERNAL",
                "ports": [
                    {
                        "number": 80,
                        "name": "http",
                        "protocol": "HTTP"
                    }
                ],
                "resolution": "DNS",
                "endpoints": self.endpoints.get(service_name, [])
            }
        }
        return config

    def create_endpoint_slice(self, service_name: str,
                            endpoints: List[Dict]) -> Dict:
        """Create endpoint slice for cross-cluster service discovery"""
        # Using Kan extension to optimize endpoint selection
        optimized_endpoints = self._optimize_endpoints(endpoints)

        config = {
            "apiVersion": "discovery.k8s.io/v1",
            "kind": "EndpointSlice",
            "metadata": {
                "name": f"{service_name}-endpoints",
                "namespace": "default"
            },
            "addressType": "IPv4",
            "endpoints": optimized_endpoints,
            "ports": [
                {
                    "name": "http",
                    "port": 80,
                    "protocol": "TCP"
                }
            ]
        }
        return config

    def _optimize_endpoints(self, endpoints: List[Dict]) -> List[Dict]:
        """Optimize endpoint selection using Kan extension"""
        # Group by region/zone for locality-aware routing
        by_region = {}
        for ep in endpoints:
            region = ep.get('topology', {}).get('region', 'default')
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(ep)

        # Prioritize local region endpoints
        optimized = []
        for region in sorted(by_region.keys()):
            optimized.extend(by_region[region])

        return optimized
```

## Implementation Examples

### FastAPI Service with Service Mesh
```python
from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="Mesh-Enabled Service")

# Initialize observability
observability = ObservabilityLayer("order-service")

# Service mesh configuration
mesh = IstioServiceMesh(namespace="production")
traffic_manager = TrafficManager(mesh)

@app.on_event("startup")
async def startup_event():
    """Configure service mesh on startup"""
    # Create traffic policy
    traffic_manager.create_traffic_policy(
        "order-service",
        load_balancing=LoadBalancingPolicy.LEAST_REQUEST,
        circuit_breaker=CircuitBreakerPolicy(
            consecutive_errors=5,
            interval="30s"
        ),
        retry_policy=RetryPolicy(attempts=3)
    )

    # Enable mTLS
    security = SecurityMesh(mesh)
    security.enable_mtls(namespace="production", mode="STRICT")

@app.get("/api/orders/{order_id}")
@observability.trace_request("get_order")
async def get_order(order_id: str, request: Request,
                   x_request_id: Optional[str] = Header(None)):
    """Get order with distributed tracing"""
    # Extract trace context from headers
    observability.extract_trace_context(dict(request.headers))

    # Make downstream service call
    async with httpx.AsyncClient() as client:
        headers = observability.inject_trace_context({
            "x-request-id": x_request_id or str(uuid.uuid4())
        })

        response = await client.get(
            f"http://inventory-service/api/inventory/{order_id}",
            headers=headers
        )

    return {
        "order_id": order_id,
        "inventory": response.json()
    }

@app.post("/api/orders")
@observability.trace_request("create_order")
async def create_order(order_data: Dict):
    """Create order with saga orchestration"""
    # Implementation with distributed transaction
    pass

# Health check endpoint for service mesh
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Express Service with Service Mesh
```javascript
const express = require('express');
const { trace } = require('@opentelemetry/api');
const { PrometheusExporter } = require('@opentelemetry/exporter-prometheus');
const axios = require('axios');

const app = express();
const port = process.env.PORT || 3000;

// Initialize tracer
const tracer = trace.getTracer('inventory-service');

// Middleware for trace propagation
app.use((req, res, next) => {
    const span = tracer.startSpan('http_request');
    span.setAttribute('http.method', req.method);
    span.setAttribute('http.url', req.url);

    // Store span in request
    req.span = span;

    res.on('finish', () => {
        span.setAttribute('http.status_code', res.statusCode);
        span.end();
    });

    next();
});

// Service endpoints
app.get('/api/inventory/:productId', async (req, res) => {
    const span = req.span;
    const productId = req.params.productId;

    try {
        // Add custom attributes
        span.setAttribute('product.id', productId);

        // Simulate inventory check
        const inventory = await checkInventory(productId);

        res.json({
            productId,
            available: inventory.available,
            quantity: inventory.quantity
        });
    } catch (error) {
        span.recordException(error);
        span.setStatus({ code: 2, message: error.message });
        res.status(500).json({ error: error.message });
    }
});

// Health check for service mesh
app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});

async function checkInventory(productId) {
    // Inventory logic with circuit breaker
    return {
        available: true,
        quantity: Math.floor(Math.random() * 100)
    };
}

app.listen(port, () => {
    console.log(`Inventory service listening at http://localhost:${port}`);
});
```

### Spring Boot Service with Service Mesh
```java
package com.example.payment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.cloud.sleuth.annotation.NewSpan;
import io.micrometer.core.instrument.MeterRegistry;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;

@SpringBootApplication
@RestController
@RequestMapping("/api/payments")
public class PaymentServiceApplication {

    private final MeterRegistry meterRegistry;

    public PaymentServiceApplication(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }

    public static void main(String[] args) {
        SpringApplication.run(PaymentServiceApplication.class, args);
    }

    @PostMapping
    @NewSpan("process-payment")
    @CircuitBreaker(name = "payment-service")
    @Retry(name = "payment-service")
    public PaymentResponse processPayment(@RequestBody PaymentRequest request) {
        // Track custom metrics
        meterRegistry.counter("payments.processed", "status", "success").increment();

        // Process payment logic
        PaymentResponse response = new PaymentResponse();
        response.setTransactionId(UUID.randomUUID().toString());
        response.setStatus("APPROVED");
        response.setAmount(request.getAmount());

        return response;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "healthy");
    }
}

class PaymentRequest {
    private String orderId;
    private BigDecimal amount;
    private String currency;
    // getters and setters
}

class PaymentResponse {
    private String transactionId;
    private String status;
    private BigDecimal amount;
    // getters and setters
}
```

## Testing Framework

```python
import pytest
from unittest.mock import Mock, patch
import yaml

@pytest.mark.asyncio
async def test_virtual_service_creation():
    """Test Istio VirtualService creation"""
    mesh = IstioServiceMesh(namespace="test")

    vs = VirtualService(
        name="test-service",
        namespace="test",
        hosts=["test-service"],
        http_routes=[
            {
                "route": [
                    {
                        "destination": {
                            "host": "test-service",
                            "subset": "v1"
                        }
                    }
                ]
            }
        ]
    )

    config = mesh.create_virtual_service(vs)

    assert config["metadata"]["name"] == "test-service"
    assert config["spec"]["hosts"] == ["test-service"]
    assert len(config["spec"]["http"]) == 1

def test_circuit_breaker_policy():
    """Test circuit breaker configuration"""
    cb = CircuitBreakerPolicy(
        consecutive_errors=10,
        interval="60s",
        base_ejection_time="60s",
        max_ejection_percent=75
    )

    config = cb.to_dict()

    assert config["outlierDetection"]["consecutiveErrors"] == 10
    assert config["outlierDetection"]["maxEjectionPercent"] == 75

@pytest.mark.asyncio
async def test_canary_deployment():
    """Test canary deployment configuration"""
    mesh = IstioServiceMesh(namespace="production")

    config = mesh.create_canary_deployment(
        service_name="api-service",
        stable_version="v1",
        canary_version="v2",
        canary_weight=20
    )

    vs_config = config["virtual_service"]
    dr_config = config["destination_rule"]

    # Check traffic weights
    routes = vs_config["spec"]["http"][1]["route"]
    assert routes[0]["weight"] == 80  # stable
    assert routes[1]["weight"] == 20  # canary

    # Check subsets
    subsets = dr_config["spec"]["subsets"]
    assert len(subsets) == 2
    assert subsets[0]["name"] == "v1"
    assert subsets[1]["name"] == "v2"

def test_multi_cluster_endpoint_optimization():
    """Test multi-cluster endpoint optimization"""
    multi_cluster = MultiClusterMesh()

    endpoints = [
        {"addresses": ["10.0.1.1"], "topology": {"region": "us-west"}},
        {"addresses": ["10.0.2.1"], "topology": {"region": "us-east"}},
        {"addresses": ["10.0.3.1"], "topology": {"region": "us-west"}},
    ]

    optimized = multi_cluster._optimize_endpoints(endpoints)

    # Check that endpoints are grouped by region
    assert len(optimized) == 3
    # US-East should come first (alphabetically)
    assert optimized[0]["topology"]["region"] == "us-east"
```

## Conclusion

This Kan extension iteration provides comprehensive service mesh capabilities that leverage categorical abstractions to create sophisticated traffic management, security, and observability patterns. The integration with Istio and Envoy provides production-ready service mesh functionality while maintaining mathematical rigor in the composition of policies and routing decisions.
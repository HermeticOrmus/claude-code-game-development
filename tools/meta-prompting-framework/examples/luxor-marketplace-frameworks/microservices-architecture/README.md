# Microservices Architecture Meta-Framework

## Overview

A comprehensive meta-framework for evolving from monolithic applications to self-healing microservices architectures. This framework provides structured progression through 7 levels of architectural maturity, with complete implementations in FastAPI, Express.js, and Spring Boot.

## Framework Structure

```
microservices-architecture/
├── framework.md                    # Main framework documentation
├── kan-iterations/                 # Kan extension iterations
│   ├── kan-extension-1.md         # Service Discovery Extensions
│   ├── kan-extension-2.md         # Event-Driven Extensions
│   ├── kan-extension-3.md         # Service Mesh Extensions
│   └── kan-extension-4.md         # Self-Healing Extensions
├── implementations/                # Working implementations
│   ├── fastapi/                   # Python/FastAPI implementation
│   │   └── order_service.py
│   ├── express/                   # Node.js/Express implementation
│   │   └── inventoryService.js
│   └── spring-boot/              # Java/Spring Boot implementation
│       └── PaymentService.java
├── configs/                       # Configuration files
│   └── docker-compose.yml
├── patterns/                      # Design patterns
└── README.md                      # This file
```

## 7 Levels of Microservices Maturity

### Level 1: Monolithic Application
- Single deployment unit
- Shared database and state
- Simple deployment model
- **Example**: Traditional web application

### Level 2: Service Separation
- Domain-driven decomposition
- Bounded contexts identification
- Service boundaries definition
- **Example**: Separate Order, Inventory, and Payment services

### Level 3: Microservices with Communication
- Independent services with APIs
- REST/messaging communication
- Database per service pattern
- **Example**: Services communicate via HTTP/REST

### Level 4: Service Discovery & Load Balancing
- Dynamic service registry (Consul/Eureka)
- Client/server-side load balancing
- Circuit breakers for resilience
- **Example**: Services register and discover each other

### Level 5: Event-Driven Architecture
- Asynchronous messaging (Kafka)
- Event sourcing and CQRS
- Saga pattern for distributed transactions
- **Example**: Order events trigger inventory and payment

### Level 6: Service Mesh Integration
- Sidecar proxies (Istio/Envoy)
- Traffic management and observability
- Distributed tracing (Jaeger)
- **Example**: Complete observability and control

### Level 7: Self-Healing Microservices
- Autonomous scaling with ML
- Failure prediction and prevention
- Chaos engineering validation
- **Example**: Services automatically recover from failures

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for FastAPI)
- Node.js 18+ (for Express)
- Java 17+ (for Spring Boot)
- Kubernetes (optional, for production)

### Running the Complete Stack

1. **Start infrastructure services**:
```bash
cd configs
docker-compose up -d consul kafka redis postgres prometheus jaeger
```

2. **Run FastAPI Order Service**:
```bash
cd implementations/fastapi
pip install -r requirements.txt
uvicorn order_service:app --reload --port 8000
```

3. **Run Express Inventory Service**:
```bash
cd implementations/express
npm install
node inventoryService.js
```

4. **Run Spring Boot Payment Service**:
```bash
cd implementations/spring-boot
./mvnw spring-boot:run
```

### Using Docker Compose

Run the entire microservices ecosystem:
```bash
cd configs
docker-compose up
```

Access services:
- Order Service: http://localhost:8000
- Inventory Service: http://localhost:3001
- Payment Service: http://localhost:8080
- Consul UI: http://localhost:8500
- Jaeger UI: http://localhost:16686
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Key Features

### Service Discovery (Level 4)
- Automatic service registration with Consul
- Health checking and failure detection
- Load balancing across instances

### Event-Driven Architecture (Level 5)
- Kafka for event streaming
- Saga pattern for distributed transactions
- Event sourcing for audit trails

### Service Mesh (Level 6)
- Envoy proxy for traffic management
- Distributed tracing with Jaeger
- Metrics collection with Prometheus
- mTLS for service-to-service security

### Self-Healing (Level 7)
- ML-based autonomous scaling
- Predictive failure detection
- Automatic recovery strategies
- Chaos engineering validation

## Implementation Examples

### Create an Order (Saga Pattern)
```python
# FastAPI implementation
@app.post("/api/orders")
async def create_order(order_data: CreateOrderRequest):
    saga = OrderSaga()
    order_id = await saga.create_order_saga(order_data)
    return {"order_id": order_id}
```

### Service Discovery
```javascript
// Express implementation
async function discoverService(serviceName) {
    const services = await consulClient.health.service(serviceName);
    return `http://${services[0].Service.Address}:${services[0].Service.Port}`;
}
```

### Circuit Breaker
```java
// Spring Boot implementation
@CircuitBreaker(name = "payment-processing", fallbackMethod = "fallback")
public PaymentResponse processPayment(PaymentRequest request) {
    // Process payment with automatic circuit breaking
}
```

## Testing

### Unit Tests
```bash
# FastAPI
pytest implementations/fastapi/tests/

# Express
npm test

# Spring Boot
./mvnw test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Chaos Engineering
```bash
# Inject failures to test self-healing
curl -X POST http://localhost:8000/chaos/inject-failure?type=latency
```

## Monitoring & Observability

### Metrics
- Prometheus metrics available at `/metrics` endpoint
- Grafana dashboards for visualization

### Tracing
- Distributed tracing with Jaeger
- Trace context propagation across services

### Logging
- Structured logging with correlation IDs
- Centralized log aggregation

## Kan Extension Iterations

### Iteration 1: Service Discovery
- Multi-registry aggregation
- Adaptive load balancing
- Predictive service discovery

### Iteration 2: Event-Driven
- Event sourcing implementation
- Saga pattern orchestration
- Complex event processing

### Iteration 3: Service Mesh
- Istio/Envoy integration
- Traffic management policies
- Security with mTLS

### Iteration 4: Self-Healing
- Autonomous scaling with ML
- Failure prediction engine
- Chaos engineering platform

## Best Practices

1. **Service Design**
   - Single responsibility principle
   - API-first development
   - Proper versioning strategy

2. **Data Management**
   - Database per service
   - Event sourcing for audit
   - CQRS for read/write optimization

3. **Resilience**
   - Circuit breakers everywhere
   - Retry with exponential backoff
   - Bulkhead isolation

4. **Security**
   - mTLS between services
   - JWT for authentication
   - API gateway for external access

5. **Deployment**
   - Container orchestration (Kubernetes)
   - Blue-green deployments
   - Feature flags for gradual rollout

## Production Deployment

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
      - name: order-service
        image: order-service:latest
        ports:
        - containerPort: 8000
```

### Istio Service Mesh
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
  - order-service
  http:
  - route:
    - destination:
        host: order-service
        subset: v2
      weight: 20  # Canary deployment
    - destination:
        host: order-service
        subset: v1
      weight: 80
```

## Troubleshooting

### Service Discovery Issues
- Check Consul UI at http://localhost:8500
- Verify service health checks
- Review service registration logs

### Event Processing Issues
- Check Kafka topics: `kafka-topics --list --bootstrap-server localhost:9092`
- Monitor consumer lag
- Review event processing logs

### Performance Issues
- Check Jaeger for slow traces
- Review Prometheus metrics
- Analyze service mesh metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## Resources

- [Microservices Patterns](https://microservices.io/patterns/)
- [Domain-Driven Design](https://dddcommunity.org/)
- [Istio Documentation](https://istio.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## License

MIT License - See LICENSE file for details

## Support

For questions and support:
- Create an issue in the repository
- Check the documentation in `/framework.md`
- Review the Kan extensions for advanced patterns
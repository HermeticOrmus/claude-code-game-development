"""
Order Service - FastAPI Microservice Implementation
Demonstrates all 7 levels of the microservices architecture framework
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import httpx
import asyncio
import json
import uuid
import logging
from enum import Enum
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import consul
from circuitbreaker import circuit
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Order Service",
    description="Microservice for order management",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration (Level 3: Database per service)
DATABASE_URL = "postgresql+asyncpg://user:password@postgres:5432/orders"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Metrics (Level 6: Observability)
request_count = Counter('order_service_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('order_service_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
active_orders = Gauge('order_service_active_orders', 'Number of active orders')

# Service discovery client (Level 4)
consul_client = consul.Consul(host='consul', port=8500)

# Redis for caching
redis_client = None

# Kafka producer for events (Level 5)
kafka_producer = None

# Models
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class CreateOrderRequest(BaseModel):
    customer_id: str
    items: List[OrderItem]
    shipping_address: Dict[str, Any]
    payment_method: str

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    status = Column(String, default=OrderStatus.PENDING)
    total_amount = Column(Float)
    items = Column(JSON)
    shipping_address = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderResponse(BaseModel):
    id: str
    customer_id: str
    status: OrderStatus
    total_amount: float
    items: List[OrderItem]
    created_at: datetime

# Service Discovery (Level 4)
async def register_service():
    """Register service with Consul"""
    try:
        consul_client.agent.service.register(
            name="order-service",
            service_id="order-service-1",
            address="order-service",
            port=8000,
            tags=["v2", "production"],
            check=consul.Check.http("http://order-service:8000/health", interval="10s")
        )
        logger.info("Service registered with Consul")
    except Exception as e:
        logger.error(f"Failed to register with Consul: {e}")

async def discover_service(service_name: str) -> Optional[str]:
    """Discover service using Consul"""
    try:
        _, services = consul_client.health.service(service_name, passing=True)
        if services:
            service = services[0]
            address = service['Service']['Address']
            port = service['Service']['Port']
            return f"http://{address}:{port}"
    except Exception as e:
        logger.error(f"Service discovery failed: {e}")
    return None

# Circuit Breaker (Level 4/6)
@circuit(failure_threshold=5, recovery_timeout=30)
async def call_inventory_service(product_ids: List[str]) -> Dict:
    """Call inventory service with circuit breaker"""
    inventory_url = await discover_service("inventory-service")
    if not inventory_url:
        raise HTTPException(status_code=503, detail="Inventory service unavailable")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{inventory_url}/api/inventory/check",
            json={"product_ids": product_ids},
            timeout=5.0
        )
        response.raise_for_status()
        return response.json()

# Event Publishing (Level 5)
async def publish_event(event_type: str, data: Dict):
    """Publish event to Kafka"""
    if kafka_producer:
        try:
            event = {
                "id": str(uuid.uuid4()),
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            await kafka_producer.send(
                "order-events",
                value=json.dumps(event).encode()
            )
            logger.info(f"Published event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

# Saga Pattern (Level 5)
class OrderSaga:
    """Saga orchestrator for order processing"""

    async def create_order_saga(self, order_data: CreateOrderRequest) -> str:
        """Execute order creation saga"""
        saga_id = str(uuid.uuid4())
        order_id = str(uuid.uuid4())

        try:
            # Step 1: Check inventory
            inventory_result = await self.reserve_inventory(order_data.items)

            # Step 2: Process payment
            payment_result = await self.process_payment(
                order_id,
                order_data.customer_id,
                self.calculate_total(order_data.items)
            )

            # Step 3: Create order
            order = await self.create_order_record(order_id, order_data)

            # Step 4: Send confirmation
            await self.send_confirmation(order_id, order_data.customer_id)

            # Publish success event
            await publish_event("order_created", {"order_id": order_id})

            return order_id

        except Exception as e:
            # Compensate on failure
            await self.compensate_order(saga_id, order_id)
            raise HTTPException(status_code=400, detail=str(e))

    async def reserve_inventory(self, items: List[OrderItem]) -> Dict:
        """Reserve inventory (with compensation support)"""
        product_ids = [item.product_id for item in items]
        return await call_inventory_service(product_ids)

    async def process_payment(self, order_id: str, customer_id: str, amount: float) -> Dict:
        """Process payment through payment service"""
        payment_url = await discover_service("payment-service")
        if not payment_url:
            raise Exception("Payment service unavailable")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{payment_url}/api/payments",
                json={
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "amount": amount
                }
            )
            response.raise_for_status()
            return response.json()

    async def create_order_record(self, order_id: str, order_data: CreateOrderRequest) -> Order:
        """Create order in database"""
        async with async_session() as session:
            order = Order(
                id=order_id,
                customer_id=order_data.customer_id,
                status=OrderStatus.CONFIRMED,
                total_amount=self.calculate_total(order_data.items),
                items=[item.dict() for item in order_data.items],
                shipping_address=order_data.shipping_address
            )
            session.add(order)
            await session.commit()
            return order

    async def send_confirmation(self, order_id: str, customer_id: str):
        """Send order confirmation"""
        await publish_event("order_confirmation_sent", {
            "order_id": order_id,
            "customer_id": customer_id
        })

    async def compensate_order(self, saga_id: str, order_id: str):
        """Compensate failed order creation"""
        logger.error(f"Compensating saga {saga_id} for order {order_id}")
        await publish_event("order_compensation", {
            "saga_id": saga_id,
            "order_id": order_id
        })

    def calculate_total(self, items: List[OrderItem]) -> float:
        """Calculate order total"""
        return sum(item.quantity * item.price for item in items)

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global redis_client, kafka_producer

    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Register with service discovery
    await register_service()

    # Initialize Redis
    redis_client = await redis.create_redis_pool('redis://redis:6379')

    # Initialize Kafka producer
    kafka_producer = AIOKafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v).encode()
    )
    await kafka_producer.start()

    logger.info("Order service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if redis_client:
        redis_client.close()
        await redis_client.wait_closed()

    if kafka_producer:
        await kafka_producer.stop()

    # Deregister from Consul
    consul_client.agent.service.deregister("order-service-1")

@app.post("/api/orders", response_model=OrderResponse)
async def create_order(
    order_data: CreateOrderRequest,
    background_tasks: BackgroundTasks,
    x_request_id: Optional[str] = Header(None)
):
    """Create new order using saga pattern"""
    request_count.labels(method="POST", endpoint="/api/orders", status="processing").inc()

    with request_duration.labels(method="POST", endpoint="/api/orders").time():
        saga = OrderSaga()
        order_id = await saga.create_order_saga(order_data)

        # Get created order
        async with async_session() as session:
            order = await session.get(Order, order_id)

        active_orders.inc()

        # Background task for async processing
        background_tasks.add_task(process_order_async, order_id)

        return OrderResponse(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            total_amount=order.total_amount,
            items=[OrderItem(**item) for item in order.items],
            created_at=order.created_at
        )

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """Get order by ID with caching"""
    # Check cache first
    if redis_client:
        cached = await redis_client.get(f"order:{order_id}")
        if cached:
            return json.loads(cached)

    async with async_session() as session:
        order = await session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

    response = OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        total_amount=order.total_amount,
        items=[OrderItem(**item) for item in order.items],
        created_at=order.created_at
    )

    # Cache result
    if redis_client:
        await redis_client.setex(
            f"order:{order_id}",
            300,  # 5 minutes TTL
            json.dumps(response.dict(), default=str)
        )

    return response

@app.patch("/api/orders/{order_id}/status")
async def update_order_status(order_id: str, status: OrderStatus):
    """Update order status and emit event"""
    async with async_session() as session:
        order = await session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        old_status = order.status
        order.status = status
        order.updated_at = datetime.utcnow()
        await session.commit()

    # Publish status change event
    await publish_event("order_status_changed", {
        "order_id": order_id,
        "old_status": old_status,
        "new_status": status
    })

    # Invalidate cache
    if redis_client:
        await redis_client.delete(f"order:{order_id}")

    return {"message": "Status updated successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint for service mesh"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "dependencies": {}
    }

    # Check database
    try:
        async with async_session() as session:
            await session.execute("SELECT 1")
        health_status["dependencies"]["database"] = "healthy"
    except:
        health_status["dependencies"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check Redis
    if redis_client:
        try:
            await redis_client.ping()
            health_status["dependencies"]["redis"] = "healthy"
        except:
            health_status["dependencies"]["redis"] = "unhealthy"

    # Check Kafka
    if kafka_producer:
        health_status["dependencies"]["kafka"] = "healthy"

    return health_status

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

async def process_order_async(order_id: str):
    """Async order processing"""
    await asyncio.sleep(2)  # Simulate processing
    logger.info(f"Order {order_id} processed asynchronously")

# Event Consumer (Level 5)
async def consume_events():
    """Consume events from Kafka"""
    consumer = AIOKafkaConsumer(
        'order-events',
        bootstrap_servers='kafka:9092',
        group_id='order-service-consumer',
        value_deserializer=lambda v: json.loads(v.decode())
    )
    await consumer.start()

    try:
        async for msg in consumer:
            event = msg.value
            logger.info(f"Received event: {event['type']}")
            # Process event based on type
    finally:
        await consumer.stop()

# Self-Healing Integration (Level 7)
class SelfHealingMonitor:
    """Monitor for self-healing capabilities"""

    async def check_health_metrics(self):
        """Check service health metrics"""
        # Monitor error rate, latency, resource usage
        pass

    async def trigger_healing(self, issue_type: str):
        """Trigger self-healing action"""
        await publish_event("healing_triggered", {
            "service": "order-service",
            "issue_type": issue_type,
            "timestamp": datetime.utcnow().isoformat()
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
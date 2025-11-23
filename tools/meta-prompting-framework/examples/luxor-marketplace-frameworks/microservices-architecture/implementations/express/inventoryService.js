/**
 * Inventory Service - Express.js Microservice Implementation
 * Demonstrates all 7 levels of the microservices architecture framework
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const { v4: uuidv4 } = require('uuid');
const consul = require('consul');
const { Kafka } = require('kafkajs');
const Redis = require('ioredis');
const { Pool } = require('pg');
const CircuitBreaker = require('opossum');
const promClient = require('prom-client');
const { trace, context, SpanStatusCode } = require('@opentelemetry/api');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');

// Initialize Express app
const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Level 3: Database per service (PostgreSQL)
const pgPool = new Pool({
    host: process.env.DB_HOST || 'postgres',
    port: process.env.DB_PORT || 5432,
    database: 'inventory',
    user: process.env.DB_USER || 'user',
    password: process.env.DB_PASSWORD || 'password',
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
});

// Level 4: Service Discovery (Consul)
const consulClient = consul({
    host: process.env.CONSUL_HOST || 'consul',
    port: process.env.CONSUL_PORT || 8500,
    promisify: true
});

// Register service with Consul
async function registerService() {
    try {
        await consulClient.agent.service.register({
            name: 'inventory-service',
            id: 'inventory-service-1',
            address: 'inventory-service',
            port: 3000,
            tags: ['v2', 'production'],
            check: {
                http: 'http://inventory-service:3000/health',
                interval: '10s'
            }
        });
        console.log('Service registered with Consul');
    } catch (error) {
        console.error('Failed to register with Consul:', error);
    }
}

// Discover services
async function discoverService(serviceName) {
    try {
        const services = await consulClient.health.service(serviceName);
        if (services && services[0]) {
            const service = services[0].Service;
            return `http://${service.Address}:${service.Port}`;
        }
    } catch (error) {
        console.error(`Service discovery failed for ${serviceName}:`, error);
    }
    return null;
}

// Level 5: Event-Driven Architecture (Kafka)
const kafka = new Kafka({
    clientId: 'inventory-service',
    brokers: [process.env.KAFKA_BROKER || 'kafka:9092'],
    retry: {
        initialRetryTime: 100,
        retries: 8
    }
});

const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: 'inventory-group' });

// Publish event to Kafka
async function publishEvent(eventType, data) {
    try {
        await producer.send({
            topic: 'inventory-events',
            messages: [{
                key: uuidv4(),
                value: JSON.stringify({
                    id: uuidv4(),
                    type: eventType,
                    timestamp: new Date().toISOString(),
                    data: data
                })
            }]
        });
        console.log(`Published event: ${eventType}`);
    } catch (error) {
        console.error('Failed to publish event:', error);
    }
}

// Level 6: Service Mesh Integration (Metrics & Tracing)
const register = new promClient.Registry();

// Define metrics
const httpRequestDuration = new promClient.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status'],
    registers: [register]
});

const inventoryGauge = new promClient.Gauge({
    name: 'inventory_items_total',
    help: 'Total number of inventory items',
    labelNames: ['product_id'],
    registers: [register]
});

// Initialize tracer
const tracer = trace.getTracer('inventory-service', '1.0.0');

// Redis for caching
const redis = new Redis({
    host: process.env.REDIS_HOST || 'redis',
    port: process.env.REDIS_PORT || 6379,
    retryStrategy: (times) => Math.min(times * 50, 2000)
});

// Circuit Breaker for external service calls
const circuitBreakerOptions = {
    timeout: 3000,
    errorThresholdPercentage: 50,
    resetTimeout: 30000
};

// Level 7: Self-Healing Patterns
class SelfHealingMonitor {
    constructor() {
        this.healthMetrics = {
            errorRate: 0,
            latency: [],
            memoryUsage: 0,
            cpuUsage: 0
        };
        this.startMonitoring();
    }

    startMonitoring() {
        setInterval(() => {
            this.collectMetrics();
            this.checkHealth();
        }, 10000); // Every 10 seconds
    }

    collectMetrics() {
        // Collect system metrics
        const usage = process.memoryUsage();
        this.healthMetrics.memoryUsage = usage.heapUsed / usage.heapTotal;

        // In production, integrate with actual metrics
        this.healthMetrics.cpuUsage = Math.random() * 0.8;
    }

    async checkHealth() {
        // Check for anomalies
        if (this.healthMetrics.errorRate > 0.1) {
            await this.triggerHealing('high_error_rate');
        }
        if (this.healthMetrics.memoryUsage > 0.9) {
            await this.triggerHealing('memory_pressure');
        }
    }

    async triggerHealing(issueType) {
        console.log(`Triggering self-healing for: ${issueType}`);
        await publishEvent('healing_required', {
            service: 'inventory-service',
            issue: issueType,
            metrics: this.healthMetrics
        });

        // Implement healing strategies
        switch (issueType) {
            case 'high_error_rate':
                // Circuit breaker activation
                break;
            case 'memory_pressure':
                // Force garbage collection
                if (global.gc) {
                    global.gc();
                }
                break;
        }
    }

    recordError() {
        this.healthMetrics.errorRate =
            (this.healthMetrics.errorRate * 0.9) + 0.1;
    }

    recordSuccess() {
        this.healthMetrics.errorRate =
            (this.healthMetrics.errorRate * 0.9);
    }
}

const selfHealingMonitor = new SelfHealingMonitor();

// Saga Pattern Implementation (Level 5)
class InventorySaga {
    async reserveInventory(items) {
        const span = tracer.startSpan('reserve_inventory');
        const reservationId = uuidv4();

        try {
            // Start transaction
            const client = await pgPool.connect();
            await client.query('BEGIN');

            const reservations = [];
            for (const item of items) {
                const result = await client.query(
                    'UPDATE inventory SET reserved = reserved + $1 WHERE product_id = $2 AND available >= $1 RETURNING *',
                    [item.quantity, item.product_id]
                );

                if (result.rows.length === 0) {
                    throw new Error(`Insufficient inventory for product ${item.product_id}`);
                }

                reservations.push({
                    product_id: item.product_id,
                    quantity: item.quantity,
                    reservation_id: reservationId
                });
            }

            await client.query('COMMIT');
            client.release();

            // Publish reservation event
            await publishEvent('inventory_reserved', {
                reservation_id: reservationId,
                items: reservations
            });

            span.setStatus({ code: SpanStatusCode.OK });
            return { success: true, reservation_id: reservationId, reservations };

        } catch (error) {
            span.recordException(error);
            span.setStatus({ code: SpanStatusCode.ERROR });

            // Compensate
            await this.releaseReservation(reservationId);
            throw error;
        } finally {
            span.end();
        }
    }

    async releaseReservation(reservationId) {
        console.log(`Compensating: Releasing reservation ${reservationId}`);
        await publishEvent('reservation_released', { reservation_id: reservationId });
    }
}

const inventorySaga = new InventorySaga();

// API Routes
app.post('/api/inventory/check', async (req, res) => {
    const startTime = Date.now();
    const span = tracer.startSpan('check_inventory');

    try {
        const { product_ids } = req.body;

        // Check cache first
        const cacheKey = `inventory:${product_ids.join(',')}`;
        const cached = await redis.get(cacheKey);
        if (cached) {
            return res.json(JSON.parse(cached));
        }

        // Query database
        const query = 'SELECT * FROM inventory WHERE product_id = ANY($1)';
        const result = await pgPool.query(query, [product_ids]);

        const inventory = result.rows.map(row => ({
            product_id: row.product_id,
            available: row.available - row.reserved,
            reserved: row.reserved,
            total: row.available
        }));

        // Cache result
        await redis.setex(cacheKey, 300, JSON.stringify(inventory));

        // Update metrics
        httpRequestDuration.labels('POST', '/api/inventory/check', '200')
            .observe((Date.now() - startTime) / 1000);

        selfHealingMonitor.recordSuccess();
        res.json(inventory);

    } catch (error) {
        span.recordException(error);
        httpRequestDuration.labels('POST', '/api/inventory/check', '500')
            .observe((Date.now() - startTime) / 1000);

        selfHealingMonitor.recordError();
        res.status(500).json({ error: error.message });
    } finally {
        span.end();
    }
});

app.post('/api/inventory/reserve', async (req, res) => {
    const startTime = Date.now();

    try {
        const { items } = req.body;
        const result = await inventorySaga.reserveInventory(items);

        httpRequestDuration.labels('POST', '/api/inventory/reserve', '200')
            .observe((Date.now() - startTime) / 1000);

        res.json(result);
    } catch (error) {
        httpRequestDuration.labels('POST', '/api/inventory/reserve', '500')
            .observe((Date.now() - startTime) / 1000);

        res.status(500).json({ error: error.message });
    }
});

app.put('/api/inventory/:productId', async (req, res) => {
    try {
        const { productId } = req.params;
        const { quantity, operation } = req.body;

        let query;
        if (operation === 'add') {
            query = 'UPDATE inventory SET available = available + $1 WHERE product_id = $2 RETURNING *';
        } else if (operation === 'remove') {
            query = 'UPDATE inventory SET available = available - $1 WHERE product_id = $2 RETURNING *';
        }

        const result = await pgPool.query(query, [quantity, productId]);

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Product not found' });
        }

        // Invalidate cache
        await redis.del(`inventory:*`);

        // Update gauge
        inventoryGauge.labels(productId).set(result.rows[0].available);

        // Publish event
        await publishEvent('inventory_updated', {
            product_id: productId,
            operation,
            quantity,
            new_total: result.rows[0].available
        });

        res.json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Health check endpoint
app.get('/health', async (req, res) => {
    const health = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '2.0.0',
        dependencies: {}
    };

    // Check database
    try {
        await pgPool.query('SELECT 1');
        health.dependencies.database = 'healthy';
    } catch {
        health.dependencies.database = 'unhealthy';
        health.status = 'degraded';
    }

    // Check Redis
    try {
        await redis.ping();
        health.dependencies.redis = 'healthy';
    } catch {
        health.dependencies.redis = 'unhealthy';
    }

    // Check Kafka
    const kafkaHealthy = producer._producer && producer._producer.isConnected();
    health.dependencies.kafka = kafkaHealthy ? 'healthy' : 'unhealthy';

    res.json(health);
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
    res.set('Content-Type', register.contentType);
    register.metrics().then(metrics => {
        res.send(metrics);
    });
});

// Event consumer
async function startEventConsumer() {
    await consumer.connect();
    await consumer.subscribe({ topic: 'order-events', fromBeginning: false });

    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            const event = JSON.parse(message.value.toString());
            console.log(`Received event: ${event.type}`);

            // Handle different event types
            switch (event.type) {
                case 'order_created':
                    // Update inventory based on order
                    break;
                case 'order_cancelled':
                    // Restore inventory
                    break;
            }
        }
    });
}

// Circuit breaker for calling order service
const callOrderService = new CircuitBreaker(
    async (orderId) => {
        const orderServiceUrl = await discoverService('order-service');
        if (!orderServiceUrl) {
            throw new Error('Order service not available');
        }

        const response = await fetch(`${orderServiceUrl}/api/orders/${orderId}`);
        if (!response.ok) {
            throw new Error(`Order service returned ${response.status}`);
        }
        return response.json();
    },
    circuitBreakerOptions
);

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('SIGTERM received, shutting down gracefully');

    // Deregister from Consul
    await consulClient.agent.service.deregister('inventory-service-1');

    // Close connections
    await producer.disconnect();
    await consumer.disconnect();
    await redis.quit();
    await pgPool.end();

    process.exit(0);
});

// Initialize database schema
async function initDatabase() {
    try {
        await pgPool.query(`
            CREATE TABLE IF NOT EXISTS inventory (
                product_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255),
                available INTEGER DEFAULT 0,
                reserved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);
        console.log('Database initialized');
    } catch (error) {
        console.error('Failed to initialize database:', error);
    }
}

// Start server
async function startServer() {
    try {
        // Initialize database
        await initDatabase();

        // Register with Consul
        await registerService();

        // Connect to Kafka
        await producer.connect();
        await startEventConsumer();

        // Start Express server
        app.listen(port, () => {
            console.log(`Inventory service listening at http://localhost:${port}`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

startServer();

module.exports = app;
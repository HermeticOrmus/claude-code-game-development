/**
 * Payment Service - Spring Boot Microservice Implementation
 * Demonstrates all 7 levels of the microservices architecture framework
 */

package com.example.payment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.cloud.netflix.hystrix.EnableHystrix;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.cloud.stream.annotation.EnableBinding;
import org.springframework.cloud.stream.annotation.StreamListener;
import org.springframework.cloud.stream.messaging.Processor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;

import io.micrometer.core.annotation.Timed;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import com.netflix.hystrix.contrib.javanica.annotation.HystrixCommand;
import com.netflix.hystrix.contrib.javanica.annotation.HystrixProperty;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.github.resilience4j.bulkhead.annotation.Bulkhead;
import io.github.resilience4j.ratelimiter.annotation.RateLimiter;
import org.springframework.cloud.sleuth.annotation.NewSpan;
import org.springframework.cloud.sleuth.annotation.SpanTag;

import javax.persistence.*;
import javax.validation.Valid;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ThreadLocalRandom;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

// Level 1-2: Service Separation
@SpringBootApplication
@EnableDiscoveryClient  // Level 4: Service Discovery (Consul/Eureka)
@EnableFeignClients     // Level 3: Microservices Communication
@EnableHystrix          // Level 4: Circuit Breaker
@EnableKafka            // Level 5: Event-Driven Architecture
@EnableScheduling       // Level 7: Self-Healing
@Slf4j
public class PaymentServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(PaymentServiceApplication.class, args);
    }

    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

// Configuration for Service Mesh Integration (Level 6)
@Configuration
class ServiceMeshConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        return template;
    }
}

// Domain Models
@Entity
@Table(name = "payments")
@Data
class Payment {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @NotNull
    private String orderId;

    @NotNull
    private String customerId;

    @NotNull
    @Positive
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    private PaymentStatus status;

    @Enumerated(EnumType.STRING)
    private PaymentMethod method;

    private String transactionId;
    private String failureReason;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

enum PaymentStatus {
    PENDING, PROCESSING, COMPLETED, FAILED, REFUNDED
}

enum PaymentMethod {
    CREDIT_CARD, DEBIT_CARD, PAYPAL, BANK_TRANSFER, CRYPTO
}

// Repository (Level 3: Database per service)
interface PaymentRepository extends JpaRepository<Payment, String> {
    List<Payment> findByOrderId(String orderId);
    List<Payment> findByCustomerId(String customerId);
    List<Payment> findByStatus(PaymentStatus status);
}

// DTOs
@Data
class PaymentRequest {
    @NotNull
    private String orderId;
    @NotNull
    private String customerId;
    @NotNull
    @Positive
    private BigDecimal amount;
    @NotNull
    private PaymentMethod method;
    private Map<String, String> metadata;
}

@Data
class PaymentResponse {
    private String paymentId;
    private String transactionId;
    private PaymentStatus status;
    private BigDecimal amount;
    private LocalDateTime timestamp;
}

// Event Models (Level 5)
@Data
class PaymentEvent {
    private String eventId = UUID.randomUUID().toString();
    private String eventType;
    private String paymentId;
    private String orderId;
    private PaymentStatus status;
    private LocalDateTime timestamp = LocalDateTime.now();
    private Map<String, Object> data;
}

// Service Layer with Saga Pattern (Level 5)
@Service
@RequiredArgsConstructor
@Slf4j
class PaymentService {

    private final PaymentRepository paymentRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final RedisTemplate<String, Object> redisTemplate;
    private final RestTemplate restTemplate;
    private final MeterRegistry meterRegistry;

    @Transactional
    @NewSpan("process-payment")
    @CircuitBreaker(name = "payment-processing", fallbackMethod = "fallbackProcessPayment")
    @Retry(name = "payment-processing")
    public PaymentResponse processPayment(@SpanTag("order.id") PaymentRequest request) {
        log.info("Processing payment for order: {}", request.getOrderId());

        // Create payment record
        Payment payment = new Payment();
        payment.setOrderId(request.getOrderId());
        payment.setCustomerId(request.getCustomerId());
        payment.setAmount(request.getAmount());
        payment.setMethod(request.getMethod());
        payment.setStatus(PaymentStatus.PROCESSING);

        payment = paymentRepository.save(payment);

        try {
            // Simulate payment processing
            String transactionId = processWithPaymentGateway(payment);
            payment.setTransactionId(transactionId);
            payment.setStatus(PaymentStatus.COMPLETED);

            // Update metrics
            meterRegistry.counter("payments.processed", "status", "success").increment();

            // Publish success event
            publishPaymentEvent(payment, "payment.completed");

            // Cache result
            cachePayment(payment);

        } catch (Exception e) {
            log.error("Payment processing failed", e);
            payment.setStatus(PaymentStatus.FAILED);
            payment.setFailureReason(e.getMessage());

            // Update metrics
            meterRegistry.counter("payments.processed", "status", "failed").increment();

            // Publish failure event
            publishPaymentEvent(payment, "payment.failed");

            // Trigger compensation
            compensatePayment(payment);
        }

        payment = paymentRepository.save(payment);

        return mapToResponse(payment);
    }

    // Circuit Breaker Fallback
    public PaymentResponse fallbackProcessPayment(PaymentRequest request, Exception ex) {
        log.error("Circuit breaker activated for payment processing", ex);

        PaymentResponse response = new PaymentResponse();
        response.setStatus(PaymentStatus.FAILED);
        response.setTimestamp(LocalDateTime.now());

        // Store for retry
        redisTemplate.opsForList().rightPush("failed-payments", request);

        return response;
    }

    @HystrixCommand(
        fallbackMethod = "fallbackPaymentGateway",
        commandProperties = {
            @HystrixProperty(name = "execution.isolation.thread.timeoutInMilliseconds", value = "3000"),
            @HystrixProperty(name = "circuitBreaker.requestVolumeThreshold", value = "10"),
            @HystrixProperty(name = "circuitBreaker.errorThresholdPercentage", value = "50")
        }
    )
    private String processWithPaymentGateway(Payment payment) throws Exception {
        // Simulate external payment gateway call
        Thread.sleep(ThreadLocalRandom.current().nextInt(100, 500));

        if (ThreadLocalRandom.current().nextDouble() > 0.9) {
            throw new RuntimeException("Payment gateway timeout");
        }

        return "TXN_" + UUID.randomUUID().toString();
    }

    private String fallbackPaymentGateway(Payment payment) {
        log.warn("Using fallback payment gateway");
        return "FALLBACK_TXN_" + UUID.randomUUID().toString();
    }

    private void publishPaymentEvent(Payment payment, String eventType) {
        PaymentEvent event = new PaymentEvent();
        event.setEventType(eventType);
        event.setPaymentId(payment.getId());
        event.setOrderId(payment.getOrderId());
        event.setStatus(payment.getStatus());

        kafkaTemplate.send("payment-events", event);
        log.info("Published event: {}", eventType);
    }

    private void cachePayment(Payment payment) {
        String key = "payment:" + payment.getId();
        redisTemplate.opsForValue().set(key, payment);
        redisTemplate.expire(key, 300, java.util.concurrent.TimeUnit.SECONDS);
    }

    private void compensatePayment(Payment payment) {
        log.info("Compensating failed payment: {}", payment.getId());

        // Release reserved funds
        // Notify order service
        // Update inventory

        PaymentEvent compensationEvent = new PaymentEvent();
        compensationEvent.setEventType("payment.compensation");
        compensationEvent.setPaymentId(payment.getId());
        compensationEvent.setOrderId(payment.getOrderId());

        kafkaTemplate.send("compensation-events", compensationEvent);
    }

    private PaymentResponse mapToResponse(Payment payment) {
        PaymentResponse response = new PaymentResponse();
        response.setPaymentId(payment.getId());
        response.setTransactionId(payment.getTransactionId());
        response.setStatus(payment.getStatus());
        response.setAmount(payment.getAmount());
        response.setTimestamp(payment.getCreatedAt());
        return response;
    }
}

// REST Controller
@RestController
@RequestMapping("/api/payments")
@RequiredArgsConstructor
@Slf4j
class PaymentController {

    private final PaymentService paymentService;
    private final PaymentRepository paymentRepository;

    @PostMapping
    @Timed(value = "payment.processing.time", description = "Payment processing time")
    @RateLimiter(name = "payment-api")
    public PaymentResponse createPayment(@Valid @RequestBody PaymentRequest request) {
        return paymentService.processPayment(request);
    }

    @GetMapping("/{paymentId}")
    @Bulkhead(name = "payment-api")
    public Payment getPayment(@PathVariable String paymentId) {
        return paymentRepository.findById(paymentId)
            .orElseThrow(() -> new RuntimeException("Payment not found"));
    }

    @PostMapping("/{paymentId}/refund")
    @Transactional
    public PaymentResponse refundPayment(@PathVariable String paymentId) {
        Payment payment = paymentRepository.findById(paymentId)
            .orElseThrow(() -> new RuntimeException("Payment not found"));

        payment.setStatus(PaymentStatus.REFUNDED);
        payment = paymentRepository.save(payment);

        return paymentService.mapToResponse(payment);
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("timestamp", LocalDateTime.now());
        health.put("service", "payment-service");
        health.put("version", "2.0.0");
        return health;
    }
}

// Event Listeners (Level 5: Event-Driven)
@Component
@RequiredArgsConstructor
@Slf4j
class PaymentEventListener {

    private final PaymentService paymentService;

    @KafkaListener(topics = "order-events", groupId = "payment-service")
    public void handleOrderEvent(String event) {
        log.info("Received order event: {}", event);
        // Process order events
    }

    @StreamListener(Processor.INPUT)
    @SendTo(Processor.OUTPUT)
    public PaymentEvent handleStreamEvent(Map<String, Object> event) {
        log.info("Processing stream event: {}", event);

        PaymentEvent response = new PaymentEvent();
        response.setEventType("payment.stream.processed");
        response.setData(event);

        return response;
    }
}

// Self-Healing Component (Level 7)
@Component
@RequiredArgsConstructor
@Slf4j
class SelfHealingManager {

    private final PaymentRepository paymentRepository;
    private final PaymentService paymentService;
    private final RedisTemplate<String, Object> redisTemplate;
    private final MeterRegistry meterRegistry;

    @Scheduled(fixedDelay = 60000) // Every minute
    public void monitorHealth() {
        // Monitor service health metrics
        double errorRate = calculateErrorRate();
        double responseTime = calculateAverageResponseTime();

        if (errorRate > 0.1) { // 10% error threshold
            triggerHealing("high_error_rate", errorRate);
        }

        if (responseTime > 1000) { // 1 second threshold
            triggerHealing("high_response_time", responseTime);
        }
    }

    @Scheduled(fixedDelay = 30000) // Every 30 seconds
    public void retryFailedPayments() {
        log.info("Checking for failed payments to retry");

        List<Object> failedPayments = redisTemplate.opsForList()
            .range("failed-payments", 0, -1);

        for (Object payment : failedPayments) {
            if (payment instanceof PaymentRequest) {
                try {
                    paymentService.processPayment((PaymentRequest) payment);
                    redisTemplate.opsForList().remove("failed-payments", 1, payment);
                } catch (Exception e) {
                    log.error("Retry failed for payment", e);
                }
            }
        }
    }

    @Scheduled(fixedDelay = 300000) // Every 5 minutes
    public void cleanupStalePayments() {
        log.info("Cleaning up stale payments");

        LocalDateTime threshold = LocalDateTime.now().minusHours(24);
        List<Payment> stalePayments = paymentRepository.findByStatus(PaymentStatus.PENDING);

        for (Payment payment : stalePayments) {
            if (payment.getCreatedAt().isBefore(threshold)) {
                payment.setStatus(PaymentStatus.FAILED);
                payment.setFailureReason("Payment timeout");
                paymentRepository.save(payment);

                log.warn("Marked stale payment as failed: {}", payment.getId());
            }
        }
    }

    private void triggerHealing(String issueType, double value) {
        log.warn("Triggering self-healing for {}: {}", issueType, value);

        switch (issueType) {
            case "high_error_rate":
                // Reduce load by enabling rate limiting
                // Scale up instances
                // Switch to fallback mode
                break;
            case "high_response_time":
                // Clear caches
                // Optimize queries
                // Scale resources
                break;
        }

        // Record healing event
        meterRegistry.counter("self_healing.triggered", "issue", issueType).increment();
    }

    private double calculateErrorRate() {
        // In production, calculate from actual metrics
        return ThreadLocalRandom.current().nextDouble(0, 0.15);
    }

    private double calculateAverageResponseTime() {
        // In production, calculate from actual metrics
        return ThreadLocalRandom.current().nextDouble(100, 1500);
    }
}

// Chaos Engineering Support (Level 7)
@RestController
@RequestMapping("/chaos")
@Slf4j
class ChaosController {

    @PostMapping("/inject-failure")
    public Map<String, String> injectFailure(@RequestParam String type) {
        log.warn("Injecting chaos: {}", type);

        switch (type) {
            case "latency":
                try {
                    Thread.sleep(5000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                break;
            case "error":
                throw new RuntimeException("Chaos: Simulated error");
            case "memory":
                List<byte[]> memory = new ArrayList<>();
                for (int i = 0; i < 100; i++) {
                    memory.add(new byte[1024 * 1024]); // 1MB blocks
                }
                break;
        }

        Map<String, String> response = new HashMap<>();
        response.put("type", type);
        response.put("status", "injected");
        return response;
    }
}
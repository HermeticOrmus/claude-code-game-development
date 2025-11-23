# Kan Extension 2: Event-Driven Extensions

## Overview

This iteration extends the framework with advanced event-driven architecture patterns using Kan extensions to create composable event processing pipelines and saga orchestration mechanisms.

## Mathematical Foundation

### Monoidal Categories for Event Composition
```
(Events, ⊗, I) forms a monoidal category where:
- Objects: Event types
- Morphisms: Event transformations
- Tensor product ⊗: Event sequencing/parallelization
- Unit I: Empty event

The Kan extension provides:
- Event aggregation patterns
- Complex event processing
- Temporal event correlation
```

### Traced Monoidal Categories for Saga Patterns
```
Traced structure adds feedback loops for:
- Compensation logic
- Rollback mechanisms
- State machines
- Long-running transactions
```

## Event-Driven Architecture Patterns

### Pattern 1: Event Sourcing with Kan Extensions
```python
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
from enum import Enum

@dataclass
class Event:
    """Base event structure"""
    id: str
    aggregate_id: str
    type: str
    data: Dict[Any, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    metadata: Dict = field(default_factory=dict)

class EventStore:
    """Kan extension-based event store with temporal composition"""

    def __init__(self):
        self.events: Dict[str, List[Event]] = {}
        self.snapshots: Dict[str, Any] = {}
        self.projections: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}

    async def append(self, event: Event) -> None:
        """Append event using left Kan extension for ordering"""
        if event.aggregate_id not in self.events:
            self.events[event.aggregate_id] = []

        # Ensure version consistency
        expected_version = len(self.events[event.aggregate_id]) + 1
        if event.version != expected_version:
            raise ValueError(f"Version conflict: expected {expected_version}, got {event.version}")

        self.events[event.aggregate_id].append(event)

        # Trigger event handlers (right Kan extension for effects)
        await self._trigger_handlers(event)

    async def get_events(self, aggregate_id: str,
                         from_version: int = 0,
                         to_version: Optional[int] = None) -> List[Event]:
        """Retrieve events with version filtering"""
        if aggregate_id not in self.events:
            return []

        events = self.events[aggregate_id]
        if to_version is None:
            return events[from_version:]
        return events[from_version:to_version]

    async def replay_events(self, aggregate_id: str,
                           projection: Callable[[Any, Event], Any],
                           initial_state: Any = None) -> Any:
        """Replay events to rebuild state using monoidal composition"""
        state = initial_state
        snapshot = self.snapshots.get(aggregate_id)

        if snapshot:
            state = snapshot['state']
            from_version = snapshot['version']
        else:
            from_version = 0

        events = await self.get_events(aggregate_id, from_version)

        for event in events:
            state = projection(state, event)

        return state

    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def _trigger_handlers(self, event: Event):
        """Trigger registered handlers for event"""
        handlers = self.event_handlers.get(event.type, [])
        for handler in handlers:
            await handler(event)

    async def create_snapshot(self, aggregate_id: str, state: Any, version: int):
        """Create snapshot for performance optimization"""
        self.snapshots[aggregate_id] = {
            'state': state,
            'version': version,
            'timestamp': datetime.now()
        }
```

### Pattern 2: Saga Pattern Implementation
```python
class SagaState(Enum):
    STARTED = "started"
    RUNNING = "running"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SagaStep:
    """Individual step in a saga"""
    name: str
    action: Callable
    compensation: Callable
    retry_policy: Dict = field(default_factory=dict)

class SagaOrchestrator:
    """Traced monoidal category for saga orchestration"""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.sagas: Dict[str, List[SagaStep]] = {}
        self.saga_states: Dict[str, Dict] = {}

    def define_saga(self, name: str, steps: List[SagaStep]):
        """Define a new saga pattern"""
        self.sagas[name] = steps

    async def start_saga(self, saga_name: str, saga_id: str,
                         initial_data: Dict) -> str:
        """Start a new saga instance"""
        if saga_name not in self.sagas:
            raise ValueError(f"Saga {saga_name} not defined")

        self.saga_states[saga_id] = {
            'name': saga_name,
            'state': SagaState.STARTED,
            'current_step': 0,
            'data': initial_data,
            'completed_steps': [],
            'failed_step': None
        }

        # Emit saga started event
        await self.event_store.append(Event(
            id=f"{saga_id}_started",
            aggregate_id=saga_id,
            type="saga_started",
            data={'saga_name': saga_name, 'initial_data': initial_data},
            version=1
        ))

        # Execute saga
        await self._execute_saga(saga_id)
        return saga_id

    async def _execute_saga(self, saga_id: str):
        """Execute saga steps with compensation on failure"""
        saga_state = self.saga_states[saga_id]
        saga_state['state'] = SagaState.RUNNING
        steps = self.sagas[saga_state['name']]

        try:
            for i, step in enumerate(steps):
                saga_state['current_step'] = i

                # Execute step with retry
                result = await self._execute_step_with_retry(
                    step, saga_state['data']
                )

                saga_state['completed_steps'].append({
                    'step': step.name,
                    'result': result
                })

                # Update data for next step
                if isinstance(result, dict):
                    saga_state['data'].update(result)

                # Emit step completed event
                await self.event_store.append(Event(
                    id=f"{saga_id}_step_{i}_completed",
                    aggregate_id=saga_id,
                    type="saga_step_completed",
                    data={'step': step.name, 'result': result},
                    version=i + 2
                ))

            saga_state['state'] = SagaState.COMPLETED

            # Emit saga completed event
            await self.event_store.append(Event(
                id=f"{saga_id}_completed",
                aggregate_id=saga_id,
                type="saga_completed",
                data={'result': saga_state['data']},
                version=len(steps) + 2
            ))

        except Exception as e:
            saga_state['state'] = SagaState.COMPENSATING
            saga_state['failed_step'] = saga_state['current_step']

            # Execute compensation
            await self._compensate_saga(saga_id)

            saga_state['state'] = SagaState.FAILED
            raise e

    async def _execute_step_with_retry(self, step: SagaStep, data: Dict) -> Any:
        """Execute step with retry policy"""
        max_retries = step.retry_policy.get('max_retries', 3)
        backoff = step.retry_policy.get('backoff', 1)

        for attempt in range(max_retries):
            try:
                return await step.action(data)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(backoff * (2 ** attempt))

    async def _compensate_saga(self, saga_id: str):
        """Execute compensation for failed saga"""
        saga_state = self.saga_states[saga_id]
        steps = self.sagas[saga_state['name']]

        # Compensate in reverse order
        for i in range(saga_state['failed_step'] - 1, -1, -1):
            step = steps[i]
            completed_step = saga_state['completed_steps'][i]

            try:
                await step.compensation(completed_step['result'])

                # Emit compensation event
                await self.event_store.append(Event(
                    id=f"{saga_id}_compensate_{i}",
                    aggregate_id=saga_id,
                    type="saga_compensation",
                    data={'step': step.name},
                    version=len(saga_state['completed_steps']) + i + 3
                ))
            except Exception as comp_error:
                # Log compensation failure but continue
                print(f"Compensation failed for step {step.name}: {comp_error}")
```

### Pattern 3: CQRS Implementation with Kan Extensions
```python
from abc import ABC, abstractmethod
import asyncio
from typing import TypeVar, Generic

T = TypeVar('T')

class Command(ABC):
    """Base command interface"""
    @abstractmethod
    def validate(self) -> bool:
        pass

class Query(ABC):
    """Base query interface"""
    pass

class CommandHandler(ABC, Generic[T]):
    """Abstract command handler"""
    @abstractmethod
    async def handle(self, command: T) -> Any:
        pass

class QueryHandler(ABC, Generic[T]):
    """Abstract query handler"""
    @abstractmethod
    async def handle(self, query: T) -> Any:
        pass

class CQRSMediator:
    """Mediator for CQRS pattern using Kan extensions"""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.command_handlers: Dict[type, CommandHandler] = {}
        self.query_handlers: Dict[type, QueryHandler] = {}
        self.read_models: Dict[str, Any] = {}

    def register_command_handler(self, command_type: type,
                                handler: CommandHandler):
        """Register command handler"""
        self.command_handlers[command_type] = handler

    def register_query_handler(self, query_type: type,
                              handler: QueryHandler):
        """Register query handler"""
        self.query_handlers[query_type] = handler

    async def send_command(self, command: Command) -> Any:
        """Send command through mediator"""
        if not command.validate():
            raise ValueError("Command validation failed")

        handler = self.command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler for command {type(command)}")

        # Execute command
        result = await handler.handle(command)

        # Emit command executed event
        await self.event_store.append(Event(
            id=f"cmd_{id(command)}",
            aggregate_id=str(type(command).__name__),
            type="command_executed",
            data={'command': str(command), 'result': result},
            version=1
        ))

        return result

    async def send_query(self, query: Query) -> Any:
        """Send query through mediator"""
        handler = self.query_handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler for query {type(query)}")

        return await handler.handle(query)

    def update_read_model(self, model_name: str, updater: Callable):
        """Update read model based on events"""
        self.event_store.register_handler("*",
            lambda event: self._update_model(model_name, updater, event)
        )

    async def _update_model(self, model_name: str, updater: Callable,
                           event: Event):
        """Internal method to update read model"""
        if model_name not in self.read_models:
            self.read_models[model_name] = {}

        self.read_models[model_name] = updater(
            self.read_models[model_name], event
        )
```

### Pattern 4: Event Streaming with Kafka Integration
```python
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json

class KafkaEventBus:
    """Kafka-based event bus with Kan extension composition"""

    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self.handlers: Dict[str, List[Callable]] = {}

    async def start(self):
        """Start Kafka producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()

    async def stop(self):
        """Stop Kafka connections"""
        if self.producer:
            await self.producer.stop()

        for consumer in self.consumers.values():
            await consumer.stop()

    async def publish(self, topic: str, event: Event):
        """Publish event to Kafka topic"""
        if not self.producer:
            await self.start()

        await self.producer.send(
            topic,
            value={
                'id': event.id,
                'aggregate_id': event.aggregate_id,
                'type': event.type,
                'data': event.data,
                'timestamp': event.timestamp.isoformat(),
                'version': event.version,
                'metadata': event.metadata
            }
        )

    async def subscribe(self, topic: str, group_id: str,
                       handler: Callable[[Event], None]):
        """Subscribe to Kafka topic"""
        if topic not in self.consumers:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda v: json.loads(v.decode())
            )
            await consumer.start()
            self.consumers[topic] = consumer

            # Start consumer loop
            asyncio.create_task(self._consume_loop(topic))

        if topic not in self.handlers:
            self.handlers[topic] = []
        self.handlers[topic].append(handler)

    async def _consume_loop(self, topic: str):
        """Internal consumer loop"""
        consumer = self.consumers[topic]
        async for msg in consumer:
            event_data = msg.value
            event = Event(
                id=event_data['id'],
                aggregate_id=event_data['aggregate_id'],
                type=event_data['type'],
                data=event_data['data'],
                timestamp=datetime.fromisoformat(event_data['timestamp']),
                version=event_data['version'],
                metadata=event_data['metadata']
            )

            # Call all registered handlers
            for handler in self.handlers.get(topic, []):
                await handler(event)
```

### Pattern 5: Complex Event Processing
```python
from collections import deque
from typing import Deque, Tuple

class CEPRule:
    """Complex event processing rule"""

    def __init__(self, name: str, pattern: str, action: Callable):
        self.name = name
        self.pattern = pattern
        self.action = action
        self.state = {}

class ComplexEventProcessor:
    """CEP engine with temporal correlation"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.event_window: Deque[Event] = deque(maxlen=window_size)
        self.rules: List[CEPRule] = []
        self.correlations: Dict[str, List[Event]] = {}

    def add_rule(self, rule: CEPRule):
        """Add processing rule"""
        self.rules.append(rule)

    async def process_event(self, event: Event):
        """Process incoming event"""
        self.event_window.append(event)

        # Check all rules
        for rule in self.rules:
            if await self._match_pattern(rule, event):
                await rule.action(event, self.event_window)

        # Temporal correlation
        await self._correlate_events(event)

    async def _match_pattern(self, rule: CEPRule, event: Event) -> bool:
        """Match event against rule pattern"""
        # Simple pattern matching - extend as needed
        if rule.pattern == "*":
            return True
        elif rule.pattern == event.type:
            return True
        elif "->" in rule.pattern:
            # Sequence pattern
            sequence = rule.pattern.split("->")
            return await self._match_sequence(sequence)
        elif "&" in rule.pattern:
            # Parallel pattern
            parallel = rule.pattern.split("&")
            return await self._match_parallel(parallel)

        return False

    async def _match_sequence(self, sequence: List[str]) -> bool:
        """Match sequential event pattern"""
        if len(self.event_window) < len(sequence):
            return False

        window_types = [e.type for e in self.event_window]
        for i in range(len(window_types) - len(sequence) + 1):
            if window_types[i:i+len(sequence)] == sequence:
                return True

        return False

    async def _match_parallel(self, parallel: List[str]) -> bool:
        """Match parallel event pattern within time window"""
        window_types = set(e.type for e in self.event_window)
        return all(p in window_types for p in parallel)

    async def _correlate_events(self, event: Event):
        """Correlate events by aggregate_id"""
        if event.aggregate_id not in self.correlations:
            self.correlations[event.aggregate_id] = []

        self.correlations[event.aggregate_id].append(event)

        # Limit correlation history
        if len(self.correlations[event.aggregate_id]) > 100:
            self.correlations[event.aggregate_id].pop(0)
```

## Example: Order Processing Saga

```python
# Define saga steps for order processing
async def create_order(data: Dict) -> Dict:
    """Create order in order service"""
    order_id = f"order_{datetime.now().timestamp()}"
    # Create order logic
    return {'order_id': order_id, 'status': 'created'}

async def compensate_order(result: Dict):
    """Cancel created order"""
    # Cancel order logic
    pass

async def reserve_inventory(data: Dict) -> Dict:
    """Reserve items in inventory"""
    # Reserve inventory logic
    return {'reservation_id': f"res_{data['order_id']}", 'status': 'reserved'}

async def compensate_inventory(result: Dict):
    """Release reserved inventory"""
    # Release inventory logic
    pass

async def process_payment(data: Dict) -> Dict:
    """Process payment"""
    # Payment processing logic
    return {'payment_id': f"pay_{data['order_id']}", 'status': 'paid'}

async def compensate_payment(result: Dict):
    """Refund payment"""
    # Refund logic
    pass

# Setup saga orchestrator
event_store = EventStore()
orchestrator = SagaOrchestrator(event_store)

# Define order processing saga
orchestrator.define_saga('order_processing', [
    SagaStep('create_order', create_order, compensate_order),
    SagaStep('reserve_inventory', reserve_inventory, compensate_inventory),
    SagaStep('process_payment', process_payment, compensate_payment)
])

# Execute saga
async def process_order(order_data: Dict):
    saga_id = await orchestrator.start_saga(
        'order_processing',
        f"saga_{datetime.now().timestamp()}",
        order_data
    )
    return saga_id
```

## Testing Framework

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_event_store():
    """Test event store functionality"""
    store = EventStore()

    # Test event appending
    event1 = Event(
        id="evt1",
        aggregate_id="agg1",
        type="test_event",
        data={'value': 1},
        version=1
    )
    await store.append(event1)

    # Test event retrieval
    events = await store.get_events("agg1")
    assert len(events) == 1
    assert events[0].id == "evt1"

    # Test version conflict
    event2 = Event(
        id="evt2",
        aggregate_id="agg1",
        type="test_event",
        data={'value': 2},
        version=3  # Wrong version
    )
    with pytest.raises(ValueError, match="Version conflict"):
        await store.append(event2)

@pytest.mark.asyncio
async def test_saga_orchestration():
    """Test saga orchestrator"""
    store = EventStore()
    orchestrator = SagaOrchestrator(store)

    # Mock saga steps
    step1 = AsyncMock(return_value={'result': 'step1'})
    step2 = AsyncMock(return_value={'result': 'step2'})
    comp1 = AsyncMock()
    comp2 = AsyncMock()

    orchestrator.define_saga('test_saga', [
        SagaStep('step1', step1, comp1),
        SagaStep('step2', step2, comp2)
    ])

    # Execute successful saga
    saga_id = await orchestrator.start_saga(
        'test_saga',
        'test_saga_1',
        {'input': 'data'}
    )

    assert orchestrator.saga_states[saga_id]['state'] == SagaState.COMPLETED
    step1.assert_called_once()
    step2.assert_called_once()
    comp1.assert_not_called()
    comp2.assert_not_called()

@pytest.mark.asyncio
async def test_saga_compensation():
    """Test saga compensation on failure"""
    store = EventStore()
    orchestrator = SagaOrchestrator(store)

    # Mock saga steps with failure
    step1 = AsyncMock(return_value={'result': 'step1'})
    step2 = AsyncMock(side_effect=Exception("Step 2 failed"))
    comp1 = AsyncMock()
    comp2 = AsyncMock()

    orchestrator.define_saga('failing_saga', [
        SagaStep('step1', step1, comp1),
        SagaStep('step2', step2, comp2)
    ])

    # Execute failing saga
    with pytest.raises(Exception, match="Step 2 failed"):
        await orchestrator.start_saga(
            'failing_saga',
            'test_saga_2',
            {'input': 'data'}
        )

    # Verify compensation was called
    comp1.assert_called_once()
    comp2.assert_not_called()

@pytest.mark.asyncio
async def test_cqrs_mediator():
    """Test CQRS mediator pattern"""
    store = EventStore()
    mediator = CQRSMediator(store)

    # Define test command
    class TestCommand(Command):
        def __init__(self, value):
            self.value = value

        def validate(self):
            return self.value > 0

    # Define test handler
    class TestCommandHandler(CommandHandler[TestCommand]):
        async def handle(self, command: TestCommand):
            return {'processed': command.value * 2}

    # Register and execute
    mediator.register_command_handler(TestCommand, TestCommandHandler())
    result = await mediator.send_command(TestCommand(5))

    assert result == {'processed': 10}

@pytest.mark.asyncio
async def test_complex_event_processing():
    """Test CEP engine"""
    cep = ComplexEventProcessor()

    # Track matched events
    matched_events = []

    # Add sequence rule
    rule = CEPRule(
        "order_complete",
        "order_created->payment_processed->order_shipped",
        lambda e, w: matched_events.append(e.type)
    )
    cep.add_rule(rule)

    # Process events in sequence
    await cep.process_event(Event("1", "order1", "order_created", {}, version=1))
    await cep.process_event(Event("2", "order1", "payment_processed", {}, version=1))
    await cep.process_event(Event("3", "order1", "order_shipped", {}, version=1))

    # Verify pattern was matched
    assert "order_shipped" in matched_events
```

## Conclusion

This Kan extension iteration provides comprehensive event-driven architecture patterns that leverage categorical abstractions for building robust, scalable, and maintainable event-driven microservices. The patterns support complex event processing, saga orchestration, and CQRS implementation while maintaining mathematical rigor and practical applicability.
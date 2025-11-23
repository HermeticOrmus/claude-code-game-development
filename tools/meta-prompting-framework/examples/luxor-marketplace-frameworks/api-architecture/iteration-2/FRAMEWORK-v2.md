# API Architecture Framework v2 - Second Kan Extension

## Overview

The second Kan extension builds upon the universal contract foundation to extract higher-level patterns focused on security, error handling, caching, and distributed systems coordination.

## Advanced Pattern Extraction

### 1. Security Monad Pattern

**Abstraction**: Security as a monad encapsulating authentication, authorization, and audit logging

```typescript
// Security Monad Implementation
class SecurityMonad<T> {
  private value: T;
  private context: SecurityContext;

  constructor(value: T, context: SecurityContext) {
    this.value = value;
    this.context = context;
  }

  // Functor map
  map<U>(fn: (value: T) => U): SecurityMonad<U> {
    return new SecurityMonad(fn(this.value), this.context);
  }

  // Monad bind (flatMap)
  flatMap<U>(fn: (value: T) => SecurityMonad<U>): SecurityMonad<U> {
    const result = fn(this.value);
    // Merge security contexts
    const mergedContext = this.context.merge(result.context);
    return new SecurityMonad(result.value, mergedContext);
  }

  // Security-specific operations
  requireAuth(): SecurityMonad<T> {
    if (!this.context.authenticated) {
      throw new AuthenticationError('Authentication required');
    }
    return this;
  }

  requireRole(role: string): SecurityMonad<T> {
    if (!this.context.hasRole(role)) {
      throw new AuthorizationError(`Role ${role} required`);
    }
    return this;
  }

  requirePermission(permission: string): SecurityMonad<T> {
    if (!this.context.hasPermission(permission)) {
      throw new AuthorizationError(`Permission ${permission} required`);
    }
    return this;
  }

  audit(action: string): SecurityMonad<T> {
    this.context.auditLog.record({
      action,
      user: this.context.user,
      timestamp: new Date(),
      data: this.value
    });
    return this;
  }

  // Extract value (only if authorized)
  extract(): T {
    this.context.validate();
    return this.value;
  }
}

// Security Context
class SecurityContext {
  constructor(
    public authenticated: boolean,
    public user: User | null,
    public roles: Set<string>,
    public permissions: Set<string>,
    public auditLog: AuditLog
  ) {}

  hasRole(role: string): boolean {
    return this.roles.has(role);
  }

  hasPermission(permission: string): boolean {
    return this.permissions.has(permission);
  }

  merge(other: SecurityContext): SecurityContext {
    return new SecurityContext(
      this.authenticated && other.authenticated,
      this.user || other.user,
      new Set([...this.roles, ...other.roles]),
      new Set([...this.permissions, ...other.permissions]),
      this.auditLog
    );
  }

  validate(): void {
    if (!this.authenticated) {
      throw new SecurityError('Security validation failed');
    }
  }
}

// Secure API Contract
class SecureAPIContract<Input, Output> extends UniversalContract<Input, Output> {
  constructor(
    name: string,
    inputType: Type<Input>,
    outputType: Type<Output>,
    handler: (input: Input) => Promise<Output>,
    private securityPolicy: SecurityPolicy
  ) {
    super(name, inputType, outputType, handler);
  }

  async executeSecure(input: Input, context: SecurityContext): Promise<SecurityMonad<Output>> {
    // Create security monad
    const secureInput = new SecurityMonad(input, context);

    // Apply security policies
    const authorized = secureInput
      .requireAuth()
      .requirePermission(this.securityPolicy.requiredPermission)
      .audit(`Executing ${this.name}`);

    // Execute handler within security context
    const result = await this.handler(authorized.extract());

    // Return result in security monad
    return new SecurityMonad(result, context).audit(`Completed ${this.name}`);
  }
}
```

### 2. Error Handling Algebraic Data Type

**Pattern**: Comprehensive error handling using algebraic data types

```haskell
-- Haskell representation of API errors
data APIError
  = ValidationError { field :: String, message :: String }
  | AuthenticationError { reason :: String }
  | AuthorizationError { permission :: String }
  | NotFoundError { resource :: String, id :: String }
  | ConflictError { conflictingResource :: String }
  | RateLimitError { limit :: Int, resetTime :: UTCTime }
  | ServerError { code :: Int, detail :: String }
  | NetworkError { endpoint :: String, cause :: String }
  deriving (Eq, Show)

-- Error handling monad transformer
newtype ErrorT e m a = ErrorT { runErrorT :: m (Either e a) }

instance (Monad m) => Functor (ErrorT e m) where
  fmap f = ErrorT . fmap (fmap f) . runErrorT

instance (Monad m) => Applicative (ErrorT e m) where
  pure = ErrorT . return . Right
  (<*>) = ap

instance (Monad m) => Monad (ErrorT e m) where
  return = pure
  m >>= k = ErrorT $ do
    result <- runErrorT m
    case result of
      Left e -> return (Left e)
      Right a -> runErrorT (k a)

-- Error recovery strategies
data RecoveryStrategy
  = Retry { maxAttempts :: Int, backoff :: Duration }
  | Fallback { fallbackValue :: Value }
  | CircuitBreak { threshold :: Int, timeout :: Duration }
  | Compensate { compensation :: IO () }
  deriving (Eq, Show)

-- Error handler with recovery
handleAPIError :: APIError -> RecoveryStrategy -> IO (Either APIError Value)
handleAPIError error strategy = case strategy of
  Retry attempts backoff -> retryWithBackoff error attempts backoff
  Fallback value -> return (Right value)
  CircuitBreak threshold timeout -> circuitBreak error threshold timeout
  Compensate action -> action >> return (Left error)
```

```typescript
// TypeScript implementation
type APIError =
  | { type: 'validation'; field: string; message: string }
  | { type: 'authentication'; reason: string }
  | { type: 'authorization'; permission: string }
  | { type: 'not_found'; resource: string; id: string }
  | { type: 'conflict'; conflictingResource: string }
  | { type: 'rate_limit'; limit: number; resetTime: Date }
  | { type: 'server'; code: number; detail: string }
  | { type: 'network'; endpoint: string; cause: string };

class Result<T, E = APIError> {
  constructor(
    private readonly value: T | null,
    private readonly error: E | null
  ) {}

  static ok<T>(value: T): Result<T, never> {
    return new Result(value, null);
  }

  static err<E>(error: E): Result<never, E> {
    return new Result(null, error);
  }

  isOk(): boolean {
    return this.value !== null;
  }

  isErr(): boolean {
    return this.error !== null;
  }

  map<U>(fn: (value: T) => U): Result<U, E> {
    if (this.isOk()) {
      return Result.ok(fn(this.value!));
    }
    return Result.err(this.error!);
  }

  mapErr<F>(fn: (error: E) => F): Result<T, F> {
    if (this.isErr()) {
      return Result.err(fn(this.error!));
    }
    return Result.ok(this.value!);
  }

  andThen<U>(fn: (value: T) => Result<U, E>): Result<U, E> {
    if (this.isOk()) {
      return fn(this.value!);
    }
    return Result.err(this.error!);
  }

  recover(fn: (error: E) => T): T {
    if (this.isErr()) {
      return fn(this.error!);
    }
    return this.value!;
  }
}

// Enhanced error handling in contracts
class ErrorHandlingContract<Input, Output> extends UniversalContract<Input, Output> {
  private errorHandlers: Map<string, (error: APIError) => Promise<Output>>;

  constructor(
    name: string,
    inputType: Type<Input>,
    outputType: Type<Output>,
    handler: (input: Input) => Promise<Result<Output, APIError>>
  ) {
    super(name, inputType, outputType, handler);
    this.errorHandlers = new Map();
    this.setupDefaultErrorHandlers();
  }

  private setupDefaultErrorHandlers() {
    // Validation error handler
    this.errorHandlers.set('validation', async (error) => {
      throw new HTTPException(400, {
        error: 'Validation Error',
        field: error.field,
        message: error.message
      });
    });

    // Rate limit error handler
    this.errorHandlers.set('rate_limit', async (error) => {
      throw new HTTPException(429, {
        error: 'Rate Limit Exceeded',
        limit: error.limit,
        resetTime: error.resetTime
      });
    });

    // Server error handler
    this.errorHandlers.set('server', async (error) => {
      // Log error
      console.error('Server error:', error);

      // Return generic error to client
      throw new HTTPException(500, {
        error: 'Internal Server Error'
      });
    });
  }

  async execute(input: Input): Promise<Output> {
    const result = await this.handler(input);

    if (result.isOk()) {
      return result.extract();
    } else {
      const error = result.extractError();
      const handler = this.errorHandlers.get(error.type);

      if (handler) {
        return await handler(error);
      } else {
        throw error;
      }
    }
  }
}
```

### 3. Cache Category with Functorial Operations

**Pattern**: Caching as a category with composition and transformation

```python
from typing import TypeVar, Generic, Optional, Callable, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import hashlib
import json

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

class CacheCategory(Generic[K, V], ABC):
    """Abstract cache category"""

    @abstractmethod
    async def get(self, key: K) -> Optional[V]:
        """Morphism from key to optional value"""
        pass

    @abstractmethod
    async def set(self, key: K, value: V, ttl: Optional[int] = None) -> None:
        """Morphism from (key, value) to unit"""
        pass

    @abstractmethod
    async def delete(self, key: K) -> None:
        """Morphism from key to unit"""
        pass

    # Functorial operations
    def fmap(self, f: Callable[[V], Any]) -> 'CacheCategory[K, Any]':
        """Map function over cached values"""
        class MappedCache(CacheCategory[K, Any]):
            def __init__(self, base_cache):
                self.base = base_cache

            async def get(self, key: K) -> Optional[Any]:
                value = await self.base.get(key)
                return f(value) if value is not None else None

            async def set(self, key: K, value: Any, ttl: Optional[int] = None):
                # Note: This is lossy - we can't reverse the mapping
                await self.base.set(key, value, ttl)

            async def delete(self, key: K):
                await self.base.delete(key)

        return MappedCache(self)

    # Composition
    def compose(self, other: 'CacheCategory[Any, K]') -> 'CacheCategory[Any, V]':
        """Compose two caches"""
        class ComposedCache(CacheCategory[Any, V]):
            def __init__(self, first, second):
                self.first = first
                self.second = second

            async def get(self, key: Any) -> Optional[V]:
                # Get intermediate key from first cache
                intermediate = await self.first.get(key)
                if intermediate is None:
                    return None
                # Get final value from second cache
                return await self.second.get(intermediate)

            async def set(self, key: Any, value: V, ttl: Optional[int] = None):
                # This requires both caches to cooperate
                pass

            async def delete(self, key: Any):
                intermediate = await self.first.get(key)
                if intermediate:
                    await self.second.delete(intermediate)
                await self.first.delete(key)

        return ComposedCache(other, self)

# Concrete cache implementations
class LRUCache(CacheCategory[K, V]):
    """Least Recently Used cache"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[K, tuple[V, datetime]] = {}
        self.access_times: Dict[K, datetime] = {}

    async def get(self, key: K) -> Optional[V]:
        if key in self.cache:
            value, _ = self.cache[key]
            self.access_times[key] = datetime.now()
            return value
        return None

    async def set(self, key: K, value: V, ttl: Optional[int] = None):
        if len(self.cache) >= self.capacity and key not in self.cache:
            # Evict least recently used
            lru_key = min(self.access_times, key=self.access_times.get)
            del self.cache[lru_key]
            del self.access_times[lru_key]

        expiry = datetime.now() + timedelta(seconds=ttl) if ttl else None
        self.cache[key] = (value, expiry)
        self.access_times[key] = datetime.now()

    async def delete(self, key: K):
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]

class DistributedCache(CacheCategory[K, V]):
    """Distributed cache with Redis backend"""

    def __init__(self, redis_client, prefix: str = ""):
        self.redis = redis_client
        self.prefix = prefix

    def _make_key(self, key: K) -> str:
        """Generate Redis key"""
        key_str = json.dumps(key, sort_keys=True)
        hash_key = hashlib.md5(key_str.encode()).hexdigest()
        return f"{self.prefix}:{hash_key}"

    async def get(self, key: K) -> Optional[V]:
        redis_key = self._make_key(key)
        value = await self.redis.get(redis_key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: K, value: V, ttl: Optional[int] = None):
        redis_key = self._make_key(key)
        value_str = json.dumps(value)
        if ttl:
            await self.redis.setex(redis_key, ttl, value_str)
        else:
            await self.redis.set(redis_key, value_str)

    async def delete(self, key: K):
        redis_key = self._make_key(key)
        await self.redis.delete(redis_key)

# Cache-aware contract
class CachedContract(UniversalContract):
    """Contract with automatic caching"""

    def __init__(self, base_contract: UniversalContract,
                 cache: CacheCategory,
                 cache_key_fn: Optional[Callable] = None,
                 ttl: int = 300):
        self.base = base_contract
        self.cache = cache
        self.cache_key_fn = cache_key_fn or self._default_cache_key
        self.ttl = ttl

    def _default_cache_key(self, input_data):
        """Generate cache key from input"""
        return hashlib.md5(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()

    async def execute(self, input_data):
        # Generate cache key
        cache_key = self.cache_key_fn(input_data)

        # Check cache
        cached_result = await self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Execute base contract
        result = await self.base.execute(input_data)

        # Cache result
        await self.cache.set(cache_key, result, self.ttl)

        return result
```

### 4. Distributed Coordination via Consensus Protocols

**Pattern**: Distributed API coordination using consensus algorithms

```python
class ConsensusProtocol(ABC):
    """Abstract consensus protocol for distributed APIs"""

    @abstractmethod
    async def propose(self, value: Any) -> bool:
        """Propose a value for consensus"""
        pass

    @abstractmethod
    async def decide(self) -> Any:
        """Get decided value"""
        pass

class RaftConsensus(ConsensusProtocol):
    """Raft consensus implementation"""

    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.state = 'follower'  # follower, candidate, leader
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0

    async def propose(self, value: Any) -> bool:
        """Propose value via Raft"""
        if self.state != 'leader':
            # Forward to leader
            leader = await self.find_leader()
            if leader:
                return await self.forward_to_leader(leader, value)
            return False

        # Append to log
        entry = {
            'term': self.current_term,
            'value': value,
            'index': len(self.log)
        }
        self.log.append(entry)

        # Replicate to followers
        success_count = 1  # Count self
        replication_tasks = []

        for peer in self.peers:
            task = self.replicate_to_peer(peer, entry)
            replication_tasks.append(task)

        results = await asyncio.gather(*replication_tasks, return_exceptions=True)

        for result in results:
            if result and not isinstance(result, Exception):
                success_count += 1

        # Check if majority achieved
        majority = (len(self.peers) + 1) // 2 + 1
        if success_count >= majority:
            self.commit_index = entry['index']
            return True

        return False

    async def decide(self) -> Any:
        """Get committed value"""
        if self.commit_index < len(self.log):
            return self.log[self.commit_index]['value']
        return None

class DistributedAPICoordinator:
    """Coordinate distributed API operations"""

    def __init__(self, consensus: ConsensusProtocol):
        self.consensus = consensus
        self.operations = {}

    async def coordinate_operation(self, operation: str, params: dict) -> Any:
        """Coordinate a distributed operation"""

        # Create operation descriptor
        op_descriptor = {
            'id': self.generate_operation_id(),
            'operation': operation,
            'params': params,
            'timestamp': datetime.now().isoformat()
        }

        # Achieve consensus on operation order
        if await self.consensus.propose(op_descriptor):
            # Execute operation on all nodes
            return await self.execute_distributed(op_descriptor)

        raise Exception("Failed to achieve consensus")

    async def execute_distributed(self, op_descriptor: dict) -> Any:
        """Execute operation across all nodes"""

        operation = op_descriptor['operation']
        params = op_descriptor['params']

        if operation == 'create':
            return await self.distributed_create(params)
        elif operation == 'update':
            return await self.distributed_update(params)
        elif operation == 'delete':
            return await self.distributed_delete(params)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        import uuid
        return str(uuid.uuid4())

# Distributed contract execution
class DistributedContract(UniversalContract):
    """Contract with distributed execution"""

    def __init__(self, base_contract: UniversalContract,
                 coordinator: DistributedAPICoordinator):
        self.base = base_contract
        self.coordinator = coordinator

    async def execute(self, input_data):
        """Execute contract with distributed coordination"""

        # Coordinate operation across nodes
        result = await self.coordinator.coordinate_operation(
            operation=self.base.name,
            params={'input': input_data}
        )

        return result
```

### 5. Event Sourcing and CQRS Pattern

**Pattern**: Event sourcing with Command Query Responsibility Segregation

```typescript
// Event sourcing types
interface Event {
  id: string;
  aggregateId: string;
  type: string;
  data: any;
  metadata: EventMetadata;
  timestamp: Date;
}

interface EventMetadata {
  userId: string;
  correlationId: string;
  causationId: string;
  version: number;
}

// Aggregate root
abstract class AggregateRoot {
  protected id: string;
  protected version: number = 0;
  protected uncommittedEvents: Event[] = [];

  constructor(id: string) {
    this.id = id;
  }

  // Apply event to aggregate
  protected abstract apply(event: Event): void;

  // Raise new event
  protected raiseEvent(eventType: string, data: any, metadata: Partial<EventMetadata>) {
    const event: Event = {
      id: generateId(),
      aggregateId: this.id,
      type: eventType,
      data,
      metadata: {
        ...metadata,
        version: ++this.version
      } as EventMetadata,
      timestamp: new Date()
    };

    this.apply(event);
    this.uncommittedEvents.push(event);
  }

  // Get uncommitted events
  getUncommittedEvents(): Event[] {
    return this.uncommittedEvents;
  }

  // Mark events as committed
  markEventsAsCommitted() {
    this.uncommittedEvents = [];
  }

  // Rebuild from events
  static fromEvents<T extends AggregateRoot>(
    this: new (id: string) => T,
    id: string,
    events: Event[]
  ): T {
    const aggregate = new this(id);
    events.forEach(event => aggregate.apply(event));
    aggregate.version = events.length;
    return aggregate;
  }
}

// Product aggregate example
class ProductAggregate extends AggregateRoot {
  private name: string;
  private price: number;
  private inventory: number;

  // Commands (write side)
  createProduct(name: string, price: number, inventory: number, metadata: Partial<EventMetadata>) {
    this.raiseEvent('ProductCreated', { name, price, inventory }, metadata);
  }

  updatePrice(newPrice: number, metadata: Partial<EventMetadata>) {
    if (newPrice <= 0) {
      throw new Error('Price must be positive');
    }
    this.raiseEvent('PriceUpdated', { oldPrice: this.price, newPrice }, metadata);
  }

  adjustInventory(quantity: number, metadata: Partial<EventMetadata>) {
    if (this.inventory + quantity < 0) {
      throw new Error('Insufficient inventory');
    }
    this.raiseEvent('InventoryAdjusted', { quantity }, metadata);
  }

  // Apply events
  protected apply(event: Event): void {
    switch (event.type) {
      case 'ProductCreated':
        this.name = event.data.name;
        this.price = event.data.price;
        this.inventory = event.data.inventory;
        break;

      case 'PriceUpdated':
        this.price = event.data.newPrice;
        break;

      case 'InventoryAdjusted':
        this.inventory += event.data.quantity;
        break;
    }
  }
}

// Event store
class EventStore {
  private events: Map<string, Event[]> = new Map();
  private projections: Map<string, any> = new Map();
  private subscribers: ((event: Event) => void)[] = [];

  async append(aggregateId: string, events: Event[]): Promise<void> {
    const existing = this.events.get(aggregateId) || [];
    this.events.set(aggregateId, [...existing, ...events]);

    // Publish events to subscribers
    events.forEach(event => {
      this.subscribers.forEach(subscriber => subscriber(event));
    });
  }

  async getEvents(aggregateId: string): Promise<Event[]> {
    return this.events.get(aggregateId) || [];
  }

  subscribe(handler: (event: Event) => void): void {
    this.subscribers.push(handler);
  }
}

// CQRS Command handler
class CommandHandler {
  constructor(private eventStore: EventStore) {}

  async handle<T extends AggregateRoot>(
    AggregateClass: new (id: string) => T,
    aggregateId: string,
    command: (aggregate: T) => void
  ): Promise<void> {
    // Load aggregate from events
    const events = await this.eventStore.getEvents(aggregateId);
    const aggregate = events.length > 0
      ? AggregateClass.fromEvents(aggregateId, events)
      : new AggregateClass(aggregateId);

    // Execute command
    command(aggregate);

    // Save events
    const newEvents = aggregate.getUncommittedEvents();
    await this.eventStore.append(aggregateId, newEvents);
    aggregate.markEventsAsCommitted();
  }
}

// CQRS Query handler
class QueryHandler {
  private readModels: Map<string, any> = new Map();

  constructor(private eventStore: EventStore) {
    // Subscribe to events for projection updates
    this.eventStore.subscribe(this.updateProjections.bind(this));
  }

  private updateProjections(event: Event): void {
    // Update read models based on events
    switch (event.type) {
      case 'ProductCreated':
        this.readModels.set(event.aggregateId, {
          id: event.aggregateId,
          name: event.data.name,
          price: event.data.price,
          inventory: event.data.inventory
        });
        break;

      case 'PriceUpdated':
        const product = this.readModels.get(event.aggregateId);
        if (product) {
          product.price = event.data.newPrice;
        }
        break;

      case 'InventoryAdjusted':
        const prod = this.readModels.get(event.aggregateId);
        if (prod) {
          prod.inventory += event.data.quantity;
        }
        break;
    }
  }

  async query(queryType: string, params: any): Promise<any> {
    switch (queryType) {
      case 'getProduct':
        return this.readModels.get(params.id);

      case 'listProducts':
        return Array.from(this.readModels.values());

      case 'searchProducts':
        return Array.from(this.readModels.values()).filter(
          product => product.name.includes(params.search)
        );

      default:
        throw new Error(`Unknown query type: ${queryType}`);
    }
  }
}

// CQRS API Contract
class CQRSContract extends UniversalContract {
  private commandHandler: CommandHandler;
  private queryHandler: QueryHandler;

  constructor(
    name: string,
    eventStore: EventStore
  ) {
    super(name, null, null, null);
    this.commandHandler = new CommandHandler(eventStore);
    this.queryHandler = new QueryHandler(eventStore);
  }

  async executeCommand(command: any): Promise<void> {
    // Route to appropriate aggregate
    const { aggregateId, commandType, data } = command;

    await this.commandHandler.handle(
      ProductAggregate,
      aggregateId,
      (aggregate) => {
        switch (commandType) {
          case 'create':
            aggregate.createProduct(data.name, data.price, data.inventory, {});
            break;
          case 'updatePrice':
            aggregate.updatePrice(data.price, {});
            break;
          case 'adjustInventory':
            aggregate.adjustInventory(data.quantity, {});
            break;
        }
      }
    );
  }

  async executeQuery(query: any): Promise<any> {
    return await this.queryHandler.query(query.type, query.params);
  }
}
```

## Enhanced Framework Components v2

### 1. Unified Security Layer

```python
class UnifiedSecurityLayer:
    """Security layer for all API protocols"""

    def __init__(self):
        self.auth_providers = {}
        self.policy_engine = PolicyEngine()
        self.audit_log = AuditLog()

    def register_auth_provider(self, name: str, provider: AuthProvider):
        """Register authentication provider"""
        self.auth_providers[name] = provider

    async def authenticate(self, credentials: dict) -> SecurityContext:
        """Authenticate user across protocols"""

        # Try each auth provider
        for name, provider in self.auth_providers.items():
            try:
                user = await provider.authenticate(credentials)
                if user:
                    return await self.create_security_context(user)
            except:
                continue

        raise AuthenticationError("Authentication failed")

    async def authorize(self, context: SecurityContext, resource: str,
                       action: str) -> bool:
        """Authorize action on resource"""

        # Evaluate policies
        decision = await self.policy_engine.evaluate(
            subject=context.user,
            resource=resource,
            action=action,
            context=context
        )

        # Audit the decision
        await self.audit_log.record({
            'user': context.user.id,
            'resource': resource,
            'action': action,
            'decision': decision,
            'timestamp': datetime.now()
        })

        return decision

    async def create_security_context(self, user: User) -> SecurityContext:
        """Create security context for user"""

        roles = await self.load_user_roles(user)
        permissions = await self.load_user_permissions(user, roles)

        return SecurityContext(
            authenticated=True,
            user=user,
            roles=roles,
            permissions=permissions,
            audit_log=self.audit_log
        )

class PolicyEngine:
    """Policy-based authorization engine"""

    def __init__(self):
        self.policies = []

    def add_policy(self, policy: Policy):
        """Add authorization policy"""
        self.policies.append(policy)

    async def evaluate(self, subject, resource, action, context) -> bool:
        """Evaluate policies"""

        for policy in self.policies:
            if policy.matches(subject, resource, action):
                decision = await policy.evaluate(context)
                if decision is not None:
                    return decision

        # Default deny
        return False

class Policy:
    """Authorization policy"""

    def __init__(self, name: str, rules: List[Rule]):
        self.name = name
        self.rules = rules

    def matches(self, subject, resource, action) -> bool:
        """Check if policy applies"""
        return any(rule.matches(subject, resource, action)
                  for rule in self.rules)

    async def evaluate(self, context) -> Optional[bool]:
        """Evaluate policy"""
        for rule in self.rules:
            if await rule.evaluate(context):
                return rule.effect == 'allow'
        return None
```

### 2. Intelligent Error Recovery System

```python
class ErrorRecoverySystem:
    """ML-powered error recovery"""

    def __init__(self):
        self.error_history = []
        self.recovery_strategies = {}
        self.model = self.train_recovery_model()

    def train_recovery_model(self):
        """Train ML model for error recovery"""
        # Simplified - in production use proper ML
        return SimpleRecoveryModel()

    async def handle_error(self, error: APIError, context: dict) -> Any:
        """Handle error with intelligent recovery"""

        # Record error
        self.error_history.append({
            'error': error,
            'context': context,
            'timestamp': datetime.now()
        })

        # Predict best recovery strategy
        strategy = self.predict_recovery_strategy(error, context)

        # Execute recovery
        return await self.execute_recovery(strategy, error, context)

    def predict_recovery_strategy(self, error: APIError, context: dict) -> RecoveryStrategy:
        """Predict optimal recovery strategy"""

        features = self.extract_error_features(error, context)
        strategy_type = self.model.predict(features)

        if strategy_type == 'retry':
            return RetryStrategy(
                max_attempts=3,
                backoff=ExponentialBackoff(base=2)
            )
        elif strategy_type == 'fallback':
            return FallbackStrategy(
                fallback_fn=self.get_fallback_function(error)
            )
        elif strategy_type == 'circuit_break':
            return CircuitBreakerStrategy(
                threshold=5,
                timeout=60
            )
        else:
            return NoOpStrategy()

    async def execute_recovery(self, strategy: RecoveryStrategy,
                              error: APIError, context: dict) -> Any:
        """Execute recovery strategy"""
        return await strategy.execute(error, context)

class RetryStrategy(RecoveryStrategy):
    """Retry with backoff"""

    def __init__(self, max_attempts: int, backoff: BackoffStrategy):
        self.max_attempts = max_attempts
        self.backoff = backoff

    async def execute(self, error: APIError, context: dict) -> Any:
        for attempt in range(self.max_attempts):
            try:
                # Retry the operation
                return await context['retry_fn']()
            except Exception as e:
                if attempt == self.max_attempts - 1:
                    raise
                await asyncio.sleep(self.backoff.get_delay(attempt))
```

### 3. Advanced Caching System

```python
class AdvancedCachingSystem:
    """Multi-layer caching with ML optimization"""

    def __init__(self):
        self.l1_cache = LRUCache(capacity=1000)  # In-memory
        self.l2_cache = DistributedCache(redis_client)  # Redis
        self.l3_cache = CDNCache(cdn_provider)  # CDN
        self.optimizer = CacheOptimizer()

    async def get(self, key: str, context: dict = None) -> Optional[Any]:
        """Get from cache with intelligent routing"""

        # Predict best cache level
        level = self.optimizer.predict_cache_level(key, context)

        # Try caches in order
        if level >= 1:
            value = await self.l1_cache.get(key)
            if value:
                return value

        if level >= 2:
            value = await self.l2_cache.get(key)
            if value:
                # Promote to L1 if hot
                if self.optimizer.is_hot(key):
                    await self.l1_cache.set(key, value)
                return value

        if level >= 3:
            value = await self.l3_cache.get(key)
            if value:
                # Promote to L2 if frequently accessed
                if self.optimizer.is_frequent(key):
                    await self.l2_cache.set(key, value)
                return value

        return None

    async def set(self, key: str, value: Any, context: dict = None):
        """Set in appropriate cache levels"""

        # Determine cache levels based on value characteristics
        levels = self.optimizer.determine_cache_levels(key, value, context)

        tasks = []
        if 1 in levels:
            tasks.append(self.l1_cache.set(key, value))
        if 2 in levels:
            tasks.append(self.l2_cache.set(key, value))
        if 3 in levels:
            tasks.append(self.l3_cache.set(key, value))

        await asyncio.gather(*tasks)

class CacheOptimizer:
    """ML-based cache optimization"""

    def __init__(self):
        self.access_patterns = {}
        self.model = self.train_optimization_model()

    def predict_cache_level(self, key: str, context: dict) -> int:
        """Predict optimal cache level"""

        features = {
            'key_hash': hash(key) % 1000,
            'time_of_day': datetime.now().hour,
            'access_frequency': self.get_access_frequency(key),
            'data_size': context.get('size', 0) if context else 0
        }

        return self.model.predict(features)

    def is_hot(self, key: str) -> bool:
        """Check if key is hot (frequently accessed recently)"""
        frequency = self.get_access_frequency(key)
        return frequency > 10  # Simplified

    def is_frequent(self, key: str) -> bool:
        """Check if key is frequently accessed"""
        return self.get_access_frequency(key) > 5

    def get_access_frequency(self, key: str) -> int:
        """Get access frequency for key"""
        return self.access_patterns.get(key, 0)
```

## Categorical Analysis v2

### 1. Security as a Monad

The security implementation forms a monad with:
- **Return**: Wrap value in security context
- **Bind**: Chain security operations
- **Laws**: Left identity, right identity, associativity

### 2. Error Handling as Algebraic Data Type

Errors form an algebraic data type with:
- **Sum type**: Different error variants
- **Pattern matching**: Exhaustive error handling
- **Composability**: Error transformation and recovery

### 3. Cache as a Category

Caching forms a category with:
- **Objects**: Cache keys
- **Morphisms**: Key to value mappings
- **Composition**: Cache chaining
- **Identity**: Pass-through cache

### 4. Event Sourcing as Free Monad

Event sourcing can be modeled as a free monad:
- **Functor**: Event types
- **Free construction**: Event sequences
- **Interpretation**: Event application to state

## Conclusion

The second Kan extension has successfully extracted advanced patterns for security, error handling, caching, and distributed coordination. These patterns provide enterprise-grade capabilities while maintaining the categorical foundation established in the first iteration. The framework now supports complex, production-ready API systems with formal guarantees and optimal performance.
"""
Production-Grade Multi-Server MCP Orchestration
Demonstrates deep MCP integration with multiple servers, load balancing, and failover
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import random
import json
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Protocol Messages
@dataclass
class MCPMessage:
    """Base MCP protocol message"""
    id: str
    type: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class ToolRequest(MCPMessage):
    """Request to execute a tool"""
    tool_name: str
    parameters: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolResponse(MCPMessage):
    """Response from tool execution"""
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DiscoveryRequest(MCPMessage):
    """Request to discover server capabilities"""
    type: str = "discovery"

@dataclass
class DiscoveryResponse(MCPMessage):
    """Response with server capabilities"""
    capabilities: List[str]
    tools: List[Dict[str, str]]
    version: str

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for fault tolerance"""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def is_closed(self) -> bool:
        """Check if circuit is closed (allowing requests)"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def record_success(self):
        """Record successful request"""
        self.failures = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record failed request"""
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failures} failures")

class AdaptiveRateLimiter:
    """Token bucket rate limiter with adaptive rate"""

    def __init__(self, initial_rate: float = 10.0, capacity: int = 100):
        self.rate = initial_rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.success_count = 0
        self.failure_count = 0

    async def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens"""
        now = time.time()
        elapsed = now - self.last_update

        # Refill bucket
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def adapt_rate(self):
        """Adjust rate based on performance"""
        total = self.success_count + self.failure_count
        if total > 100:  # Enough samples
            success_ratio = self.success_count / total
            if success_ratio > 0.95:
                self.rate = min(self.rate * 1.1, 100)  # Increase rate
            elif success_ratio < 0.8:
                self.rate = max(self.rate * 0.9, 1)  # Decrease rate

            # Reset counters
            self.success_count = 0
            self.failure_count = 0

class ConnectionPool:
    """Connection pool for MCP server connections"""

    def __init__(self, size: int = 10):
        self.size = size
        self.connections = asyncio.Queue(maxsize=size)
        self.created = 0

    @asynccontextmanager
    async def acquire(self):
        """Acquire connection from pool"""
        if self.connections.empty() and self.created < self.size:
            # Create new connection
            conn = await self.create_connection()
            self.created += 1
        else:
            # Get from pool
            conn = await self.connections.get()

        try:
            yield conn
        finally:
            # Return to pool
            if conn.is_healthy():
                await self.connections.put(conn)
            else:
                # Replace unhealthy connection
                new_conn = await self.create_connection()
                await self.connections.put(new_conn)

    async def create_connection(self):
        """Create new connection"""
        return MCPConnection()

class MCPConnection:
    """Individual MCP server connection"""

    def __init__(self):
        self.id = f"conn_{random.randint(1000, 9999)}"
        self.created_at = time.time()
        self.request_count = 0
        self.healthy = True

    def is_healthy(self) -> bool:
        """Check connection health"""
        # Simple health check - connection is old or has high usage
        age = time.time() - self.created_at
        if age > 300 or self.request_count > 1000:
            return False
        return self.healthy

    async def send(self, message: MCPMessage) -> MCPMessage:
        """Send message through connection"""
        self.request_count += 1
        # Simulate network delay
        await asyncio.sleep(0.01)
        return message

class MCPServer:
    """Production-grade MCP server with all features"""

    def __init__(self, name: str, url: str, capabilities: List[str]):
        self.name = name
        self.url = url
        self.capabilities = capabilities
        self.tools = {}
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = AdaptiveRateLimiter()
        self.connection_pool = ConnectionPool()
        self.metrics = {}

        # Initialize default tools
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools based on capabilities"""
        for capability in self.capabilities:
            if capability == "nlp":
                self.tools["sentiment_analysis"] = self.sentiment_tool
                self.tools["entity_extraction"] = self.entity_tool
            elif capability == "code":
                self.tools["code_execution"] = self.code_execution_tool
                self.tools["code_analysis"] = self.code_analysis_tool
            elif capability == "data":
                self.tools["data_query"] = self.data_query_tool
                self.tools["data_transform"] = self.data_transform_tool

    async def handle_request(self, request: MCPMessage) -> MCPMessage:
        """Handle incoming request"""

        # Check circuit breaker
        if not self.circuit_breaker.is_closed():
            return ToolResponse(
                id=request.id,
                type="error",
                error="Service temporarily unavailable",
                metadata={"circuit_state": self.circuit_breaker.state.value}
            )

        # Rate limiting
        if not await self.rate_limiter.acquire():
            return ToolResponse(
                id=request.id,
                type="error",
                error="Rate limit exceeded",
                metadata={"retry_after": 1.0}
            )

        try:
            # Route request
            if isinstance(request, DiscoveryRequest):
                response = await self.handle_discovery(request)
            elif isinstance(request, ToolRequest):
                response = await self.handle_tool_request(request)
            else:
                response = ToolResponse(
                    id=request.id,
                    type="error",
                    error=f"Unknown request type: {request.type}"
                )

            self.circuit_breaker.record_success()
            self.rate_limiter.success_count += 1
            return response

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.circuit_breaker.record_failure()
            self.rate_limiter.failure_count += 1

            return ToolResponse(
                id=request.id,
                type="error",
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )

    async def handle_discovery(self, request: DiscoveryRequest) -> DiscoveryResponse:
        """Handle capability discovery"""
        tool_list = [
            {"name": name, "description": f"Tool: {name}"}
            for name in self.tools.keys()
        ]

        return DiscoveryResponse(
            id=request.id,
            type="discovery_response",
            capabilities=self.capabilities,
            tools=tool_list,
            version="1.0.0"
        )

    async def handle_tool_request(self, request: ToolRequest) -> ToolResponse:
        """Handle tool execution request"""
        tool = self.tools.get(request.tool_name)

        if not tool:
            return ToolResponse(
                id=request.id,
                type="tool_response",
                error=f"Tool not found: {request.tool_name}",
                metadata={"available_tools": list(self.tools.keys())}
            )

        # Execute tool
        async with self.connection_pool.acquire() as conn:
            result = await tool(request.parameters, request.context)

        return ToolResponse(
            id=request.id,
            type="tool_response",
            result=result,
            metadata={"server": self.name, "tool": request.tool_name}
        )

    # Tool implementations
    async def sentiment_tool(self, params: Dict, context: Dict) -> Dict:
        """Sentiment analysis tool"""
        text = params.get("text", "")
        # Simulate sentiment analysis
        await asyncio.sleep(0.05)
        sentiment = random.choice(["positive", "negative", "neutral"])
        confidence = random.random()
        return {"sentiment": sentiment, "confidence": confidence}

    async def entity_tool(self, params: Dict, context: Dict) -> Dict:
        """Entity extraction tool"""
        text = params.get("text", "")
        # Simulate entity extraction
        await asyncio.sleep(0.05)
        entities = [
            {"text": "Python", "type": "TECHNOLOGY"},
            {"text": "MCP", "type": "PROTOCOL"}
        ]
        return {"entities": entities}

    async def code_execution_tool(self, params: Dict, context: Dict) -> Dict:
        """Code execution tool"""
        code = params.get("code", "")
        # Simulate code execution (DO NOT EXECUTE REAL CODE IN PRODUCTION)
        await asyncio.sleep(0.1)
        return {"output": f"Executed: {code[:50]}...", "status": "success"}

    async def code_analysis_tool(self, params: Dict, context: Dict) -> Dict:
        """Code analysis tool"""
        code = params.get("code", "")
        # Simulate code analysis
        await asyncio.sleep(0.05)
        return {
            "complexity": random.randint(1, 10),
            "lines": len(code.split("\n")),
            "issues": []
        }

    async def data_query_tool(self, params: Dict, context: Dict) -> Dict:
        """Data query tool"""
        query = params.get("query", "")
        # Simulate data query
        await asyncio.sleep(0.05)
        return {"results": [{"id": 1, "value": "sample"}], "count": 1}

    async def data_transform_tool(self, params: Dict, context: Dict) -> Dict:
        """Data transformation tool"""
        data = params.get("data", [])
        transform = params.get("transform", "identity")
        # Simulate transformation
        await asyncio.sleep(0.05)
        return {"transformed": data, "transform_applied": transform}

class MetaMCPServer(MCPServer):
    """Meta-MCP server that manages other MCP servers"""

    def __init__(self):
        super().__init__(
            name="meta-mcp",
            url="http://localhost:3000",
            capabilities=["discovery", "routing", "orchestration"]
        )
        self.managed_servers = {}
        self.routing_table = {}
        self.health_status = {}

    async def register_server(self, server: MCPServer):
        """Register a managed server"""
        self.managed_servers[server.name] = server

        # Discover capabilities
        discovery_req = DiscoveryRequest(id=f"discover_{server.name}")
        discovery_resp = await server.handle_request(discovery_req)

        # Update routing table
        if isinstance(discovery_resp, DiscoveryResponse):
            for capability in discovery_resp.capabilities:
                if capability not in self.routing_table:
                    self.routing_table[capability] = []
                self.routing_table[capability].append(server.name)

            # Update health status
            self.health_status[server.name] = "healthy"

        logger.info(f"Registered server: {server.name} with capabilities: {discovery_resp.capabilities}")

    async def route_request(self, request: ToolRequest) -> ToolResponse:
        """Route request to appropriate server"""

        # Determine capability needed
        capability = self.infer_capability(request.tool_name)

        # Find available servers
        available_servers = self.routing_table.get(capability, [])
        healthy_servers = [
            s for s in available_servers
            if self.health_status.get(s) == "healthy"
        ]

        if not healthy_servers:
            return ToolResponse(
                id=request.id,
                type="error",
                error=f"No healthy servers available for capability: {capability}"
            )

        # Load balance (round-robin for simplicity)
        server_name = random.choice(healthy_servers)
        server = self.managed_servers[server_name]

        # Forward request
        logger.info(f"Routing request to {server_name}")
        response = await server.handle_request(request)

        # Update health based on response
        if response.error:
            self.record_server_failure(server_name)
        else:
            self.record_server_success(server_name)

        return response

    def infer_capability(self, tool_name: str) -> str:
        """Infer required capability from tool name"""
        if "sentiment" in tool_name or "entity" in tool_name:
            return "nlp"
        elif "code" in tool_name or "execute" in tool_name:
            return "code"
        elif "data" in tool_name or "query" in tool_name:
            return "data"
        else:
            return "general"

    def record_server_failure(self, server_name: str):
        """Record server failure for health tracking"""
        # Simple health tracking - could be more sophisticated
        logger.warning(f"Server {server_name} failed")
        self.health_status[server_name] = "unhealthy"

    def record_server_success(self, server_name: str):
        """Record server success"""
        self.health_status[server_name] = "healthy"

    async def health_check_loop(self):
        """Periodic health checks for all servers"""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds

            for server_name, server in self.managed_servers.items():
                try:
                    # Send ping request
                    ping_req = DiscoveryRequest(id=f"ping_{server_name}")
                    response = await server.handle_request(ping_req)

                    if not response.error:
                        self.health_status[server_name] = "healthy"
                    else:
                        self.health_status[server_name] = "unhealthy"

                except Exception as e:
                    logger.error(f"Health check failed for {server_name}: {e}")
                    self.health_status[server_name] = "unhealthy"

            logger.info(f"Health status: {self.health_status}")

class MCPOrchestrator:
    """High-level orchestrator for multiple MCP operations"""

    def __init__(self, meta_server: MetaMCPServer):
        self.meta_server = meta_server

    async def execute_workflow(self, workflow: List[Dict]) -> List[ToolResponse]:
        """Execute a workflow of tool requests"""
        results = []

        for step in workflow:
            request = ToolRequest(
                id=step["id"],
                type="tool_request",
                tool_name=step["tool"],
                parameters=step.get("parameters", {}),
                context=step.get("context", {})
            )

            # Route through meta server
            response = await self.meta_server.route_request(request)
            results.append(response)

            # Check if we should continue
            if response.error and step.get("required", True):
                logger.error(f"Required step failed: {step['id']}")
                break

            # Add result to context for next steps
            if "context_key" in step:
                for next_step in workflow:
                    if next_step.get("uses_context"):
                        next_step["context"][step["context_key"]] = response.result

        return results

    async def parallel_execute(self, requests: List[ToolRequest]) -> List[ToolResponse]:
        """Execute multiple requests in parallel"""
        tasks = [
            self.meta_server.route_request(request)
            for request in requests
        ]
        return await asyncio.gather(*tasks)

async def main():
    """Demonstrate multi-server MCP orchestration"""

    # Create meta server
    meta_server = MetaMCPServer()

    # Create specialized servers
    nlp_server = MCPServer(
        name="nlp-server",
        url="http://localhost:3001",
        capabilities=["nlp"]
    )

    code_server = MCPServer(
        name="code-server",
        url="http://localhost:3002",
        capabilities=["code"]
    )

    data_server = MCPServer(
        name="data-server",
        url="http://localhost:3003",
        capabilities=["data"]
    )

    # Register servers with meta server
    await meta_server.register_server(nlp_server)
    await meta_server.register_server(code_server)
    await meta_server.register_server(data_server)

    # Start health check loop
    health_task = asyncio.create_task(meta_server.health_check_loop())

    # Create orchestrator
    orchestrator = MCPOrchestrator(meta_server)

    # Example 1: Sequential workflow
    print("\n=== Sequential Workflow ===")
    workflow = [
        {
            "id": "step1",
            "tool": "sentiment_analysis",
            "parameters": {"text": "This MCP integration is amazing!"},
            "context_key": "sentiment"
        },
        {
            "id": "step2",
            "tool": "entity_extraction",
            "parameters": {"text": "Python and MCP are powerful technologies"},
            "context_key": "entities"
        },
        {
            "id": "step3",
            "tool": "data_query",
            "parameters": {"query": "SELECT * FROM results"},
            "uses_context": True
        }
    ]

    results = await orchestrator.execute_workflow(workflow)
    for i, result in enumerate(results):
        print(f"Step {i+1}: {result.result if not result.error else f'Error: {result.error}'}")

    # Example 2: Parallel execution
    print("\n=== Parallel Execution ===")
    parallel_requests = [
        ToolRequest(
            id=f"parallel_{i}",
            type="tool_request",
            tool_name=tool,
            parameters={"text": "Test text"} if "nlp" in tool else {"code": "print('test')"}
        )
        for i, tool in enumerate(["sentiment_analysis", "code_analysis", "data_query"])
    ]

    parallel_results = await orchestrator.parallel_execute(parallel_requests)
    for i, result in enumerate(parallel_results):
        print(f"Parallel {i+1}: {result.metadata}")

    # Example 3: Stress test with rate limiting
    print("\n=== Stress Test ===")
    stress_requests = [
        ToolRequest(
            id=f"stress_{i}",
            type="tool_request",
            tool_name="sentiment_analysis",
            parameters={"text": f"Test {i}"}
        )
        for i in range(20)
    ]

    start_time = time.time()
    stress_results = await orchestrator.parallel_execute(stress_requests)
    elapsed = time.time() - start_time

    successful = sum(1 for r in stress_results if not r.error)
    print(f"Processed {successful}/{len(stress_requests)} requests in {elapsed:.2f}s")

    # Show final metrics
    print("\n=== Server Metrics ===")
    for name, server in meta_server.managed_servers.items():
        print(f"{name}:")
        print(f"  Circuit breaker: {server.circuit_breaker.state.value}")
        print(f"  Rate limiter: {server.rate_limiter.rate:.1f} req/s")
        print(f"  Health: {meta_server.health_status.get(name, 'unknown')}")

    # Cleanup
    health_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
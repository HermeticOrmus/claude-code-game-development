"""
FastAPI Universal Contract Example
Demonstrates how to use universal contracts with FastAPI
"""

from typing import List, Optional, Generic, TypeVar
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import asyncio
from enum import Enum

# Type definitions
T = TypeVar('T')
R = TypeVar('R')

class Protocol(Enum):
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"

# Domain models
class Product(BaseModel):
    id: int
    name: str
    price: float
    inventory: int
    category: str
    created_at: datetime
    updated_at: datetime

class ProductFilter(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = True

class ProductList(BaseModel):
    products: List[Product]
    total: int
    page: int
    page_size: int

# Universal Contract Implementation
class UniversalContract(Generic[T, R]):
    """Universal API Contract that works across protocols"""

    def __init__(self, name: str, input_type: type, output_type: type,
                 handler: callable, description: str = ""):
        self.name = name
        self.input_type = input_type
        self.output_type = output_type
        self.handler = handler
        self.description = description
        self.implementations = {}
        self._generate_implementations()

    def _generate_implementations(self):
        """Generate protocol-specific implementations"""

        # REST implementation
        self.implementations[Protocol.REST] = {
            'method': 'POST' if self.input_type != type(None) else 'GET',
            'path': f'/{self.name.lower()}',
            'handler': self._create_rest_handler()
        }

        # GraphQL implementation
        self.implementations[Protocol.GRAPHQL] = {
            'type_def': self._generate_graphql_schema(),
            'resolver': self._create_graphql_resolver()
        }

        # gRPC implementation
        self.implementations[Protocol.GRPC] = {
            'proto': self._generate_proto_definition(),
            'service': self._create_grpc_service()
        }

    def _create_rest_handler(self):
        """Create REST-specific handler"""
        async def rest_handler(input_data: Optional[self.input_type] = None):
            if self.input_type == type(None):
                result = await self.handler(None)
            else:
                result = await self.handler(input_data)
            return result
        return rest_handler

    def _create_graphql_resolver(self):
        """Create GraphQL resolver"""
        async def resolver(parent, info, **kwargs):
            if self.input_type != type(None):
                input_data = self.input_type(**kwargs.get('input', {}))
                return await self.handler(input_data)
            return await self.handler(None)
        return resolver

    def _create_grpc_service(self):
        """Create gRPC service method"""
        async def grpc_service(request, context):
            if self.input_type != type(None):
                input_data = self.input_type(**request)
                result = await self.handler(input_data)
            else:
                result = await self.handler(None)
            return result
        return grpc_service

    def _generate_graphql_schema(self) -> str:
        """Generate GraphQL schema from types"""
        input_str = ""
        if self.input_type != type(None):
            input_str = f"(input: {self.input_type.__name__}Input)"

        return f"""
        type Query {{
            {self.name}{input_str}: {self.output_type.__name__}
        }}
        """

    def _generate_proto_definition(self) -> str:
        """Generate Protocol Buffer definition"""
        return f"""
        service {self.name}Service {{
            rpc {self.name}({self.input_type.__name__}Request) returns ({self.output_type.__name__}Response);
        }}
        """

# Universal Server Implementation
class UniversalServer:
    """Server that supports multiple protocols simultaneously"""

    def __init__(self):
        self.contracts = {}
        self.app = FastAPI(title="Universal API Server")
        self.metrics = {
            'requests': 0,
            'errors': 0,
            'latency': []
        }

    def register_contract(self, contract: UniversalContract):
        """Register a universal contract"""
        self.contracts[contract.name] = contract
        self._setup_endpoints(contract)

    def _setup_endpoints(self, contract: UniversalContract):
        """Setup protocol-specific endpoints"""

        # Setup REST endpoint
        rest_impl = contract.implementations[Protocol.REST]

        if rest_impl['method'] == 'GET':
            @self.app.get(rest_impl['path'], response_model=contract.output_type)
            async def get_endpoint():
                return await self._execute_with_metrics(
                    contract.name, Protocol.REST, rest_impl['handler'], None
                )
        else:
            @self.app.post(rest_impl['path'], response_model=contract.output_type)
            async def post_endpoint(input_data: contract.input_type):
                return await self._execute_with_metrics(
                    contract.name, Protocol.REST, rest_impl['handler'], input_data
                )

        # Setup GraphQL endpoint (simplified - in production use Strawberry/Ariadne)
        @self.app.post(f"/graphql/{contract.name.lower()}")
        async def graphql_endpoint(query: dict):
            resolver = contract.implementations[Protocol.GRAPHQL]['resolver']
            return await self._execute_with_metrics(
                contract.name, Protocol.GRAPHQL, resolver, query
            )

    async def _execute_with_metrics(self, contract_name: str, protocol: Protocol,
                                   handler: callable, input_data):
        """Execute handler with metrics collection"""
        start_time = datetime.now()
        self.metrics['requests'] += 1

        try:
            if input_data is None:
                result = await handler()
            else:
                result = await handler(input_data)

            # Record latency
            latency = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics['latency'].append(latency)

            return result

        except Exception as e:
            self.metrics['errors'] += 1
            raise HTTPException(status_code=500, detail=str(e))

    def get_metrics(self) -> dict:
        """Get server metrics"""
        avg_latency = sum(self.metrics['latency']) / len(self.metrics['latency']) if self.metrics['latency'] else 0

        return {
            'total_requests': self.metrics['requests'],
            'total_errors': self.metrics['errors'],
            'error_rate': self.metrics['errors'] / self.metrics['requests'] if self.metrics['requests'] > 0 else 0,
            'avg_latency_ms': avg_latency,
            'p99_latency_ms': sorted(self.metrics['latency'])[int(len(self.metrics['latency']) * 0.99)] if self.metrics['latency'] else 0
        }

# Product Service Implementation
class ProductService:
    """Mock product service"""

    def __init__(self):
        self.products = [
            Product(
                id=i,
                name=f"Product {i}",
                price=10.0 * i,
                inventory=100 - i,
                category="Electronics" if i % 2 == 0 else "Books",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            for i in range(1, 101)
        ]

    async def get_all_products(self, filter_input: Optional[ProductFilter]) -> ProductList:
        """Get filtered products"""
        filtered = self.products

        if filter_input:
            if filter_input.category:
                filtered = [p for p in filtered if p.category == filter_input.category]
            if filter_input.min_price is not None:
                filtered = [p for p in filtered if p.price >= filter_input.min_price]
            if filter_input.max_price is not None:
                filtered = [p for p in filtered if p.price <= filter_input.max_price]
            if filter_input.in_stock:
                filtered = [p for p in filtered if p.inventory > 0]

        return ProductList(
            products=filtered[:20],  # Pagination
            total=len(filtered),
            page=1,
            page_size=20
        )

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get single product"""
        for product in self.products:
            if product.id == product_id:
                return product
        return None

    async def create_product(self, product: Product) -> Product:
        """Create new product"""
        product.id = max(p.id for p in self.products) + 1
        product.created_at = datetime.now()
        product.updated_at = datetime.now()
        self.products.append(product)
        return product

    async def update_inventory(self, product_id: int, quantity: int) -> Product:
        """Update product inventory"""
        product = await self.get_product_by_id(product_id)
        if product:
            product.inventory = quantity
            product.updated_at = datetime.now()
        return product

# Initialize services
product_service = ProductService()
server = UniversalServer()

# Define universal contracts
get_products_contract = UniversalContract(
    name="GetProducts",
    input_type=ProductFilter,
    output_type=ProductList,
    handler=product_service.get_all_products,
    description="Get filtered list of products"
)

get_product_contract = UniversalContract(
    name="GetProduct",
    input_type=int,
    output_type=Product,
    handler=product_service.get_product_by_id,
    description="Get single product by ID"
)

create_product_contract = UniversalContract(
    name="CreateProduct",
    input_type=Product,
    output_type=Product,
    handler=product_service.create_product,
    description="Create new product"
)

# Register contracts with server
server.register_contract(get_products_contract)
server.register_contract(get_product_contract)
server.register_contract(create_product_contract)

# Adaptive Protocol Selection
class AdaptiveProtocolSelector:
    """ML-based protocol selection"""

    def __init__(self):
        self.performance_history = {
            Protocol.REST: [],
            Protocol.GRAPHQL: [],
            Protocol.GRPC: []
        }

    def select_protocol(self, request_context: dict) -> Protocol:
        """Select optimal protocol based on request characteristics"""

        # Simple heuristic-based selection (in production, use ML model)
        payload_size = request_context.get('payload_size', 0)
        query_complexity = request_context.get('query_complexity', 1)
        real_time_required = request_context.get('real_time', False)

        if real_time_required:
            return Protocol.WEBSOCKET
        elif query_complexity > 3:
            return Protocol.GRAPHQL
        elif payload_size > 10000:
            return Protocol.GRPC
        else:
            return Protocol.REST

    def record_performance(self, protocol: Protocol, latency: float):
        """Record performance for learning"""
        self.performance_history[protocol].append(latency)

# Middleware for adaptive routing
@server.app.middleware("http")
async def adaptive_routing_middleware(request, call_next):
    """Middleware for intelligent protocol routing"""

    selector = AdaptiveProtocolSelector()

    # Extract request context
    context = {
        'payload_size': len(await request.body()) if request.method == "POST" else 0,
        'query_complexity': request.url.path.count('/'),
        'real_time': request.headers.get('X-Real-Time', False)
    }

    # Select optimal protocol
    selected_protocol = selector.select_protocol(context)

    # Add protocol header to response
    response = await call_next(request)
    response.headers["X-Selected-Protocol"] = selected_protocol.value

    return response

# Metrics endpoint
@server.app.get("/metrics")
async def get_metrics():
    """Get server metrics"""
    return server.get_metrics()

# Health check
@server.app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "contracts": list(server.contracts.keys()),
        "protocols": ["REST", "GraphQL", "gRPC"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn

    print("Starting Universal API Server...")
    print("Available contracts:", list(server.contracts.keys()))
    print("\nEndpoints:")
    print("  REST: http://localhost:8000/getproducts")
    print("  REST: http://localhost:8000/getproduct")
    print("  REST: http://localhost:8000/createproduct")
    print("  GraphQL: http://localhost:8000/graphql/*")
    print("  Metrics: http://localhost:8000/metrics")
    print("  Health: http://localhost:8000/health")

    uvicorn.run(server.app, host="0.0.0.0", port=8000)
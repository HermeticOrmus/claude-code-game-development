// Next.js Advanced Patterns - SSR/SSG/ISR with Performance Optimization

import { GetStaticPaths, GetStaticProps, GetServerSideProps, NextPage } from 'next';
import dynamic from 'next/dynamic';
import Image from 'next/image';
import { Suspense, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import type { ParsedUrlQuery } from 'querystring';

// ============================================================================
// Level 1: Dynamic Imports with Code Splitting
// ============================================================================

// Lazy load heavy components
const HeavyChart = dynamic(
  () => import('./components/HeavyChart'),
  {
    loading: () => <div className="skeleton">Loading chart...</div>,
    ssr: false // Disable SSR for client-only components
  }
);

// Parallel loading with named exports
const DynamicComponents = dynamic(
  async () => {
    const [module1, module2] = await Promise.all([
      import('./components/Module1'),
      import('./components/Module2')
    ]);

    return {
      Module1: module1.default,
      Module2: module2.default
    };
  },
  { loading: () => <div>Loading modules...</div> }
);

// ============================================================================
// Level 2: SSG with Incremental Static Regeneration
// ============================================================================

interface ProductPageProps {
  product: {
    id: string;
    name: string;
    description: string;
    price: number;
    image: string;
    updatedAt: string;
  };
  relatedProducts: Array<{
    id: string;
    name: string;
    price: number;
  }>;
}

// Static Generation with ISR
export const ProductPage: NextPage<ProductPageProps> = ({ product, relatedProducts }) => {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <div className="product-page">
      {/* Optimized image loading */}
      <Image
        src={product.image}
        alt={product.name}
        width={800}
        height={600}
        priority // Load immediately for LCP
        placeholder="blur"
        blurDataURL={generateBlurDataURL(product.image)}
      />

      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <p className="price">${product.price}</p>

      {/* Client-only interactive features */}
      {isClient && <InteractiveFeatures productId={product.id} />}

      {/* Related products with lazy loading */}
      <Suspense fallback={<div>Loading related products...</div>}>
        <RelatedProducts products={relatedProducts} />
      </Suspense>

      {/* Heavy chart component loaded on demand */}
      {isClient && <HeavyChart data={generateChartData(product)} />}
    </div>
  );
};

export const getStaticPaths: GetStaticPaths = async () => {
  // Generate paths for top products
  const topProducts = await fetchTopProducts(100);

  return {
    paths: topProducts.map((id) => ({
      params: { id }
    })),
    fallback: 'blocking' // Generate other pages on-demand
  };
};

export const getStaticProps: GetStaticProps<ProductPageProps> = async ({ params }) => {
  const productId = params?.id as string;

  try {
    const [product, relatedProducts] = await Promise.all([
      fetchProduct(productId),
      fetchRelatedProducts(productId)
    ]);

    return {
      props: {
        product,
        relatedProducts
      },
      revalidate: 60, // Revalidate every minute for ISR
      notFound: !product // Return 404 if product not found
    };
  } catch (error) {
    return {
      notFound: true
    };
  }
};

// ============================================================================
// Level 3: Server-Side Rendering with Edge Functions
// ============================================================================

interface DashboardProps {
  user: {
    id: string;
    name: string;
    role: string;
  };
  metrics: {
    views: number;
    clicks: number;
    conversions: number;
  };
  realtimeData: any;
}

export const Dashboard: NextPage<DashboardProps> = ({ user, metrics, realtimeData }) => {
  const [liveMetrics, setLiveMetrics] = useState(metrics);

  useEffect(() => {
    // Establish WebSocket connection for real-time updates
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL!);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLiveMetrics(data.metrics);
    };

    return () => ws.close();
  }, []);

  return (
    <div className="dashboard">
      <h1>Welcome, {user.name}</h1>

      <div className="metrics-grid">
        <MetricCard title="Views" value={liveMetrics.views} />
        <MetricCard title="Clicks" value={liveMetrics.clicks} />
        <MetricCard title="Conversions" value={liveMetrics.conversions} />
      </div>

      {/* Streamed content from edge function */}
      <StreamedContent initialData={realtimeData} userId={user.id} />
    </div>
  );
};

// Edge API route for better performance
export const config = {
  runtime: 'edge', // Use Edge Runtime
};

export const getServerSideProps: GetServerSideProps<DashboardProps> = async (context) => {
  const session = await getSession(context.req);

  if (!session) {
    return {
      redirect: {
        destination: '/login',
        permanent: false
      }
    };
  }

  // Parallel data fetching
  const [user, metrics, realtimeData] = await Promise.all([
    fetchUser(session.userId),
    fetchMetrics(session.userId),
    fetchRealtimeData(session.userId)
  ]);

  // Set cache headers for CDN
  context.res.setHeader(
    'Cache-Control',
    'private, s-maxage=10, stale-while-revalidate=59'
  );

  return {
    props: {
      user,
      metrics,
      realtimeData
    }
  };
};

// ============================================================================
// Level 4: API Routes with Middleware
// ============================================================================

// API route with performance optimization
// pages/api/optimize/[...params].ts
import { NextApiRequest, NextApiResponse } from 'next';
import { withRateLimit } from '@/middleware/rateLimit';
import { withCache } from '@/middleware/cache';
import { withMetrics } from '@/middleware/metrics';

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  const { params } = req.query;
  const path = Array.isArray(params) ? params.join('/') : params;

  // Stream response for large payloads
  if (req.headers.accept?.includes('text/event-stream')) {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });

    const stream = createDataStream(path);

    stream.on('data', (chunk) => {
      res.write(`data: ${JSON.stringify(chunk)}\n\n`);
    });

    stream.on('end', () => {
      res.end();
    });

    return;
  }

  // Regular JSON response with caching
  const data = await fetchOptimizedData(path);

  res.status(200).json({
    data,
    timestamp: Date.now(),
    cache: 'HIT' // or 'MISS'
  });
};

// Apply middleware chain
export default withMetrics(
  withRateLimit(
    withCache(handler, { ttl: 60 })
  )
);

// ============================================================================
// Level 5: Advanced Data Fetching Patterns
// ============================================================================

// SWR for client-side data fetching
import useSWR, { SWRConfig, mutate } from 'swr';
import useSWRInfinite from 'swr/infinite';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

function useProducts(category: string) {
  const { data, error, isLoading, isValidating, mutate } = useSWR(
    `/api/products?category=${category}`,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      dedupingInterval: 2000,
      errorRetryCount: 3,
      shouldRetryOnError: true,
      // Optimistic UI updates
      onSuccess: (data) => {
        console.log('Products loaded:', data.length);
      }
    }
  );

  return {
    products: data,
    isLoading,
    isError: error,
    refresh: mutate
  };
}

// Infinite scrolling with SWR
function useInfiniteProducts() {
  const getKey = (pageIndex: number, previousPageData: any) => {
    if (previousPageData && !previousPageData.length) return null;
    return `/api/products?page=${pageIndex}&limit=20`;
  };

  const { data, error, size, setSize, isValidating } = useSWRInfinite(
    getKey,
    fetcher,
    {
      revalidateFirstPage: false,
      persistSize: true
    }
  );

  const products = data ? data.flat() : [];
  const isLoadingMore = size > 0 && data && typeof data[size - 1] === 'undefined';
  const isEmpty = data?.[0]?.length === 0;
  const isReachingEnd = isEmpty || (data && data[data.length - 1]?.length < 20);

  return {
    products,
    error,
    isLoadingMore,
    size,
    setSize,
    isReachingEnd
  };
}

// ============================================================================
// Level 6: Performance Monitoring
// ============================================================================

// Custom performance observer
function usePerformanceMonitor() {
  useEffect(() => {
    // Web Vitals monitoring
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        // Send metrics to analytics
        analytics.track('performance', {
          name: entry.name,
          value: entry.startTime,
          metric: entry.entryType
        });
      }
    });

    observer.observe({ entryTypes: ['navigation', 'resource', 'paint'] });

    // Report Core Web Vitals
    reportWebVitals((metric) => {
      analytics.track('web-vitals', {
        name: metric.name,
        value: metric.value,
        id: metric.id,
        label: metric.label
      });
    });

    return () => observer.disconnect();
  }, []);
}

// ============================================================================
// Level 7: Progressive Enhancement
// ============================================================================

interface ProgressiveFormProps {
  action: string;
  method?: 'GET' | 'POST';
  onSubmit?: (data: FormData) => Promise<void>;
}

function ProgressiveForm({ action, method = 'POST', onSubmit }: ProgressiveFormProps) {
  const [isEnhanced, setIsEnhanced] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Progressive enhancement - form works without JS
    setIsEnhanced(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    if (!isEnhanced || !onSubmit) return;

    e.preventDefault();
    setIsSubmitting(true);

    const formData = new FormData(e.currentTarget);

    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      action={action}
      method={method}
      onSubmit={handleSubmit}
      className={isEnhanced ? 'enhanced' : 'basic'}
    >
      <input type="text" name="query" required />

      {isEnhanced ? (
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Searching...' : 'Search'}
        </button>
      ) : (
        <button type="submit">Search</button>
      )}

      {/* Fallback for no-JS */}
      <noscript>
        <style>{`.enhanced { display: none; }`}</style>
      </noscript>
    </form>
  );
}

// ============================================================================
// Level 8: Edge Middleware
// ============================================================================

// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // A/B testing
  const bucket = request.cookies.get('bucket')?.value || Math.random() > 0.5 ? 'a' : 'b';

  const response = NextResponse.next();
  response.cookies.set('bucket', bucket);

  // Feature flags
  const features = {
    newDesign: bucket === 'a',
    experimentalApi: request.geo?.country === 'US'
  };

  response.headers.set('x-features', JSON.stringify(features));

  // Geolocation-based routing
  if (request.geo?.country === 'CN') {
    return NextResponse.rewrite(new URL('/cn', request.url));
  }

  // Rate limiting
  const ip = request.ip || 'unknown';
  const rateLimit = getRateLimit(ip);

  if (rateLimit.exceeded) {
    return new NextResponse('Too Many Requests', { status: 429 });
  }

  return response;
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

// ============================================================================
// Helper Functions
// ============================================================================

function generateBlurDataURL(src: string): string {
  // Generate base64 blur placeholder
  return 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...';
}

function generateChartData(product: any): any {
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'Sales',
      data: [12, 19, 3, 5, 2]
    }]
  };
}

async function fetchTopProducts(limit: number): Promise<string[]> {
  // Fetch top product IDs
  return Array.from({ length: limit }, (_, i) => `product-${i}`);
}

async function fetchProduct(id: string): Promise<any> {
  // Fetch product data
  return {
    id,
    name: `Product ${id}`,
    description: 'Description',
    price: 99.99,
    image: '/product.jpg',
    updatedAt: new Date().toISOString()
  };
}

async function fetchRelatedProducts(id: string): Promise<any[]> {
  return Array.from({ length: 4 }, (_, i) => ({
    id: `related-${i}`,
    name: `Related Product ${i}`,
    price: 49.99
  }));
}

// Component placeholders
const InteractiveFeatures: React.FC<{ productId: string }> = ({ productId }) => (
  <div>Interactive features for {productId}</div>
);

const RelatedProducts: React.FC<{ products: any[] }> = ({ products }) => (
  <div className="related-products">
    {products.map((p) => (
      <div key={p.id}>{p.name}</div>
    ))}
  </div>
);

const MetricCard: React.FC<{ title: string; value: number }> = ({ title, value }) => (
  <div className="metric-card">
    <h3>{title}</h3>
    <p>{value}</p>
  </div>
);

const StreamedContent: React.FC<{ initialData: any; userId: string }> = ({ initialData, userId }) => (
  <div>Streamed content for {userId}</div>
);

// Utility functions
async function getSession(req: any): Promise<any> {
  return { userId: '123' };
}

async function fetchUser(userId: string): Promise<any> {
  return { id: userId, name: 'John Doe', role: 'admin' };
}

async function fetchMetrics(userId: string): Promise<any> {
  return { views: 1000, clicks: 100, conversions: 10 };
}

async function fetchRealtimeData(userId: string): Promise<any> {
  return { live: true };
}

function createDataStream(path: string): any {
  const { EventEmitter } = require('events');
  const emitter = new EventEmitter();

  setTimeout(() => {
    emitter.emit('data', { path, timestamp: Date.now() });
    emitter.emit('end');
  }, 100);

  return emitter;
}

async function fetchOptimizedData(path: string): Promise<any> {
  return { path, optimized: true };
}

function getRateLimit(ip: string): { exceeded: boolean } {
  return { exceeded: false };
}

function reportWebVitals(onReport: (metric: any) => void): void {
  // Web Vitals reporting implementation
}

const analytics = {
  track: (event: string, data: any) => console.log('Analytics:', event, data)
};

export default ProductPage;
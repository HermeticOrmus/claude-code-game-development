# Web Hosting for Games

Web hosting is the fastest, easiest, and most accessible way to deploy games. No app store approvals, no installation required—just share a link and players can start immediately. This guide covers everything from free GitHub Pages hosting to professional CDN-backed deployments.

## Why Web Hosting?

**Instant distribution with zero friction**:

- Deploy in minutes, not days
- No app store approval process
- Instant updates (push and it's live)
- Cross-platform by default
- Free or extremely cheap
- Perfect for prototypes, game jams, and portfolio pieces

**Real-world example**: A developer deployed a game jam entry to GitHub Pages in 2 minutes after the deadline. It got 10,000 plays in the first week, all from a simple link shared on Twitter.

## GitHub Pages: Free and Easy

GitHub Pages is perfect for getting started. It's completely free, integrates with your repository, and requires minimal configuration.

### Step-by-Step GitHub Pages Deployment

**1. Prepare Your Project**

Your game must be built into static files (HTML, CSS, JS, assets). Most build tools output to a `dist/` or `build/` directory.

```json
// package.json
{
  "name": "my-game",
  "scripts": {
    "build": "vite build",
    "deploy": "gh-pages -d dist"
  }
}
```

**2. Install gh-pages**

```bash
npm install --save-dev gh-pages
```

**3. Configure Build Output**

For Vite (adjust paths for your build tool):

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  base: '/your-repo-name/', // Important: must match your repo name
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false, // Disable for production
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs
      },
    },
  },
});
```

**4. Deploy**

```bash
# Build and deploy
npm run build
npm run deploy
```

Your game is now live at: `https://username.github.io/repo-name/`

### Automated GitHub Pages Deployment

Set up automatic deployment on every push to `main`:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Build game
      run: npm run build

    - name: Setup Pages
      uses: actions/configure-pages@v3

    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: './dist'

    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2
```

Now every push to `main` automatically builds and deploys your game!

### GitHub Pages Best Practices

**Asset optimization**:
```javascript
// vite.config.js - Advanced optimization
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['phaser'], // Separate vendor code
        },
      },
    },
    assetsInlineLimit: 4096, // Inline small assets as base64
    chunkSizeWarningLimit: 1000,
  },
});
```

**Cache busting**:
```javascript
// Vite automatically adds content hashes to filenames
// dist/assets/game-a3b4c5d6.js
// This ensures players always get the latest version
```

## Netlify: Professional Hosting

Netlify offers more features than GitHub Pages: custom domains, SSL, edge functions, and better performance.

### Netlify Deployment

**Method 1: Drag and Drop (Quickest)**

1. Build your game: `npm run build`
2. Visit [netlify.com](https://netlify.com)
3. Drag `dist/` folder to the upload area
4. Done! Your game is live

**Method 2: Continuous Deployment (Recommended)**

1. Create `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"

# Headers for performance and security
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

# Cache static assets aggressively
[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

# Don't cache HTML
[[headers]]
  for = "/*.html"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"
```

2. Connect to GitHub:
   - Go to Netlify dashboard
   - Click "New site from Git"
   - Choose your repository
   - Netlify auto-detects settings from `netlify.toml`

3. Deploy!

Every push to `main` triggers automatic deployment.

### Custom Domain on Netlify

```bash
# 1. In Netlify dashboard: Domain settings → Add custom domain
# 2. Add DNS records (Netlify provides exact values)
# 3. Wait for DNS propagation (5 minutes to 24 hours)
# 4. Enable HTTPS (Netlify provides free SSL via Let's Encrypt)
```

**DNS Configuration Example**:
```
Type: A
Name: @
Value: 75.2.60.5

Type: CNAME
Name: www
Value: your-site.netlify.app
```

### Netlify Edge Functions for Games

Use edge functions for leaderboards, authentication, etc.:

```javascript
// netlify/edge-functions/leaderboard.js
export default async (request, context) => {
  const { method } = request;

  if (method === 'GET') {
    // Fetch leaderboard from database
    const scores = await fetch('https://your-api.com/scores');
    return new Response(JSON.stringify(await scores.json()), {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  if (method === 'POST') {
    // Submit new score
    const { player, score } = await request.json();

    // Validate score server-side (prevent cheating)
    if (score > 10000 || score < 0) {
      return new Response('Invalid score', { status: 400 });
    }

    // Save to database
    await fetch('https://your-api.com/scores', {
      method: 'POST',
      body: JSON.stringify({ player, score }),
    });

    return new Response('Score saved', { status: 200 });
  }
};

export const config = { path: '/api/leaderboard' };
```

## Vercel: Optimized for Performance

Vercel focuses on speed with edge network deployment and automatic optimization.

### Vercel Deployment

**1. Install Vercel CLI**:
```bash
npm install -g vercel
```

**2. Deploy from command line**:
```bash
vercel
```

That's it! Vercel automatically:
- Detects your framework
- Builds your project
- Deploys to edge network
- Provides HTTPS URL

**3. Configure with `vercel.json`**:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**4. Automatic deployments**:

Connect to GitHub and Vercel automatically deploys:
- Every push to `main` → Production
- Every PR → Preview deployment with unique URL

### Vercel Analytics

```javascript
// Add to your game's HTML
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
```

Track custom events:
```javascript
// In your game code
window.va('event', { name: 'level_complete', data: { level: 5, time: 120 } });
window.va('event', { name: 'game_over', data: { score: 1250 } });
```

## Custom Domain Setup

### Buying a Domain

**Recommended registrars**:
- **Namecheap**: ~$10/year, good UI
- **Google Domains**: ~$12/year, simple
- **Cloudflare**: At-cost pricing (~$8-10/year)

### DNS Configuration

**For Netlify**:
```
Type: A
Name: @
Value: 75.2.60.5

Type: CNAME
Name: www
Value: your-site.netlify.app
```

**For Vercel**:
```
Type: A
Name: @
Value: 76.76.19.19

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**For GitHub Pages**:
```
Type: A
Name: @
Values:
  185.199.108.153
  185.199.109.153
  185.199.110.153
  185.199.111.153

Type: CNAME
Name: www
Value: username.github.io
```

### SSL/HTTPS Configuration

**All platforms provide free SSL automatically**:

- **GitHub Pages**: Automatic via Let's Encrypt (may take a few minutes)
- **Netlify**: Automatic, instant
- **Vercel**: Automatic, instant

**Force HTTPS** (in your HTML):
```html
<script>
  // Redirect HTTP to HTTPS
  if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    location.replace('https:' + window.location.href.substring(window.location.protocol.length));
  }
</script>
```

## Asset Optimization for Production

### Image Optimization

**Use modern formats**:
```bash
# Convert PNGs to WebP (smaller, better quality)
npm install --save-dev imagemin imagemin-webp

# scripts/optimize-images.js
import imagemin from 'imagemin';
import imageminWebp from 'imagemin-webp';

await imagemin(['src/assets/*.{jpg,png}'], {
  destination: 'dist/assets',
  plugins: [
    imageminWebp({ quality: 80 })
  ]
});
```

**Responsive images**:
```html
<picture>
  <source srcset="hero-800.webp" media="(max-width: 800px)" type="image/webp">
  <source srcset="hero-1200.webp" media="(max-width: 1200px)" type="image/webp">
  <source srcset="hero-1920.webp" type="image/webp">
  <img src="hero-1200.jpg" alt="Game hero image">
</picture>
```

### Audio Optimization

**Use appropriate formats**:
```javascript
// Use OGG for web (smaller than MP3)
const audio = new Audio();
audio.src = audio.canPlayType('audio/ogg')
  ? 'sound.ogg'
  : 'sound.mp3';
```

**Lazy load audio**:
```javascript
// Don't load audio until user interaction
document.addEventListener('click', () => {
  loadAudio();
}, { once: true });
```

### Code Splitting

**Split large games into chunks**:
```javascript
// Load levels on demand
async function loadLevel(levelNumber) {
  const level = await import(`./levels/level-${levelNumber}.js`);
  return level.default;
}

// Usage
const level1 = await loadLevel(1);
```

### Compression

**Enable gzip/brotli compression**:

Most hosts (Netlify, Vercel) do this automatically. For custom servers:

```javascript
// Express.js example
import compression from 'compression';
app.use(compression());
```

## CDN Integration (Cloudflare)

Cloudflare provides free CDN, DDoS protection, and performance optimization.

### Cloudflare Setup

1. **Sign up** at cloudflare.com
2. **Add your site** (domain)
3. **Update nameservers** at your registrar:
   ```
   molly.ns.cloudflare.com
   paul.ns.cloudflare.com
   ```
4. **Configure settings**:

**Recommended Cloudflare settings for games**:
```
Speed → Optimization
  ✓ Auto Minify: JavaScript, CSS, HTML
  ✓ Brotli compression
  ✓ Rocket Loader: Off (can break games)

Caching → Configuration
  Browser Cache TTL: 4 hours

Page Rules:
  *.js, *.css → Cache Level: Cache Everything, Edge Cache TTL: 1 month
  *.png, *.jpg, *.webp → Cache Level: Cache Everything, Edge Cache TTL: 1 year
  *.html → Cache Level: Bypass (always fresh)
```

**Cloudflare Workers for game features**:
```javascript
// Cloudflare Worker - Rate limiting for API endpoints
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/api/submit-score') {
      const ip = request.headers.get('CF-Connecting-IP');

      // Rate limit: 10 requests per minute per IP
      const rateLimit = await checkRateLimit(ip, env);
      if (!rateLimit.allowed) {
        return new Response('Too many requests', { status: 429 });
      }

      // Process request
      return handleScoreSubmission(request);
    }

    return fetch(request);
  }
};
```

## Cost Analysis Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| **GitHub Pages** | Unlimited public repos | N/A | Open source, portfolios |
| **Netlify** | 100GB bandwidth, 300 build minutes | $19/mo for 400GB | Small to medium games |
| **Vercel** | 100GB bandwidth, unlimited builds | $20/mo for 1TB | Performance-critical games |
| **Cloudflare Pages** | Unlimited bandwidth, 500 builds/mo | $20/mo for 5000 builds | High-traffic games |
| **AWS S3 + CloudFront** | First year free, then ~$5/mo | Scales with traffic | Enterprise games |

**Example costs for 10,000 monthly players**:
- **GitHub Pages**: $0
- **Netlify**: $0 (within free tier)
- **Vercel**: $0 (within free tier)
- **Self-hosted + Cloudflare**: ~$5/mo

## Complete Deployment Example

**Full-featured deployment with GitHub Actions**:

```yaml
# .github/workflows/deploy-production.yml
name: Deploy Production

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Build game
      run: npm run build
      env:
        NODE_ENV: production
        VITE_API_URL: https://api.mygame.com

    - name: Optimize images
      run: node scripts/optimize-images.js

    - name: Generate sitemap
      run: node scripts/generate-sitemap.js

    - name: Deploy to Netlify
      uses: nwtgck/actions-netlify@v2
      with:
        publish-dir: './dist'
        production-branch: main
        github-token: ${{ secrets.GITHUB_TOKEN }}
        deploy-message: "Deploy from GitHub Actions"
        enable-pull-request-comment: true
        enable-commit-comment: true
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
        vercel-args: '--prod'

    - name: Purge Cloudflare cache
      run: |
        curl -X POST "https://api.cloudflare.com/client/v4/zones/${{ secrets.CLOUDFLARE_ZONE_ID }}/purge_cache" \
          -H "Authorization: Bearer ${{ secrets.CLOUDFLARE_API_TOKEN }}" \
          -H "Content-Type: application/json" \
          --data '{"purge_everything":true}'

    - name: Notify Discord
      uses: sarisia/actions-status-discord@v1
      if: always()
      with:
        webhook: ${{ secrets.DISCORD_WEBHOOK }}
        title: "Game Deployed! 🎮"
        description: "New version deployed to production"
        url: "https://mygame.com"
```

## Claude Code Prompts for Deployment

**Generate deployment configuration**:
```
Create deployment configurations for this game to:
- GitHub Pages
- Netlify
- Vercel

Include:
- Build optimization
- Asset compression
- Cache headers
- SEO meta tags
- Error handling

Generate config files and GitHub Actions workflows.
```

**Optimize for production**:
```
Optimize this game for production deployment:
- Minify and bundle code
- Compress images to WebP
- Implement code splitting
- Add loading screen
- Configure caching headers
- Remove console.logs

Provide optimized build configuration.
```

## Best Practices

1. **Use CDN** - Serve assets from edge locations
2. **Enable compression** - Gzip or Brotli
3. **Optimize images** - Use WebP, responsive images
4. **Code splitting** - Load code on demand
5. **Cache aggressively** - Long cache for assets, short for HTML
6. **Monitor performance** - Track loading times
7. **Test on real devices** - Especially mobile
8. **Provide loading feedback** - Progress bars, not blank screens
9. **Error tracking** - Know when things break
10. **Analytics** - Understand your players

## Common Issues and Solutions

**Issue: Game loads slowly**
- Solution: Optimize assets, implement code splitting, use CDN

**Issue: Assets 404 after deployment**
- Solution: Check `base` path in build config, use relative URLs

**Issue: Game works locally but not in production**
- Solution: Check browser console, ensure all assets are included in build

**Issue: Updates don't appear for players**
- Solution: Implement cache busting, service worker updates

**Issue: High hosting costs**
- Solution: Optimize bundle size, implement better caching

## Next Steps

Now that your game is hosted on the web, you might want to expand to mobile devices. Continue to [Mobile Packaging](./mobile-packaging.md) to learn how to create Progressive Web Apps and native mobile apps.

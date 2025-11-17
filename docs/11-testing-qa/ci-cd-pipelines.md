# CI/CD Pipelines for Game Development

Continuous Integration and Continuous Deployment (CI/CD) automates testing and deployment, ensuring every code change is validated before reaching players. This guide shows you how to set up robust pipelines specifically for game development.

## Why CI/CD for Games?

**Manual testing is slow and error-prone**. CI/CD pipelines:

- Run tests automatically on every commit
- Catch bugs before they reach production
- Deploy new versions without manual steps
- Ensure consistent build quality
- Enable rapid iteration
- Provide instant feedback to developers

**Real-world impact**: A small indie game team reduced their QA time from 2 hours per release to 5 minutes automated, shipping updates 3x faster.

## GitHub Actions for Games

GitHub Actions is free for public repositories and integrates seamlessly with your code.

### Basic Workflow Structure

Create `.github/workflows/test.yml`:

```yaml
name: Test Game

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run unit tests
      run: npm test

    - name: Run integration tests
      run: npm run test:integration

    - name: Generate coverage report
      run: npm run test:coverage

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage/coverage-final.json
```

### Complete Test Pipeline

```yaml
name: Complete Game Testing Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run ESLint
      run: npm run lint

  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run unit tests
      run: npm test -- --coverage

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright browsers
      run: npx playwright install --with-deps

    - name: Run integration tests
      run: npm run test:integration

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: playwright-results
        path: test-results/

  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run performance benchmarks
      run: npm run test:performance

    - name: Compare with baseline
      run: node scripts/compare-performance.js

    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const results = JSON.parse(fs.readFileSync('performance-results.json'));
          const body = `## Performance Results

          | Metric | Before | After | Change |
          |--------|--------|-------|--------|
          | Avg FPS | ${results.baseline.fps} | ${results.current.fps} | ${results.delta.fps}% |
          | Frame Time | ${results.baseline.frameTime}ms | ${results.current.frameTime}ms | ${results.delta.frameTime}% |
          | Memory | ${results.baseline.memory}MB | ${results.current.memory}MB | ${results.delta.memory}% |
          `;

          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: body
          });

  build:
    name: Build Game
    runs-on: ubuntu-latest
    needs: [lint, unit-tests]
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Build production bundle
      run: npm run build

    - name: Check bundle size
      run: node scripts/check-bundle-size.js

    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: game-build
        path: dist/

  automated-playtesting:
    name: Automated Playtesting
    runs-on: ubuntu-latest
    needs: build
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: game-build
        path: dist/

    - name: Run automated playtests
      run: npm run playtest:automated

    - name: Generate playtest report
      run: node scripts/generate-playtest-report.js

    - name: Upload playtest results
      uses: actions/upload-artifact@v3
      with:
        name: playtest-results
        path: playtest-results.json
```

### Performance Comparison Script

```javascript
// scripts/compare-performance.js
const fs = require('fs');
const path = require('path');

const currentResults = JSON.parse(
  fs.readFileSync('performance-current.json', 'utf8')
);

let baselineResults;
const baselinePath = 'performance-baseline.json';

if (fs.existsSync(baselinePath)) {
  baselineResults = JSON.parse(fs.readFileSync(baselinePath, 'utf8'));
} else {
  // First run, set as baseline
  fs.writeFileSync(baselinePath, JSON.stringify(currentResults, null, 2));
  console.log('Baseline performance metrics saved');
  process.exit(0);
}

const delta = {
  fps: ((currentResults.fps - baselineResults.fps) / baselineResults.fps * 100).toFixed(2),
  frameTime: ((currentResults.frameTime - baselineResults.frameTime) / baselineResults.frameTime * 100).toFixed(2),
  memory: ((currentResults.memory - baselineResults.memory) / baselineResults.memory * 100).toFixed(2),
};

const results = {
  baseline: baselineResults,
  current: currentResults,
  delta: delta,
};

fs.writeFileSync('performance-results.json', JSON.stringify(results, null, 2));

console.log('Performance Comparison:');
console.log(`FPS: ${baselineResults.fps} → ${currentResults.fps} (${delta.fps}%)`);
console.log(`Frame Time: ${baselineResults.frameTime}ms → ${currentResults.frameTime}ms (${delta.frameTime}%)`);
console.log(`Memory: ${baselineResults.memory}MB → ${currentResults.memory}MB (${delta.memory}%)`);

// Fail if performance degraded significantly
const thresholds = {
  fps: -10, // Fail if FPS drops more than 10%
  frameTime: 15, // Fail if frame time increases more than 15%
  memory: 25, // Fail if memory increases more than 25%
};

const failures = [];

if (parseFloat(delta.fps) < thresholds.fps) {
  failures.push(`FPS degraded by ${delta.fps}%`);
}

if (parseFloat(delta.frameTime) > thresholds.frameTime) {
  failures.push(`Frame time increased by ${delta.frameTime}%`);
}

if (parseFloat(delta.memory) > thresholds.memory) {
  failures.push(`Memory usage increased by ${delta.memory}%`);
}

if (failures.length > 0) {
  console.error('\n❌ Performance regression detected:');
  failures.forEach(f => console.error(`  - ${f}`));
  process.exit(1);
}

console.log('\n✅ Performance within acceptable bounds');
```

### Bundle Size Check Script

```javascript
// scripts/check-bundle-size.js
const fs = require('fs');
const path = require('path');

const distPath = path.join(__dirname, '../dist');

function getDirectorySize(dir) {
  let size = 0;

  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stats = fs.statSync(filePath);

    if (stats.isDirectory()) {
      size += getDirectorySize(filePath);
    } else {
      size += stats.size;
    }
  }

  return size;
}

const totalSize = getDirectorySize(distPath);
const totalSizeMB = (totalSize / 1024 / 1024).toFixed(2);

console.log(`Total bundle size: ${totalSizeMB} MB`);

// Read individual file sizes
const files = fs.readdirSync(distPath);
const fileSizes = files
  .map(file => {
    const filePath = path.join(distPath, file);
    const stats = fs.statSync(filePath);
    return {
      name: file,
      size: (stats.size / 1024).toFixed(2) + ' KB',
      sizeBytes: stats.size,
    };
  })
  .filter(f => !fs.statSync(path.join(distPath, f.name)).isDirectory())
  .sort((a, b) => b.sizeBytes - a.sizeBytes);

console.log('\nLargest files:');
fileSizes.slice(0, 5).forEach(f => {
  console.log(`  ${f.name}: ${f.size}`);
});

// Set size limit (e.g., 5MB)
const MAX_SIZE_MB = 5;

if (totalSize > MAX_SIZE_MB * 1024 * 1024) {
  console.error(`\n❌ Bundle size (${totalSizeMB} MB) exceeds limit (${MAX_SIZE_MB} MB)`);
  process.exit(1);
}

console.log(`\n✅ Bundle size within ${MAX_SIZE_MB} MB limit`);
```

## Automated Deployment

Deploy automatically when tests pass:

```yaml
name: Deploy Game

on:
  push:
    branches: [ main ]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run all tests
      run: npm test

  deploy:
    name: Deploy to GitHub Pages
    runs-on: ubuntu-latest
    needs: test
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Build game
      run: npm run build

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./dist

  deploy-netlify:
    name: Deploy to Netlify
    runs-on: ubuntu-latest
    needs: test
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Build game
      run: npm run build

    - name: Deploy to Netlify
      uses: nwtgck/actions-netlify@v2
      with:
        publish-dir: './dist'
        production-branch: main
        github-token: ${{ secrets.GITHUB_TOKEN }}
        deploy-message: "Deploy from GitHub Actions"
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}

  deploy-itch:
    name: Deploy to Itch.io
    runs-on: ubuntu-latest
    needs: test
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Build game
      run: npm run build

    - name: Package for Itch.io
      run: zip -r game.zip dist/*

    - name: Upload to Itch.io
      uses: josephbmanley/butler-publish-itchio-action@master
      env:
        BUTLER_CREDENTIALS: ${{ secrets.BUTLER_CREDENTIALS }}
        CHANNEL: html5
        ITCH_GAME: my-awesome-game
        ITCH_USER: myusername
        PACKAGE: game.zip
```

## Multi-Platform Testing

Test on different browsers and operating systems:

```yaml
name: Cross-Platform Testing

on: [push, pull_request]

jobs:
  test:
    name: Test on ${{ matrix.os }} with Node ${{ matrix.node }}
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [16, 18, 20]
        browser: [chromium, firefox, webkit]

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node }}

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright browsers
      run: npx playwright install --with-deps ${{ matrix.browser }}

    - name: Run tests on ${{ matrix.browser }}
      run: npm run test:integration -- --browser=${{ matrix.browser }}

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.os }}-node${{ matrix.node }}-${{ matrix.browser }}
        path: test-results/
```

## Scheduled Playtesting

Run automated playtests on a schedule:

```yaml
name: Scheduled Playtesting

on:
  schedule:
    # Run every night at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  extended-playtest:
    name: Extended Automated Playtest
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run 1000 playthroughs
      run: npm run playtest:extensive
      timeout-minutes: 60

    - name: Analyze results
      run: node scripts/analyze-playtests.js

    - name: Generate report
      run: node scripts/generate-html-report.js

    - name: Upload report
      uses: actions/upload-artifact@v3
      with:
        name: playtest-report-${{ github.run_number }}
        path: reports/

    - name: Notify on failures
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: 'Automated Playtest Failed',
            body: 'The scheduled playtest run failed. Check the artifacts for details.',
            labels: ['bug', 'automated-test']
          });
```

## Complete Package.json Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:integration": "playwright test",
    "test:integration:ui": "playwright test --ui",
    "test:performance": "node tests/performance/run-benchmarks.js",
    "playtest:automated": "node tests/playtest/run-automated.js",
    "playtest:extensive": "node tests/playtest/run-automated.js --iterations=1000",
    "lint": "eslint src/",
    "lint:fix": "eslint src/ --fix",
    "build": "vite build",
    "build:analyze": "vite build --mode analyze",
    "dev": "vite",
    "preview": "vite preview"
  }
}
```

## Notification Integration

Get notified when builds fail or succeed:

### Discord Notifications

```yaml
- name: Discord notification
  if: always()
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    status: ${{ job.status }}
    title: "Game Build ${{ job.status }}"
    description: "Build #${{ github.run_number }}"
    color: ${{ job.status == 'success' && '0x00FF00' || '0xFF0000' }}
```

### Slack Notifications

```yaml
- name: Slack notification
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Game build ${{ job.status }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Advanced: Docker for Consistent Builds

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Run tests and build
CMD npm test && npm run build
```

```yaml
# .github/workflows/docker-build.yml
name: Docker Build and Test

on: [push, pull_request]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: docker build -t game-test .

    - name: Run tests in Docker
      run: docker run game-test npm test

    - name: Build game in Docker
      run: docker run -v $PWD/dist:/app/dist game-test npm run build
```

## Claude Code Prompts for CI/CD

**Generate GitHub Actions workflow**:
```
Create a complete GitHub Actions CI/CD workflow for this game project that:
1. Runs unit tests with Jest
2. Runs integration tests with Playwright
3. Checks code quality with ESLint
4. Runs performance benchmarks
5. Builds production bundle
6. Deploys to GitHub Pages on main branch
7. Posts performance metrics as PR comments

Include matrix testing for multiple browsers.
```

**Generate deployment script**:
```
Create deployment scripts for this game to:
- GitHub Pages
- Netlify
- Itch.io

Include:
- Build optimization
- Asset minification
- Cache busting
- Deployment verification

Generate both GitHub Actions workflows and manual deploy scripts.
```

**Generate performance monitoring**:
```
Create a performance monitoring system for CI that:
- Runs benchmarks on every PR
- Compares against baseline
- Fails if performance regresses >10%
- Generates visual performance charts
- Posts results as PR comments

Include scripts for tracking FPS, memory, and bundle size.
```

## Best Practices

1. **Fail fast** - Run quick tests first (lint, unit tests)
2. **Parallelize** - Run independent jobs concurrently
3. **Cache dependencies** - Use npm/yarn cache for speed
4. **Timeout protection** - Set reasonable timeouts
5. **Artifact retention** - Save test results and builds
6. **Branch protection** - Require passing tests before merge
7. **Performance budgets** - Enforce size and speed limits
8. **Automated notifications** - Alert team of failures

## Measuring Pipeline Health

Track these metrics:

- **Pipeline success rate**: % of builds that pass
- **Average pipeline duration**: How long builds take
- **Flaky test rate**: Tests that intermittently fail
- **Deployment frequency**: How often you ship
- **Time to recovery**: How quickly you fix failures

**Example dashboard** (using GitHub Actions API):

```javascript
// scripts/pipeline-health.js
const { Octokit } = require('@octokit/rest');

async function analyzePipelineHealth() {
  const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

  const { data: runs } = await octokit.actions.listWorkflowRunsForRepo({
    owner: 'myuser',
    repo: 'mygame',
    per_page: 100,
  });

  const successful = runs.workflow_runs.filter(r => r.conclusion === 'success').length;
  const failed = runs.workflow_runs.filter(r => r.conclusion === 'failure').length;
  const successRate = (successful / runs.workflow_runs.length * 100).toFixed(2);

  const durations = runs.workflow_runs.map(r =>
    new Date(r.updated_at) - new Date(r.created_at)
  );
  const avgDuration = durations.reduce((a, b) => a + b) / durations.length;

  console.log(`Success Rate: ${successRate}%`);
  console.log(`Average Duration: ${(avgDuration / 1000 / 60).toFixed(2)} minutes`);
}

analyzePipelineHealth();
```

## Next Steps

With CI/CD in place, you're ready to deploy your game. Continue to [Deployment & Distribution](../12-deployment-distribution/README.md) to learn how to get your game to players.

**Remember**: CI/CD is an investment that pays dividends. The time you spend setting it up will be repaid many times over in faster iteration and higher quality.

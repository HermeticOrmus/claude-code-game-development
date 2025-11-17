# Monetization Strategies

Turning games into revenue requires thoughtful strategy. This guide covers ethical monetization approaches, from ads to premium models, with complete implementation examples and revenue optimization techniques.

## Monetization Overview

**The reality**: Most free games make $0. Successful monetization requires planning from day one, not as an afterthought.

**Revenue models**:
1. **Advertising** - Free game supported by ads
2. **Premium** - Pay once to download/play
3. **Freemium** - Free with optional purchases
4. **Subscription** - Recurring payment for access
5. **Sponsorship** - Brand deals and partnerships
6. **Donations** - Patreon, Ko-fi, etc.

## Ad Integration

### Google AdSense for Web Games

**Setup**:
```html
<!-- Add to index.html -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
     crossorigin="anonymous"></script>
```

**Display ads between levels**:
```javascript
// AdManager.js
export class AdManager {
  constructor(config = {}) {
    this.adClient = config.adClient;
    this.adSlot = config.adSlot;
    this.enabled = config.enabled !== false;
    this.minTimeBetweenAds = config.minTimeBetweenAds || 120000; // 2 minutes
    this.lastAdTime = 0;
  }

  canShowAd() {
    if (!this.enabled) return false;
    const now = Date.now();
    return (now - this.lastAdTime) >= this.minTimeBetweenAds;
  }

  showInterstitial() {
    if (!this.canShowAd()) {
      console.log('Too soon for another ad');
      return Promise.resolve(false);
    }

    return new Promise((resolve) => {
      // Create ad container
      const adContainer = document.createElement('div');
      adContainer.id = 'interstitial-ad';
      adContainer.className = 'ad-interstitial';

      const adInner = document.createElement('ins');
      adInner.className = 'adsbygoogle';
      adInner.style.display = 'block';
      adInner.dataset.adClient = this.adClient;
      adInner.dataset.adSlot = this.adSlot;
      adInner.dataset.adFormat = 'auto';
      adInner.dataset.fullWidthResponsive = 'true';

      const closeButton = document.createElement('button');
      closeButton.textContent = 'Continue (5)';
      closeButton.className = 'ad-close-button';
      closeButton.disabled = true;

      adContainer.appendChild(adInner);
      adContainer.appendChild(closeButton);
      document.body.appendChild(adContainer);

      // Load ad
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (error) {
        console.error('Failed to load ad:', error);
      }

      // Enable close button after 5 seconds
      let countdown = 5;
      const countdownInterval = setInterval(() => {
        countdown--;
        closeButton.textContent = `Continue (${countdown})`;

        if (countdown <= 0) {
          clearInterval(countdownInterval);
          closeButton.textContent = 'Continue';
          closeButton.disabled = false;
        }
      }, 1000);

      closeButton.addEventListener('click', () => {
        adContainer.remove();
        this.lastAdTime = Date.now();
        resolve(true);
      });
    });
  }

  showRewarded(reward) {
    // Rewarded video ads require AdMob or similar
    return new Promise((resolve) => {
      // Integration with rewarded ad network
      console.log('Showing rewarded ad for:', reward);

      // On completion
      setTimeout(() => {
        resolve(true); // User watched ad
      }, 30000);
    });
  }
}

// Usage in game
const adManager = new AdManager({
  adClient: 'ca-pub-XXXXXXXXXXXXXXXX',
  adSlot: '1234567890',
  enabled: true,
});

async function onLevelComplete() {
  // Show ad every few levels
  if (currentLevel % 3 === 0) {
    await game.pause();
    await adManager.showInterstitial();
    await game.resume();
  }

  loadNextLevel();
}

async function onGameOver() {
  const watchedAd = await adManager.showRewarded('extra life');

  if (watchedAd) {
    grantExtraLife();
  } else {
    showGameOverScreen();
  }
}
```

### Google AdMob for Mobile

**Setup**:
```bash
npm install @capacitor-community/admob
npx cap sync
```

**Configure**:
```typescript
// admobConfig.ts
import { AdMob } from '@capacitor-community/admob';

export async function initializeAdMob() {
  await AdMob.initialize({
    requestTrackingAuthorization: true,
    testingDevices: ['YOUR_DEVICE_ID'],
  });
}

export async function showInterstitial() {
  await AdMob.prepareInterstitial({
    adId: 'ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY',
  });

  await AdMob.showInterstitial();
}

export async function showRewarded() {
  await AdMob.prepareRewardVideoAd({
    adId: 'ca-app-pub-XXXXXXXXXXXXXXXX/ZZZZZZZZZZ',
  });

  const result = await AdMob.showRewardVideoAd();
  return result.rewarded;
}
```

## In-App Purchases

### Web Payments API

```javascript
// IAPManager.js
export class IAPManager {
  constructor() {
    this.products = {
      removeAds: { id: 'remove_ads', price: 2.99 },
      extraLives: { id: 'extra_lives_5', price: 0.99 },
      premiumSkins: { id: 'premium_skins', price: 4.99 },
    };
  }

  async purchase(productId) {
    const product = this.products[productId];
    if (!product) throw new Error('Unknown product');

    if (!window.PaymentRequest) {
      // Fallback to payment processor
      return this.fallbackPayment(product);
    }

    const paymentMethods = [{
      supportedMethods: 'https://your-payment-processor.com',
    }];

    const paymentDetails = {
      total: {
        label: 'Purchase',
        amount: { currency: 'USD', value: product.price.toString() },
      },
    };

    try {
      const request = new PaymentRequest(paymentMethods, paymentDetails);
      const payment = await request.show();
      const result = await this.processPayment(payment, product);

      if (result.success) {
        await payment.complete('success');
        this.grantPurchase(productId);
        return true;
      } else {
        await payment.complete('fail');
        return false;
      }
    } catch (error) {
      console.error('Payment failed:', error);
      return false;
    }
  }

  async processPayment(payment, product) {
    // Send to your backend
    const response = await fetch('/api/process-payment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product: product.id,
        paymentDetails: payment.details,
      }),
    });

    return response.json();
  }

  grantPurchase(productId) {
    switch (productId) {
      case 'removeAds':
        localStorage.setItem('ads_removed', 'true');
        game.adManager.enabled = false;
        break;

      case 'extraLives':
        game.state.lives += 5;
        break;

      case 'premiumSkins':
        game.unlockAllSkins();
        break;
    }
  }

  hasPurchased(productId) {
    return localStorage.getItem(`purchased_${productId}`) === 'true';
  }
}

// Usage
const iapManager = new IAPManager();

async function showShop() {
  const shopUI = createShopUI();

  shopUI.on('purchase', async (productId) => {
    const success = await iapManager.purchase(productId);

    if (success) {
      showMessage('Purchase successful!');
    } else {
      showMessage('Purchase failed');
    }
  });
}
```

### Mobile IAP with Capacitor

```bash
npm install @capacitor-community/in-app-purchases
```

```typescript
// mobileIAP.ts
import { InAppPurchases } from '@capacitor-community/in-app-purchases';

export class MobileIAP {
  async initialize() {
    await InAppPurchases.restorePurchases();

    InAppPurchases.addListener('purchaseUpdated', (purchase) => {
      if (purchase.state === 'purchased') {
        this.grantPurchase(purchase.productId);
        InAppPurchases.finalizePurchase({ purchase });
      }
    });
  }

  async purchase(productId: string) {
    try {
      await InAppPurchases.purchaseProduct({ productId });
      return true;
    } catch (error) {
      console.error('Purchase failed:', error);
      return false;
    }
  }

  async getProducts() {
    const result = await InAppPurchases.getProducts({
      productIds: ['remove_ads', 'extra_lives_5', 'premium_skins'],
    });

    return result.products;
  }

  grantPurchase(productId: string) {
    // Same as web version
  }
}
```

## Premium Version Strategy

### Feature Comparison

Create clear value proposition:

```javascript
// PremiumManager.js
export class PremiumManager {
  constructor() {
    this.isPremium = this.checkPremiumStatus();

    this.premiumFeatures = {
      noAds: true,
      allLevels: true,
      cloudSaves: true,
      exclusiveSkins: true,
      prioritySupport: true,
    };

    this.freeFeatures = {
      noAds: false,
      firstTenLevels: true,
      localSaves: true,
      basicSkins: true,
    };
  }

  checkPremiumStatus() {
    // Check if user has premium
    return localStorage.getItem('premium') === 'true' ||
           this.checkPlatformPurchase();
  }

  checkPlatformPurchase() {
    // Check Steam/App Store purchase
    if (window.greenworks) {
      // Steam - premium is owning the game
      return true;
    }

    if (window.cordova && window.store) {
      // Mobile app store
      return window.store.owned('premium_version');
    }

    return false;
  }

  async upgradeToPremium() {
    const price = 9.99;

    if (confirm(`Upgrade to Premium for $${price}?`)) {
      const success = await this.processPurchase();

      if (success) {
        this.isPremium = true;
        localStorage.setItem('premium', 'true');
        this.enablePremiumFeatures();
        return true;
      }
    }

    return false;
  }

  enablePremiumFeatures() {
    // Unlock all levels
    game.unlockAllLevels();

    // Disable ads
    game.adManager.enabled = false;

    // Enable cloud saves
    game.enableCloudSaves();

    // Show thank you message
    showMessage('Thanks for upgrading to Premium! 🎮');
  }

  showUpgradePrompt() {
    // Show at strategic moments
    const modal = createModal({
      title: 'Upgrade to Premium',
      content: `
        <h3>Get the full experience!</h3>
        <ul>
          <li>✓ No ads</li>
          <li>✓ All 50 levels</li>
          <li>✓ Cloud saves</li>
          <li>✓ Exclusive skins</li>
          <li>✓ Priority support</li>
        </ul>
        <p class="price">Only $9.99</p>
      `,
      buttons: [
        { text: 'Upgrade Now', action: () => this.upgradeToPremium() },
        { text: 'Maybe Later', action: () => modal.close() },
      ],
    });
  }
}
```

## Sponsorship Opportunities

### Finding Sponsors

**Platforms for game sponsorships**:
- **FGL (FlashGameLicense)** - Game licensing marketplace
- **Poki** - Exclusive licensing deals
- **CrazyGames** - Revenue share + sponsorships
- **Newgrounds** - Community-driven sponsorships

**Typical sponsorship deals**:
- **Exclusive license**: $500-$5,000 (game only on their site)
- **Non-exclusive license**: $200-$2,000 (game on multiple sites)
- **Site-locked version**: $100-$500 (custom version for one site)

**What sponsors want**:
```javascript
// Sponsor branding integration
export class SponsorIntegration {
  constructor(sponsor) {
    this.sponsor = sponsor;
  }

  showPreloader() {
    // Sponsor logo during loading
    const logo = document.createElement('img');
    logo.src = this.sponsor.logoUrl;
    logo.className = 'sponsor-logo';
    document.getElementById('preloader').appendChild(logo);
  }

  showMoreGames() {
    // Link to sponsor's game portal
    const button = document.createElement('button');
    button.textContent = 'More Games';
    button.onclick = () => {
      window.open(this.sponsor.moreGamesUrl, '_blank');
    };
    document.getElementById('menu').appendChild(button);
  }

  trackAnalytics() {
    // Send gameplay data to sponsor
    fetch(this.sponsor.analyticsUrl, {
      method: 'POST',
      body: JSON.stringify({
        event: 'game_start',
        game_id: this.sponsor.gameId,
      }),
    });
  }
}
```

## Ethical Monetization

### Best Practices

**DO**:
- Be transparent about costs
- Provide value for money
- Respect player time
- Allow earning through gameplay
- Make ads skippable when possible
- Offer one-time purchases to remove ads

**DON'T**:
- Use deceptive pricing
- Create pay-to-win mechanics
- Force ads too frequently
- Hide gameplay behind paywalls
- Use loot boxes without disclosure
- Exploit addictive mechanics

**Example: Ethical freemium**:
```javascript
export class EthicalMonetization {
  constructor() {
    this.watchedAdsToday = 0;
    this.maxAdsPerDay = 10; // Respect players' time
  }

  canShowAd() {
    return this.watchedAdsToday < this.maxAdsPerDay;
  }

  offerChoice(context) {
    // Always give players a choice
    return {
      options: [
        {
          text: 'Watch ad for reward',
          action: async () => {
            if (this.canShowAd()) {
              await this.showRewardedAd();
              return 'rewarded';
            } else {
              return 'limit_reached';
            }
          },
        },
        {
          text: 'Skip (costs 10 coins)',
          action: () => {
            if (game.coins >= 10) {
              game.coins -= 10;
              return 'paid';
            }
            return 'insufficient_funds';
          },
        },
        {
          text: 'Come back later',
          action: () => 'declined',
        },
      ],
    };
  }
}
```

## Revenue Analytics

### Tracking Monetization

```javascript
// RevenueTracker.js
export class RevenueTracker {
  constructor() {
    this.revenue = {
      ads: 0,
      iap: 0,
      premium: 0,
      total: 0,
    };
  }

  trackAdRevenue(amount) {
    this.revenue.ads += amount;
    this.revenue.total += amount;
    this.sendToAnalytics('ad_revenue', amount);
  }

  trackPurchase(productId, amount) {
    this.revenue.iap += amount;
    this.revenue.total += amount;
    this.sendToAnalytics('purchase', { productId, amount });
  }

  trackPremiumUpgrade(amount) {
    this.revenue.premium += amount;
    this.revenue.total += amount;
    this.sendToAnalytics('premium_upgrade', amount);
  }

  sendToAnalytics(event, data) {
    if (window.gtag) {
      gtag('event', event, {
        value: data.amount || data,
        currency: 'USD',
      });
    }
  }

  getARPU() {
    // Average Revenue Per User
    const totalUsers = this.getTotalUsers();
    return this.revenue.total / totalUsers;
  }

  getConversionRate() {
    const totalUsers = this.getTotalUsers();
    const payingUsers = this.getPayingUsers();
    return (payingUsers / totalUsers) * 100;
  }
}
```

## Legal Considerations

### Privacy Policy (Required)

**Minimum requirements**:
```markdown
# Privacy Policy

## Data Collection
We collect:
- Gameplay statistics (scores, levels completed)
- Device information (screen size, OS)
- Ad interaction data

## Data Usage
Data is used to:
- Improve game experience
- Show relevant ads
- Track revenue
- Fix bugs

## Third-Party Services
We use:
- Google AdSense for advertisements
- Google Analytics for usage tracking

## User Rights
You can:
- Request data deletion
- Opt out of analytics
- Contact us: privacy@yourgame.com
```

### GDPR Compliance

```javascript
// CookieConsent.js
export class CookieConsent {
  constructor() {
    this.hasConsent = localStorage.getItem('cookie_consent') === 'true';
  }

  async requestConsent() {
    if (this.hasConsent) return true;

    return new Promise((resolve) => {
      const banner = createConsentBanner();

      banner.onAccept = () => {
        localStorage.setItem('cookie_consent', 'true');
        this.hasConsent = true;
        this.enableTracking();
        resolve(true);
      };

      banner.onDecline = () => {
        this.hasConsent = false;
        this.disableTracking();
        resolve(false);
      };
    });
  }

  enableTracking() {
    // Enable analytics
    window.gtag('consent', 'update', {
      'analytics_storage': 'granted',
      'ad_storage': 'granted',
    });
  }

  disableTracking() {
    // Disable analytics
    window.gtag('consent', 'update', {
      'analytics_storage': 'denied',
      'ad_storage': 'denied',
    });
  }
}
```

## Claude Code Prompts

**Generate monetization system**:
```
Create a complete monetization system for this game that includes:
- Ad integration (Google AdSense)
- In-app purchases (3 products)
- Premium upgrade option
- Ethical design (no pay-to-win)
- Revenue tracking
- GDPR-compliant consent system

Game type: [type]
Target platform: [web/mobile/desktop]
```

**Optimize revenue**:
```
Analyze this game's monetization and suggest improvements:
[describe current monetization]

Provide:
- A/B test ideas
- Pricing optimization
- Better conversion funnels
- Ethical monetization improvements
- Revenue projection models
```

## Best Practices Summary

1. **Respect players** - Never exploit addictive mechanics
2. **Provide value** - Premium features should be worth the price
3. **Be transparent** - Clear pricing, no hidden costs
4. **Give choices** - Ads vs. payment vs. waiting
5. **Track metrics** - Know what works
6. **Iterate based on data** - A/B test pricing and placement
7. **Stay legal** - Privacy policies, GDPR compliance, age ratings

## Next Steps

Understanding monetization is crucial, but tracking player behavior is equally important. Continue to [Analytics & Telemetry](./analytics-telemetry.md) to learn how to understand your players and optimize your game.

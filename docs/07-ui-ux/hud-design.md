# HUD Design

## Overview

Heads-Up Displays (HUDs) provide real-time game information without interrupting gameplay. This guide covers health bars, minimaps, resource displays, damage numbers, and performance-optimized implementations.

## Health Bar Implementation

```javascript
class HealthBar {
  constructor(container, maxHealth = 100) {
    this.container = container;
    this.maxHealth = maxHealth;
    this.currentHealth = maxHealth;
    this.createElements();
  }

  createElements() {
    this.barContainer = document.createElement('div');
    this.barContainer.className = 'health-bar-container';
    
    this.barBackground = document.createElement('div');
    this.barBackground.className = 'health-bar-background';
    
    this.barFill = document.createElement('div');
    this.barFill.className = 'health-bar-fill';
    this.barFill.style.width = '100%';
    
    this.barBackground.appendChild(this.barFill);
    this.barContainer.appendChild(this.barBackground);
    this.container.appendChild(this.barContainer);
  }

  setHealth(newHealth, animated = true) {
    this.currentHealth = Math.max(0, Math.min(newHealth, this.maxHealth));
    const percentage = (this.currentHealth / this.maxHealth) * 100;
    
    if (animated) {
      this.barFill.style.transition = 'width 0.3s ease, background-color 0.3s ease';
    } else {
      this.barFill.style.transition = 'none';
    }
    
    this.barFill.style.width = percentage + '%';
    
    // Color based on health
    if (percentage > 60) {
      this.barFill.style.backgroundColor = '#4caf50';
    } else if (percentage > 30) {
      this.barFill.style.backgroundColor = '#ff9800';
    } else {
      this.barFill.style.backgroundColor = '#f44336';
    }
  }

  damage(amount) {
    this.setHealth(this.currentHealth - amount, true);
  }

  heal(amount) {
    this.setHealth(this.currentHealth + amount, true);
  }
}

// CSS
const styles = `
.health-bar-container {
  position: fixed;
  top: 20px;
  left: 20px;
  width: 200px;
}

.health-bar-background {
  width: 100%;
  height: 20px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.health-bar-fill {
  height: 100%;
  background: #4caf50;
  border-radius: 8px;
  transition: width 0.3s ease, background-color 0.3s ease;
}
`;
```

**Claude Code Prompt:**
```
Create a smooth health bar with animated transitions, color changes based on
health percentage, and damage/heal methods with visual feedback.
```

## Minimap System

```javascript
class Minimap {
  constructor(canvas, worldWidth, worldHeight) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.worldWidth = worldWidth;
    this.worldHeight = worldHeight;
    this.scale = canvas.width / worldWidth;
  }

  update(player, entities) {
    this.clear();
    this.drawBorder();
    this.drawEntities(entities);
    this.drawPlayer(player);
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawBorder() {
    this.ctx.strokeStyle = '#ffffff';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawPlayer(player) {
    const x = player.x * this.scale;
    const y = player.y * this.scale;
    
    this.ctx.fillStyle = '#00ff00';
    this.ctx.beginPath();
    this.ctx.arc(x, y, 3, 0, Math.PI * 2);
    this.ctx.fill();
  }

  drawEntities(entities) {
    for (const entity of entities) {
      const x = entity.x * this.scale;
      const y = entity.y * this.scale;
      
      this.ctx.fillStyle = entity.type === 'enemy' ? '#ff0000' : '#ffff00';
      this.ctx.beginPath();
      this.ctx.arc(x, y, 2, 0, Math.PI * 2);
      this.ctx.fill();
    }
  }
}
```

## Damage Numbers

```javascript
class DamageNumber {
  constructor(x, y, value, type = 'damage') {
    this.x = x;
    this.y = y;
    this.value = value;
    this.type = type;
    this.lifetime = 1000;
    this.startTime = Date.now();
    this.element = this.create();
  }

  create() {
    const el = document.createElement('div');
    el.className = `damage-number ${this.type}`;
    el.textContent = this.value;
    el.style.left = this.x + 'px';
    el.style.top = this.y + 'px';
    document.getElementById('hud-container').appendChild(el);
    return el;
  }

  update() {
    const elapsed = Date.now() - this.startTime;
    const progress = elapsed / this.lifetime;
    
    if (progress >= 1) {
      this.remove();
      return false;
    }
    
    // Float upward
    this.y -= 0.5;
    this.element.style.top = this.y + 'px';
    
    // Fade out
    this.element.style.opacity = 1 - progress;
    
    return true;
  }

  remove() {
    this.element.remove();
  }
}

// CSS
const damageStyles = `
.damage-number {
  position: fixed;
  font-size: 24px;
  font-weight: bold;
  pointer-events: none;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
  animation: float-up 1s ease-out forwards;
}

.damage-number.damage {
  color: #ff4444;
}

.damage-number.heal {
  color: #44ff44;
}

.damage-number.critical {
  color: #ffaa00;
  font-size: 32px;
}

@keyframes float-up {
  0% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(-50px) scale(1.2);
    opacity: 0;
  }
}
`;
```

**Claude Code Prompt:**
```
Create floating damage numbers that appear at hit location, animate upward
with fade out, support different types (damage, heal, critical), and clean
up automatically after animation.
```

## Best Practices

1. **Minimize clutter** - Only show essential information
2. **Consistent positioning** - Same info always in same place
3. **Readable text** - High contrast, appropriate size
4. **Performance** - Canvas for dynamic, DOM for static
5. **Responsive design** - Scale with screen size
6. **Color coding** - Red for danger, green for good
7. **Animations** - Smooth but not distracting
8. **Transparency** - Semi-transparent to not block view
9. **Toggle-able** - Let players hide/customize HUD
10. **Mobile optimization** - Larger elements for touch


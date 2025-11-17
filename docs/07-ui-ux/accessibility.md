# Accessibility

## Overview

Accessibility ensures everyone can play your game regardless of abilities. This guide covers keyboard navigation, screen reader support, colorblind modes, customizable controls, and WCAG compliance for inclusive game design.

## Keyboard Navigation

```javascript
class KeyboardNavigationManager {
  constructor() {
    this.focusableElements = [];
    this.currentFocusIndex = 0;
    this.enabled = true;
    this.setupGlobalListeners();
  }

  setupGlobalListeners() {
    document.addEventListener('keydown', (e) => {
      if (!this.enabled) return;

      switch(e.key) {
        case 'Tab':
          e.preventDefault();
          e.shiftKey ? this.focusPrevious() : this.focusNext();
          break;
        case 'Enter':
        case ' ':
          this.activateFocused(e);
          break;
        case 'Escape':
          this.handleEscape();
          break;
        case 'ArrowUp':
        case 'ArrowDown':
        case 'ArrowLeft':
        case 'ArrowRight':
          this.handleArrowKeys(e);
          break;
      }
    });
  }

  registerFocusableElements(container) {
    this.focusableElements = Array.from(
      container.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    );
  }

  focusNext() {
    this.currentFocusIndex = (this.currentFocusIndex + 1) % this.focusableElements.length;
    this.focusCurrent();
  }

  focusPrevious() {
    this.currentFocusIndex = (this.currentFocusIndex - 1 + this.focusableElements.length) 
      % this.focusableElements.length;
    this.focusCurrent();
  }

  focusCurrent() {
    const element = this.focusableElements[this.currentFocusIndex];
    if (element) {
      element.focus();
      element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  activateFocused(e) {
    const focused = document.activeElement;
    if (focused) {
      e.preventDefault();
      focused.click();
    }
  }

  handleEscape() {
    // Close modals, menus, etc.
    document.dispatchEvent(new CustomEvent('escape-pressed'));
  }

  handleArrowKeys(e) {
    const focused = document.activeElement;
    if (!focused) return;

    // Check if in a list or grid
    if (focused.closest('[role="menu"]') || focused.closest('[role="grid"]')) {
      e.preventDefault();
      this.navigateList(e.key);
    }
  }

  navigateList(key) {
    const directions = {
      'ArrowUp': -1,
      'ArrowDown': 1,
      'ArrowLeft': -1,
      'ArrowRight': 1
    };

    const direction = directions[key];
    if (direction) {
      if (key === 'ArrowUp' || key === 'ArrowDown') {
        direction > 0 ? this.focusNext() : this.focusPrevious();
      }
    }
  }
}

// Usage
const keyboardNav = new KeyboardNavigationManager();

// When showing a menu
function showMenu(menuElement) {
  menuElement.style.display = 'block';
  keyboardNav.registerFocusableElements(menuElement);
  keyboardNav.focusCurrent();
}
```

**Claude Code Prompt:**
```
Create a keyboard navigation system with Tab cycling, Enter/Space activation,
Escape key handling, arrow key support for menus/grids, and automatic focus
management with visual indicators.
```

## Screen Reader Support

```javascript
class ScreenReaderAnnouncer {
  constructor() {
    this.liveRegion = this.createLiveRegion();
  }

  createLiveRegion() {
    const region = document.createElement('div');
    region.setAttribute('role', 'status');
    region.setAttribute('aria-live', 'polite');
    region.setAttribute('aria-atomic', 'true');
    region.className = 'sr-only';
    document.body.appendChild(region);
    return region;
  }

  announce(message, priority = 'polite') {
    this.liveRegion.setAttribute('aria-live', priority);
    this.liveRegion.textContent = '';

    // Trigger announcement
    setTimeout(() => {
      this.liveRegion.textContent = message;
    }, 100);
  }

  announceGameState(state) {
    const messages = {
      health: `Health: ${state.health} of ${state.maxHealth}`,
      score: `Score: ${state.score}`,
      level: `Level ${state.level}`,
      enemiesRemaining: `${state.enemies} enemies remaining`
    };

    const announcement = Object.values(messages).join('. ');
    this.announce(announcement);
  }
}

// Add semantic HTML and ARIA labels
function createAccessibleButton(text, onClick, description) {
  const button = document.createElement('button');
  button.textContent = text;
  button.setAttribute('aria-label', description || text);
  button.onclick = onClick;
  return button;
}

function createAccessibleHealthBar(current, max) {
  const container = document.createElement('div');
  container.setAttribute('role', 'progressbar');
  container.setAttribute('aria-valuenow', current);
  container.setAttribute('aria-valuemin', '0');
  container.setAttribute('aria-valuemax', max);
  container.setAttribute('aria-label', `Health: ${current} of ${max}`);

  const bar = document.createElement('div');
  bar.className = 'health-bar';
  bar.style.width = `${(current / max) * 100}%`;

  container.appendChild(bar);
  return container;
}

// CSS for screen reader only content
const srOnlyStyles = `
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
`;
```

**Claude Code Prompt:**
```
Create screen reader support with ARIA live regions, semantic HTML, proper
labels, focus management, and announcements for game state changes. Follow
WCAG 2.1 guidelines.
```

## Colorblind Modes

```javascript
class ColorblindMode {
  constructor() {
    this.modes = {
      normal: {},
      protanopia: { // Red-blind
        '#ff0000': '#1a5490',
        '#00ff00': '#3d9140',
        '#ff6600': '#cc7722'
      },
      deuteranopia: { // Green-blind
        '#ff0000': '#d4aa00',
        '#00ff00': '#1a5490',
        '#ff6600': '#cc7722'
      },
      tritanopia: { // Blue-blind
        '#0000ff': '#00ffff',
        '#ff00ff': '#ff0000',
        '#6600ff': '#ff00aa'
      }
    };

    this.currentMode = 'normal';
  }

  setMode(mode) {
    if (!this.modes[mode]) return;

    this.currentMode = mode;
    this.applyColorAdjustments();
  }

  applyColorAdjustments() {
    const root = document.documentElement;
    const adjustments = this.modes[this.currentMode];

    // Apply CSS custom properties
    for (const [original, adjusted] of Object.entries(adjustments)) {
      const propName = `--color-${original.replace('#', '')}`;
      root.style.setProperty(propName, adjusted);
    }

    // Update game colors
    document.dispatchEvent(new CustomEvent('colorblind-mode-changed', {
      detail: { mode: this.currentMode, colors: adjustments }
    }));
  }

  // Alternative: Use filters
  applyFilterMode(mode) {
    const filters = {
      protanopia: 'url(#protanopia-filter)',
      deuteranopia: 'url(#deuteranopia-filter)',
      tritanopia: 'url(#tritanopia-filter)'
    };

    const canvas = document.getElementById('game-canvas');
    if (mode === 'normal') {
      canvas.style.filter = 'none';
    } else {
      canvas.style.filter = filters[mode];
    }
  }

  // Create SVG filters
  createSVGFilters() {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.style.display = 'none';
    svg.innerHTML = `
      <defs>
        <filter id="protanopia-filter">
          <feColorMatrix type="matrix" values="
            0.567, 0.433, 0, 0, 0
            0.558, 0.442, 0, 0, 0
            0, 0.242, 0.758, 0, 0
            0, 0, 0, 1, 0"/>
        </filter>
        <filter id="deuteranopia-filter">
          <feColorMatrix type="matrix" values="
            0.625, 0.375, 0, 0, 0
            0.7, 0.3, 0, 0, 0
            0, 0.3, 0.7, 0, 0
            0, 0, 0, 1, 0"/>
        </filter>
        <filter id="tritanopia-filter">
          <feColorMatrix type="matrix" values="
            0.95, 0.05, 0, 0, 0
            0, 0.433, 0.567, 0, 0
            0, 0.475, 0.525, 0, 0
            0, 0, 0, 1, 0"/>
        </filter>
      </defs>
    `;
    document.body.appendChild(svg);
  }
}

// Usage
const colorblindMode = new ColorblindMode();
colorblindMode.createSVGFilters();

// Settings menu
document.getElementById('colorblind-select').onchange = (e) => {
  colorblindMode.setMode(e.target.value);
};
```

**Claude Code Prompt:**
```
Create colorblind mode support with filters for protanopia, deuteranopia, and
tritanopia. Include both CSS filter approach and color palette adjustments.
Allow players to choose their preferred mode.
```

## Customizable Controls

```javascript
class ControlsCustomization {
  constructor() {
    this.bindings = this.getDefaultBindings();
    this.loadSavedBindings();
  }

  getDefaultBindings() {
    return {
      moveUp: ['w', 'ArrowUp'],
      moveDown: ['s', 'ArrowDown'],
      moveLeft: ['a', 'ArrowLeft'],
      moveRight: ['d', 'ArrowRight'],
      jump: [' ', 'z'],
      attack: ['x', 'Enter'],
      pause: ['Escape', 'p']
    };
  }

  rebind(action, newKey) {
    // Check if key is already bound
    for (const [boundAction, keys] of Object.entries(this.bindings)) {
      if (keys.includes(newKey) && boundAction !== action) {
        return { success: false, error: `Key already bound to ${boundAction}` };
      }
    }

    // Update binding
    this.bindings[action] = [newKey];
    this.saveBindings();

    return { success: true };
  }

  isActionPressed(action, event) {
    const keys = this.bindings[action];
    return keys && keys.includes(event.key);
  }

  saveBindings() {
    localStorage.setItem('controls', JSON.stringify(this.bindings));
  }

  loadSavedBindings() {
    const saved = localStorage.getItem('controls');
    if (saved) {
      try {
        this.bindings = JSON.parse(saved);
      } catch (e) {
        console.error('Failed to load saved bindings:', e);
      }
    }
  }

  resetToDefaults() {
    this.bindings = this.getDefaultBindings();
    this.saveBindings();
  }

  createRebindUI() {
    const container = document.createElement('div');
    container.className = 'controls-customization';

    for (const [action, keys] of Object.entries(this.bindings)) {
      const row = document.createElement('div');
      row.className = 'control-row';
      row.innerHTML = `
        <span class="action-name">${this.formatActionName(action)}</span>
        <span class="current-keys">${keys.join(', ')}</span>
        <button class="rebind-btn" data-action="${action}">Change</button>
      `;

      row.querySelector('.rebind-btn').onclick = () => {
        this.startRebinding(action, row);
      };

      container.appendChild(row);
    }

    return container;
  }

  startRebinding(action, row) {
    const btn = row.querySelector('.rebind-btn');
    btn.textContent = 'Press any key...';
    btn.disabled = true;

    const listener = (e) => {
      e.preventDefault();
      const result = this.rebind(action, e.key);

      if (result.success) {
        row.querySelector('.current-keys').textContent = e.key;
        btn.textContent = 'Change';
      } else {
        alert(result.error);
        btn.textContent = 'Try again';
      }

      btn.disabled = false;
      document.removeEventListener('keydown', listener);
    };

    document.addEventListener('keydown', listener);
  }

  formatActionName(action) {
    return action.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase());
  }
}
```

**Claude Code Prompt:**
```
Create a control customization system that allows players to rebind keys,
prevents duplicate bindings, saves preferences to localStorage, and provides
an intuitive rebinding interface with visual feedback.
```

## Best Practices

1. **Keyboard navigation** - Full game playable without mouse
2. **Screen reader support** - ARIA labels, semantic HTML, announcements
3. **Visual alternatives** - Don't rely solely on color
4. **Customizable controls** - Let players rebind keys
5. **Text scaling** - Support browser zoom (100-200%)
6. **High contrast mode** - Alternative color schemes
7. **Reduced motion** - Option to disable animations
8. **Subtitles/captions** - For all audio content
9. **Pause anytime** - Accessible for all players
10. **Clear focus indicators** - Visible keyboard focus

## Testing Accessibility

1. **Keyboard only** - Try playing without mouse
2. **Screen reader** - Test with NVDA or VoiceOver
3. **Colorblind simulator** - Use browser extensions
4. **High contrast mode** - Enable OS high contrast
5. **Zoom testing** - Test at 200% zoom
6. **Reduced motion** - Disable animations
7. **Real users** - Get feedback from disabled players


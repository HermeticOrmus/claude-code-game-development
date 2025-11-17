# Menu Systems

## Overview

Menu systems are the first UI players interact with and set expectations for your entire game. This guide covers menu architecture, navigation patterns, responsive design, state management, and complete working examples.

## Menu Architecture

```javascript
class MenuSystem {
  constructor() {
    this.currentMenu = null;
    this.menuStack = [];
    this.menus = new Map();
    this.transitioning = false;
  }

  registerMenu(name, config) {
    this.menus.set(name, {
      element: document.getElementById(config.elementId),
      onEnter: config.onEnter || (() => {}),
      onExit: config.onExit || (() => {}),
      canGoBack: config.canGoBack !== false
    });
  }

  async showMenu(name, options = {}) {
    if (this.transitioning) return;
    
    const menu = this.menus.get(name);
    if (!menu) return;

    this.transitioning = true;

    // Hide current menu
    if (this.currentMenu) {
      const current = this.menus.get(this.currentMenu);
      await this.hideMenu(current);
      current.onExit();
      
      if (!options.replace) {
        this.menuStack.push(this.currentMenu);
      }
    }

    // Show new menu
    await this.displayMenu(menu);
    menu.onEnter();
    this.currentMenu = name;
    this.transitioning = false;
  }

  async hideMenu(menu) {
    menu.element.classList.add('menu-exit');
    await this.wait(300);
    menu.element.style.display = 'none';
    menu.element.classList.remove('menu-exit');
  }

  async displayMenu(menu) {
    menu.element.style.display = 'flex';
    menu.element.classList.add('menu-enter');
    await this.wait(50);
    menu.element.classList.remove('menu-enter');
  }

  async goBack() {
    if (this.menuStack.length === 0) return;
    
    const previousMenu = this.menuStack.pop();
    await this.showMenu(previousMenu, { replace: true });
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Usage
const menuSystem = new MenuSystem();

menuSystem.registerMenu('main', {
  elementId: 'main-menu',
  onEnter: () => console.log('Main menu entered')
});

menuSystem.registerMenu('settings', {
  elementId: 'settings-menu',
  onEnter: () => console.log('Settings entered')
});

// Navigation
menuSystem.showMenu('main');
document.getElementById('settings-btn').onclick = () => menuSystem.showMenu('settings');
document.getElementById('back-btn').onclick = () => menuSystem.goBack();
```

**Claude Code Prompt:**
```
Create a menu system with navigation stack, smooth transitions between menus,
state management, and support for forward/back navigation with animations.
```

## Responsive Menu Design

```css
.menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.menu.active {
  opacity: 1;
}

.menu-container {
  width: 90%;
  max-width: 600px;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.menu-button {
  width: 100%;
  padding: 1rem 2rem;
  margin: 0.5rem 0;
  font-size: 1.2rem;
  background: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.menu-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.menu-button:active {
  transform: translateY(0);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .menu-container {
    width: 95%;
    padding: 1.5rem;
  }

  .menu-button {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
  }
}
```

## Accessibility

```javascript
class AccessibleMenu {
  constructor(menuElement) {
    this.menu = menuElement;
    this.focusableElements = [];
    this.currentFocusIndex = 0;
    this.setupKeyboardNav();
  }

  setupKeyboardNav() {
    this.focusableElements = Array.from(
      this.menu.querySelectorAll('button, a, input, [tabindex="0"]')
    );

    this.menu.addEventListener('keydown', (e) => {
      switch(e.key) {
        case 'ArrowDown':
        case 'ArrowRight':
          e.preventDefault();
          this.focusNext();
          break;
        case 'ArrowUp':
        case 'ArrowLeft':
          e.preventDefault();
          this.focusPrevious();
          break;
        case 'Home':
          e.preventDefault();
          this.focusFirst();
          break;
        case 'End':
          e.preventDefault();
          this.focusLast();
          break;
      }
    });
  }

  focusNext() {
    this.currentFocusIndex = (this.currentFocusIndex + 1) % this.focusableElements.length;
    this.focusableElements[this.currentFocusIndex].focus();
  }

  focusPrevious() {
    this.currentFocusIndex = (this.currentFocusIndex - 1 + this.focusableElements.length) % this.focusableElements.length;
    this.focusableElements[this.currentFocusIndex].focus();
  }

  focusFirst() {
    this.currentFocusIndex = 0;
    this.focusableElements[0].focus();
  }

  focusLast() {
    this.currentFocusIndex = this.focusableElements.length - 1;
    this.focusableElements[this.currentFocusIndex].focus();
  }
}
```

**Claude Code Prompt:**
```
Create an accessible menu system with full keyboard navigation (arrow keys,
Home/End), focus management, screen reader support with ARIA labels, and
responsive design for desktop and mobile.
```

## Best Practices

1. **Clear visual hierarchy** - Most important actions should be prominent
2. **Keyboard navigation** - Support arrow keys and Enter/Escape
3. **Touch-friendly sizes** - Minimum 44x44px touch targets
4. **Loading states** - Show progress for async operations
5. **Error handling** - Clear error messages with recovery options
6. **Animations** - Smooth but not slow (200-300ms)
7. **Mobile-first** - Design for touch, enhance for mouse
8. **Persistent state** - Remember settings and selections
9. **Escape key** - Always close/go back
10. **Focus indication** - Clear visual focus for keyboard users


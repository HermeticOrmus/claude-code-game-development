# Inventory Systems

## Overview

Inventory systems manage player items, equipment, and resources. This guide covers grid-based and list-based inventories, drag-and-drop functionality, item stacking, and complete implementations.

## Grid-Based Inventory

```javascript
class GridInventory {
  constructor(rows, cols, container) {
    this.rows = rows;
    this.cols = cols;
    this.container = container;
    this.grid = Array(rows).fill(null).map(() => Array(cols).fill(null));
    this.draggedItem = null;
    this.createUI();
  }

  createUI() {
    this.container.innerHTML = '';
    this.container.className = 'inventory-grid';
    this.container.style.gridTemplateColumns = `repeat(${this.cols}, 60px)`;

    for (let row = 0; row < this.rows; row++) {
      for (let col = 0; col < this.cols; col++) {
        const cell = document.createElement('div');
        cell.className = 'inventory-cell';
        cell.dataset.row = row;
        cell.dataset.col = col;
        
        cell.addEventListener('dragover', this.onDragOver.bind(this));
        cell.addEventListener('drop', this.onDrop.bind(this));
        
        this.container.appendChild(cell);
      }
    }
  }

  addItem(item, row, col) {
    if (!this.canPlaceItem(row, col)) {
      return false;
    }

    this.grid[row][col] = item;
    this.renderItem(item, row, col);
    return true;
  }

  canPlaceItem(row, col) {
    return this.grid[row] && this.grid[row][col] === null;
  }

  renderItem(item, row, col) {
    const cellIndex = row * this.cols + col;
    const cell = this.container.children[cellIndex];

    const itemElement = document.createElement('div');
    itemElement.className = 'inventory-item';
    itemElement.draggable = true;
    itemElement.innerHTML = `
      <img src="${item.icon}" alt="${item.name}">
      ${item.quantity > 1 ? `<span class="item-quantity">${item.quantity}</span>` : ''}
    `;
    
    itemElement.addEventListener('dragstart', (e) => {
      this.draggedItem = { item, row, col };
      itemElement.classList.add('dragging');
    });
    
    itemElement.addEventListener('dragend', () => {
      itemElement.classList.remove('dragging');
    });
    
    cell.appendChild(itemElement);
  }

  onDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
  }

  onDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    if (!this.draggedItem) return;

    const targetRow = parseInt(e.currentTarget.dataset.row);
    const targetCol = parseInt(e.currentTarget.dataset.col);
    
    // Remove from old position
    this.removeItem(this.draggedItem.row, this.draggedItem.col);
    
    // Add to new position
    this.addItem(this.draggedItem.item, targetRow, targetCol);
    
    this.draggedItem = null;
  }

  removeItem(row, col) {
    this.grid[row][col] = null;
    const cellIndex = row * this.cols + col;
    const cell = this.container.children[cellIndex];
    cell.innerHTML = '';
  }

  findItem(itemId) {
    for (let row = 0; row < this.rows; row++) {
      for (let col = 0; col < this.cols; col++) {
        const item = this.grid[row][col];
        if (item && item.id === itemId) {
          return { item, row, col };
        }
      }
    }
    return null;
  }

  stackItem(item) {
    // Try to stack with existing items
    for (let row = 0; row < this.rows; row++) {
      for (let col = 0; col < this.cols; col++) {
        const existingItem = this.grid[row][col];
        if (existingItem && existingItem.id === item.id && existingItem.stackable) {
          existingItem.quantity += item.quantity;
          this.renderItem(existingItem, row, col);
          return true;
        }
      }
    }
    
    // Find empty slot
    for (let row = 0; row < this.rows; row++) {
      for (let col = 0; col < this.cols; col++) {
        if (this.grid[row][col] === null) {
          return this.addItem(item, row, col);
        }
      }
    }
    
    return false; // Inventory full
  }
}

// CSS
const inventoryStyles = `
.inventory-grid {
  display: grid;
  gap: 4px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.8);
  border: 2px solid #555;
  border-radius: 8px;
}

.inventory-cell {
  width: 60px;
  height: 60px;
  background: rgba(50, 50, 50, 0.9);
  border: 2px solid #333;
  border-radius: 4px;
  position: relative;
  transition: background 0.2s;
}

.inventory-cell.drag-over {
  background: rgba(100, 150, 255, 0.3);
  border-color: #6096ff;
}

.inventory-item {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  position: relative;
}

.inventory-item.dragging {
  opacity: 0.5;
}

.inventory-item img {
  max-width: 80%;
  max-height: 80%;
}

.item-quantity {
  position: absolute;
  bottom: 2px;
  right: 4px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 12px;
  font-weight: bold;
  padding: 2px 4px;
  border-radius: 3px;
}
`;

// Usage
const inventory = new GridInventory(4, 6, document.getElementById('inventory'));

// Add items
inventory.stackItem({
  id: 'potion',
  name: 'Health Potion',
  icon: '/items/potion.png',
  quantity: 5,
  stackable: true
});

inventory.addItem({
  id: 'sword',
  name: 'Iron Sword',
  icon: '/items/sword.png',
  quantity: 1,
  stackable: false
}, 0, 0);
```

**Claude Code Prompt:**
```
Create a grid-based inventory system with drag-and-drop item movement, item
stacking for stackable items, visual feedback for dragging, and automatic
inventory management.
```

## List-Based Inventory

```javascript
class ListInventory {
  constructor(container, capacity = 20) {
    this.container = container;
    this.capacity = capacity;
    this.items = [];
    this.render();
  }

  addItem(item) {
    // Check if stackable
    const existing = this.items.find(i => i.id === item.id && i.stackable);
    if (existing) {
      existing.quantity += item.quantity;
      this.render();
      return true;
    }

    // Add new item
    if (this.items.length < this.capacity) {
      this.items.push(item);
      this.render();
      return true;
    }

    return false; // Inventory full
  }

  removeItem(itemId, quantity = 1) {
    const index = this.items.findIndex(i => i.id === itemId);
    if (index === -1) return false;

    const item = this.items[index];
    item.quantity -= quantity;

    if (item.quantity <= 0) {
      this.items.splice(index, 1);
    }

    this.render();
    return true;
  }

  render() {
    this.container.innerHTML = '';

    for (const item of this.items) {
      const itemElement = document.createElement('div');
      itemElement.className = 'inventory-list-item';
      itemElement.innerHTML = `
        <img src="${item.icon}" alt="${item.name}">
        <div class="item-info">
          <div class="item-name">${item.name}</div>
          <div class="item-description">${item.description || ''}</div>
        </div>
        <div class="item-quantity">${item.quantity}</div>
        <button class="item-use-btn" data-id="${item.id}">Use</button>
      `;

      itemElement.querySelector('.item-use-btn').onclick = () => {
        this.useItem(item);
      };

      this.container.appendChild(itemElement);
    }

    // Show empty slots
    const emptySlots = this.capacity - this.items.length;
    for (let i = 0; i < emptySlots; i++) {
      const emptyElement = document.createElement('div');
      emptyElement.className = 'inventory-list-item empty';
      emptyElement.innerHTML = '<div class="empty-slot">Empty</div>';
      this.container.appendChild(emptyElement);
    }
  }

  useItem(item) {
    if (item.onUse) {
      item.onUse();
      this.removeItem(item.id, 1);
    }
  }

  sortBy(criteria = 'name') {
    this.items.sort((a, b) => {
      if (criteria === 'name') {
        return a.name.localeCompare(b.name);
      } else if (criteria === 'quantity') {
        return b.quantity - a.quantity;
      } else if (criteria === 'type') {
        return a.type.localeCompare(b.type);
      }
      return 0;
    });

    this.render();
  }
}
```

**Claude Code Prompt:**
```
Create a list-based inventory system with item stacking, use button, sorting
options, and visual representation of empty slots. Include item descriptions
and quantity display.
```

## Best Practices

1. **Clear visual feedback** - Highlight drop zones, show dragging state
2. **Item stacking** - Combine similar items automatically
3. **Sort and filter** - Help players find items
4. **Item tooltips** - Show details on hover
5. **Quick actions** - Right-click or long-press for menus
6. **Keyboard shortcuts** - Quick access to inventory
7. **Capacity indication** - Show available space
8. **Undo actions** - Let players recover mistakes
9. **Mobile optimization** - Large touch targets, swipe gestures
10. **Persistence** - Save inventory state


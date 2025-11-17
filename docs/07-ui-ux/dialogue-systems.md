# Dialogue Systems

## Overview

Dialogue systems enable narrative experiences through branching conversations. This guide covers dialogue trees, typewriter effects, choice systems, and voice integration for interactive storytelling.

## Dialogue Tree Implementation

```javascript
class DialogueSystem {
  constructor(container) {
    this.container = container;
    this.dialogueTree = {};
    this.currentNode = null;
    this.onChoice = null;
  }

  loadDialogue(tree) {
    this.dialogueTree = tree;
  }

  async showNode(nodeId) {
    const node = this.dialogueTree[nodeId];
    if (!node) return;

    this.currentNode = nodeId;
    
    // Clear previous
    this.container.innerHTML = '';
    
    // Show speaker
    if (node.speaker) {
      const speaker = document.createElement('div');
      speaker.className = 'dialogue-speaker';
      speaker.textContent = node.speaker;
      this.container.appendChild(speaker);
    }
    
    // Show text with typewriter effect
    const textContainer = document.createElement('div');
    textContainer.className = 'dialogue-text';
    this.container.appendChild(textContainer);
    
    await this.typewriterEffect(textContainer, node.text);
    
    // Show choices
    if (node.choices) {
      const choicesContainer = document.createElement('div');
      choicesContainer.className = 'dialogue-choices';
      
      for (const choice of node.choices) {
        const button = document.createElement('button');
        button.className = 'dialogue-choice-button';
        button.textContent = choice.text;
        button.onclick = () => this.selectChoice(choice);
        choicesContainer.appendChild(button);
      }
      
      this.container.appendChild(choicesContainer);
    }
  }

  async typewriterEffect(element, text, speed = 30) {
    element.textContent = '';
    
    for (let i = 0; i < text.length; i++) {
      element.textContent += text[i];
      await this.wait(speed);
    }
  }

  selectChoice(choice) {
    if (choice.action) {
      choice.action();
    }
    
    if (choice.next) {
      this.showNode(choice.next);
    } else {
      this.endDialogue();
    }
  }

  endDialogue() {
    this.container.innerHTML = '';
    this.currentNode = null;
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Example dialogue tree
const sampleDialogue = {
  'start': {
    speaker: 'Old Wizard',
    text: 'Greetings, traveler. What brings you to my tower?',
    choices: [
      {
        text: 'I seek knowledge',
        next: 'knowledge'
      },
      {
        text: 'I seek power',
        next: 'power'
      },
      {
        text: 'I\'m just passing through',
        next: 'leaving'
      }
    ]
  },
  'knowledge': {
    speaker: 'Old Wizard',
    text: 'Ah, a student of the arcane arts. I can teach you, but first you must prove yourself worthy.',
    choices: [
      {
        text: 'I accept your challenge',
        action: () => console.log('Quest started!'),
        next: 'end'
      },
      {
        text: 'Perhaps another time',
        next: 'leaving'
      }
    ]
  },
  'power': {
    speaker: 'Old Wizard',
    text: 'Power without wisdom leads only to destruction. Return when you understand this.',
    choices: [
      {
        text: 'I understand',
        next: 'leaving'
      }
    ]
  },
  'leaving': {
    speaker: 'Old Wizard',
    text: 'Farewell, traveler. May your path be clear.',
    choices: []
  }
};

// Usage
const dialogue = new DialogueSystem(document.getElementById('dialogue-container'));
dialogue.loadDialogue(sampleDialogue);
dialogue.showNode('start');
```

**Claude Code Prompt:**
```
Create a branching dialogue system with typewriter text effects, multiple
choice options, speaker names, and support for triggering game actions from
dialogue choices.
```

## Dialogue Styling

```css
.dialogue-container {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 800px;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.95), rgba(20, 20, 40, 0.95));
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
}

.dialogue-speaker {
  font-size: 18px;
  font-weight: bold;
  color: #4CAF50;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.dialogue-text {
  font-size: 16px;
  line-height: 1.6;
  color: #ffffff;
  margin-bottom: 20px;
  min-height: 60px;
}

.dialogue-choices {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dialogue-choice-button {
  padding: 12px 20px;
  background: rgba(76, 175, 80, 0.2);
  border: 2px solid #4CAF50;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.dialogue-choice-button:hover {
  background: rgba(76, 175, 80, 0.4);
  transform: translateX(5px);
}
```

## Voice Integration

```javascript
class VoicedDialogue extends DialogueSystem {
  constructor(container) {
    super(container);
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    this.voiceClips = new Map();
  }

  async loadVoiceClip(nodeId, audioUrl) {
    const response = await fetch(audioUrl);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
    this.voiceClips.set(nodeId, audioBuffer);
  }

  async showNode(nodeId) {
    // Show dialogue
    await super.showNode(nodeId);
    
    // Play voice clip if available
    const voiceClip = this.voiceClips.get(nodeId);
    if (voiceClip) {
      this.playVoiceClip(voiceClip);
    }
  }

  playVoiceClip(audioBuffer) {
    const source = this.audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.audioContext.destination);
    source.start(0);
  }
}
```

**Claude Code Prompt:**
```
Extend dialogue system with voice acting support by loading and playing
audio clips synchronized with text display, including audio context
management and cleanup.
```

## Best Practices

1. **Skip-able text** - Let players skip typewriter effect
2. **Clear speaker identification** - Names, portraits, colors
3. **Readable text** - High contrast, appropriate size
4. **Auto-advance option** - For cutscenes
5. **Save dialogue state** - Resume conversations
6. **Localization support** - Separate text from code
7. **Variable substitution** - Player name, stats in dialogue
8. **Conditional branches** - Based on game state
9. **History/log** - Let players review past dialogue
10. **Accessibility** - Screen reader support for text


# Animation Systems

Animation brings life to games. From character walk cycles to particle effects, smooth and expressive animation is crucial for creating engaging experiences. This guide covers sprite sheet animation, frame-based systems, tweening, animation state machines, and procedural animation.

## Table of Contents

1. [Animation Fundamentals](#animation-fundamentals)
2. [Sprite Sheet Animation](#sprite-sheet-animation)
3. [Frame-Based Animation](#frame-based-animation)
4. [Time-Based Animation](#time-based-animation)
5. [Animation State Machines](#animation-state-machines)
6. [Skeletal Animation Basics](#skeletal-animation-basics)
7. [Procedural Animation](#procedural-animation)
8. [Tweening and Easing Functions](#tweening-and-easing-functions)
9. [Integration with Game Loops](#integration-with-game-loops)
10. [Performance Optimization](#performance-optimization)

## Animation Fundamentals

### Core Concepts

Animation in games is typically achieved through one of these methods:

1. **Sprite Animation**: Displaying a sequence of pre-drawn images
2. **Skeletal Animation**: Moving interconnected bones with sprites attached
3. **Procedural Animation**: Calculating animation mathematically at runtime
4. **Particle Systems**: Spawning and animating many small objects
5. **Tweening**: Smoothly interpolating between values over time

### Frame Rate vs Update Rate

Games typically update at 60 FPS, but animations don't need to change every frame. A walk cycle might only have 8 frames played at 12 FPS, while the game updates at 60 FPS.

## Sprite Sheet Animation

Sprite sheets pack multiple animation frames into a single image for efficiency.

### Claude Code Prompt

```
Prompt: "Create a sprite sheet animation system that loads sprite sheets,
defines animations with frame sequences, supports different animation speeds,
handles looping and one-shot animations, and includes a debug view showing
frame boundaries and current frame number. Include a character with walk,
run, jump, and idle animations."
```

### Implementation

```javascript
class SpriteSheet {
    constructor(image, frameWidth, frameHeight) {
        this.image = image;
        this.frameWidth = frameWidth;
        this.frameHeight = frameHeight;

        // Calculate frames per row/column
        this.framesPerRow = Math.floor(image.width / frameWidth);
        this.framesPerColumn = Math.floor(image.height / frameHeight);
        this.totalFrames = this.framesPerRow * this.framesPerColumn;
    }

    // Get frame coordinates in sprite sheet
    getFrameCoords(frameIndex) {
        const row = Math.floor(frameIndex / this.framesPerRow);
        const col = frameIndex % this.framesPerRow;

        return {
            x: col * this.frameWidth,
            y: row * this.frameHeight,
            width: this.frameWidth,
            height: this.frameHeight
        };
    }

    // Draw specific frame
    drawFrame(ctx, frameIndex, x, y, scale = 1) {
        const coords = this.getFrameCoords(frameIndex);

        ctx.drawImage(
            this.image,
            coords.x,
            coords.y,
            coords.width,
            coords.height,
            x,
            y,
            coords.width * scale,
            coords.height * scale
        );
    }
}

class Animation {
    constructor(name, frames, frameRate = 12, loop = true) {
        this.name = name;
        this.frames = frames; // Array of frame indices
        this.frameRate = frameRate; // Frames per second
        this.loop = loop;

        // Timing
        this.frameDuration = 1 / frameRate; // Seconds per frame
        this.currentFrame = 0;
        this.timer = 0;
        this.finished = false;
    }

    update(dt) {
        if (this.finished && !this.loop) return;

        this.timer += dt;

        if (this.timer >= this.frameDuration) {
            this.timer -= this.frameDuration;
            this.currentFrame++;

            if (this.currentFrame >= this.frames.length) {
                if (this.loop) {
                    this.currentFrame = 0;
                } else {
                    this.currentFrame = this.frames.length - 1;
                    this.finished = true;
                }
            }
        }
    }

    getCurrentFrameIndex() {
        return this.frames[this.currentFrame];
    }

    reset() {
        this.currentFrame = 0;
        this.timer = 0;
        this.finished = false;
    }

    clone() {
        return new Animation(this.name, [...this.frames], this.frameRate, this.loop);
    }
}

class AnimatedSprite {
    constructor(spriteSheet, x, y) {
        this.spriteSheet = spriteSheet;
        this.x = x;
        this.y = y;
        this.scale = 2;
        this.flipX = false;

        // Animations
        this.animations = new Map();
        this.currentAnimation = null;

        // Debug
        this.debugEnabled = false;
    }

    addAnimation(animation) {
        this.animations.set(animation.name, animation);
    }

    playAnimation(name, reset = true) {
        if (this.currentAnimation && this.currentAnimation.name === name && !reset) {
            return; // Already playing this animation
        }

        const animation = this.animations.get(name);
        if (!animation) {
            console.error(`Animation '${name}' not found`);
            return;
        }

        this.currentAnimation = animation;
        if (reset) {
            this.currentAnimation.reset();
        }
    }

    update(dt) {
        if (this.currentAnimation) {
            this.currentAnimation.update(dt);
        }
    }

    render(ctx) {
        if (!this.currentAnimation) return;

        ctx.save();

        // Flip horizontally if needed
        if (this.flipX) {
            ctx.translate(this.x + this.spriteSheet.frameWidth * this.scale, this.y);
            ctx.scale(-1, 1);
            this.spriteSheet.drawFrame(
                ctx,
                this.currentAnimation.getCurrentFrameIndex(),
                0,
                0,
                this.scale
            );
        } else {
            this.spriteSheet.drawFrame(
                ctx,
                this.currentAnimation.getCurrentFrameIndex(),
                this.x,
                this.y,
                this.scale
            );
        }

        ctx.restore();

        // Debug visualization
        if (this.debugEnabled) {
            this.renderDebug(ctx);
        }
    }

    renderDebug(ctx) {
        const width = this.spriteSheet.frameWidth * this.scale;
        const height = this.spriteSheet.frameHeight * this.scale;

        // Frame boundary
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 2;
        ctx.strokeRect(this.x, this.y, width, height);

        // Animation info
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(this.x, this.y - 40, 200, 35);

        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.fillText(
            `Anim: ${this.currentAnimation.name}`,
            this.x + 5,
            this.y - 25
        );
        ctx.fillText(
            `Frame: ${this.currentAnimation.currentFrame}/${this.currentAnimation.frames.length}`,
            this.x + 5,
            this.y - 10
        );
    }
}

// Example Usage (would need actual sprite sheet image)
/*
const image = new Image();
image.onload = () => {
    const spriteSheet = new SpriteSheet(image, 32, 32);
    const player = new AnimatedSprite(spriteSheet, 100, 100);

    // Define animations (frame indices from sprite sheet)
    player.addAnimation(new Animation('idle', [0, 1, 2, 3], 8, true));
    player.addAnimation(new Animation('walk', [4, 5, 6, 7, 8, 9], 12, true));
    player.addAnimation(new Animation('run', [10, 11, 12, 13, 14, 15], 16, true));
    player.addAnimation(new Animation('jump', [16, 17, 18, 19], 15, false));
    player.addAnimation(new Animation('attack', [20, 21, 22, 23, 24], 20, false));

    player.playAnimation('idle');
    player.debugEnabled = true;

    function gameLoop(dt) {
        player.update(dt);
        player.render(ctx);
    }
};
image.src = 'player-spritesheet.png';
*/
```

## Frame-Based Animation

Frame-based animation advances animation frames based on game frames rather than time.

### Implementation

```javascript
class FrameBasedAnimation {
    constructor(frames, framesPerUpdate = 5) {
        this.frames = frames;
        this.framesPerUpdate = framesPerUpdate; // Advance animation every N game frames
        this.currentFrame = 0;
        this.frameCounter = 0;
    }

    update() {
        this.frameCounter++;

        if (this.frameCounter >= this.framesPerUpdate) {
            this.frameCounter = 0;
            this.currentFrame = (this.currentFrame + 1) % this.frames.length;
        }
    }

    getCurrentFrame() {
        return this.frames[this.currentFrame];
    }
}
```

**Note**: Frame-based animation is simpler but not frame-rate independent. Prefer time-based animation for consistent results across different frame rates.

## Time-Based Animation

Time-based animation uses delta time for frame-rate independence.

### Claude Code Prompt

```
Prompt: "Create a time-based animation system with support for animation
blending, animation events (callbacks at specific frames), and animation
curves for non-linear playback speed. Include visual timeline showing
animation progress and events."
```

### Implementation

```javascript
class TimeBasedAnimation {
    constructor(name, frames, duration, loop = true) {
        this.name = name;
        this.frames = frames;
        this.duration = duration; // Total animation duration in seconds
        this.loop = loop;

        this.time = 0;
        this.finished = false;

        // Animation events (callbacks at specific times)
        this.events = [];

        // Animation curve (for variable playback speed)
        this.curve = (t) => t; // Linear by default
    }

    // Add event at specific time
    addEvent(time, callback) {
        this.events.push({ time, callback, fired: false });
        this.events.sort((a, b) => a.time - b.time);
    }

    // Set animation curve (easing function)
    setCurve(curveFunction) {
        this.curve = curveFunction;
    }

    update(dt) {
        if (this.finished && !this.loop) return;

        const previousTime = this.time;
        this.time += dt;

        // Check for events
        for (const event of this.events) {
            if (!event.fired && previousTime < event.time && this.time >= event.time) {
                event.callback();
                event.fired = true;
            }
        }

        // Handle loop/finish
        if (this.time >= this.duration) {
            if (this.loop) {
                this.time = this.time % this.duration;
                // Reset events
                this.events.forEach(e => e.fired = false);
            } else {
                this.time = this.duration;
                this.finished = true;
            }
        }
    }

    getCurrentFrameIndex() {
        // Apply curve to time
        const normalizedTime = this.time / this.duration;
        const curvedTime = this.curve(normalizedTime);

        // Get frame index from curved time
        const frameIndex = Math.floor(curvedTime * this.frames.length);
        return this.frames[Math.min(frameIndex, this.frames.length - 1)];
    }

    getProgress() {
        return this.time / this.duration;
    }

    reset() {
        this.time = 0;
        this.finished = false;
        this.events.forEach(e => e.fired = false);
    }
}
```

## Animation State Machines

Animation state machines manage transitions between animations based on game state.

### Claude Code Prompt

```
Prompt: "Create an animation state machine for a platformer character. Include
states for idle, walk, run, jump, fall, land, and attack. Define transition
conditions between states and animation blending for smooth transitions.
Add visualization showing current state and available transitions."
```

### Implementation

```javascript
class AnimationState {
    constructor(name, animation) {
        this.name = name;
        this.animation = animation;
        this.transitions = new Map(); // Map of condition -> target state name
    }

    addTransition(targetStateName, conditionFn) {
        if (!this.transitions.has(targetStateName)) {
            this.transitions.set(targetStateName, []);
        }
        this.transitions.get(targetStateName).push(conditionFn);
    }

    checkTransitions(context) {
        for (const [targetState, conditions] of this.transitions) {
            for (const condition of conditions) {
                if (condition(context)) {
                    return targetState;
                }
            }
        }
        return null;
    }
}

class AnimationStateMachine {
    constructor(spriteSheet) {
        this.spriteSheet = spriteSheet;
        this.states = new Map();
        this.currentState = null;
        this.previousState = null;

        // Blend settings
        this.blendDuration = 0.1; // seconds
        this.blendTimer = 0;
        this.blending = false;
    }

    addState(state) {
        this.states.set(state.name, state);
    }

    setState(stateName, force = false) {
        const newState = this.states.get(stateName);
        if (!newState) {
            console.error(`State '${stateName}' not found`);
            return;
        }

        if (this.currentState === newState && !force) {
            return; // Already in this state
        }

        this.previousState = this.currentState;
        this.currentState = newState;
        this.currentState.animation.reset();

        // Start blend
        if (this.previousState && !force) {
            this.blending = true;
            this.blendTimer = 0;
        }
    }

    update(dt, context) {
        if (!this.currentState) return;

        // Update blend
        if (this.blending) {
            this.blendTimer += dt;
            if (this.blendTimer >= this.blendDuration) {
                this.blending = false;
            }
        }

        // Check for state transitions
        const targetState = this.currentState.checkTransitions(context);
        if (targetState) {
            this.setState(targetState);
        }

        // Update current animation
        this.currentState.animation.update(dt);
    }

    render(ctx, x, y, scale = 1, flipX = false) {
        if (!this.currentState) return;

        // During blend, could render both animations with alpha
        const alpha = this.blending ? this.blendTimer / this.blendDuration : 1;

        ctx.save();
        ctx.globalAlpha = alpha;

        if (flipX) {
            ctx.translate(x + this.spriteSheet.frameWidth * scale, y);
            ctx.scale(-1, 1);
            this.spriteSheet.drawFrame(
                ctx,
                this.currentState.animation.getCurrentFrameIndex(),
                0,
                0,
                scale
            );
        } else {
            this.spriteSheet.drawFrame(
                ctx,
                this.currentState.animation.getCurrentFrameIndex(),
                x,
                y,
                scale
            );
        }

        ctx.restore();
    }

    renderDebug(ctx, x, y) {
        if (!this.currentState) return;

        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(x, y, 250, 100);

        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText(`Current: ${this.currentState.name}`, x + 10, y + 20);

        if (this.previousState) {
            ctx.fillText(`Previous: ${this.previousState.name}`, x + 10, y + 40);
        }

        if (this.blending) {
            const blendProgress = (this.blendTimer / this.blendDuration * 100).toFixed(0);
            ctx.fillText(`Blending: ${blendProgress}%`, x + 10, y + 60);
        }

        // Show available transitions
        let offsetY = 80;
        ctx.fillStyle = '#888';
        ctx.font = '12px monospace';

        for (const targetState of this.currentState.transitions.keys()) {
            ctx.fillText(`-> ${targetState}`, x + 10, y + offsetY);
            offsetY += 15;
        }
    }
}

// Example: Setup character animation state machine
/*
function setupCharacterAnimations(spriteSheet) {
    const asm = new AnimationStateMachine(spriteSheet);

    // Create states
    const idleState = new AnimationState(
        'idle',
        new Animation('idle', [0, 1, 2, 3], 8, true)
    );

    const walkState = new AnimationState(
        'walk',
        new Animation('walk', [4, 5, 6, 7], 12, true)
    );

    const jumpState = new AnimationState(
        'jump',
        new Animation('jump', [8, 9, 10], 15, false)
    );

    const fallState = new AnimationState(
        'fall',
        new Animation('fall', [11, 12], 10, true)
    );

    // Define transitions
    idleState.addTransition('walk', ctx => ctx.isMoving);
    idleState.addTransition('jump', ctx => ctx.jumpPressed && ctx.onGround);
    idleState.addTransition('fall', ctx => !ctx.onGround && ctx.vy > 0);

    walkState.addTransition('idle', ctx => !ctx.isMoving);
    walkState.addTransition('jump', ctx => ctx.jumpPressed && ctx.onGround);
    walkState.addTransition('fall', ctx => !ctx.onGround);

    jumpState.addTransition('fall', ctx => ctx.vy > 0);
    jumpState.addTransition('idle', ctx => ctx.onGround);

    fallState.addTransition('idle', ctx => ctx.onGround && !ctx.isMoving);
    fallState.addTransition('walk', ctx => ctx.onGround && ctx.isMoving);

    // Add states to machine
    asm.addState(idleState);
    asm.addState(walkState);
    asm.addState(jumpState);
    asm.addState(fallState);

    asm.setState('idle', true);

    return asm;
}
*/
```

## Skeletal Animation Basics

Skeletal animation uses a hierarchy of bones to animate sprites.

### Simple Implementation

```javascript
class Bone {
    constructor(x, y, length, angle = 0) {
        this.x = x;
        this.y = y;
        this.length = length;
        this.angle = angle; // radians
        this.children = [];
        this.sprite = null; // Optional sprite attached to bone
    }

    addChild(bone) {
        this.children.push(bone);
    }

    // Get end position of bone
    getEndPoint() {
        return {
            x: this.x + Math.cos(this.angle) * this.length,
            y: this.y + Math.sin(this.angle) * this.length
        };
    }

    update(parentX = 0, parentY = 0, parentAngle = 0) {
        // Update position relative to parent
        this.x = parentX;
        this.y = parentY;
        this.globalAngle = parentAngle + this.angle;

        // Get this bone's end point for children
        const endPoint = this.getEndPoint();

        // Update children
        for (const child of this.children) {
            child.update(endPoint.x, endPoint.y, this.globalAngle);
        }
    }

    render(ctx) {
        ctx.save();

        // Draw bone
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);

        const endPoint = this.getEndPoint();
        ctx.lineTo(endPoint.x, endPoint.y);
        ctx.stroke();

        // Draw joint
        ctx.fillStyle = '#ff0000';
        ctx.beginPath();
        ctx.arc(this.x, this.y, 5, 0, Math.PI * 2);
        ctx.fill();

        // Draw sprite if attached
        if (this.sprite) {
            ctx.translate(this.x, this.y);
            ctx.rotate(this.globalAngle);
            // Draw sprite...
        }

        ctx.restore();

        // Render children
        for (const child of this.children) {
            child.render(ctx);
        }
    }
}

// Example: Simple character skeleton
class SimpleSkeleton {
    constructor(x, y) {
        // Root bone (torso)
        this.root = new Bone(x, y, 40, -Math.PI / 2);

        // Arms
        const leftArm = new Bone(0, 0, 30, -Math.PI / 4);
        const rightArm = new Bone(0, 0, 30, -Math.PI * 3 / 4);

        // Legs
        const leftLeg = new Bone(0, 0, 35, Math.PI / 6);
        const rightLeg = new Bone(0, 0, 35, -Math.PI / 6);

        this.root.addChild(leftArm);
        this.root.addChild(rightArm);
        this.root.addChild(leftLeg);
        this.root.addChild(rightLeg);

        this.bones = [this.root, leftArm, rightArm, leftLeg, rightLeg];
        this.walkCycleTime = 0;
    }

    update(dt) {
        this.walkCycleTime += dt * 4;

        // Animate walk cycle
        const [root, leftArm, rightArm, leftLeg, rightLeg] = this.bones;

        // Swing arms
        leftArm.angle = -Math.PI / 4 + Math.sin(this.walkCycleTime) * 0.5;
        rightArm.angle = -Math.PI * 3 / 4 - Math.sin(this.walkCycleTime) * 0.5;

        // Swing legs
        leftLeg.angle = Math.PI / 6 + Math.sin(this.walkCycleTime) * 0.4;
        rightLeg.angle = -Math.PI / 6 - Math.sin(this.walkCycleTime) * 0.4;

        // Update bone hierarchy
        this.root.update();
    }

    render(ctx) {
        this.root.render(ctx);
    }
}
```

## Procedural Animation

Procedural animation generates motion algorithmically rather than from pre-made assets.

### Claude Code Prompt

```
Prompt: "Create procedural animations for particles, waves, and bouncing effects.
Include sine wave motion, spring physics, and perlin noise for organic movement.
Add visual examples of each type with adjustable parameters."
```

### Implementation

```javascript
class ProceduralAnimations {
    // Sine wave motion
    static sineWave(time, amplitude, frequency, phase = 0) {
        return amplitude * Math.sin(time * frequency + phase);
    }

    // Spring physics (damped harmonic oscillator)
    static spring(position, target, velocity, stiffness = 0.1, damping = 0.8) {
        const force = (target - position) * stiffness;
        velocity += force;
        velocity *= damping;
        position += velocity;

        return { position, velocity };
    }

    // Bounce easing
    static bounce(t) {
        const n1 = 7.5625;
        const d1 = 2.75;

        if (t < 1 / d1) {
            return n1 * t * t;
        } else if (t < 2 / d1) {
            return n1 * (t -= 1.5 / d1) * t + 0.75;
        } else if (t < 2.5 / d1) {
            return n1 * (t -= 2.25 / d1) * t + 0.9375;
        } else {
            return n1 * (t -= 2.625 / d1) * t + 0.984375;
        }
    }

    // Smooth step
    static smoothstep(t) {
        return t * t * (3 - 2 * t);
    }
}

// Example: Floating coin with procedural animation
class FloatingCoin {
    constructor(x, y) {
        this.baseX = x;
        this.baseY = y;
        this.x = x;
        this.y = y;
        this.time = Math.random() * Math.PI * 2;
        this.floatAmplitude = 10;
        this.floatFrequency = 2;
        this.rotation = 0;
        this.rotationSpeed = 3;
    }

    update(dt) {
        this.time += dt;

        // Floating motion (sine wave)
        this.y = this.baseY + ProceduralAnimations.sineWave(
            this.time,
            this.floatAmplitude,
            this.floatFrequency
        );

        // Rotation
        this.rotation += this.rotationSpeed * dt;
    }

    render(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);

        // Draw coin
        ctx.fillStyle = '#ffd700';
        ctx.beginPath();
        ctx.arc(0, 0, 15, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = '#ff8800';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.restore();
    }
}
```

## Tweening and Easing Functions

Tweening smoothly interpolates values over time.

### Claude Code Prompt

```
Prompt: "Create a comprehensive tweening system with multiple easing functions
(linear, easeIn, easeOut, easeInOut, elastic, bounce). Support tweening
multiple properties simultaneously, chaining tweens, and tween callbacks.
Include visual comparison of all easing functions."
```

### Implementation

```javascript
class Tween {
    constructor(target, properties, duration, easing = 'linear') {
        this.target = target;
        this.duration = duration;
        this.easing = Tween.easings[easing] || Tween.easings.linear;

        // Store start and end values
        this.properties = {};
        for (const prop in properties) {
            this.properties[prop] = {
                start: target[prop],
                end: properties[prop],
                delta: properties[prop] - target[prop]
            };
        }

        this.time = 0;
        this.finished = false;
        this.onComplete = null;
    }

    update(dt) {
        if (this.finished) return;

        this.time += dt;
        const t = Math.min(this.time / this.duration, 1);
        const easedT = this.easing(t);

        // Update properties
        for (const prop in this.properties) {
            const p = this.properties[prop];
            this.target[prop] = p.start + p.delta * easedT;
        }

        if (t >= 1) {
            this.finished = true;
            if (this.onComplete) {
                this.onComplete();
            }
        }
    }

    // Static easing functions
    static easings = {
        linear: t => t,
        easeInQuad: t => t * t,
        easeOutQuad: t => t * (2 - t),
        easeInOutQuad: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
        easeInCubic: t => t * t * t,
        easeOutCubic: t => (--t) * t * t + 1,
        easeInOutCubic: t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
        easeInElastic: t => {
            const c4 = (2 * Math.PI) / 3;
            return t === 0 ? 0 : t === 1 ? 1 :
                -Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * c4);
        },
        easeOutElastic: t => {
            const c4 = (2 * Math.PI) / 3;
            return t === 0 ? 0 : t === 1 ? 1 :
                Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
        },
        easeOutBounce: t => {
            const n1 = 7.5625;
            const d1 = 2.75;

            if (t < 1 / d1) {
                return n1 * t * t;
            } else if (t < 2 / d1) {
                return n1 * (t -= 1.5 / d1) * t + 0.75;
            } else if (t < 2.5 / d1) {
                return n1 * (t -= 2.25 / d1) * t + 0.9375;
            } else {
                return n1 * (t -= 2.625 / d1) * t + 0.984375;
            }
        }
    };
}

class TweenManager {
    constructor() {
        this.tweens = [];
    }

    add(tween) {
        this.tweens.push(tween);
        return tween;
    }

    to(target, properties, duration, easing = 'linear') {
        const tween = new Tween(target, properties, duration, easing);
        this.add(tween);
        return tween;
    }

    update(dt) {
        // Update all tweens
        for (let i = this.tweens.length - 1; i >= 0; i--) {
            this.tweens[i].update(dt);

            // Remove finished tweens
            if (this.tweens[i].finished) {
                this.tweens.splice(i, 1);
            }
        }
    }

    clear() {
        this.tweens = [];
    }
}

// Example usage
/*
const tweenManager = new TweenManager();

const box = { x: 50, y: 50, scale: 1 };

// Tween to new position
tweenManager.to(box, { x: 400, y: 300 }, 2, 'easeInOutCubic');

// Chain tweens
tweenManager.to(box, { scale: 2 }, 1, 'easeOutElastic').onComplete = () => {
    tweenManager.to(box, { scale: 1 }, 1, 'easeOutBounce');
};

function gameLoop(dt) {
    tweenManager.update(dt);
    // Render box...
}
*/
```

## Integration with Game Loops

Animation systems must integrate cleanly with game loops.

### Best Practices

1. **Update animations with delta time** for frame-rate independence
2. **Separate update and render** logic
3. **Use animation events** for gameplay triggers (attack damage frame, footstep sounds)
4. **Pool animation objects** to avoid garbage collection
5. **Cache frame calculations** when possible

## Performance Optimization

### Optimization Techniques

1. **Sprite Atlasing**: Pack multiple sprites into one texture
2. **Object Pooling**: Reuse animation objects
3. **Culling**: Don't update off-screen animations
4. **LOD**: Use simpler animations for distant objects
5. **Sprite Batching**: Render similar sprites in one draw call

```javascript
class OptimizedAnimationManager {
    constructor() {
        this.animations = [];
        this.visibleAnimations = [];
    }

    update(dt, camera) {
        // Only update visible animations
        this.visibleAnimations = this.animations.filter(anim => {
            return this.isVisible(anim, camera);
        });

        for (const anim of this.visibleAnimations) {
            anim.update(dt);
        }
    }

    isVisible(anim, camera) {
        // Simple AABB check against camera viewport
        return anim.x + anim.width > camera.x &&
               anim.x < camera.x + camera.width &&
               anim.y + anim.height > camera.y &&
               anim.y < camera.y + camera.height;
    }

    render(ctx) {
        // Batch render visible animations
        for (const anim of this.visibleAnimations) {
            anim.render(ctx);
        }
    }
}
```

## Conclusion

Animation systems range from simple sprite playback to complex state machines and procedural generation. Start with basic sprite sheet animation, add state machines when you have multiple related animations, and use tweening for smooth UI and effects. Always optimize by culling off-screen animations and batching rendering.

---

**Related Documentation:**
- [Game Loops and Timing](./game-loops-and-timing.md)
- [State Management](./state-management.md)
- [Graphics Rendering](../03-graphics-rendering/)

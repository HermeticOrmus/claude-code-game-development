# Three.js for Game Development

Three.js is a lightweight, flexible 3D library that provides excellent abstraction over WebGL. While not specifically a game engine, it's powerful for building custom 3D games.

## Table of Contents
- [Three.js Fundamentals](#threejs-fundamentals)
- [Scene Setup](#scene-setup)
- [Game Loop Integration](#game-loop-integration)
- [Complete 3D Game Example](#complete-3d-game-example)
- [Three.js vs Babylon.js](#threejs-vs-babylonjs)
- [Claude Code Prompts](#claude-code-prompts)

## Three.js Fundamentals

### Core Concepts

Three.js games require three fundamental components:

1. **Scene** - Container for all 3D objects
2. **Camera** - Point of view
3. **Renderer** - Draws the scene to canvas

### Installation

```bash
npm install three
# TypeScript types
npm install --save-dev @types/three
```

### Basic Setup

```typescript
// src/game.ts
import * as THREE from 'three';

export class Game {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private clock: THREE.Clock;

  constructor(container: HTMLElement) {
    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x87ceeb);
    this.scene.fog = new THREE.Fog(0x87ceeb, 10, 100);

    // Camera
    const aspect = window.innerWidth / window.innerHeight;
    this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
    this.camera.position.set(0, 5, 10);
    this.camera.lookAt(0, 0, 0);

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(this.renderer.domElement);

    // Clock for delta time
    this.clock = new THREE.Clock();

    // Handle window resize
    window.addEventListener('resize', () => this.onWindowResize());
  }

  private onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  public start() {
    this.animate();
  }

  private animate = () => {
    requestAnimationFrame(this.animate);

    const deltaTime = this.clock.getDelta();
    this.update(deltaTime);
    this.render();
  };

  private update(deltaTime: number) {
    // Game logic here
  }

  private render() {
    this.renderer.render(this.scene, this.camera);
  }
}

// main.ts
const game = new Game(document.body);
game.start();
```

## Scene Setup

### Lighting

```typescript
export class LightingManager {
  static setupLights(scene: THREE.Scene) {
    // Ambient light (soft global illumination)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    // Directional light (sun)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 100, 50);
    directionalLight.castShadow = true;

    // Shadow configuration
    directionalLight.shadow.camera.left = -50;
    directionalLight.shadow.camera.right = 50;
    directionalLight.shadow.camera.top = 50;
    directionalLight.shadow.camera.bottom = -50;
    directionalLight.shadow.camera.near = 0.1;
    directionalLight.shadow.camera.far = 200;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;

    scene.add(directionalLight);

    // Point light (torch, lamp)
    const pointLight = new THREE.PointLight(0xff9900, 1, 100);
    pointLight.position.set(10, 5, 10);
    pointLight.castShadow = true;
    scene.add(pointLight);

    // Spot light (flashlight)
    const spotLight = new THREE.SpotLight(0xffffff, 1);
    spotLight.position.set(0, 10, 0);
    spotLight.angle = Math.PI / 6;
    spotLight.penumbra = 0.2;
    spotLight.decay = 2;
    spotLight.distance = 50;
    spotLight.castShadow = true;
    scene.add(spotLight);

    return {
      ambient: ambientLight,
      directional: directionalLight,
      point: pointLight,
      spot: spotLight
    };
  }
}
```

### Geometry and Materials

```typescript
export class GeometryManager {
  // Basic primitives
  static createBox(size: number = 1): THREE.Mesh {
    const geometry = new THREE.BoxGeometry(size, size, size);
    const material = new THREE.MeshStandardMaterial({
      color: 0x00ff00,
      metalness: 0.3,
      roughness: 0.7
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    return mesh;
  }

  static createSphere(radius: number = 1): THREE.Mesh {
    const geometry = new THREE.SphereGeometry(radius, 32, 32);
    const material = new THREE.MeshStandardMaterial({
      color: 0xff0000,
      metalness: 0.5,
      roughness: 0.5
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    return mesh;
  }

  // Textured mesh
  static createTexturedMesh(
    geometry: THREE.BufferGeometry,
    texturePath: string
  ): THREE.Mesh {
    const textureLoader = new THREE.TextureLoader();
    const texture = textureLoader.load(texturePath);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(4, 4);

    const material = new THREE.MeshStandardMaterial({
      map: texture,
      metalness: 0.2,
      roughness: 0.8
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    return mesh;
  }

  // Ground plane
  static createGround(size: number = 100): THREE.Mesh {
    const geometry = new THREE.PlaneGeometry(size, size);
    const material = new THREE.MeshStandardMaterial({
      color: 0x3a8f3a,
      roughness: 0.9,
      metalness: 0.1
    });

    const ground = new THREE.Mesh(geometry, material);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    return ground;
  }

  // Custom geometry
  static createCustomMesh(): THREE.Mesh {
    const geometry = new THREE.BufferGeometry();

    const vertices = new Float32Array([
      -1, -1, 0,  // vertex 0
       1, -1, 0,  // vertex 1
       1,  1, 0,  // vertex 2
      -1,  1, 0   // vertex 3
    ]);

    const indices = new Uint16Array([
      0, 1, 2,  // triangle 1
      0, 2, 3   // triangle 2
    ]);

    const uvs = new Float32Array([
      0, 0,  // vertex 0
      1, 0,  // vertex 1
      1, 1,  // vertex 2
      0, 1   // vertex 3
    ]);

    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
    geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    geometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: 0x0088ff,
      side: THREE.DoubleSide
    });

    return new THREE.Mesh(geometry, material);
  }
}
```

### Camera Controls

```typescript
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls';

export class CameraController {
  // Orbit controls (third-person)
  static createOrbitControls(
    camera: THREE.Camera,
    domElement: HTMLElement
  ): OrbitControls {
    const controls = new OrbitControls(camera, domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 5;
    controls.maxDistance = 50;
    controls.maxPolarAngle = Math.PI / 2;
    return controls;
  }

  // First-person controls
  static createPointerLockControls(
    camera: THREE.Camera,
    domElement: HTMLElement
  ): PointerLockControls {
    const controls = new PointerLockControls(camera, domElement);

    domElement.addEventListener('click', () => {
      controls.lock();
    });

    return controls;
  }

  // Custom third-person camera
  static updateThirdPersonCamera(
    camera: THREE.PerspectiveCamera,
    target: THREE.Object3D,
    offset: THREE.Vector3,
    deltaTime: number
  ) {
    const idealOffset = offset.clone();
    idealOffset.applyQuaternion(target.quaternion);
    idealOffset.add(target.position);

    const idealLookAt = target.position.clone();
    idealLookAt.y += 1;

    const t = 1 - Math.pow(0.001, deltaTime);
    camera.position.lerp(idealOffset, t);

    const currentLookAt = new THREE.Vector3();
    camera.getWorldDirection(currentLookAt);
    currentLookAt.multiplyScalar(10);
    currentLookAt.add(camera.position);

    currentLookAt.lerp(idealLookAt, t);
    camera.lookAt(currentLookAt);
  }
}
```

## Game Loop Integration

### Fixed Timestep Game Loop

```typescript
export class GameLoop {
  private lastTime: number = 0;
  private accumulator: number = 0;
  private readonly fixedDeltaTime: number = 1 / 60; // 60 FPS
  private readonly maxSubSteps: number = 3;

  constructor(
    private updateCallback: (deltaTime: number) => void,
    private renderCallback: () => void
  ) {}

  public start() {
    this.lastTime = performance.now();
    this.loop();
  }

  private loop = () => {
    requestAnimationFrame(this.loop);

    const currentTime = performance.now();
    const deltaTime = Math.min((currentTime - this.lastTime) / 1000, 0.1);
    this.lastTime = currentTime;

    this.accumulator += deltaTime;

    let steps = 0;
    while (this.accumulator >= this.fixedDeltaTime && steps < this.maxSubSteps) {
      this.updateCallback(this.fixedDeltaTime);
      this.accumulator -= this.fixedDeltaTime;
      steps++;
    }

    this.renderCallback();
  };
}

// Usage
const gameLoop = new GameLoop(
  (deltaTime) => {
    // Fixed update for physics
    player.update(deltaTime);
    enemies.forEach(enemy => enemy.update(deltaTime));
  },
  () => {
    // Render
    renderer.render(scene, camera);
  }
);
gameLoop.start();
```

### Physics Integration

```typescript
import * as CANNON from 'cannon-es';

export class PhysicsWorld {
  private world: CANNON.World;
  private meshes: Map<CANNON.Body, THREE.Mesh> = new Map();

  constructor() {
    this.world = new CANNON.World({
      gravity: new CANNON.Vec3(0, -9.82, 0)
    });

    // Default contact material
    const defaultMaterial = new CANNON.Material('default');
    const defaultContactMaterial = new CANNON.ContactMaterial(
      defaultMaterial,
      defaultMaterial,
      {
        friction: 0.3,
        restitution: 0.3
      }
    );
    this.world.addContactMaterial(defaultContactMaterial);
    this.world.defaultContactMaterial = defaultContactMaterial;
  }

  public addBox(
    mesh: THREE.Mesh,
    mass: number = 1,
    position?: THREE.Vector3
  ): CANNON.Body {
    const box = mesh.geometry.boundingBox!;
    const size = new THREE.Vector3();
    box.getSize(size);

    const shape = new CANNON.Box(
      new CANNON.Vec3(size.x / 2, size.y / 2, size.z / 2)
    );

    const body = new CANNON.Body({ mass, shape });

    if (position) {
      body.position.set(position.x, position.y, position.z);
      mesh.position.copy(position);
    }

    this.world.addBody(body);
    this.meshes.set(body, mesh);

    return body;
  }

  public addSphere(
    mesh: THREE.Mesh,
    radius: number,
    mass: number = 1
  ): CANNON.Body {
    const shape = new CANNON.Sphere(radius);
    const body = new CANNON.Body({ mass, shape });
    body.position.copy(mesh.position as any);

    this.world.addBody(body);
    this.meshes.set(body, mesh);

    return body;
  }

  public update(deltaTime: number) {
    this.world.step(deltaTime);

    // Sync Three.js meshes with Cannon.js bodies
    this.meshes.forEach((mesh, body) => {
      mesh.position.copy(body.position as any);
      mesh.quaternion.copy(body.quaternion as any);
    });
  }

  public raycast(
    from: THREE.Vector3,
    to: THREE.Vector3
  ): CANNON.RaycastResult | null {
    const result = new CANNON.RaycastResult();
    this.world.raycastClosest(
      new CANNON.Vec3(from.x, from.y, from.z),
      new CANNON.Vec3(to.x, to.y, to.z),
      {},
      result
    );

    return result.hasHit ? result : null;
  }
}
```

## Complete 3D Game Example

Here's a complete third-person action game:

```typescript
// src/ActionGame.ts
import * as THREE from 'three';
import * as CANNON from 'cannon-es';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

interface InputState {
  forward: boolean;
  backward: boolean;
  left: boolean;
  right: boolean;
  jump: boolean;
  sprint: boolean;
}

export class ActionGame {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private physicsWorld: CANNON.World;

  private player: {
    mesh: THREE.Mesh;
    body: CANNON.Body;
    velocity: THREE.Vector3;
    speed: number;
    jumpForce: number;
    canJump: boolean;
  };

  private enemies: Array<{
    mesh: THREE.Mesh;
    body: CANNON.Body;
    health: number;
  }> = [];

  private inputState: InputState = {
    forward: false,
    backward: false,
    left: false,
    right: false,
    jump: false,
    sprint: false
  };

  private clock: THREE.Clock;
  private score: number = 0;
  private cameraOffset: THREE.Vector3 = new THREE.Vector3(0, 5, -10);

  constructor(container: HTMLElement) {
    // Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x87ceeb);
    this.scene.fog = new THREE.Fog(0x87ceeb, 50, 200);

    // Camera
    const aspect = window.innerWidth / window.innerHeight;
    this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(this.renderer.domElement);

    // Physics
    this.physicsWorld = new CANNON.World({
      gravity: new CANNON.Vec3(0, -20, 0)
    });

    // Clock
    this.clock = new THREE.Clock();

    // Setup game
    this.setupLights();
    this.createGround();
    this.player = this.createPlayer();
    this.createObstacles();
    this.spawnEnemies(5);
    this.setupInput();
    this.setupUI();

    // Event listeners
    window.addEventListener('resize', () => this.onWindowResize());

    // Start game loop
    this.animate();
  }

  private setupLights() {
    // Ambient
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambient);

    // Directional (sun)
    const sun = new THREE.DirectionalLight(0xffffff, 0.8);
    sun.position.set(50, 100, 50);
    sun.castShadow = true;
    sun.shadow.camera.left = -100;
    sun.shadow.camera.right = 100;
    sun.shadow.camera.top = 100;
    sun.shadow.camera.bottom = -100;
    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;
    this.scene.add(sun);
  }

  private createGround() {
    // Visual
    const geometry = new THREE.PlaneGeometry(200, 200);
    const material = new THREE.MeshStandardMaterial({
      color: 0x3a8f3a,
      roughness: 0.9
    });
    const ground = new THREE.Mesh(geometry, material);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    this.scene.add(ground);

    // Physics
    const groundBody = new CANNON.Body({
      type: CANNON.Body.STATIC,
      shape: new CANNON.Plane()
    });
    groundBody.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
    this.physicsWorld.addBody(groundBody);
  }

  private createPlayer() {
    // Visual
    const geometry = new THREE.CapsuleGeometry(0.5, 1.5, 4, 8);
    const material = new THREE.MeshStandardMaterial({ color: 0x0066ff });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(0, 2, 0);
    mesh.castShadow = true;
    this.scene.add(mesh);

    // Physics
    const body = new CANNON.Body({
      mass: 70,
      shape: new CANNON.Cylinder(0.5, 0.5, 2, 8),
      fixedRotation: true,
      linearDamping: 0.9,
      angularDamping: 0.9
    });
    body.position.set(0, 2, 0);

    // Prevent tipping over
    body.addEventListener('collide', (event: any) => {
      body.angularVelocity.set(0, 0, 0);
    });

    this.physicsWorld.addBody(body);

    return {
      mesh,
      body,
      velocity: new THREE.Vector3(),
      speed: 8,
      jumpForce: 10,
      canJump: true
    };
  }

  private createObstacles() {
    const obstacleData = [
      { pos: [10, 1, 10], size: [2, 2, 2] },
      { pos: [-10, 1, 10], size: [2, 2, 2] },
      { pos: [10, 1, -10], size: [2, 2, 2] },
      { pos: [-10, 1, -10], size: [2, 2, 2] },
      { pos: [0, 1, 20], size: [5, 2, 2] }
    ];

    obstacleData.forEach(({ pos, size }) => {
      // Visual
      const geometry = new THREE.BoxGeometry(...size);
      const material = new THREE.MeshStandardMaterial({ color: 0x888888 });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(...pos);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      this.scene.add(mesh);

      // Physics
      const shape = new CANNON.Box(
        new CANNON.Vec3(size[0] / 2, size[1] / 2, size[2] / 2)
      );
      const body = new CANNON.Body({ mass: 0, shape });
      body.position.set(...pos);
      this.physicsWorld.addBody(body);
    });
  }

  private spawnEnemies(count: number) {
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count;
      const radius = 20;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;

      this.createEnemy(new THREE.Vector3(x, 1, z));
    }
  }

  private createEnemy(position: THREE.Vector3) {
    // Visual
    const geometry = new THREE.SphereGeometry(0.8, 16, 16);
    const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(position);
    mesh.castShadow = true;
    this.scene.add(mesh);

    // Physics
    const body = new CANNON.Body({
      mass: 1,
      shape: new CANNON.Sphere(0.8)
    });
    body.position.copy(position as any);
    this.physicsWorld.addBody(body);

    const enemy = { mesh, body, health: 100 };
    this.enemies.push(enemy);

    return enemy;
  }

  private setupInput() {
    window.addEventListener('keydown', (e) => {
      switch (e.code) {
        case 'KeyW': this.inputState.forward = true; break;
        case 'KeyS': this.inputState.backward = true; break;
        case 'KeyA': this.inputState.left = true; break;
        case 'KeyD': this.inputState.right = true; break;
        case 'Space': this.inputState.jump = true; break;
        case 'ShiftLeft': this.inputState.sprint = true; break;
      }
    });

    window.addEventListener('keyup', (e) => {
      switch (e.code) {
        case 'KeyW': this.inputState.forward = false; break;
        case 'KeyS': this.inputState.backward = false; break;
        case 'KeyA': this.inputState.left = false; break;
        case 'KeyD': this.inputState.right = false; break;
        case 'Space': this.inputState.jump = false; break;
        case 'ShiftLeft': this.inputState.sprint = false; break;
      }
    });

    // Mouse click to attack
    window.addEventListener('click', () => this.attack());
  }

  private setupUI() {
    const scoreElement = document.createElement('div');
    scoreElement.id = 'score';
    scoreElement.style.position = 'absolute';
    scoreElement.style.top = '20px';
    scoreElement.style.right = '20px';
    scoreElement.style.color = 'white';
    scoreElement.style.fontSize = '24px';
    scoreElement.style.fontFamily = 'Arial';
    scoreElement.textContent = `Score: ${this.score}`;
    document.body.appendChild(scoreElement);
  }

  private updatePlayer(deltaTime: number) {
    const direction = new THREE.Vector3();
    const speed = this.inputState.sprint ? this.player.speed * 1.5 : this.player.speed;

    if (this.inputState.forward) direction.z += 1;
    if (this.inputState.backward) direction.z -= 1;
    if (this.inputState.left) direction.x -= 1;
    if (this.inputState.right) direction.x += 1;

    if (direction.length() > 0) {
      direction.normalize();

      // Apply camera-relative movement
      const cameraDirection = new THREE.Vector3();
      this.camera.getWorldDirection(cameraDirection);
      cameraDirection.y = 0;
      cameraDirection.normalize();

      const cameraRight = new THREE.Vector3();
      cameraRight.crossVectors(cameraDirection, new THREE.Vector3(0, 1, 0));

      const movement = cameraDirection.multiplyScalar(direction.z)
        .add(cameraRight.multiplyScalar(direction.x));

      this.player.body.velocity.x = movement.x * speed;
      this.player.body.velocity.z = movement.z * speed;

      // Rotate player to face movement direction
      const angle = Math.atan2(movement.x, movement.z);
      this.player.mesh.rotation.y = angle;
    } else {
      this.player.body.velocity.x *= 0.9;
      this.player.body.velocity.z *= 0.9;
    }

    // Jump
    if (this.inputState.jump && this.player.canJump) {
      this.player.body.velocity.y = this.player.jumpForce;
      this.player.canJump = false;
    }

    // Check if on ground
    if (Math.abs(this.player.body.velocity.y) < 0.1) {
      this.player.canJump = true;
    }

    // Sync mesh with body
    this.player.mesh.position.copy(this.player.body.position as any);
    this.player.mesh.quaternion.copy(this.player.body.quaternion as any);
  }

  private updateEnemies(deltaTime: number) {
    this.enemies.forEach(enemy => {
      // Chase player
      const direction = new THREE.Vector3()
        .copy(this.player.mesh.position)
        .sub(enemy.mesh.position);
      direction.y = 0;
      direction.normalize();

      enemy.body.velocity.x = direction.x * 3;
      enemy.body.velocity.z = direction.z * 3;

      // Sync mesh with body
      enemy.mesh.position.copy(enemy.body.position as any);
      enemy.mesh.quaternion.copy(enemy.body.quaternion as any);

      // Look at player
      enemy.mesh.lookAt(this.player.mesh.position);
    });
  }

  private updateCamera(deltaTime: number) {
    const idealOffset = this.cameraOffset.clone();
    idealOffset.applyQuaternion(this.player.mesh.quaternion);
    idealOffset.add(this.player.mesh.position);

    const t = 1 - Math.pow(0.001, deltaTime);
    this.camera.position.lerp(idealOffset, t);

    const lookAtPosition = this.player.mesh.position.clone();
    lookAtPosition.y += 1;
    this.camera.lookAt(lookAtPosition);
  }

  private attack() {
    // Raycast from camera
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(0, 0), this.camera);

    const intersects = raycaster.intersectObjects(
      this.enemies.map(e => e.mesh)
    );

    if (intersects.length > 0) {
      const hitMesh = intersects[0].object as THREE.Mesh;
      const enemy = this.enemies.find(e => e.mesh === hitMesh);

      if (enemy) {
        enemy.health -= 34;

        if (enemy.health <= 0) {
          this.killEnemy(enemy);
        }
      }
    }
  }

  private killEnemy(enemy: typeof this.enemies[0]) {
    this.scene.remove(enemy.mesh);
    this.physicsWorld.removeBody(enemy.body);
    this.enemies = this.enemies.filter(e => e !== enemy);

    this.score += 100;
    const scoreElement = document.getElementById('score');
    if (scoreElement) {
      scoreElement.textContent = `Score: ${this.score}`;
    }

    // Spawn new enemy
    const angle = Math.random() * Math.PI * 2;
    const radius = 30;
    this.createEnemy(new THREE.Vector3(
      Math.cos(angle) * radius,
      1,
      Math.sin(angle) * radius
    ));
  }

  private onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  private animate = () => {
    requestAnimationFrame(this.animate);

    const deltaTime = Math.min(this.clock.getDelta(), 0.1);

    // Update physics
    this.physicsWorld.step(1 / 60, deltaTime, 3);

    // Update game logic
    this.updatePlayer(deltaTime);
    this.updateEnemies(deltaTime);
    this.updateCamera(deltaTime);

    // Render
    this.renderer.render(this.scene, this.camera);
  };
}

// main.ts
new ActionGame(document.body);
```

## Three.js vs Babylon.js

| Feature | Three.js | Babylon.js |
|---------|----------|------------|
| **Philosophy** | Library (bring your own structure) | Complete engine (opinionated) |
| **File Size** | ~600 KB | ~2 MB |
| **Learning Curve** | Moderate | Moderate-High |
| **Documentation** | Excellent examples | Excellent API docs |
| **Physics** | External (Cannon, Ammo) | Integrated |
| **Scene Management** | Manual | Built-in |
| **Asset Pipeline** | Manual | Inspector tool |
| **Shadows** | Good | Excellent |
| **Post-Processing** | Good | Excellent |
| **VR/AR** | WebXR Device API | Built-in WebXR |
| **Performance** | Excellent | Excellent |
| **Best For** | Custom experiences | Complete games |

### When to Choose Three.js

- You want minimal file size
- You need maximum flexibility
- You're building custom visualizations
- You prefer minimal abstraction
- You want fine-grained control

### When to Choose Babylon.js

- You want an all-in-one solution
- You need visual development tools
- You're building complex 3D games
- You want built-in optimizations
- You need VR/AR support

## Claude Code Prompts

```
Create a Three.js third-person game with physics and camera controls
```

```
Build a space shooter using Three.js with particle effects
```

```
Implement terrain generation in Three.js with LOD
```

```
Add post-processing effects to my Three.js game
```

```
Create a custom shader for water in Three.js
```

```
Implement frustum culling optimization in Three.js
```

## Next Steps

- Explore [PixiJS Performance](./pixi-js-performance.md) for 2D rendering
- Learn [Custom Engine Development](./custom-engine-development.md)
- Review [Performance Optimization](../10-performance-optimization/README.md)

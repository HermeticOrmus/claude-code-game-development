# Babylon.js Workflows for 3D Game Development

Babylon.js is a powerful, open-source 3D engine for the web with complete tooling for building production-ready 3D games and experiences.

## Table of Contents
- [Setup and Configuration](#setup-and-configuration)
- [Scene Creation](#scene-creation)
- [Meshes and Materials](#meshes-and-materials)
- [Lighting Systems](#lighting-systems)
- [Physics Integration](#physics-integration)
- [Complete 3D Game Example](#complete-3d-game-example)
- [Claude Code Prompts](#claude-code-prompts)
- [Performance Optimization](#performance-optimization)

## Setup and Configuration

### Installation

```bash
npm install @babylonjs/core @babylonjs/loaders @babylonjs/materials
# Optional but recommended
npm install @babylonjs/inspector @babylonjs/gui
```

### Basic Scene Setup

```typescript
// src/game.ts
import {
  Engine,
  Scene,
  ArcRotateCamera,
  HemisphericLight,
  Vector3,
  MeshBuilder
} from '@babylonjs/core';

export class Game {
  private canvas: HTMLCanvasElement;
  private engine: Engine;
  private scene: Scene;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.engine = new Engine(this.canvas, true, {
      preserveDrawingBuffer: true,
      stencil: true
    });

    this.scene = this.createScene();

    // Render loop
    this.engine.runRenderLoop(() => {
      this.scene.render();
    });

    // Handle window resize
    window.addEventListener('resize', () => {
      this.engine.resize();
    });
  }

  private createScene(): Scene {
    const scene = new Scene(this.engine);
    scene.clearColor = new BABYLON.Color4(0.2, 0.2, 0.3, 1);

    // Camera
    const camera = new ArcRotateCamera(
      'camera',
      -Math.PI / 2,
      Math.PI / 2.5,
      10,
      Vector3.Zero(),
      scene
    );
    camera.attachControl(this.canvas, true);
    camera.minZ = 0.1; // Near clipping plane
    camera.maxZ = 1000; // Far clipping plane

    // Light
    const light = new HemisphericLight(
      'light',
      new Vector3(0, 1, 0),
      scene
    );
    light.intensity = 0.7;

    return scene;
  }

  public dispose() {
    this.scene.dispose();
    this.engine.dispose();
  }
}

// main.ts
const canvas = document.getElementById('renderCanvas') as HTMLCanvasElement;
const game = new Game(canvas);
```

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "lib": ["ES2020", "DOM"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  }
}
```

### Vite Configuration for Babylon.js

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  optimizeDeps: {
    exclude: ['@babylonjs/core', '@babylonjs/loaders']
  },
  build: {
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: {
          babylon: [
            '@babylonjs/core',
            '@babylonjs/loaders',
            '@babylonjs/materials'
          ]
        }
      }
    }
  }
});
```

## Scene Creation

### Advanced Scene Setup

```typescript
import {
  Scene,
  Engine,
  SceneLoader,
  ActionManager,
  ExecuteCodeAction
} from '@babylonjs/core';
import '@babylonjs/loaders'; // Required for loading models

export class GameScene {
  private scene: Scene;

  constructor(engine: Engine) {
    this.scene = new Scene(engine);
    this.setupEnvironment();
    this.setupPhysics();
    this.setupOptimizations();
  }

  private setupEnvironment() {
    // Skybox
    const skybox = MeshBuilder.CreateBox('skyBox', { size: 1000 }, this.scene);
    const skyboxMaterial = new StandardMaterial('skyBox', this.scene);
    skyboxMaterial.backFaceCulling = false;
    skyboxMaterial.reflectionTexture = new CubeTexture(
      'assets/skybox/skybox',
      this.scene
    );
    skyboxMaterial.reflectionTexture.coordinatesMode = Texture.SKYBOX_MODE;
    skyboxMaterial.diffuseColor = new Color3(0, 0, 0);
    skyboxMaterial.specularColor = new Color3(0, 0, 0);
    skybox.material = skyboxMaterial;

    // Ground
    const ground = MeshBuilder.CreateGround(
      'ground',
      { width: 100, height: 100 },
      this.scene
    );
    const groundMaterial = new StandardMaterial('groundMat', this.scene);
    groundMaterial.diffuseTexture = new Texture(
      'assets/textures/ground.jpg',
      this.scene
    );
    groundMaterial.diffuseTexture.uScale = 10;
    groundMaterial.diffuseTexture.vScale = 10;
    ground.material = groundMaterial;
    ground.checkCollisions = true;

    // Fog
    this.scene.fogMode = Scene.FOGMODE_EXP2;
    this.scene.fogDensity = 0.01;
    this.scene.fogColor = new Color3(0.9, 0.9, 0.95);
  }

  private setupPhysics() {
    // Enable physics (using Cannon.js)
    this.scene.enablePhysics(
      new Vector3(0, -9.81, 0),
      new CannonJSPlugin()
    );
  }

  private setupOptimizations() {
    // Frustum culling
    this.scene.autoClear = false;
    this.scene.autoClearDepthAndStencil = false;

    // Hardware scaling
    const optimizeForLowEnd = this.detectLowEndDevice();
    if (optimizeForLowEnd) {
      this.engine.setHardwareScalingLevel(2);
    }

    // Scene optimizer
    const options = new SceneOptimizerOptions(60, 2000);
    options.addOptimization(new HardwareScalingOptimization(0, 2));
    options.addOptimization(new TextureOptimization(0, 512));

    const optimizer = new SceneOptimizer(this.scene, options);
    optimizer.start();
  }

  private detectLowEndDevice(): boolean {
    const canvas = this.engine.getRenderingCanvas();
    const gl = canvas?.getContext('webgl2') || canvas?.getContext('webgl');
    if (!gl) return true;

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
      const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
      return /Intel|Mali|Adreno [34]/i.test(renderer);
    }
    return false;
  }

  public getScene(): Scene {
    return this.scene;
  }
}
```

## Meshes and Materials

### Creating and Managing Meshes

```typescript
import {
  MeshBuilder,
  StandardMaterial,
  PBRMaterial,
  Texture,
  Color3,
  Vector3
} from '@babylonjs/core';

export class MeshManager {
  private scene: Scene;

  constructor(scene: Scene) {
    this.scene = scene;
  }

  // Basic primitives
  createPrimitives() {
    // Box
    const box = MeshBuilder.CreateBox('box', {
      width: 2,
      height: 2,
      depth: 2
    }, this.scene);

    // Sphere
    const sphere = MeshBuilder.CreateSphere('sphere', {
      diameter: 2,
      segments: 32
    }, this.scene);

    // Cylinder
    const cylinder = MeshBuilder.CreateCylinder('cylinder', {
      height: 3,
      diameterTop: 1,
      diameterBottom: 2,
      tessellation: 24
    }, this.scene);

    // Plane
    const plane = MeshBuilder.CreatePlane('plane', {
      width: 5,
      height: 5
    }, this.scene);

    // Torus
    const torus = MeshBuilder.CreateTorus('torus', {
      diameter: 3,
      thickness: 1,
      tessellation: 32
    }, this.scene);

    return { box, sphere, cylinder, plane, torus };
  }

  // Standard Material
  createStandardMaterial(name: string) {
    const material = new StandardMaterial(name, this.scene);

    // Diffuse (base color)
    material.diffuseColor = new Color3(1, 0, 0);
    material.diffuseTexture = new Texture('assets/diffuse.jpg', this.scene);

    // Specular (shininess)
    material.specularColor = new Color3(1, 1, 1);
    material.specularPower = 64;

    // Emissive (glow)
    material.emissiveColor = new Color3(0.2, 0, 0);

    // Ambient
    material.ambientColor = new Color3(0.3, 0.3, 0.3);

    // Alpha
    material.alpha = 1.0;

    // Backface culling
    material.backFaceCulling = true;

    return material;
  }

  // PBR Material (Physically Based Rendering)
  createPBRMaterial(name: string) {
    const material = new PBRMaterial(name, this.scene);

    // Albedo (base color)
    material.albedoColor = new Color3(1, 0, 0);
    material.albedoTexture = new Texture('assets/albedo.jpg', this.scene);

    // Metallic and roughness
    material.metallic = 0.7;
    material.roughness = 0.3;
    material.metallicTexture = new Texture('assets/metallic.jpg', this.scene);

    // Normal map
    material.bumpTexture = new Texture('assets/normal.jpg', this.scene);

    // Ambient occlusion
    material.ambientTexture = new Texture('assets/ao.jpg', this.scene);
    material.useAmbientOcclusionFromMetallicTextureRed = true;

    // Emissive
    material.emissiveColor = new Color3(0, 0, 0);
    material.emissiveTexture = new Texture('assets/emissive.jpg', this.scene);
    material.emissiveIntensity = 1;

    return material;
  }

  // Dynamic mesh creation
  createCustomMesh() {
    const mesh = new Mesh('custom', this.scene);

    const positions = [
      -1, -1, 0,  // vertex 0
       1, -1, 0,  // vertex 1
       1,  1, 0,  // vertex 2
      -1,  1, 0   // vertex 3
    ];

    const indices = [
      0, 1, 2,  // triangle 1
      0, 2, 3   // triangle 2
    ];

    const normals: number[] = [];
    const uvs = [
      0, 1,  // vertex 0
      1, 1,  // vertex 1
      1, 0,  // vertex 2
      0, 0   // vertex 3
    ];

    VertexData.ComputeNormals(positions, indices, normals);

    const vertexData = new VertexData();
    vertexData.positions = positions;
    vertexData.indices = indices;
    vertexData.normals = normals;
    vertexData.uvs = uvs;

    vertexData.applyToMesh(mesh);

    return mesh;
  }

  // Instancing for performance
  createInstances(master: Mesh, count: number) {
    const instances: InstancedMesh[] = [];

    for (let i = 0; i < count; i++) {
      const instance = master.createInstance(`instance${i}`);
      instance.position = new Vector3(
        Math.random() * 100 - 50,
        Math.random() * 10,
        Math.random() * 100 - 50
      );
      instances.push(instance);
    }

    return instances;
  }
}
```

## Lighting Systems

```typescript
import {
  HemisphericLight,
  PointLight,
  DirectionalLight,
  SpotLight,
  Vector3,
  Color3,
  ShadowGenerator
} from '@babylonjs/core';

export class LightingSystem {
  private scene: Scene;

  constructor(scene: Scene) {
    this.scene = scene;
  }

  // Hemispheric light (ambient)
  createAmbientLight() {
    const light = new HemisphericLight(
      'ambient',
      new Vector3(0, 1, 0),
      this.scene
    );
    light.intensity = 0.5;
    light.diffuse = new Color3(1, 1, 1);
    light.specular = new Color3(0.5, 0.5, 0.5);
    light.groundColor = new Color3(0.3, 0.3, 0.5);

    return light;
  }

  // Point light (omnidirectional)
  createPointLight(position: Vector3) {
    const light = new PointLight(
      'point',
      position,
      this.scene
    );
    light.intensity = 1.0;
    light.diffuse = new Color3(1, 0.8, 0.6);
    light.specular = new Color3(1, 1, 1);

    // Range and falloff
    light.range = 50;
    light.radius = 0.1;

    return light;
  }

  // Directional light (sun)
  createDirectionalLight() {
    const light = new DirectionalLight(
      'sun',
      new Vector3(-1, -2, -1),
      this.scene
    );
    light.position = new Vector3(20, 40, 20);
    light.intensity = 1.0;
    light.diffuse = new Color3(1, 0.95, 0.8);
    light.specular = new Color3(1, 1, 1);

    // Shadows
    const shadowGenerator = new ShadowGenerator(1024, light);
    shadowGenerator.useBlurExponentialShadowMap = true;
    shadowGenerator.blurKernel = 32;
    shadowGenerator.setDarkness(0.3);

    return { light, shadowGenerator };
  }

  // Spot light (flashlight)
  createSpotLight(position: Vector3, direction: Vector3) {
    const light = new SpotLight(
      'spot',
      position,
      direction,
      Math.PI / 3,
      2,
      this.scene
    );
    light.intensity = 2.0;
    light.diffuse = new Color3(1, 1, 1);

    return light;
  }

  // Dynamic day/night cycle
  createDayNightCycle() {
    let time = 0;
    const sun = this.createDirectionalLight().light;

    this.scene.onBeforeRenderObservable.add(() => {
      time += this.scene.getEngine().getDeltaTime() / 1000;

      // Rotate sun
      const angle = (time * 0.1) % (Math.PI * 2);
      sun.direction = new Vector3(
        Math.cos(angle),
        -Math.sin(angle),
        0
      );

      // Change color based on time
      const dayColor = new Color3(1, 0.95, 0.8);
      const nightColor = new Color3(0.2, 0.2, 0.4);
      const sunHeight = Math.sin(angle);

      if (sunHeight > 0) {
        sun.diffuse = dayColor;
        sun.intensity = sunHeight;
      } else {
        sun.diffuse = nightColor;
        sun.intensity = Math.abs(sunHeight) * 0.3;
      }
    });
  }
}
```

## Physics Integration

```typescript
import {
  PhysicsImpostor,
  Vector3,
  Mesh,
  Scene
} from '@babylonjs/core';
import { CannonJSPlugin } from '@babylonjs/core/Physics/Plugins';
import * as CANNON from 'cannon';

export class PhysicsSystem {
  private scene: Scene;

  constructor(scene: Scene) {
    this.scene = scene;
    this.initialize();
  }

  private initialize() {
    // Initialize physics engine
    const gravityVector = new Vector3(0, -9.81, 0);
    const physicsPlugin = new CannonJSPlugin(true, 10, CANNON);
    this.scene.enablePhysics(gravityVector, physicsPlugin);
  }

  // Create physics-enabled ground
  createPhysicsGround() {
    const ground = MeshBuilder.CreateGround(
      'ground',
      { width: 100, height: 100 },
      this.scene
    );

    ground.physicsImpostor = new PhysicsImpostor(
      ground,
      PhysicsImpostor.BoxImpostor,
      { mass: 0, restitution: 0.5, friction: 0.5 },
      this.scene
    );

    return ground;
  }

  // Create dynamic physics objects
  createPhysicsBox(position: Vector3) {
    const box = MeshBuilder.CreateBox('box', { size: 2 }, this.scene);
    box.position = position;

    box.physicsImpostor = new PhysicsImpostor(
      box,
      PhysicsImpostor.BoxImpostor,
      { mass: 1, restitution: 0.3, friction: 0.5 },
      this.scene
    );

    return box;
  }

  createPhysicsSphere(position: Vector3) {
    const sphere = MeshBuilder.CreateSphere(
      'sphere',
      { diameter: 2 },
      this.scene
    );
    sphere.position = position;

    sphere.physicsImpostor = new PhysicsImpostor(
      sphere,
      PhysicsImpostor.SphereImpostor,
      { mass: 1, restitution: 0.9, friction: 0.1 },
      this.scene
    );

    return sphere;
  }

  // Apply forces
  applyImpulse(mesh: Mesh, direction: Vector3, magnitude: number) {
    if (mesh.physicsImpostor) {
      const impulse = direction.normalize().scale(magnitude);
      mesh.physicsImpostor.applyImpulse(
        impulse,
        mesh.getAbsolutePosition()
      );
    }
  }

  // Raycasting for shooting
  shootRaycast(origin: Vector3, direction: Vector3) {
    const ray = new Ray(origin, direction, 1000);
    const hit = this.scene.pickWithRay(ray);

    if (hit?.pickedMesh) {
      const mesh = hit.pickedMesh as Mesh;

      // Apply force at hit point
      if (mesh.physicsImpostor) {
        const force = direction.normalize().scale(50);
        mesh.physicsImpostor.applyImpulse(force, hit.pickedPoint!);
      }

      // Visual feedback
      const sphere = MeshBuilder.CreateSphere(
        'impact',
        { diameter: 0.2 },
        this.scene
      );
      sphere.position = hit.pickedPoint!;

      setTimeout(() => sphere.dispose(), 100);

      return hit;
    }

    return null;
  }

  // Collision detection
  onCollision(meshA: Mesh, meshB: Mesh, callback: () => void) {
    if (meshA.physicsImpostor && meshB.physicsImpostor) {
      meshA.physicsImpostor.registerOnPhysicsCollide(
        meshB.physicsImpostor,
        callback
      );
    }
  }
}
```

## Complete 3D Game Example

Here's a complete first-person shooter game:

```typescript
// src/FPSGame.ts
import {
  Engine,
  Scene,
  UniversalCamera,
  Vector3,
  HemisphericLight,
  MeshBuilder,
  StandardMaterial,
  Color3,
  Mesh,
  ActionManager,
  ExecuteCodeAction,
  Ray,
  ParticleSystem,
  Texture,
  Color4
} from '@babylonjs/core';
import { CannonJSPlugin } from '@babylonjs/core/Physics/Plugins';
import * as CANNON from 'cannon';

export class FPSGame {
  private canvas: HTMLCanvasElement;
  private engine: Engine;
  private scene: Scene;
  private camera: UniversalCamera;
  private enemies: Mesh[] = [];
  private score: number = 0;
  private health: number = 100;
  private ammo: number = 30;

  // Movement
  private moveForward: boolean = false;
  private moveBackward: boolean = false;
  private moveLeft: boolean = false;
  private moveRight: boolean = false;
  private movementSpeed: number = 0.5;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.engine = new Engine(this.canvas, true);
    this.scene = this.createScene();
    this.camera = this.createCamera();

    this.setupEnvironment();
    this.setupPhysics();
    this.spawnEnemies();
    this.setupInput();
    this.setupUI();
    this.startGameLoop();
  }

  private createScene(): Scene {
    const scene = new Scene(this.engine);
    scene.clearColor = new Color4(0.5, 0.8, 0.95, 1);

    // Lighting
    const light = new HemisphericLight(
      'light',
      new Vector3(0, 1, 0),
      scene
    );
    light.intensity = 0.8;

    return scene;
  }

  private createCamera(): UniversalCamera {
    const camera = new UniversalCamera(
      'camera',
      new Vector3(0, 1.8, -10),
      this.scene
    );

    camera.attachControl(this.canvas, true);
    camera.speed = this.movementSpeed;
    camera.minZ = 0.1;

    // FPS camera settings
    camera.angularSensibility = 1000;
    camera.keysUp = [];
    camera.keysDown = [];
    camera.keysLeft = [];
    camera.keysRight = [];

    // Lock pointer on click
    this.canvas.addEventListener('click', () => {
      this.canvas.requestPointerLock();
    });

    return camera;
  }

  private setupEnvironment() {
    // Ground
    const ground = MeshBuilder.CreateGround(
      'ground',
      { width: 100, height: 100 },
      this.scene
    );
    const groundMat = new StandardMaterial('groundMat', this.scene);
    groundMat.diffuseColor = new Color3(0.4, 0.6, 0.4);
    ground.material = groundMat;
    ground.checkCollisions = true;

    // Walls
    this.createWall(new Vector3(0, 2.5, 50), 100, 5, 1);
    this.createWall(new Vector3(0, 2.5, -50), 100, 5, 1);
    this.createWall(new Vector3(50, 2.5, 0), 1, 5, 100);
    this.createWall(new Vector3(-50, 2.5, 0), 1, 5, 100);

    // Cover objects
    for (let i = 0; i < 10; i++) {
      const cover = MeshBuilder.CreateBox(
        `cover${i}`,
        { width: 3, height: 2, depth: 3 },
        this.scene
      );
      cover.position = new Vector3(
        Math.random() * 80 - 40,
        1,
        Math.random() * 80 - 40
      );
      cover.checkCollisions = true;

      const coverMat = new StandardMaterial(`coverMat${i}`, this.scene);
      coverMat.diffuseColor = new Color3(0.6, 0.6, 0.6);
      cover.material = coverMat;
    }
  }

  private createWall(position: Vector3, width: number, height: number, depth: number) {
    const wall = MeshBuilder.CreateBox(
      'wall',
      { width, height, depth },
      this.scene
    );
    wall.position = position;
    wall.checkCollisions = true;

    const wallMat = new StandardMaterial('wallMat', this.scene);
    wallMat.diffuseColor = new Color3(0.7, 0.7, 0.7);
    wall.material = wallMat;

    return wall;
  }

  private setupPhysics() {
    const gravityVector = new Vector3(0, -9.81, 0);
    this.scene.enablePhysics(gravityVector, new CannonJSPlugin(true, 10, CANNON));
  }

  private spawnEnemies() {
    for (let i = 0; i < 5; i++) {
      const enemy = this.createEnemy(
        new Vector3(
          Math.random() * 60 - 30,
          1,
          Math.random() * 60 - 30
        )
      );
      this.enemies.push(enemy);
    }
  }

  private createEnemy(position: Vector3): Mesh {
    const enemy = MeshBuilder.CreateCylinder(
      'enemy',
      { height: 2, diameter: 1 },
      this.scene
    );
    enemy.position = position;

    const enemyMat = new StandardMaterial('enemyMat', this.scene);
    enemyMat.diffuseColor = new Color3(1, 0, 0);
    enemyMat.emissiveColor = new Color3(0.2, 0, 0);
    enemy.material = enemyMat;

    // Enemy AI
    this.scene.onBeforeRenderObservable.add(() => {
      const direction = this.camera.position.subtract(enemy.position);
      direction.y = 0;
      direction.normalize();

      enemy.position.addInPlace(direction.scale(0.02));
      enemy.lookAt(this.camera.position);

      // Check if enemy reached player
      const distance = Vector3.Distance(enemy.position, this.camera.position);
      if (distance < 2) {
        this.takeDamage(1);
      }
    });

    return enemy;
  }

  private setupInput() {
    this.scene.actionManager = new ActionManager(this.scene);

    // Keyboard
    this.scene.actionManager.registerAction(
      new ExecuteCodeAction(ActionManager.OnKeyDownTrigger, (evt) => {
        switch (evt.sourceEvent.key.toLowerCase()) {
          case 'w':
            this.moveForward = true;
            break;
          case 's':
            this.moveBackward = true;
            break;
          case 'a':
            this.moveLeft = true;
            break;
          case 'd':
            this.moveRight = true;
            break;
          case 'r':
            this.reload();
            break;
        }
      })
    );

    this.scene.actionManager.registerAction(
      new ExecuteCodeAction(ActionManager.OnKeyUpTrigger, (evt) => {
        switch (evt.sourceEvent.key.toLowerCase()) {
          case 'w':
            this.moveForward = false;
            break;
          case 's':
            this.moveBackward = false;
            break;
          case 'a':
            this.moveLeft = false;
            break;
          case 'd':
            this.moveRight = false;
            break;
        }
      })
    );

    // Mouse click to shoot
    this.canvas.addEventListener('mousedown', (evt) => {
      if (evt.button === 0) { // Left click
        this.shoot();
      }
    });
  }

  private setupUI() {
    // Create HUD using Babylon GUI
    const advancedTexture = AdvancedDynamicTexture.CreateFullscreenUI('UI');

    // Crosshair
    const crosshair = new Ellipse();
    crosshair.width = '20px';
    crosshair.height = '20px';
    crosshair.color = 'white';
    crosshair.thickness = 2;
    advancedTexture.addControl(crosshair);

    // Health bar
    const healthText = new TextBlock();
    healthText.text = `Health: ${this.health}`;
    healthText.color = 'white';
    healthText.fontSize = 24;
    healthText.textHorizontalAlignment = Control.HORIZONTAL_ALIGNMENT_LEFT;
    healthText.textVerticalAlignment = Control.VERTICAL_ALIGNMENT_TOP;
    healthText.left = 20;
    healthText.top = 20;
    advancedTexture.addControl(healthText);

    // Ammo counter
    const ammoText = new TextBlock();
    ammoText.text = `Ammo: ${this.ammo}`;
    ammoText.color = 'white';
    ammoText.fontSize = 24;
    ammoText.textHorizontalAlignment = Control.HORIZONTAL_ALIGNMENT_RIGHT;
    ammoText.textVerticalAlignment = Control.VERTICAL_ALIGNMENT_BOTTOM;
    ammoText.left = -20;
    ammoText.top = -20;
    advancedTexture.addControl(ammoText);

    // Score
    const scoreText = new TextBlock();
    scoreText.text = `Score: ${this.score}`;
    scoreText.color = 'white';
    scoreText.fontSize = 24;
    scoreText.textHorizontalAlignment = Control.HORIZONTAL_ALIGNMENT_RIGHT;
    scoreText.textVerticalAlignment = Control.VERTICAL_ALIGNMENT_TOP;
    scoreText.left = -20;
    scoreText.top = 20;
    advancedTexture.addControl(scoreText);

    // Update UI
    this.scene.onBeforeRenderObservable.add(() => {
      healthText.text = `Health: ${this.health}`;
      ammoText.text = `Ammo: ${this.ammo}`;
      scoreText.text = `Score: ${this.score}`;
    });
  }

  private shoot() {
    if (this.ammo <= 0) return;

    this.ammo--;

    // Create ray from camera
    const ray = this.camera.getForwardRay();
    const hit = this.scene.pickWithRay(ray!);

    if (hit?.pickedMesh && this.enemies.includes(hit.pickedMesh as Mesh)) {
      // Hit enemy
      const enemy = hit.pickedMesh as Mesh;
      this.killEnemy(enemy);

      // Spawn particle effect
      this.createHitEffect(hit.pickedPoint!);
    }

    // Muzzle flash effect
    this.createMuzzleFlash();
  }

  private killEnemy(enemy: Mesh) {
    enemy.dispose();
    this.enemies = this.enemies.filter(e => e !== enemy);
    this.score += 100;

    // Spawn new enemy
    const newEnemy = this.createEnemy(
      new Vector3(
        Math.random() * 60 - 30,
        1,
        Math.random() * 60 - 30
      )
    );
    this.enemies.push(newEnemy);
  }

  private createHitEffect(position: Vector3) {
    const particleSystem = new ParticleSystem('particles', 2000, this.scene);
    particleSystem.particleTexture = new Texture('assets/flare.png', this.scene);
    particleSystem.emitter = position;
    particleSystem.minEmitBox = new Vector3(-0.1, -0.1, -0.1);
    particleSystem.maxEmitBox = new Vector3(0.1, 0.1, 0.1);
    particleSystem.color1 = new Color4(1, 0, 0, 1);
    particleSystem.color2 = new Color4(1, 0.5, 0, 1);
    particleSystem.minSize = 0.1;
    particleSystem.maxSize = 0.3;
    particleSystem.minLifeTime = 0.2;
    particleSystem.maxLifeTime = 0.5;
    particleSystem.emitRate = 1000;
    particleSystem.blendMode = ParticleSystem.BLENDMODE_ONEONE;
    particleSystem.gravity = new Vector3(0, -9.81, 0);
    particleSystem.direction1 = new Vector3(-1, 1, -1);
    particleSystem.direction2 = new Vector3(1, 1, 1);
    particleSystem.minAngularSpeed = 0;
    particleSystem.maxAngularSpeed = Math.PI;
    particleSystem.minEmitPower = 1;
    particleSystem.maxEmitPower = 3;
    particleSystem.updateSpeed = 0.01;

    particleSystem.start();

    setTimeout(() => {
      particleSystem.stop();
      setTimeout(() => particleSystem.dispose(), 1000);
    }, 100);
  }

  private createMuzzleFlash() {
    const flash = MeshBuilder.CreateSphere(
      'flash',
      { diameter: 0.2 },
      this.scene
    );
    flash.position = this.camera.position.add(
      this.camera.getDirection(Vector3.Forward()).scale(1)
    );

    const flashMat = new StandardMaterial('flashMat', this.scene);
    flashMat.emissiveColor = new Color3(1, 1, 0);
    flash.material = flashMat;

    setTimeout(() => flash.dispose(), 50);
  }

  private reload() {
    this.ammo = 30;
  }

  private takeDamage(amount: number) {
    this.health -= amount;

    // Flash screen red
    this.scene.clearColor = new Color4(1, 0, 0, 0.3);
    setTimeout(() => {
      this.scene.clearColor = new Color4(0.5, 0.8, 0.95, 1);
    }, 100);

    if (this.health <= 0) {
      this.gameOver();
    }
  }

  private gameOver() {
    console.log('Game Over! Final Score:', this.score);
    // Show game over screen
  }

  private startGameLoop() {
    this.engine.runRenderLoop(() => {
      this.updateMovement();
      this.scene.render();
    });

    window.addEventListener('resize', () => {
      this.engine.resize();
    });
  }

  private updateMovement() {
    const direction = Vector3.Zero();

    if (this.moveForward) direction.z += 1;
    if (this.moveBackward) direction.z -= 1;
    if (this.moveLeft) direction.x -= 1;
    if (this.moveRight) direction.x += 1;

    if (direction.length() > 0) {
      direction.normalize();

      const forward = this.camera.getDirection(Vector3.Forward());
      forward.y = 0;
      forward.normalize();

      const right = this.camera.getDirection(Vector3.Right());
      right.y = 0;
      right.normalize();

      const movement = forward.scale(direction.z).add(right.scale(direction.x));
      this.camera.position.addInPlace(movement.scale(this.movementSpeed));
    }
  }
}
```

## Claude Code Prompts

```
Create a Babylon.js 3D platformer with physics and collectibles
```

```
Build a first-person shooter in Babylon.js with raycasting and enemy AI
```

```
Implement a 3D racing game using Babylon.js with vehicle physics
```

```
Add shadow mapping and PBR materials to my Babylon.js scene
```

```
Create a particle system for explosions in Babylon.js
```

```
Implement LOD (Level of Detail) optimization in my Babylon.js game
```

## Performance Optimization

### Instancing

```typescript
const original = MeshBuilder.CreateBox('box', { size: 1 }, scene);
for (let i = 0; i < 1000; i++) {
  const instance = original.createInstance(`box${i}`);
  instance.position = new Vector3(
    Math.random() * 100,
    0,
    Math.random() * 100
  );
}
```

### Octree Optimization

```typescript
scene.createOrUpdateSelectionOctree();
```

### Texture Optimization

```typescript
texture.updateSamplingMode(Texture.NEAREST_SAMPLINGMODE);
const compressedTexture = new Texture('texture.ktx', scene);
```

## Next Steps

- Explore [Three.js Games](./three-js-games.md) for comparison
- Learn [Advanced Patterns](../09-advanced-patterns/README.md)
- Review [Performance Optimization](../10-performance-optimization/README.md)

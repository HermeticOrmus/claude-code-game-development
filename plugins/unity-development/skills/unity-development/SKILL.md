---
name: unity-development
description: "Unity 6 reference patterns: an architecture decision tree, render pipeline and Addressables migration recipes, Input System patterns, a DOTS quick reference, a common mistakes catalog, component and ScriptableObject event channel patterns, and a generic object pool. Use when designing, writing, or reviewing Unity C#."
---

# Unity development pattern library

Reference patterns for Unity 6 development. Use as lookup.

## Architecture decision tree

```
Project type: 2D? 3D? Mixed?
  Pick Render Pipeline: URP (most), HDRP (high-end), Built-in (legacy maintenance only)

Entity count at peak: < 100? 100-1000? > 1000?
  < 100: MonoBehaviour everywhere
  100-1000: MonoBehaviour with pooling
  > 1000: Consider ECS/DOTS — does team have experience?

Multiplayer?
  No: skip
  Cooperative / co-op: Netcode for GameObjects (current Unity recommendation)
  Competitive < 16 players: Netcode for GameObjects or Mirror
  Competitive 16+ players: dedicated server architecture, possibly DOTS for sim

Platform mix:
  PC only: easiest, no compromise
  PC + mobile: bake compromises in early (texture sizes, shader complexity)
  Console: budget for cert (3+ months); platform-specific work isolated to per-platform modules
  WebGL: GC pauses are devastating; profile early
```

## Render Pipeline migration recipes

### Built-in → URP

1. Install URP via Package Manager
2. Create URP Asset (right-click → Create → Rendering → URP Asset)
3. Project Settings → Graphics → Scriptable Render Pipeline Settings: drag URP Asset
4. Window → Rendering → Render Pipeline Converter (Unity 6 has automated converter)
5. Migrate custom shaders to Shader Graph or rewrite as URP-compatible HLSL
6. Verify post-processing — old PostProcessing Stack v2 replaced by URP Volume system

### Built-in → HDRP

Heavier lift. Materials rebuild, lighting re-bake, custom shaders rewritten. Allocate weeks for a small project, months for a large one.

### Custom shader patterns

```hlsl
// URP unlit shader skeleton
Shader "Custom/MyUnlit"
{
    Properties { _MainTex ("Texture", 2D) = "white" {} }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            struct Attributes { float4 positionOS : POSITION; float2 uv : TEXCOORD0; };
            struct Varyings { float4 positionHCS : SV_POSITION; float2 uv : TEXCOORD0; };
            Varyings vert(Attributes IN) {
                Varyings OUT;
                OUT.positionHCS = TransformObjectToHClip(IN.positionOS.xyz);
                OUT.uv = IN.uv;
                return OUT;
            }
            half4 frag(Varyings IN) : SV_Target { return tex2D(_MainTex, IN.uv); }
            ENDHLSL
        }
    }
}
```

## Addressables migration recipe

```csharp
// Old (Resources)
GameObject prefab = Resources.Load<GameObject>("Enemies/Drone");
GameObject instance = Instantiate(prefab);

// New (Addressables, async)
[SerializeField] private AssetReference droneRef;

private async void SpawnDrone()
{
    GameObject prefab = await droneRef.LoadAssetAsync<GameObject>().Task;
    GameObject instance = Instantiate(prefab);
    // Track instance for later Addressables.Release
}

// New (Addressables, by key)
private async void SpawnByKey()
{
    GameObject prefab = await Addressables.LoadAssetAsync<GameObject>("Drone").Task;
    GameObject instance = Instantiate(prefab);
}
```

Always pair `LoadAssetAsync` with `Release`. Without release, the asset stays in memory.

## Input System patterns

### Pattern: PlayerInput component

```csharp
[RequireComponent(typeof(PlayerInput))]
public class Player : MonoBehaviour
{
    private PlayerInput _input;
    private InputAction _move;

    private void Awake()
    {
        _input = GetComponent<PlayerInput>();
        _move = _input.actions["Move"];
    }

    private void OnEnable() { _move.performed += OnMove; }
    private void OnDisable() { _move.performed -= OnMove; }

    private void OnMove(InputAction.CallbackContext ctx) { /* ... */ }
}
```

### Pattern: InputActionAsset reference

```csharp
[SerializeField] private InputActionAsset inputActions;
private InputAction _move;

private void OnEnable()
{
    _move = inputActions.FindAction("Player/Move");
    _move.Enable();
}
```

### Pattern: Runtime rebinding

```csharp
private void StartRebinding(InputAction action, int bindingIndex)
{
    action.Disable();
    action.PerformInteractiveRebinding(bindingIndex)
        .OnComplete(operation =>
        {
            action.Enable();
            operation.Dispose();
        })
        .Start();
}
```

## DOTS / ECS quick reference

```csharp
// Define a component
public struct Velocity : IComponentData { public float3 Value; }

// Define a system
public partial struct MovementSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        float deltaTime = SystemAPI.Time.DeltaTime;
        foreach (var (transform, velocity) in SystemAPI.Query<RefRW<LocalTransform>, RefRO<Velocity>>())
        {
            transform.ValueRW.Position += velocity.ValueRO.Value * deltaTime;
        }
    }
}
```

DOTS pays off when:
- 1000+ entities updating per frame
- Burst-compiled jobs can vectorize the math
- Determinism is required

Doesn't pay off:
- < 1000 entities
- Logic is event-driven, not iterative
- Team doesn't have ECS experience

## Common mistakes catalog

### "Performance tanked when I added many enemies"

Profile first. Common culprits:

1. **Find / FindObjectsOfType** in Update → O(n) per call per frame
2. **Instantiate / Destroy without pooling** → GC pauses
3. **Many small scripts each with Update** → Update call overhead
4. **`Rigidbody.velocity = X` in Update** → use FixedUpdate
5. **Per-frame string concatenation** → allocate hell

### "Build is huge"

Check Build Report (Window → Analysis → Build Report). Common bloat:

- Resources folder containing assets that aren't used
- Textures at max-quality on mobile
- Shader variants ballooning (every #pragma multi_compile multiplies variants)
- Editor-only assets accidentally in build

### "WebGL build runs slow / has GC stutter"

WebGL specific:

- No threading (background work blocks main thread)
- GC pauses are devastating; pooling is essential
- Texture compression different per browser
- Audio constraints (no MP3 in some browsers)

### "Scene loading freezes the game"

Use async loading:

```csharp
SceneManager.LoadSceneAsync("Level2", LoadSceneMode.Single);
```

If still freezing, the assets in the scene are loading synchronously. Use Addressables with explicit load + scene activation:

```csharp
var op = Addressables.LoadSceneAsync("Level2");
op.Completed += handle => SceneManager.SetActiveScene(handle.Result.Scene);
```

### "Domain reload makes Play mode slow"

Project Settings → Editor → Enter Play Mode Options: enable, then disable "Reload Domain" and "Reload Scene." 5-10× faster Play mode iteration. Re-enable for CI builds.

### "Coroutine fires twice / never stops"

Coroutines stay active until `StopCoroutine` or the GameObject is disabled / destroyed. If you start a coroutine in `OnEnable` without storing the handle, you can't stop it.

```csharp
private Coroutine _routine;

private void OnEnable() { _routine = StartCoroutine(MyRoutine()); }
private void OnDisable() { if (_routine != null) StopCoroutine(_routine); }
```

## Project structure conventions

```
Assets/
├── Scripts/           # All C# scripts
├── Scenes/            # .unity files
├── Prefabs/           # Reusable GameObjects
├── Materials/         # Materials + shaders
├── Textures/          # Source textures
├── Models/            # 3D models (.fbx, .obj)
├── Audio/             # Audio clips
├── ScriptableObjects/ # Data assets (configs, item defs)
├── Addressables/      # Addressable groups (or just mark assets)
└── Editor/            # Editor-only scripts (custom Inspectors, tools)

Packages/
└── manifest.json      # Package dependencies
```

## MonoBehaviour Component Pattern

```csharp
// Well-structured MonoBehaviour: serialized fields, cached references, event lifecycle
using UnityEngine;

[RequireComponent(typeof(Rigidbody), typeof(Collider))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float _moveSpeed = 6f;
    [SerializeField] private float _jumpForce = 8f;

    [Header("Ground Check")]
    [SerializeField] private LayerMask _groundMask;
    [SerializeField] private Transform _groundCheck;
    [SerializeField] private float _groundCheckRadius = 0.2f;

    // Cached component references - filled in Awake, never in Update
    private Rigidbody _rb;
    private bool _isGrounded;
    private Vector2 _moveInput;

    private void Awake()
    {
        _rb = GetComponent<Rigidbody>();
    }

    private void OnEnable()
    {
        // Subscribe to input or events here
    }

    private void OnDisable()
    {
        // Unsubscribe here - prevents memory leaks
    }

    private void Update()
    {
        _moveInput = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"));
        _isGrounded = Physics.CheckSphere(_groundCheck.position, _groundCheckRadius, _groundMask);

        if (_isGrounded && Input.GetButtonDown("Jump"))
        {
            _rb.AddForce(Vector3.up * _jumpForce, ForceMode.Impulse);
        }
    }

    private void FixedUpdate()
    {
        // Physics forces go in FixedUpdate
        Vector3 move = transform.right * _moveInput.x + transform.forward * _moveInput.y;
        _rb.MovePosition(_rb.position + move * _moveSpeed * Time.fixedDeltaTime);
    }
}
```

## ScriptableObject Event Channel

```csharp
// Decoupled event system using ScriptableObject channels (Ryan Hipple pattern)
using System;
using UnityEngine;

[CreateAssetMenu(menuName = "Events/Game Event")]
public class GameEventSO : ScriptableObject
{
    private Action _listeners;

    public void Raise()
    {
        _listeners?.Invoke();
    }

    public void Subscribe(Action listener) => _listeners += listener;
    public void Unsubscribe(Action listener) => _listeners -= listener;
}

// Generic version for typed events
[CreateAssetMenu(menuName = "Events/Float Event")]
public class FloatEventSO : ScriptableObject
{
    private Action<float> _listeners;

    public void Raise(float value) => _listeners?.Invoke(value);
    public void Subscribe(Action<float> l) => _listeners += l;
    public void Unsubscribe(Action<float> l) => _listeners -= l;
}

// Usage: MonoBehaviour subscribes/unsubscribes via lifecycle
public class HealthDisplay : MonoBehaviour
{
    [SerializeField] private FloatEventSO _healthChangedEvent;

    private void OnEnable() => _healthChangedEvent.Subscribe(OnHealthChanged);
    private void OnDisable() => _healthChangedEvent.Unsubscribe(OnHealthChanged);

    private void OnHealthChanged(float newHealth)
    {
        // Update UI
    }
}
```

## ScriptableObject Item Database

```csharp
using UnityEngine;

[CreateAssetMenu(menuName = "Items/Item Definition")]
public class ItemDefinitionSO : ScriptableObject
{
    [field: SerializeField] public string ItemId { get; private set; }
    [field: SerializeField] public string DisplayName { get; private set; }
    [field: SerializeField] public Sprite Icon { get; private set; }
    [field: SerializeField] public ItemType Type { get; private set; }
    [field: SerializeField, Range(0, 999)] public int MaxStack { get; private set; } = 1;

    [TextArea(2, 4)]
    [SerializeField] private string _description;
    public string Description => _description;
}

public enum ItemType { Weapon, Armor, Consumable, Quest, Misc }

// Database asset holds all items - no scene dependency
[CreateAssetMenu(menuName = "Items/Item Database")]
public class ItemDatabaseSO : ScriptableObject
{
    [SerializeField] private ItemDefinitionSO[] _items;

    private System.Collections.Generic.Dictionary<string, ItemDefinitionSO> _lookup;

    private void OnEnable()
    {
        _lookup = new();
        foreach (var item in _items)
            if (item != null)
                _lookup[item.ItemId] = item;
    }

    public ItemDefinitionSO GetItem(string id) =>
        _lookup.TryGetValue(id, out var item) ? item : null;
}
```

## New Input System Integration

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class InputHandler : MonoBehaviour
{
    // Cached hash values - avoids string lookup per call
    private static readonly int SpeedHash = Animator.StringToHash("Speed");
    private static readonly int JumpHash = Animator.StringToHash("Jump");

    [SerializeField] private Animator _animator;

    private PlayerInputActions _inputActions;
    private Vector2 _moveInput;

    private void Awake()
    {
        _inputActions = new PlayerInputActions();
    }

    private void OnEnable()
    {
        _inputActions.Player.Enable();
        _inputActions.Player.Jump.performed += OnJump;
    }

    private void OnDisable()
    {
        _inputActions.Player.Jump.performed -= OnJump;
        _inputActions.Player.Disable();
    }

    private void Update()
    {
        _moveInput = _inputActions.Player.Move.ReadValue<Vector2>();
        _animator.SetFloat(SpeedHash, _moveInput.magnitude);
    }

    private void OnJump(InputAction.CallbackContext ctx)
    {
        _animator.SetTrigger(JumpHash);
    }
}
```

## Object Pool (Generic)

```csharp
using System.Collections.Generic;
using UnityEngine;

public class ObjectPool<T> where T : Component
{
    private readonly T _prefab;
    private readonly Transform _parent;
    private readonly Queue<T> _pool = new();

    public ObjectPool(T prefab, Transform parent, int initialSize = 10)
    {
        _prefab = prefab;
        _parent = parent;
        for (int i = 0; i < initialSize; i++)
            _pool.Enqueue(CreateNew());
    }

    public T Get(Vector3 position, Quaternion rotation)
    {
        T instance = _pool.Count > 0 ? _pool.Dequeue() : CreateNew();
        instance.transform.SetPositionAndRotation(position, rotation);
        instance.gameObject.SetActive(true);
        return instance;
    }

    public void Return(T instance)
    {
        instance.gameObject.SetActive(false);
        _pool.Enqueue(instance);
    }

    private T CreateNew()
    {
        T obj = Object.Instantiate(_prefab, _parent);
        obj.gameObject.SetActive(false);
        return obj;
    }
}

// Usage:
// private ObjectPool<Bullet> _bulletPool;
// void Awake() => _bulletPool = new ObjectPool<Bullet>(_bulletPrefab, transform, 20);
// void Fire() => _bulletPool.Get(muzzle.position, muzzle.rotation);
// (Bullet calls _bulletPool.Return(this) on OnDisable)
```

## Anti-Patterns

- **`GetComponent` in `Update()`**: Allocates and searches every frame. Cache in `Awake()` with `_rb = GetComponent<Rigidbody>()`.
- **`FindObjectOfType` in `Update()` or `Start()`**: Scene-wide search on every call. Use dependency injection via `[SerializeField]` or a service locator.
- **Direct scene references between unrelated systems**: Creates coupling that breaks on scene change. Use ScriptableObject event channels or an EventBus singleton.
- **Physics in `Update()`**: Force application in `Update` is framerate-dependent. Physics always goes in `FixedUpdate`.
- **LINQ in hot path**: `enemies.Where(e => e.IsAlive).ToList()` allocates a new list every call. Use manual loops or pre-allocated `List<T>` with `Clear()` + add.
- **`public` fields for inspector exposure**: Exposes fields to all code. Use `[SerializeField] private` instead; same inspector visibility, better encapsulation.

## Cross-references

- See `docs/08-game-engines/` for cross-engine comparison
- See `docs/09-advanced-patterns/` for ECS, data-oriented design patterns
- See `docs/10-performance-optimization/` for profiling and Unity Profiler patterns
- See `docs/12-deployment-distribution/` for build pipeline + platform-specific deployment

---
name: level-design-patterns
description: "Level construction patterns: Godot TileMap configuration, NavigationRegion3D bake parameters, background-loaded level streaming, zone trigger volumes, a CSG greybox-to-final-art pipeline, and modular kit alignment checks. Use when building levels in code or setting up level tooling."
---

# Level Design Patterns

## Godot TileMap Configuration

```gdscript
# TileMap setup and painting at runtime
class_name LevelTileMap extends TileMap

const LAYER_GROUND: int = 0
const LAYER_DECOR: int = 1
const SOURCE_ID: int = 0  # TileSet source index

func paint_tile(pos: Vector2i, atlas_x: int, atlas_y: int, layer: int = LAYER_GROUND) -> void:
    set_cell(layer, pos, SOURCE_ID, Vector2i(atlas_x, atlas_y))

func clear_tile(pos: Vector2i, layer: int = LAYER_GROUND) -> void:
    erase_cell(layer, pos)

func get_terrain_type(pos: Vector2i) -> StringName:
    var tile_data: TileData = get_cell_tile_data(LAYER_GROUND, pos)
    if tile_data:
        return tile_data.get_custom_data(&"terrain_type") as StringName
    return &""

# Terrain autotile: paint using terrain set instead of individual atlas coords
func paint_terrain_region(positions: Array[Vector2i], terrain_set: int, terrain: int) -> void:
    set_cells_terrain_connect(LAYER_GROUND, positions, terrain_set, terrain)
```

## NavigationRegion3D Baking Parameters

```gdscript
# Configure NavMesh baking for specific agent types
@tool
class_name NavMeshConfigurator extends EditorScript

func configure_for_humanoid(nav_region: NavigationRegion3D) -> void:
    var mesh := NavigationMesh.new()
    # Agent dimensions
    mesh.agent_radius = 0.5         # Half character width
    mesh.agent_height = 1.8         # Character height
    mesh.agent_max_climb = 0.35     # Step height (stair riser)
    mesh.agent_max_slope = 45.0     # Max walkable slope degrees
    # Mesh generation precision
    mesh.cell_size = 0.25           # Smaller = more precise, slower bake
    mesh.cell_height = 0.1
    # Filtering
    mesh.filter_low_hanging_obstacles = true
    mesh.filter_ledge_spans = true
    mesh.filter_walkable_low_height_spans = true
    nav_region.navigation_mesh = mesh

func bake_async(nav_region: NavigationRegion3D) -> void:
    # Bake on background thread to avoid frame hitches
    nav_region.bake_navigation_mesh(true)  # true = on_thread
```

## Level Streaming with Background Loading

```gdscript
class_name LevelStreamer extends Node
signal zone_loaded(zone_name: StringName)
signal zone_unloaded(zone_name: StringName)

var _loaded_zones: Dictionary = {}  # zone_name -> Node
var _loading_requests: Dictionary = {}  # zone_name -> path

func request_zone_load(zone_name: StringName, scene_path: String) -> void:
    if zone_name in _loaded_zones or zone_name in _loading_requests:
        return
    _loading_requests[zone_name] = scene_path
    ResourceLoader.load_threaded_request(scene_path)

func _process(_delta: float) -> void:
    for zone_name in _loading_requests.keys():
        var path: String = _loading_requests[zone_name]
        var status := ResourceLoader.load_threaded_get_status(path)
        match status:
            ResourceLoader.THREAD_LOAD_LOADED:
                var scene: PackedScene = ResourceLoader.load_threaded_get(path)
                _activate_zone(zone_name, scene)
                _loading_requests.erase(zone_name)
            ResourceLoader.THREAD_LOAD_FAILED:
                push_error("Failed to load zone: %s" % path)
                _loading_requests.erase(zone_name)

func _activate_zone(zone_name: StringName, scene: PackedScene) -> void:
    var instance := scene.instantiate()
    instance.name = zone_name
    get_tree().root.add_child(instance)
    _loaded_zones[zone_name] = instance
    zone_loaded.emit(zone_name)

func unload_zone(zone_name: StringName) -> void:
    if zone_name not in _loaded_zones:
        return
    _loaded_zones[zone_name].queue_free()
    _loaded_zones.erase(zone_name)
    zone_unloaded.emit(zone_name)
```

## Zone Trigger Volumes

```gdscript
# Area3D trigger that loads next zone on player enter
class_name ZoneTrigger extends Area3D
@export var zone_to_load: String
@export var zone_to_unload: String
@export var preload_distance: float = 30.0  # meters before trigger

@onready var streamer: LevelStreamer = get_node("/root/LevelStreamer")

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    # Visual range pre-trigger: start loading before player arrives
    monitoring = true

func _on_body_entered(body: Node3D) -> void:
    if body.is_in_group(&"player"):
        if zone_to_load and not zone_to_load.is_empty():
            streamer.request_zone_load(zone_to_load as StringName, "res://levels/%s.tscn" % zone_to_load)
        if zone_to_unload and not zone_to_unload.is_empty():
            # Delay unload to prevent pop-in during transition
            get_tree().create_timer(2.0).timeout.connect(
                func(): streamer.unload_zone(zone_to_unload as StringName)
            )
```

## Greybox to Final Art Pipeline (CSG Nodes)

```gdscript
# @tool script: replace CSG greybox with final modular pieces
@tool
class_name GreyboxReplacer extends EditorScript

# In editor, select CSGBox3D nodes and run this to measure for kit piece placement
func measure_csg_for_kit(csg: CSGBox3D) -> Dictionary:
    return {
        "position": csg.global_position,
        "size": csg.size,
        "rotation": csg.rotation,
        # Output: designer places kit piece matching these dimensions
    }

# CSG usage for greybox (do NOT use CSG in final build - poor performance)
# res://levels/greybox/
#   csg_corridor_ns.tscn  - North-South corridor
#   csg_room_small.tscn   - Small room
#   csg_room_large.tscn   - Large room
```

## Modular Kit Alignment Check

```gdscript
# Validates kit pieces snap to grid
@tool
class_name KitGridValidator extends EditorScript
const GRID_SIZE: float = 4.0  # 4m grid

func validate_grid_alignment(node: Node3D) -> bool:
    var pos := node.global_position
    var snapped := pos.snapped(Vector3.ONE * GRID_SIZE)
    var offset := (pos - snapped).length()
    if offset > 0.01:
        push_warning("%s is %.3f off grid at %s" % [node.name, offset, pos])
        return false
    return true

func snap_to_grid(node: Node3D) -> void:
    node.global_position = node.global_position.snapped(Vector3.ONE * GRID_SIZE)
```

## Anti-Patterns

- **Art before greybox confirmation**: Never add final art to a space that hasn't passed a playtest greybox. Art makes it harder to see spatial problems.
- **NavMesh too coarse**: cell_size > 0.5 means NavMesh misses narrow passages. Set cell_size = agent_radius * 0.5.
- **Tile physics gaps at seams**: Edge physics between tiles creates gaps where characters can catch. Use composite collider (Godot: enable use_parent on CollisionShape2D layer) or check tile physics polygon extends to tile boundary.
- **Using CSG in final build**: CSG nodes are not performance-optimized for rendering. Convert to MeshInstance3D before shipping.
- **Single-path levels**: Memorable levels have multiple routes; single corridor = no player agency and no replayability.

# aic_assets

The `aic_assets` package contains the **3D mesh models and SDF descriptions** for all physical objects in the AI for Industry Challenge simulation environment, including robot hardware, cables, connectors, ports, and the workspace enclosure.

---

## Overview

These assets are referenced by `aic_description` URDF/SDF files and the Gazebo simulation world. Each model includes a visual mesh (`.glb` or `.stl`), an SDF physics description (`model.sdf`), a model metadata file (`model.config`), and optionally a Xacro macro (`*_macro.xacro`) for inclusion in URDF robot descriptions.

---

## Asset Catalog

### Robot Hardware

| Model | Description |
|-------|-------------|
| `Robotiq Hand-E` | Parallel-jaw gripper attached to the robot wrist. |
| `Axia80 M20` | ATI Axia80-M20 6-axis force/torque sensor. |
| `Basler Camera` | Wrist-mounted camera (×3 on the robot). |
| `Camera Mount` | Bracket for mounting the cameras to the robot. |

### Cables

| Model | Description |
|-------|-------------|
| `lc_cable` | LC fiber optic cable. |
| `sc_cable` | SC fiber optic cable. |
| `lc_sc_cable` | Combined LC-to-SC cable. |
| `sfp_sc_cable` | SFP-to-SC cable. |
| `sfp_sc_cable_reversed` | SFP-to-SC cable (reversed orientation). |
| `cable_base_c_rotated` | Cable base variant (rotated). |
| `cable_base_c_rotated_reversed` | Cable base variant (rotated, reversed). |

### Plugs and Ports

| Model | Description |
|-------|-------------|
| `LC Plug` | LC fiber optic plug/connector. |
| `SC Plug` | SC fiber optic plug/connector. |
| `LC Mount` | Mounting point for LC plug. |
| `SC Mount` | Mounting point for SC plug. |
| `SC Port` | SC fiber optic port (target for insertion). |
| `SFP Mount` | Mounting point for SFP module. |
| `SFP Module` | Small Form-factor Pluggable transceiver module. |

### Task Board Components

| Model | Description |
|-------|-------------|
| `Task Board Base` | Base plate of the task board. |
| `NIC Card` | Network Interface Card with fiber ports. |
| `NIC Card Mount` | Bracket for mounting the NIC card. |

### Environment

| Model | Description |
|-------|-------------|
| `Enclosure` | Workspace enclosure walls and frame. |
| `Enclosure Walls` | Individual enclosure wall panels. |
| `Floor` | Floor and background walls of the scene. |

---

## Package Layout

```
aic_assets/
├── models/
│   ├── <ModelName>/
│   │   ├── model.sdf           # Physics and visual description
│   │   ├── model.config        # Model metadata (name, description, author)
│   │   ├── *_visual.glb        # 3D mesh for rendering
│   │   └── *_macro.xacro       # Xacro macro for URDF inclusion (where applicable)
│   └── ...
├── scripts/
│   └── cable.sdf.erb           # Template script for generating cable SDF files
└── hooks/
    └── aic_assets.dsv.in       # Environment hook to set GZ_SIM_RESOURCE_PATH
```

---

## See Also

- [aic_description](../aic_description/README.md) – URDF/SDF files that reference these assets.
- [Scene Description](../docs/scene_description.md) – Overview of the full simulation scene.
- [Task Board Description](../docs/task_board_description.md) – Physical layout and dimensions of the task board.

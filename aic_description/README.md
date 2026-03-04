# aic_description

The `aic_description` package contains the **URDF/SDF robot and world descriptions** for the AI for Industry Challenge simulation environment. These files define the geometry, kinematics, and sensor configuration of the UR robot arm, gripper, cameras, and the task workspace.

---

## Overview

The description files are consumed by the simulation (Gazebo) and the robot state publisher. They define:

- The **UR robot arm** with a Robotiq Hand-E gripper and ATI Axia80-M20 force/torque sensor.
- **Three wrist-mounted Basler cameras** for visual observation.
- The **task board** with NIC card and cable ports.
- The **simulation world** (`aic.sdf`) including lighting, floor, and enclosure walls.

---

## Package Layout

```
aic_description/
├── urdf/
│   ├── ur_gz.urdf.xacro        # Main robot description (UR arm + gripper + sensors)
│   ├── cable.sdf.xacro         # Cable model description
│   └── task_board.urdf.xacro   # Task board description
└── world/
    └── aic.sdf                 # Gazebo simulation world
```

---

## Robot Hardware

| Component | Model | Notes |
|-----------|-------|-------|
| Robot arm | Universal Robots UR (default: UR5e) | 6-DOF manipulator |
| Gripper | Robotiq Hand-E | Parallel-jaw gripper |
| Force/Torque sensor | ATI Axia80-M20 | 6-axis wrist-mounted |
| Cameras (×3) | Basler | Left, center, right wrist-mounted |

---

## See Also

- [Scene Description](../docs/scene_description.md) – Detailed description of the simulation environment.
- [Task Board Description](../docs/task_board_description.md) – Physical layout and port specifications.
- [aic_assets](../aic_assets/README.md) – 3D mesh and SDF model files used by this description.
- [aic_bringup](../aic_bringup/README.md) – Launch files that load these descriptions into Gazebo.

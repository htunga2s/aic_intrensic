# aic_gazebo

The `aic_gazebo` package provides **Gazebo Sim (gz-sim) plugins** that implement the simulation-specific behavior for the AI for Industry Challenge, including cable physics, off-limit contact detection, scoring, joint resets, and world generation.

---

## Overview

These plugins are loaded by the Gazebo simulation world to add challenge-specific behavior that is not available in standard Gazebo. They communicate with the broader ROS 2 system via `gz-transport` and ROS 2 topics/services.

---

## Plugins

### `CablePlugin`

Manages the lifecycle and physics of the flexible cable model in the simulation:

- Initializes the cable in a "harnessed" (static) state before the task begins.
- Attaches the cable to the robot gripper when grasped.
- Detects when the cable plug is successfully inserted into a port.
- Publishes cable state updates to the scoring and engine components.

### `ScoringPlugin`

Monitors the cable insertion outcome and computes contact-based scoring data:

- Tracks contact between the cable plug and the target port.
- Detects collisions with off-limit surfaces.
- Publishes scoring results via the `scoring.proto` protobuf format.

### `OffLimitContactsPlugin`

Detects collisions between the robot or cable and surfaces that are designated as off-limits (e.g., enclosure walls, electronic components). Penalties are applied by the scoring system when off-limit contacts occur.

### `ResetJointsPlugin`

Provides a Gazebo service to reset the robot's joints to a home configuration. Used by `aic_engine` to reset the robot between trials.

### `WorldSdfGeneratorPlugin`

Dynamically generates the Gazebo world SDF at runtime based on the trial configuration, allowing `aic_engine` to specify which cables, ports, and task-board configurations should be present in each trial.

---

## Package Layout

```
aic_gazebo/
├── include/aic_gazebo/
│   └── ScoringPlugin.hh
├── src/
│   ├── CablePlugin.{hh,cc}
│   ├── OffLimitContactsPlugin.{hh,cc}
│   ├── ResetJointsPlugin.{hh,cc}
│   ├── ScoringPlugin.cc
│   └── WorldSdfGeneratorPlugin.{hh,cc}
├── proto/
│   └── scoring.proto              # Protobuf schema for scoring messages
└── hooks/
    └── aic_gazebo.{sh,dsv}.in    # Environment hooks
```

---

## See Also

- [aic_bringup](../aic_bringup/README.md) – Launch files that start the Gazebo simulation with these plugins.
- [aic_description](../aic_description/README.md) – World and robot SDF/URDF files consumed by Gazebo.
- [aic_scoring](../aic_scoring/README.md) – Higher-level scoring logic that consumes data from `ScoringPlugin`.
- [Scene Description](../docs/scene_description.md) – Overview of the simulation environment.

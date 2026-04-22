# aic_model

The `aic_model` package provides the **participant-facing policy framework** for the AI for Industry Challenge. It implements a ROS 2 Lifecycle node that dynamically loads and executes a Python policy class at runtime, handling all ROS 2 boilerplate so participants can focus on writing their cable-insertion logic.

> **This is the primary package you need to understand and work with as a challenge participant.**

For the full integration guide, see [Policy Integration Guide](../docs/policy.md).

---

## Overview

`aic_model` is a ROS 2 [Lifecycle node](https://design.ros2.org/articles/node_lifecycle.html) named `aic_model` that:

1. Loads a participant-supplied Python policy class at startup via the `policy` ROS parameter.
2. Subscribes to `/observations` to receive fused sensor data from `aic_adapter`.
3. Exposes the `/insert_cable` action server that `aic_engine` calls to start a task.
4. Forwards motion commands from the policy to `/aic_controller/pose_commands` (Cartesian) or `/aic_controller/joint_commands` (joint-space).
5. Provides a `/cancel_task` service to abort an in-progress insertion.

---

## Package Layout

```
aic_model/
├── aic_model/
│   ├── aic_model.py   # AicModel Lifecycle node implementation
│   └── policy.py      # Abstract Policy base class for participants
└── test/
    ├── cancel_task.py
    ├── create_and_cancel_task.py
    └── cycle_through_lifecycle.py
```

---

## Writing Your Policy

Derive from the abstract `Policy` class in `aic_model.policy` and implement the `insert_cable()` method:

```python
from aic_model.policy import Policy

class MyPolicy(Policy):
    def insert_cable(self, task, get_observation, move_robot, send_feedback) -> bool:
        # task            – aic_task_interfaces/Task describing the cable to insert
        # get_observation – callable returning the latest Observation message
        # move_robot      – callable to send motion commands to the controller
        # send_feedback   – callable to report progress strings back to aic_engine
        ...
        return True  # True = success, False = failure
```

### Useful helpers inherited from `Policy`

| Method | Description |
|--------|-------------|
| `set_pose_target(move_robot, pose, frame_id)` | Send a Cartesian pose target with sensible default impedance parameters. |
| `sleep_for(duration_sec)` | Sim-time-aware sleep. |
| `time_now()` | Returns current clock time (sim-time aware). |
| `get_logger()` | ROS 2 logger. |

---

## Running the Node

```bash
ros2 run aic_model aic_model \
  --ros-args \
  -p use_sim_time:=true \
  -p policy:=my_package.MyPolicy
```

The `policy` parameter is a fully-qualified Python module path. The class name must match the last component of the module path (e.g., `my_package.MyPolicy` → class `MyPolicy`).

---

## ROS 2 Interfaces

### Published Topics

| Topic | Message Type | Description |
|-------|-------------|-------------|
| `/aic_controller/pose_commands` | `aic_control_interfaces/MotionUpdate` | Cartesian pose/velocity commands. |
| `/aic_controller/joint_commands` | `aic_control_interfaces/JointMotionUpdate` | Joint-space commands. |

### Subscribed Topics

| Topic | Message Type | Description |
|-------|-------------|-------------|
| `/observations` | `aic_model_interfaces/Observation` | Fused sensor data at 20 Hz. |

### Action Server

| Name | Action Type | Description |
|------|------------|-------------|
| `/insert_cable` | `aic_task_interfaces/InsertCable` | Called by `aic_engine` to start a cable insertion task. |

### Service Server

| Name | Service Type | Description |
|------|-------------|-------------|
| `/cancel_task` | `std_srvs/Empty` | Aborts the currently active insertion task. |

### Service Client

| Name | Service Type | Description |
|------|-------------|-------------|
| `/aic_controller/change_target_mode` | `aic_control_interfaces/ChangeTargetMode` | Switches the controller between Cartesian and joint-space mode. |

---

## See Also

- [Policy Integration Guide](../docs/policy.md) – Full tutorial with examples.
- [AIC Interfaces](../docs/aic_interfaces.md) – All available ROS topics, services, and actions.
- [aic_example_policies](../aic_example_policies/README.md) – Ready-to-run reference implementations.
- [Challenge Rules](../docs/challenge_rules.md) – Required lifecycle and interface compliance.

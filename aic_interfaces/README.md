# aic_interfaces

The `aic_interfaces` package group contains all **custom ROS 2 message, service, and action definitions** used in the AI for Industry Challenge. These interfaces define the communication contracts between the evaluation infrastructure and participant models.

For a full description of how these interfaces are used, see [AIC Interfaces](../docs/aic_interfaces.md).

---

## Sub-packages

```
aic_interfaces/
├── aic_control_interfaces/    # Controller commands and state
├── aic_engine_interfaces/     # Engine services (e.g., joint reset)
├── aic_model_interfaces/      # Observation message consumed by policies
└── aic_task_interfaces/       # Task definition and InsertCable action
```

---

## `aic_control_interfaces`

Interfaces for sending motion commands to and receiving state from `aic_controller`.

| Definition | Type | Description |
|------------|------|-------------|
| `MotionUpdate.msg` | Message | Cartesian pose/velocity target with impedance parameters. |
| `JointMotionUpdate.msg` | Message | Joint-space target with stiffness/damping per joint. |
| `ControllerState.msg` | Message | Current TCP pose, velocity, reference pose, and tracking error. |
| `TargetMode.msg` | Message | Enum: `MODE_UNSPECIFIED`, `MODE_CARTESIAN`, `MODE_JOINT`. |
| `TrajectoryGenerationMode.msg` | Message | Enum: position or velocity trajectory generation mode. |
| `ChangeTargetMode.srv` | Service | Switch `aic_controller` between Cartesian and joint modes. |

---

## `aic_engine_interfaces`

Interfaces used by `aic_engine` to manage the simulation and robot state.

| Definition | Type | Description |
|------------|------|-------------|
| `ResetJoints.srv` | Service | Reset the robot's joints to specified initial positions. |

---

## `aic_model_interfaces`

Interfaces for the fused sensor observation delivered to participant policies.

| Definition | Type | Description |
|------------|------|-------------|
| `Observation.msg` | Message | Snapshot of all sensors: 3 camera images + camera infos, wrist wrench, joint states, and controller state. |

---

## `aic_task_interfaces`

Interfaces for task definition and execution.

| Definition | Type | Description |
|------------|------|-------------|
| `Task.msg` | Message | Describes the cable insertion task: cable type/name, plug type/name, port type/name, target module, and time limit. |
| `InsertCable.action` | Action | Action called by `aic_engine` to request a cable insertion. Goal contains a `Task`, result contains `success` and `message`, feedback contains a progress `message`. |

---

## Key Message: `Observation.msg`

```
sensor_msgs/Image left_image
sensor_msgs/CameraInfo left_camera_info
sensor_msgs/Image center_image
sensor_msgs/CameraInfo center_camera_info
sensor_msgs/Image right_image
sensor_msgs/CameraInfo right_camera_info
geometry_msgs/WrenchStamped wrist_wrench
sensor_msgs/JointState joint_states
aic_control_interfaces/ControllerState controller_state
```

---

## See Also

- [AIC Interfaces Documentation](../docs/aic_interfaces.md) – Detailed topic/service/action reference including standard ROS interfaces.
- [Policy Integration Guide](../docs/policy.md) – How to use these interfaces in your policy.
- [aic_model](../aic_model/README.md) – The node that exposes the `InsertCable` action server.
- [aic_controller](../aic_controller/README.md) – The node that consumes `MotionUpdate` and `JointMotionUpdate`.

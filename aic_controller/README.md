# aic_controller

The `aic_controller` package is a ROS 2 controller plugin that **bridges high-level motion commands from a participant policy to low-level robot joint torques** at approximately 500 Hz, with built-in safety checks, trajectory smoothing, and impedance control.

For the full technical documentation, see [AIC Controller](../docs/aic_controller.md).

---

## Overview

`aic_controller` receives target commands (Cartesian or joint-space) from the participant's `aic_model` node at ~10–30 Hz and converts them into smooth, safe joint torques that are sent to the robot hardware at ~500 Hz.

### Control Pipeline

```
Policy (10–30 Hz)
       │
       ▼
  Command Clamping   ← safety bounds
       │
       ▼
  Command Interpolation   ← trajectory smoothing
       │
       ▼
  Impedance Control   ← Cartesian or joint impedance
       │
       ▼
  Gravity Compensation
       │
       ▼
  Robot Hardware (~500 Hz)
```

### Control Modes

| Mode | Input Topic | Description |
|------|------------|-------------|
| **Cartesian** | `/aic_controller/pose_commands` | End-effector pose/velocity target with stiffness/damping matrices. |
| **Joint** | `/aic_controller/joint_commands` | Per-joint position/velocity targets with stiffness/damping. |

Switch between modes at runtime using the `/aic_controller/change_target_mode` service.

---

## Package Layout

```
aic_controller/
├── include/aic_controller/
│   └── (controller headers and action implementations)
└── src/
    └── (controller source files)
```

---

## ROS 2 Interfaces

### Subscribed Topics

| Topic | Message Type | Description |
|-------|-------------|-------------|
| `/aic_controller/pose_commands` | `aic_control_interfaces/MotionUpdate` | Cartesian pose/velocity commands. |
| `/aic_controller/joint_commands` | `aic_control_interfaces/JointMotionUpdate` | Joint-space commands. |

### Published Topics

| Topic | Message Type | Description |
|-------|-------------|-------------|
| `/aic_controller/controller_state` | `aic_control_interfaces/ControllerState` | Current TCP pose, velocity, and tracking error. |

### Service Server

| Name | Service Type | Description |
|------|-------------|-------------|
| `/aic_controller/change_target_mode` | `aic_control_interfaces/ChangeTargetMode` | Switches between Cartesian and joint-space modes. |

---

## Configuration

Controller parameters are configured in [`aic_bringup/config/aic_ros2_controllers.yaml`](../aic_bringup/config/aic_ros2_controllers.yaml).

---

## See Also

- [AIC Controller Documentation](../docs/aic_controller.md) – Architecture, impedance control equations, and configuration details.
- [AIC Interfaces](../docs/aic_interfaces.md) – Full topic and message reference.
- [`aic_control_interfaces/MotionUpdate.msg`](../aic_interfaces/aic_control_interfaces/msg/MotionUpdate.msg) – Cartesian command message definition.
- [`aic_control_interfaces/JointMotionUpdate.msg`](../aic_interfaces/aic_control_interfaces/msg/JointMotionUpdate.msg) – Joint command message definition.

# aic_adapter

The `aic_adapter` package is a ROS 2 C++ node that **fuses time-synchronized sensor data** into a single `Observation` message and publishes it at 20 Hz for consumption by the participant's `aic_model` node.

---

## Overview

The robot provides several independent sensor streams at different rates and with different timestamps. `aic_adapter` collects the most recent readings from all streams, aligns them in time, and packages them into a single composite [`aic_model_interfaces/Observation`](../aic_interfaces/aic_model_interfaces/msg/Observation.msg) message that is published at a fixed 20 Hz rate.

### Sensor Sources

| Source | ROS Topic | Notes |
|--------|-----------|-------|
| Left wrist camera | `/left_camera/image`, `/left_camera/camera_info` | Rectified |
| Center wrist camera | `/center_camera/image`, `/center_camera/camera_info` | Rectified |
| Right wrist camera | `/right_camera/image`, `/right_camera/camera_info` | Rectified |
| Force/Torque sensor | `/fts_broadcaster/wrench` | 3D force + 3D torque at wrist |
| Joint states | `/joint_states` | Robot arm joints |
| Controller state | `/aic_controller/controller_state` | Actual/target TCP pose and velocity |
| TF tree | `/tf`, `/tf_static` | Coordinate frame transforms |

---

## Package Layout

```
aic_adapter/
├── include/aic_adapter/
│   └── aic_adapter.hpp    # AicAdapterNode class declaration
└── src/
    └── aic_adapter.cpp    # Node implementation
```

---

## Published Topics

| Topic | Message Type | Rate | Description |
|-------|-------------|------|-------------|
| `/observations` | `aic_model_interfaces/Observation` | 20 Hz | Fused sensor snapshot. |

---

## Subscribed Topics

| Topic | Message Type | Description |
|-------|-------------|-------------|
| `/left_camera/image` | `sensor_msgs/Image` | Left wrist camera image. |
| `/left_camera/camera_info` | `sensor_msgs/CameraInfo` | Left camera calibration. |
| `/center_camera/image` | `sensor_msgs/Image` | Center wrist camera image. |
| `/center_camera/camera_info` | `sensor_msgs/CameraInfo` | Center camera calibration. |
| `/right_camera/image` | `sensor_msgs/Image` | Right wrist camera image. |
| `/right_camera/camera_info` | `sensor_msgs/CameraInfo` | Right camera calibration. |
| `/fts_broadcaster/wrench` | `geometry_msgs/WrenchStamped` | Wrist force/torque. |
| `/joint_states` | `sensor_msgs/JointState` | Robot joint positions and velocities. |
| `/aic_controller/controller_state` | `aic_control_interfaces/ControllerState` | Controller TCP pose and velocity. |

---

## See Also

- [AIC Interfaces](../docs/aic_interfaces.md) – Full description of all available topics.
- [Policy Integration Guide](../docs/policy.md) – How the `Observation` message is used by participant policies.
- [`aic_model_interfaces/Observation.msg`](../aic_interfaces/aic_model_interfaces/msg/Observation.msg) – Message definition.

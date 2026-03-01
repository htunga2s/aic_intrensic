# AIC Isaac Lab Integration

This package provides documentation, scripts, and utilities for setting up AI for Industry Challenge (AIC) environment in Isaac Lab.


## Overview

[Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html) is a unified and modular framework for robot learning that aims to simplify 
common workflows in robotics research (such as reinforcement learning, learning from demonstrations, and motion planning). In collaboration with 
**NVIDIA**, this integration enables participants to:

- Perform teleoperation in AIC environment for Imitation Learning
- Use Reinforcement Learning with rsl-rl library for training policy

Optionally, you can convert Gazebo SDF worlds to Isaac Lab USD format using the **aic_converter** (see [Optional: Generating assets with aic_converter](#optional-generating-assets-with-aic_converter)); this path requires additional setup including manual tweaking of USD files and is intended for advanced use.


## Workflow


> [!TIP]
> If you run into issues that appear to be related to **Isaac Lab** (e.g. framework behavior, Docker setup, or Isaac Lab APIs), please open an issue on the [Isaac Lab GitHub repository](https://github.com/isaac-sim/IsaacLab). The maintainers there are best placed to help. For issues specific to the AIC integration or challenge assets, use this repo’s issue tracker.

**Recommended:** Use the assets prepared by the NVIDIA team. Download and place them as instructed, then start the container and run the task.

| Step | What you do | Section |
|------|-------------|---------|
| 1 | Install Docker and NVIDIA Container Toolkit | [Prerequisites](#prerequisites) |
| 2 | Clone and build Isaac Lab, then clone the AIC repo into `IsaacLab` | [Installation & Setup](#installation--setup) |
| 3 | Download the NVIDIA-prepared assets and place them in `Intrinsic_assets` | [Assets](#assets) |
| 4 | Start the Isaac Lab container and enter it | [Assets](#assets) |
| 5 | Run teleoperation or reinforcement learning from inside the container | [Usage](#usage) |

**Optional (advanced):** If you need to generate or modify the world, enclosure, or robot USDs from Gazebo SDF yourself (e.g. for custom scenes), you can use the **aic_converter**. This path requires extra setup and work, see [Optional: Generating assets with aic_converter](#optional-generating-assets-with-aic_converter).


## Prerequisites

### Docker

1. Install [Docker Engine](https://docs.docker.com/engine/install/) for your platform.
2. Complete the [Linux post-installation steps for Docker Engine](https://docs.docker.com/engine/install/linux-postinstall/) to enable managing Docker as a non-root user.

### NVIDIA Container Toolkit (Optional)

1. Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to allow Docker Engine to access your NVIDIA GPU.

2. After installation, configure Docker to use the NVIDIA runtime:
    ```bash
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
    ```


## Setup 

> [!NOTE]
> All commands in this section are to be executed on your **host machine** (not inside Docker).

> [!WARNING]
> The integration is testing with Isaac Lab version *2.3.2*.

Clone the Isaac Lab repository in your home directory:
```bash
cd ~
git clone git@github.com:isaac-sim/IsaacLab.git
```

Clone the AIC repository inside `IsaacLab` directory:
```bash
cd ~IsaacLab
git clone git@github.com:intrinsic-dev/aic.git
```

## Assets

The **NVIDIA team has prepared the assets** needed for the challenge. [Download the provided asset pack](), extract it, and place the files as follows.

Place the `Intrinsic_assets` directory inside `intrinsic_task`:

```bash
~/IsaacLab/aic/aic_utils/aic_isaac/intrinsic_aic_isaaclab/source/intrinsic_task/intrinsic_task/tasks/manager_based/intrinsic_task/
```

**Files to place there** (from the downloaded pack):
- `nic_card.usd`
- `sc_port.usd`
- `robot_cable.usd`
- `aic.usd`
- `Task_board_rigid.usd`
- `cable.usd`

If the asset pack includes world, enclosure, or robot USDs and separate placement instructions, follow those. Otherwise the prepared pack is self-contained.


## Installation

Build the `base` profile (this creates the `isaac-lab-base` Docker image):
```bash
cd ~IsaacLab
./docker/container.py build base
```

Start the container and attach shell to it (from the Isaac Lab repo):
```bash
cd ~/IsaacLab
./docker/container.py start base
./docker/container.py enter base
```

Install `intrinsic_task` in the Isaac Lab container with edit mode:
```
 python -m pip install -e aic/aic_utils/aic_isaac/intrinsic_aic_isaaclab/source/intrinsic_task
 ```


## Usage

> [!NOTE]
> The following commands are to be executed **inside the Isaac Lab container** after starting and entering it.

### Environment and Sensor Reading

### Teleoperation and Imitation Learning
To teleoperate the robot in AIC world with keyboard:
```bash
python3 scripts/teleop.py --task Intrinsic-AIC-Task-v0 --num_envs 1 --teleop_device keyboard --enable_cameras
```

> [!NOTE]
> Users will have to connect the external environment with Isaac Lab for recording teleoperated data.

Additional resources:
1. [Teleoperation using Keyboard, Spacemouse and XR]()
2. [Recording Teleoperation data]()
3. [Imitation Learning in Isaac Lab]()

### Reinforcement Learning
To run training using RL and rsl-rl library, follow these steps

#### 1. Execute the Training Script
Run the training script from your terminal using the following command:
```bash
python scripts/rsl_rl/train.py --task Intrinsic-AIC-Task-v0 --num_envs 1 --enable_cameras
```

Other Resources:
1. [Gear Assembly Task]()
2. [Creating a manager-based RL environment]()
3. [Domain Randomization]
4. Task Curation, VLA training and Policy Evaluation using Isaac Lab Arena


## Directory Structure

The integration is organized as follows:
```
├── aic_utils
│   ├── aic_isaac
│   │   ├── aic_unified_robot.urdf
│   │   ├── aic_usd_generator.sh
│   │   ├── config
│   │   │   ├── aic_enclosure.yaml
│   │   │   └── aic_world.yaml
│   │   ├── README.md
│   │   └── scripts
│   │       ├── filter_sdf.py
│   │       └── patch_usda.py
├── docker
│   ├── aic_converter
│   │   ├── Dockerfile
│   │   └── zenoh_router_config.json5
```

Organization of the **assets** directory produced by `aic_usd_generator.sh` (aic_converter):
```
└── assets
    ├── aic_enclosure.usda
    ├── aic_world.usda
    ├── aic_robot.usda
    ├── staging (intermediate files)
    │   ├── SDFs
    │   │   ├── aic_enclosure.sdf
    │   │   ├── aic_raw.sdf
    │   │   └── aic_world.sdf
    │   ├── URDFs
    │   │   └── aic_robot.urdf
    │   ├── USDAs
    │   │   ├── aic_enclosure.usda
    │   │   ├── aic_world.usda
    │   │   ├── enclosure_visual.usda
    │   │   ├── floor_visual.usda
    │   │   ├── light_visual.usda
    │   │   └── walls_visual.usda
    │   └── USDs
    │       ├── aic_enclosure.usd
    │       ├── aic_world.usd
    │       ├── config.yaml
    │       ├── enclosure_visual.usd
    │       ├── floor_visual.usd
    │       ├── light_visual.usd
    │       ├── textures
    │       │   └── clean-concrete_albedo.png
    │       └── walls_visual.usd
    └── textures
        └── clean-concrete_albedo.png
```


## Technical Details: Asset Conversion Workflow 

The USD generation process is encapsulated within a multi-stage Docker build (```docker/aic_converter/Dockerfile```) that automates 
the conversion of Gazebo assets to Isaac Lab-compatible USD files. 

### 1. Static Asset Conversion 
- **Base**: nvcr.io/nvidia/isaac-lab:2.3.2 
- **Process**: Raw .glb assets (enclosure, floor, walls, lights) are copied into the container and converted to .usd format using Isaac Lab's 
internal mesh conversion tools (convert_mesh.py). 

### 2. Scene Capture via Gazebo 
- **Base**: ros:kilted-ros-base 
- **Setup**: Installs ROS 2 Kilted, Gazebo Ionic, OpenUSD, and gz-usd.
- **Execution**: Launches the AIC Gazebo environment (aic_gz_bringup) in headless mode. A Gazebo system plugin captures the complete world state and exports it as a single SDF file (/tmp/aic.sdf).

### 3. SDF Processing and Conversion 
The exported SDF undergoes a pipeline of transformations: 
1. **Filtering**: ```filter_sdf.py``` splits the raw SDF into specific components (e.g., aic_world.sdf, aic_enclosure.sdf) based on configuration rules. 
2. **SDF to USD**: ```sdf2usd``` (from gz-usd) converts the filtered SDF files into binary USD files. 
3. **USD to USDA**: ```usdcat``` (from OpenUSD) converts binary USDs to human-readable USDA files for easier inspection and patching. 

### 4. Post-Processing 
- **Patching**: ```patch_usda.py``` injects Isaac Lab specific attributes and visual mesh fixes into the USDA files. 
- **URDF Generation**: The robot description is processed via xacro to generate a clean URDF file (aic_robot.urdf). 

The final build artifacts are staged in ```aic/aic_utils/aic_isaac/assets/``` directory and copied to the host system.

### Optional: Generating assets with aic_converter

If you want to **generate or regenerate** the world, enclosure, or robot USDs from Gazebo SDF yourself (e.g. for custom scenes or tooling), you can use the **aic_converter**. This path is **optional** and **requires additional work** (Docker build, Gazebo pipeline, etc.). Most participants should use the [NVIDIA-prepared assets](#assets) above.

The `aic_usd_generator.sh` script builds the **aic_converter** Docker image and produces an **assets** directory with:

- World: `aic_world.usda`
- Enclosure: `aic_enclosure.usda`
- Robot: `aic_robot.usda`

If you use this path:

**Output location:** `~/IsaacLab/ws_aic/src/aic/aic_utils/aic_isaac/assets`

**1. Generate the USDs** (on the host, from the AIC repo):

```bash
cd ~/IsaacLab/ws_aic/src/aic
./aic_utils/aic_isaac/aic_usd_generator.sh
```

**2. Start the Isaac Lab container** (from the Isaac Lab repo):

```bash
cd ~/IsaacLab
./docker/container.py start base
```

**3. Copy the assets into the container** (run from the Isaac Lab repo root, `~/IsaacLab`):

```bash
docker cp ws_aic/src/aic/aic_utils/aic_isaac/assets isaac-lab-base:/workspace/isaaclab
```

> [!TIP]
> If the container has a different name, run `docker ps` and use the actual container name in place of `isaac-lab-base`.

**4. Enter the container** to run teleoperation or training:

```bash
cd ~/IsaacLab
./docker/container.py enter base
```

When using the NVIDIA-prepared assets, you only need to start and enter the container; when using aic_converter, complete steps 1–4 above first.


## Future Work

Planned improvements for the workflow:
- Export USD files instead of USDA
- Add support to generate USD of Task Board


## Resources

- [Isaac Lab Documentation](https://isaac-sim.github.io/IsaacLab/main/index.html)
- [AIC Getting Started Guide](../../docs/getting_started.md)
- [AIC Scene Description](../../docs/scene_description.md)
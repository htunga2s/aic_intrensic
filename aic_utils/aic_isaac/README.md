# AIC Isaac Lab Integration

This package provides documentation, scripts, and utilities for setting up AI for Industry Challenge (AIC) environment in Isaac Lab.

## Overview

[Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html) is a unified and modular framework for robot learning that aims to simplify common workflows in robotics research (such as reinforcement learning, learning from demonstrations, and motion planning). 
n collaboration with **NVIDIA**, this integration enables participants to:

- Convert Gazebo SDF worlds to Isaac Lab USD format using `aic_converter`
- Load the AIC task board and robot from exported Gazebo worlds (`/tmp/aic.sdf`)
- Control the UR5e robot using Isaac Lab built-in teleoperation
- Leverage domain randomization 

## Quick Start

TODO: Add instructions to run Intrinsic Isaac Lab environment


## Workflow Summary

1. **Generate AIC USD Assets**: Execute `aic_utils/aic_isaac/aic_converter.sh` script to generate AIC USD files.


## Prerequisites

### Docker

1. Install [Docker Engine](https://docs.docker.com/engine/install/) for your platform.
2. Complete the [Linux post-installation steps for Docker Engine](https://docs.docker.com/engine/install/linux-postinstall/) to enable managing Docker as a non-root user.

### NVIDIA Container Toolkit (Optional)

> [!NOTE]
> This step is only required if you have an NVIDIA GPU and want to use GPU acceleration for optimal performance.

1. Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to allow Docker Engine to access your NVIDIA GPU.

2. After installation, configure Docker to use the NVIDIA runtime:
    ```bash
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
    ```


## Setup

### AIC Repo
In the home directory create ```ws_aic/src```:
```bash
mkdir -p ~/ws_aic/src
```

Clone aic repo in the ```src``` directory:
```bash
cd ~/ws_aic/src
git clone git@github.com:intrinsic-dev/aic.git -b trushant/usd_asset_generator
```


### Isaac Lab 2.3.2 
Now clone Isaac Lab the same directory level as ws_aic:
```bash
cd ~
git clone git@github.com:isaac-sim/IsaacLab.git
```

Build ```base``` profile which will create ```isaac-lab-base``` docker image:
```bash
cd IsaacLab
./docker/container.py build base
```

Start ```isaac-lab-base``` docker container:
```bash
./docker/container.py start base
```

Attach ```bash``` shell to ```isaac-lab-base``` docker container:
```bash
./docker/container.py enter base
```


## Usage

### Generate AIC USD Assets

We have provided ```aic_usd_generator.sh``` utility script which builds **aic_converter** docker and exports
**assets** directory container following USDs at location ```aic_utils/aic_isaac/assets```:
1. World USD File (```aic_world.usda```)
2. Enclosure USD File (```aic_enclosure.usda```)
3. Robot USD File (```aic_robot.usda```)

Generate the USDs utilizing following:
```bash
./aic_utils/aic_isaac/aic_usd_generator.sh
```





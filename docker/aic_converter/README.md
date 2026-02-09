# aic_converter

**aic_converter** docker image is developed for AIC asset conversion. Current support includes:
- SDF <-> USD
- URDF <-> USD

Along with this docker, a named volume is created which binds ROS2 workspace build artifacts from **ws_aic**. The fork of IsaacLab is configured to access this shared named volume which is crucial for URDF to USD conversion.


## Setup

### AIC Repo 
At user home create ```ws_aic/src```:
```bash
mkdir -p ~/ws_aic/src
```

Clone aic repo in the ```src``` directory:
```bash
cd ~/ws_aic/src
git clone git@github.com:intrinsic-dev/aic.git -b trushant/usd_asset_generator
```

Start ```converter``` docker compose service which will build ```aic_converter``` docker image:
```bash
cd aic/docker 
docker compose up converter -d
```

> [!NOTE]
> The ```compose up``` command should create ```ghcr.io/intrinsic-dev/aic/aic_conveter``` image with **aic_shared-aic** named volume. While building the docker image, ROS2 build artifacts will be copied to named volume which will be available in IsaacLab docker.

> [!TIP]
> To verfiy **aic_shared-aic** volume is present:
> ```bash
> docker volume ls
> ```

### IsaacLab 2.3.2 Fork
Now clone IsaacLab fork at the same directory level at ws_aic:
```bash
cd ~
git clone git@github.com:trushant05/IsaacLab.git
```

Build ```ros2``` profile which will create ```isaac-lab-ros2``` docker image:
```bash
cd IsaacLab
./docker/container.py build ros2
```

> [!WARNING]
> Make sure **aic_shared-aic** volume is present, else ```isaac-lab-ros2``` 
> container will fail to start. 

Start ```isaac-lab-ros2``` docker container:
```bash
./docker/container.py start ros2
```

Attach ```bash``` shell to ```isaac-lab-ros2``` docker container:
```bash
./docker/container.py enter ros2
```

> [!NOTE]
> If everything worked perfectly, you should see build artifacts at ```/workspace/ws_aic```.

## Troubleshooting

# TODO: Add this in the workflow
> [!WARNING]
> Limitations:
> 1. gz-usd can't handle complete glb conversion and losses mesh details.
> 2. Manual update for path is required when converting URDF to USD. (package:// is not reachable)


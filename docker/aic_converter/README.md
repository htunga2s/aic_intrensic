# aic_converter

**aic_converter** docker image is developed for AIC asset conversion. Current support includes:
- SDF <-> USD
- URDF <-> USD

Along with this docker, a named volume is created which binds ROS2 workspace build artifacts from **ws_aic**. The fork of IsaacLab is configured to access this shared named volume which is crucial for URDF to USD conversion.


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

Start ```converter``` docker compose service which will build ```ghcr.io/intrinsic-dev/aic/aic_converter``` docker image:
```bash
cd aic/docker 
docker compose up converter -d
```

> [!NOTE]
> The ```compose up``` command should create ```ghcr.io/intrinsic-dev/aic/aic_conveter``` image with **aic_shared-aic** named volume. While building the docker image, ROS2 build artifacts will be copied to named volume which will be available in IsaacLab docker.

> [!TIP]
> Verfiy **aic_shared-aic** volume is present:
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


## Workflows

### Scene Conversion (SDF to USD)

Following the setup instruction, we will attach a shell to **aic_converter** docker container:
```bash
docker exec -it aic_converter bash
```

Run ```generate_sdf.sh``` script which will launch gazebo world and save ```aic.sdf``` in ```/tmp``` directory which is copied into ```ws_aic```:
```bash
/generate_sdf.sh
```

Now in the ```isaac-lab-ros2``` container, you should see the ```aic.sdf``` file:
```bash
cat /workspace/ws_aic/aic.sdf
```

For converting the scene, comment out robot model:
```bash
<!--
<model name='ur5e'>
    .
    .
    .
</model>
-->
```

Now in the ```aic_converter``` docker container run sdf2usd converter:
```bash
source /ws_aic/install/setup.bash
./gz-usd/build/bin/sdf2usd aic.sdf aic_scene.usd
```

Start Isaac Sim and load the ```aic.usd``` file:
```bash
isaaclab -s
```

> [!TIP]
> - After loading the USD file in the Isaac Sim, add a dome light and increase the intensity of other lights by order of 2.
> - If the meshes are incomplete, import corresponding glb file and replace the original USD file mesh with that.



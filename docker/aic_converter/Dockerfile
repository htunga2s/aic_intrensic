FROM nvcr.io/nvidia/isaac-lab:2.3.2 AS aic_isaaclab_stage

COPY aic_assets/models/Enclosure/enclosure_visual.glb /workspace/isaaclab/artifacts/enclosure_visual.glb
COPY aic_assets/models/Enclosure/light_visual.glb /workspace/isaaclab/artifacts/light_visual.glb
COPY aic_assets/models/Floor/floor_visual.glb /workspace/isaaclab/artifacts/floor_visual.glb
COPY aic_assets/models/Floor/walls_visual.glb /workspace/isaaclab/artifacts/walls_visual.glb

RUN set -euo pipefail && \
    cd /workspace/isaaclab/artifacts && \
    for in_file in *.glb */*.glb; do \
      [ -e "$in_file" ] || continue; \
      out_file="${in_file%.glb}.usd"; \
      echo "Converting $in_file -> $out_file"; \
      /workspace/isaaclab/isaaclab.sh -p ../scripts/tools/convert_mesh.py \
        --collision-approximation none \
        --headless --device cpu \
        "$in_file" "$out_file"; \
    done && \
    rm *.glb


# --- STAGE 1: AIC Workspace build with ROS 2 Kilted (Primary) ---
FROM ros:kilted-ros-base AS aic_kilted

# Copy build artifacts from aic_isaaclab_stage
COPY --from=aic_isaaclab_stage /workspace/isaaclab/artifacts /ws_aic/assets/staging/USDs

SHELL ["/bin/bash", "-c"]

# Add `packages.osrfoundation.org` to the apt sources list:
RUN curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# Build the workspace
COPY --exclude=docker . /ws_aic/src/aic
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt upgrade -y && \
  # undeclared deps
  apt install python3-numpy && \
  cd /ws_aic/src && \
  vcs import . < /ws_aic/src/aic/aic.repos --recursive && \
  # Install Gazebo dependencies.
  apt -y install $(sort -u $(find . -iname 'packages-'`lsb_release -cs`'.apt' -o -iname 'packages.apt' | grep -v '/\.git/') | sed '/gz\|sdf/d' | tr '\n' ' ') 
  
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
  cd /ws_aic && \
  # Install ROS dependencies using rosdep.
  rosdep install --from-paths src --ignore-src --rosdistro kilted -yr --skip-keys "gz-cmake3 DART libogre-dev libogre-next-2.3-dev" && \
  source /opt/ros/kilted/setup.bash && \
  GZ_BUILD_FROM_SOURCE=1 colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release --merge-install --executor sequential

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt upgrade -y && \
  apt install libpyside2-dev \
  cmake \
  freeglut3-dev \
  libglu1-mesa-dev \
  mesa-common-dev \
  python3-opengl \
  vim -y && \
  cd /ws_aic && \
  git clone --depth 1 -b v24.08 https://github.com/PixarAnimationStudios/OpenUSD.git 

ENV USD_PATH=/ws_aic/OpenUSD
ENV PATH=$USD_PATH/bin:$PATH
ENV LD_LIBRARY_PATH=$USD_PATH/lib:$LD_LIBRARY_PATH
ENV CMAKE_PREFIX_PATH=$USD_PATH:$CMAKE_PREFIX_PATH

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
  cd /ws_aic/OpenUSD && \
  python3 build_scripts/build_usd.py --build-variant release --no-tests --no-examples --no-imaging --onetbb --no-tutorials --no-docs --no-python $USD_PATH && \
  cd /ws_aic && \
  git clone https://github.com/gazebosim/gz-usd && \
  source /ws_aic/install/setup.bash && \
  cd /ws_aic/gz-usd && \
  mkdir build && \
  cd /ws_aic/gz-usd/build && \
  export GZ_VERSION=ionic && \
  cmake .. && \
  make
 
COPY docker/aic_eval/zenoh_router_config.json5 /zenoh_router_config.json5

RUN /bin/bash -c '\
    source /ws_aic/install/setup.bash && \
    \
    # 1. Configure Zenoh
    export RMW_IMPLEMENTATION=rmw_zenoh_cpp && \
    export ZENOH_ROUTER_CONFIG_URI=/zenoh_router_config.json5 && \
    \
    # 2. Start Zenoh Router in background
    ros2 run rmw_zenoh_cpp rmw_zenohd & \
    ZENOHD_PID=$! && \
    \
    # 3. Launch with timeout to allow file generation
    # Use "timeout" to ensure the build proceeds after the file is written
    echo "Launching Gazebo to generate SDF..." && \
    source /ws_aic/install/setup.bash && \
    timeout 60s ros2 launch aic_bringup aic_gz_bringup.launch.py \
        gazebo_gui:=false \
        launch_rviz:=false || true && \
    \
    # 4. Cleanup background processes
    kill -SIGINT $ZENOHD_PID && \
    \
    # 5. Validation: Ensure the file actually exists before finishing the layer
    if [ -f /tmp/aic.sdf ]; then \
        echo "SDF successfully generated."; \
    else \
        echo "Error: /tmp/aic.sdf not found!" && exit 1; \
    fi'


RUN cat <<'EOF' > /entrypoint.sh
#!/bin/bash
set -e
source /ws_aic/install/setup.bash
exec "$@"
EOF

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]


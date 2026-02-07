FROM ros:kilted-ros-base AS build

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
  apt -y install $(sort -u $(find . -iname 'packages-'`lsb_release -cs`'.apt' -o -iname 'packages.apt' | grep -v '/\.git/') | sed '/gz\|sdf/d' | tr '\n' ' ') && \
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
  python3-opengl -y && \
  cd /ws_aic && \
  git clone --depth 1 -b v24.08 https://github.com/PixarAnimationStudios/OpenUSD.git && \
  export USD_PATH=/ws_aic/OpenUSD && \
  cd /ws_aic/OpenUSD && \
  python3 build_scripts/build_usd.py --build-variant release --no-tests --no-examples --no-imaging --onetbb --no-tutorials --no-docs --no-python $USD_PATH && \
  export PATH=$USD_PATH/bin:$PATH && \
  export LD_LIBRARY_PATH=$USD_PATH/lib:$LD_LIBRARY_PATH && \
  export CMAKE_PREFIX_PATH=$USD_PATH:$CMAKE_PREFIX_PATH && \
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

RUN cat <<'EOF' > /entrypoint.sh
#!/bin/bash
set -e
source /ws_aic/install/setup.bash
exec "$@"
EOF

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]


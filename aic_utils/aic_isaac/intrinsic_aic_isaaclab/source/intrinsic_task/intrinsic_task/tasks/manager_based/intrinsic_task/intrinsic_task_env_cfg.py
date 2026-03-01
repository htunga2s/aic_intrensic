# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import math
import os
from dataclasses import MISSING

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.envs.mdp import JointPositionActionCfg
from isaaclab.managers import ActionTermCfg as ActionTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise
from isaaclab.sensors import TiledCameraCfg

from . import mdp
from .mdp.events import randomize_object_pose

# Resolve asset directory relative to this file (portable across machines)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
INTRINSIC_ASSET_DIR = os.path.join(_THIS_DIR, "Intrinsic_assets")
INTRINSIC_SCENE_DIR = INTRINSIC_ASSET_DIR
INTRINSIC_PARTS_DIR = os.path.join(INTRINSIC_ASSET_DIR, "assets")


##
# Scene definition
##


@configclass
class IntrinsicTaskSceneCfg(InteractiveSceneCfg):
    """Scene for intrinsic task: UR5e robot, aic_scene, task_board."""

    # UR5e + gripper (fully defined here using local asset)
    robot: ArticulationCfg = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=os.path.join(INTRINSIC_ASSET_DIR, "UR5e+gripper_0217.usda"),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                max_depenetration_velocity=5.0,
            ),
            activate_contact_sensors=False,
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0, 0, 0),
            rot=(1.0, 0.0, 0.0, 0.0),
            joint_pos={
                "shoulder_pan_joint": 0.0,
                "shoulder_lift_joint": -1.5708,
                "elbow_joint": 1.5708,
                "wrist_1_joint": 0.0,
                "wrist_2_joint": 0.0,
                "wrist_3_joint": 0.0,
            },
        ),
        actuators={
            "arm": ImplicitActuatorCfg(
                joint_names_expr=[".*"],
                effort_limit_sim=87.0,
                stiffness=800.0,
                damping=40.0,
            ),
        },
    )

    # lights
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(color=(0.75, 0.75, 0.75), intensity=2500.0),
    )

    # table = AssetBaseCfg(
    #     prim_path="{ENV_REGEX_NS}/Table",
    #     spawn=sim_utils.UsdFileCfg(
    #         usd_path=f"{ISAAC_NUCLEUS_DIR}/Props/Mounts/SeattleLabTable/table_instanceable.usd",
    #     ),
    #     init_state=AssetBaseCfg.InitialStateCfg(pos=(0.55, 0.0, 0.0), rot=(0.70711, 0.0, 0.0, 0.70711)),
    # )

    # world
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.GroundPlaneCfg(),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -1.05)),
    )

    aic_scene = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/aic_scene",
        spawn=sim_utils.UsdFileCfg(
            usd_path=os.path.join(INTRINSIC_SCENE_DIR, "scene", "aic.usd"),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(0.55, 0.0, -1.15),
            rot=(1.0, 0.0, 0.0, 0.0),
        ),
    )

    task_board = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/task_board",
        spawn=sim_utils.UsdFileCfg(
            usd_path=os.path.join(
                INTRINSIC_PARTS_DIR, "Task Board Base", "base_visual.usd"
            ),
            scale=(0.00001, 0.00001, 0.00001),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(0.7479, -0.113, 0.01),
            rot=(0.0, -0.7071, -0.0, 0.7071),
        ),
    )

    sc_port = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/sc_port",
        spawn=sim_utils.UsdFileCfg(
            usd_path=os.path.join(INTRINSIC_PARTS_DIR, "SC Port", "sc_port_visual.usd"),
            scale=(0.005, 0.005, 0.005),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(0.668, -0.078, 0.05),
            rot=(0.70711, 0.70711, 0.0, 0.0),
        ),
    )

    nic_card = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/nic_card",
        spawn=sim_utils.UsdFileCfg(
            usd_path=os.path.join(
                INTRINSIC_PARTS_DIR, "NIC Card", "nic_card_visual.usd"
            ),
            scale=(0.009, 0.009, 0.009),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(0.938, -0.078, 0.11),
            rot=(0.5, -0.5, -0.5, 0.5),
        ),
    )

    nic_card_mount = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/nic_card_mount",
        spawn=sim_utils.UsdFileCfg(
            usd_path=os.path.join(
                INTRINSIC_PARTS_DIR, "NIC Card Mount", "nic_card_mount_visual.usd"
            ),
            scale=(0.00001, 0.00001, 0.00001),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(1.02, -0.010, 0.080),
            rot=(0.7073, 0.7073, 0.7073, -0.7073),
        ),
    )

    cable = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/cable",
        spawn=sim_utils.UsdFileCfg(
            usd_path=os.path.join(INTRINSIC_ASSET_DIR, "cable_0217.usd"),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(0.4, 0, 0.2),
            rot=(0.7071, 0, 0, 0.7071),
        ),
    )

    def __post_init__(self):
        super().__post_init__()

        self.center_camera = TiledCameraCfg(
            prim_path="{ENV_REGEX_NS}/Robot/ur5e/camera_block/basler_cam_center/Camera",
            # update_period=0.1,
            height=480,
            width=640,
            data_types=["rgb"],
            spawn=None,  # the camera is already spawned in the scene
        )

        self.left_camera = TiledCameraCfg(
            prim_path="{ENV_REGEX_NS}/Robot/ur5e/camera_block/basler_cam_left/Camera",
            # update_period=0.1,
            height=480,
            width=640,
            data_types=["rgb"],
            spawn=None,  # the camera is already spawned in the scene
        )

        self.right_camera = TiledCameraCfg(
            prim_path="{ENV_REGEX_NS}/Robot/ur5e/camera_block/basler_cam_right/Camera",
            # update_period=0.1,
            height=480,
            width=640,
            data_types=["rgb"],
            spawn=None,  # the camera is already spawned in the scene
        )


##
# MDP settings
##


@configclass
class CommandsCfg:
    """Command terms for the MDP."""

    ee_pose = mdp.UniformPoseCommandCfg(
        asset_name="robot",
        body_name=MISSING,
        resampling_time_range=(4.0, 4.0),
        debug_vis=True,
        ranges=mdp.UniformPoseCommandCfg.Ranges(
            pos_x=(0.35, 0.65),
            pos_y=(-0.2, 0.2),
            pos_z=(0.15, 0.5),
            roll=(0.0, 0.0),
            pitch=MISSING,  # depends on end-effector axis
            yaw=(-3.14, 3.14),
        ),
    )


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""

    arm_action: ActionTerm = MISSING
    gripper_action: ActionTerm | None = None


@configclass
class EventCfg:
    """Configuration for events."""

    reset_robot_joints = EventTerm(
        func=mdp.reset_joints_by_scale,
        mode="reset",
        params={
            "position_range": (0.5, 1.5),
            "velocity_range": (0.0, 0.0),
        },
    )


@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""

    time_out = DoneTerm(func=mdp.time_out, time_out=True)


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP: robot state, ee pose, pose command."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for policy: joint state, ee pose, pose command."""

        # Robot state (joint space)
        joint_pos = ObsTerm(
            func=mdp.joint_pos_rel, noise=Unoise(n_min=-0.01, n_max=0.01)
        )
        joint_vel = ObsTerm(
            func=mdp.joint_vel_rel, noise=Unoise(n_min=-0.01, n_max=0.01)
        )
        # End-effector pose in env frame (pos xyz + quat wxyz = 7 dims)
        eef_pose = ObsTerm(
            func=mdp.body_pose_w,
            params={"asset_cfg": SceneEntityCfg("robot", body_names="wrist_3_link")},
            noise=Unoise(n_min=-0.001, n_max=0.001),
        )
        # Command (target ee pose)
        pose_command = ObsTerm(
            func=mdp.generated_commands, params={"command_name": "ee_pose"}
        )

        # Body forces
        body_forces = ObsTerm(
            func=mdp.body_incoming_wrench,
            scale=0.1,
            params={
                "asset_cfg": SceneEntityCfg(
                    "robot",
                    body_names=[
                        "base_link",
                        "shoulder_link",
                        "upper_arm_link",
                        "forearm_link",
                        "wrist_1_link",
                        "wrist_2_link",
                        "wrist_3_link",
                    ],
                )
            },
        )

        center_rgb = ObsTerm(
            func=mdp.image,  # Or mdp.image_features
            params={"sensor_cfg": SceneEntityCfg("center_camera"), "data_type": "rgb"},
        )

        left_rgb = ObsTerm(
            func=mdp.image,  # Or mdp.image_features
            params={"sensor_cfg": SceneEntityCfg("left_camera"), "data_type": "rgb"},
        )

        right_rgb = ObsTerm(
            func=mdp.image,  # Or mdp.image_features
            params={"sensor_cfg": SceneEntityCfg("right_camera"), "data_type": "rgb"},
        )

        # Last action
        actions = ObsTerm(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = False

    # observation groups
    policy: PolicyCfg = PolicyCfg()


@configclass
class RewardsCfg:
    """Reward terms for the MDP."""

    # task terms
    end_effector_position_tracking = RewTerm(
        func=mdp.position_command_error,
        weight=-0.2,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=MISSING),
            "command_name": "ee_pose",
        },
    )
    end_effector_position_tracking_fine_grained = RewTerm(
        func=mdp.position_command_error_tanh,
        weight=0.1,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=MISSING),
            "std": 0.1,
            "command_name": "ee_pose",
        },
    )
    end_effector_orientation_tracking = RewTerm(
        func=mdp.orientation_command_error,
        weight=-0.1,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=MISSING),
            "command_name": "ee_pose",
        },
    )

    # action penalty
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.0001)
    joint_vel = RewTerm(
        func=mdp.joint_vel_l2,
        weight=-0.0001,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )


##
# Environment configuration
##


@configclass
class IntrinsicTaskEnvCfg(ManagerBasedRLEnvCfg):
    """Intrinsic task env: UR5e robot and custom scene."""

    # Scene settings
    scene: IntrinsicTaskSceneCfg = IntrinsicTaskSceneCfg(num_envs=1, env_spacing=4.0)
    # Basic settings
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    # MDP settings
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()

    def __post_init__(self) -> None:
        super().__post_init__()

        # General settings
        self.decimation = 2
        self.sim.render_interval = self.decimation
        self.episode_length_s = 12.0
        self.sim.dt = 1.0 / 60.0
        self.viewer.eye = (8.0, 0.0, 5.0)

        # Override reward/command body to UR end-effector
        self.rewards.end_effector_position_tracking.params["asset_cfg"].body_names = [
            "wrist_3_link"
        ]
        self.rewards.end_effector_position_tracking_fine_grained.params[
            "asset_cfg"
        ].body_names = ["wrist_3_link"]
        self.rewards.end_effector_orientation_tracking.params[
            "asset_cfg"
        ].body_names = ["wrist_3_link"]

        # Arm action: joint position control
        self.actions.arm_action = JointPositionActionCfg(
            asset_name="robot", joint_names=[".*"], scale=0.5, use_default_offset=True
        )

        # Command generator: end-effector body and pitch (wrist_3_link, EE along x)
        self.commands.ee_pose.body_name = "wrist_3_link"
        self.commands.ee_pose.ranges.pitch = (math.pi / 2, math.pi / 2)

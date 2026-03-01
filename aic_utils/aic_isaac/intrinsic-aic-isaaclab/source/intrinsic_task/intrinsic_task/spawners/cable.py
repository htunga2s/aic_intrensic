from pxr import Usd, UsdGeom, Gf, UsdPhysics, UsdShade, Sdf, PhysxSchema
from omni.physx.scripts import physicsUtils

from isaaclab.sim.spawners.spawner_cfg import RigidObjectSpawnerCfg
from isaaclab.sim.utils import clone, create_prim, get_current_stage
from isaaclab.sim import schemas
from isaaclab.utils import configclass
from collections.abc import Callable

from isaaclab.sim.utils.stage import get_current_stage


# 1. Config class
@configclass
class CableCfg(RigidObjectSpawnerCfg):
    """Config for a cable/rope."""
    func: Callable = None  # Set below after function definition
    rope_length: float = 1.0      # total rope length in meters
    link_radius: float = 0.01     # capsule radius in meters
    spawn_height: float = 0.5     # Z height at which the rope is spawned


# 2. Spawner function
@clone  # Handles regex prim paths + cloning across envs
def spawn_cable(
    prim_path: str,
    cfg: CableCfg,
    translation: tuple[float, float, float] | None = None,
    orientation: tuple[float, float, float, float] | None = None,
    **kwargs,
) -> Usd.Prim:
    """Spawn a cuboid with a sphere on top."""
    stage = get_current_stage()

    # # Create root Xform
    # create_prim(prim_path, "Xform", translation=translation, orientation=orientation, stage=stage)

    # # Create cuboid base
    # base_path = f"{prim_path}/geometry/base"
    # base_prim = UsdGeom.Cube.Define(stage, base_path)
    # base_prim.GetSizeAttr().Set(1.0)
    # UsdGeom.Xformable(base_prim).AddScaleOp().Set(cfg.base_size)

    # # Create sphere on top
    # sphere_path = f"{prim_path}/geometry/sphere"
    # sphere_prim = UsdGeom.Sphere.Define(stage, sphere_path)
    # sphere_prim.GetRadiusAttr().Set(cfg.sphere_radius)
    # offset = (0.0, 0.0, cfg.base_size[2] / 2 + cfg.sphere_radius)
    # UsdGeom.Xformable(sphere_prim).AddTranslateOp().Set(offset)

    # # Apply physics properties
    # if cfg.collision_props is not None:
    #     schemas.define_collision_properties(base_path, cfg.collision_props, stage=stage)
    #     schemas.define_collision_properties(sphere_path, cfg.collision_props, stage=stage)
    # if cfg.rigid_props is not None:
    #     schemas.define_rigid_body_properties(prim_path, cfg.rigid_props, stage=stage)
    # if cfg.mass_props is not None:
    #     schemas.define_mass_properties(prim_path, cfg.mass_props, stage=stage)


    # configure ropes (all units in meters):
    linkRadius = cfg.link_radius              # e.g. 0.01 m
    linkHalfLength = linkRadius * 2.0         # capsule half-height; keeps a reasonable aspect ratio
    ropeLength = cfg.rope_length              # e.g. 1.0 m
    ropeColor = Gf.Vec3f(0.9, 0.5, 0.5)
    coneAngleLimit = 110
    rope_damping = 10.0
    rope_stiffness = 1.0
    contactOffset = linkRadius * 0.2          # small relative to link size

    stage = get_current_stage()
    UsdShade.Material.Define(stage, f"{prim_path}/PhysicsMaterial")
    material = UsdPhysics.MaterialAPI.Apply(stage.GetPrimAtPath(f"{prim_path}/PhysicsMaterial"))
    material.CreateStaticFrictionAttr().Set(0.5)
    material.CreateDynamicFrictionAttr().Set(0.5)
    material.CreateRestitutionAttr().Set(0)

    linkLength = 2.0 * linkHalfLength - linkRadius
    numLinks = max(1, int(ropeLength / linkLength))
    xStart = -numLinks * linkLength * 0.5
    yStart = 0.0

    scopePath = Sdf.Path(prim_path).AppendChild("Rope")
    UsdGeom.Scope.Define(stage, scopePath)

    y = yStart
    z = cfg.spawn_height
    jointX = linkHalfLength - 0.5 * linkRadius

    # Create one capsule prim per link
    linkPaths = []
    for linkInd in range(numLinks):
        linkPath = scopePath.AppendChild(f"link_{linkInd}")
        linkPaths.append(linkPath)

        capsuleGeom = UsdGeom.Capsule.Define(stage, linkPath)
        capsuleGeom.CreateHeightAttr(linkHalfLength)
        capsuleGeom.CreateRadiusAttr(linkRadius)
        capsuleGeom.CreateAxisAttr("X")
        capsuleGeom.CreateDisplayColorAttr().Set([ropeColor])

        x = xStart + linkInd * linkLength
        UsdGeom.Xformable(capsuleGeom).AddTranslateOp().Set(Gf.Vec3d(x, y, z))

        prim = capsuleGeom.GetPrim()
        UsdPhysics.CollisionAPI.Apply(prim)
        UsdPhysics.RigidBodyAPI.Apply(prim)
        massAPI = UsdPhysics.MassAPI.Apply(prim)
        massAPI.CreateDensityAttr().Set(0.00005)
        physxCollisionAPI = PhysxSchema.PhysxCollisionAPI.Apply(prim)
        physxCollisionAPI.CreateRestOffsetAttr().Set(0.0)
        physxCollisionAPI.CreateContactOffsetAttr().Set(contactOffset)
        physicsUtils.add_physics_material_to_prim(stage, prim, f"{prim_path}/PhysicsMaterial")

    # Create one joint prim per consecutive link pair
    for linkInd in range(numLinks - 1):
        jointPath = scopePath.AppendChild(f"joint_{linkInd}_{linkInd + 1}")
        joint = UsdPhysics.Joint.Define(stage, jointPath)

        joint.GetBody0Rel().SetTargets([linkPaths[linkInd]])
        joint.GetBody1Rel().SetTargets([linkPaths[linkInd + 1]])
        joint.CreateLocalPos0Attr().Set(Gf.Vec3f(jointX, 0, 0))
        joint.CreateLocalPos1Attr().Set(Gf.Vec3f(-jointX, 0, 0))
        joint.CreateLocalRot0Attr().Set(Gf.Quatf(1.0))
        joint.CreateLocalRot1Attr().Set(Gf.Quatf(1.0))

        d6Prim = joint.GetPrim()

        # Locked DOFs (low > high means locked)
        for dof in ["transX", "transY", "transZ", "rotX"]:
            limitAPI = UsdPhysics.LimitAPI.Apply(d6Prim, dof)
            limitAPI.CreateLowAttr(1.0)
            limitAPI.CreateHighAttr(-1.0)

        # Free DOFs with drives for rope dynamics
        for dof in ["rotY", "rotZ"]:
            limitAPI = UsdPhysics.LimitAPI.Apply(d6Prim, dof)
            limitAPI.CreateLowAttr(-coneAngleLimit)
            limitAPI.CreateHighAttr(coneAngleLimit)

            driveAPI = UsdPhysics.DriveAPI.Apply(d6Prim, dof)
            driveAPI.CreateTypeAttr("force")
            driveAPI.CreateDampingAttr(rope_damping)
            driveAPI.CreateStiffnessAttr(rope_stiffness)


    return stage.GetPrimAtPath(prim_path)


# 3. Link function to config
CableCfg.func = spawn_cable
